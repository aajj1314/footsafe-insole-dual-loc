# -*- coding: utf-8 -*-
"""
命令服务模块
"""

import uuid
import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database.mysql import mysql_pool
from app.core.logger import logger
from app.config.constants import (
    COMMAND_RESULT_SUCCESS,
    COMMAND_RESULT_FAILED,
)


class CommandService:
    """命令服务"""

    async def create_command(
        self,
        device_id: str,
        command_type: str,
        command_data: Optional[Dict[str, Any]] = None,
        protocol: str = "tcp",
        max_retries: int = 3,
    ) -> Optional[str]:
        """
        创建命令记录

        Args:
            device_id: 设备IMEI
            command_type: 命令类型
            command_data: 命令数据
            protocol: 协议类型
            max_retries: 最大重试次数

        Returns:
            命令ID或None
        """
        command_id = str(uuid.uuid4())

        try:
            await mysql_pool.execute_write(
                """
                INSERT INTO commands (
                    command_id, device_id, command_type, command_data,
                    protocol, status, max_retries, created_at
                )
                VALUES (
                    :command_id, :device_id, :command_type, :command_data,
                    :protocol, 'pending', :max_retries, NOW()
                )
                """,
                {
                    "command_id": command_id,
                    "device_id": device_id,
                    "command_type": command_type,
                    "command_data": json.dumps(command_data) if command_data else None,
                    "protocol": protocol,
                    "max_retries": max_retries,
                },
            )

            logger.info(
                f"Command created: {command_id}, device: {device_id}, "
                f"type: {command_type}"
            )

            return command_id

        except Exception as e:
            logger.error(f"Failed to create command: {e}")
            return None

    async def update_command_status(
        self,
        command_id: str,
        status: str,
        result: Optional[str] = None,
        result_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        更新命令状态

        Args:
            command_id: 命令ID
            status: 状态
            result: 执行结果
            result_data: 结果数据

        Returns:
            是否更新成功
        """
        try:
            updates = {"status": status}

            if result:
                updates["result"] = result

            if result_data:
                updates["result_data"] = json.dumps(result_data)

            if status == "sent":
                updates["sent_at"] = datetime.utcnow()
            elif status == "acknowledged":
                updates["acknowledged_at"] = datetime.utcnow()

            set_clauses = [f"{k} = :{k}" for k in updates.keys()]
            set_clauses.append("updated_at = NOW()")

            sql = f"UPDATE commands SET {', '.join(set_clauses)} WHERE command_id = :command_id"
            params = {"command_id": command_id, **updates}

            await mysql_pool.execute_write(sql, params)

            return True

        except Exception as e:
            logger.error(f"Failed to update command status: {e}")
            return False

    async def get_pending_commands(self, device_id: str) -> list:
        """
        获取设备的待处理命令

        Args:
            device_id: 设备IMEI

        Returns:
            命令列表
        """
        try:
            return await mysql_pool.execute(
                """
                SELECT * FROM commands
                WHERE device_id = :device_id AND status = 'pending'
                ORDER BY created_at ASC
                """,
                {"device_id": device_id},
            )

        except Exception as e:
            logger.error(f"Failed to get pending commands: {e}")
            return []

    async def get_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        """
        获取命令信息

        Args:
            command_id: 命令ID

        Returns:
            命令信息或None
        """
        try:
            return await mysql_pool.execute_one(
                "SELECT * FROM commands WHERE command_id = :command_id",
                {"command_id": command_id},
            )

        except Exception as e:
            logger.error(f"Failed to get command: {e}")
            return None


# 全局命令服务实例
command_service = CommandService()


# ==================== 消息处理器 ====================


async def handle_command_response(message: Dict[str, Any], remote_addr: tuple) -> None:
    """
    处理命令响应消息

    Args:
        message: 消息字典
        remote_addr: 远程地址
    """
    from app.core.security.checksum import verify_checksum
    from app.core.security.nonce import nonce_manager
    from app.config.settings import settings

    device_id = message.get("device_id")
    data = message.get("data", {})

    command_id = data.get("command_id")
    command_type = data.get("command_type")
    result = data.get("result")
    result_data = data.get("result_data")

    # 验证nonce
    nonce = message.get("nonce")
    timestamp = message.get("timestamp")
    if not await nonce_manager.is_nonce_valid(nonce, timestamp):
        logger.warning(f"Invalid nonce for device: {device_id}")
        return

    # 验证校验和
    checksum = message.get("checksum")
    if not verify_checksum(
        message["version"],
        device_id,
        timestamp,
        nonce,
        data,
        checksum,
        settings.DEVICE_PRESHARED_KEY,
    ):
        logger.warning(f"Checksum failed for device: {device_id}")
        return

    # 更新命令状态
    if result == COMMAND_RESULT_SUCCESS:
        await command_service.update_command_status(
            command_id,
            "acknowledged",
            COMMAND_RESULT_SUCCESS,
            result_data,
        )
    else:
        await command_service.update_command_status(
            command_id,
            "timeout",
            COMMAND_RESULT_FAILED,
            result_data,
        )

    logger.info(
        f"Command response processed: command_id={command_id}, "
        f"device={device_id}, result={result}"
    )


async def handle_tcp_heartbeat(message: Dict[str, Any], conn) -> bytes:
    """
    处理TCP心跳消息

    Args:
        message: 消息字典
        conn: TCP连接对象

    Returns:
        响应字节
    """
    from app.core.security.checksum import verify_checksum
    from app.core.security.nonce import nonce_manager
    from app.protocol.serializer import ResponseSerializer
    from app.protocol.tcp.session import tcp_session_manager
    from app.config.settings import settings
    from app.config.constants import ERROR_SUCCESS

    device_id = message.get("device_id")
    session_id = message.get("session_id")
    data = message.get("data", {})

    # 验证会话
    if not await tcp_session_manager.validate_session(session_id, device_id):
        logger.warning(f"Invalid session for device: {device_id}")
        return ResponseSerializer.serialize_error(3001, "session_invalid")

    # 验证nonce
    nonce = message.get("nonce")
    timestamp = message.get("timestamp")
    if not await nonce_manager.is_nonce_valid(nonce, timestamp):
        logger.warning(f"Invalid nonce for device: {device_id}")
        return ResponseSerializer.serialize_error(1002, "checksum_failed")

    # 验证校验和
    checksum = message.get("checksum")
    if not verify_checksum(
        message["version"],
        device_id,
        timestamp,
        nonce,
        data,
        checksum,
        settings.DEVICE_PRESHARED_KEY,
    ):
        logger.warning(f"Checksum failed for device: {device_id}")
        return ResponseSerializer.serialize_error(1002, "checksum_failed")

    # 更新会话
    await tcp_session_manager.update_session(session_id)

    # 更新设备状态
    from app.services.device_service import device_service
    await device_service.update_status(device_id, "online")

    # 更新连接信息
    conn.session_id = session_id
    conn.is_authenticated = True

    logger.debug(f"TCP heartbeat processed for device: {device_id}")

    return ResponseSerializer.serialize_success()
