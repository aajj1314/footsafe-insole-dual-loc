# -*- coding: utf-8 -*-
"""
错误服务模块
"""

import uuid
import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database.mysql import mysql_pool
from app.core.logger import logger


class ErrorService:
    """设备错误服务"""

    async def create_error(
        self,
        device_id: str,
        error_type: str,
        error_level: int,
        error_code: int,
        error_message: str,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        创建设备错误记录

        Args:
            device_id: 设备IMEI
            error_type: 错误类型
            error_level: 错误级别
            error_code: 错误码
            error_message: 错误信息
            extra_data: 附加数据

        Returns:
            错误ID或None
        """
        error_id = str(uuid.uuid4())

        try:
            await mysql_pool.execute_write(
                """
                INSERT INTO device_errors (
                    error_id, device_id, error_type, error_level,
                    error_code, error_message, extra_data, status, created_at
                )
                VALUES (
                    :error_id, :device_id, :error_type, :error_level,
                    :error_code, :error_message, :extra_data, 'pending', NOW()
                )
                """,
                {
                    "error_id": error_id,
                    "device_id": device_id,
                    "error_type": error_type,
                    "error_level": error_level,
                    "error_code": error_code,
                    "error_message": error_message,
                    "extra_data": json.dumps(extra_data) if extra_data else None,
                },
            )

            logger.warning(
                f"Device error created: error_id={error_id}, device={device_id}, "
                f"type={error_type}, code={error_code}"
            )

            return error_id

        except Exception as e:
            logger.error(f"Failed to create device error: {e}")
            return None

    async def resolve_error(self, error_id: str) -> bool:
        """
        解决设备错误

        Args:
            error_id: 错误ID

        Returns:
            是否解决成功
        """
        try:
            await mysql_pool.execute_write(
                """
                UPDATE device_errors
                SET status = 'resolved', resolved_at = NOW()
                WHERE error_id = :error_id
                """,
                {"error_id": error_id},
            )

            return True

        except Exception as e:
            logger.error(f"Failed to resolve device error: {e}")
            return False

    async def get_device_errors(
        self,
        device_id: str,
        status: Optional[str] = None,
    ) -> list:
        """
        获取设备错误列表

        Args:
            device_id: 设备IMEI
            status: 状态过滤

        Returns:
            错误列表
        """
        try:
            if status:
                return await mysql_pool.execute(
                    """
                    SELECT * FROM device_errors
                    WHERE device_id = :device_id AND status = :status
                    ORDER BY created_at DESC
                    """,
                    {"device_id": device_id, "status": status},
                )
            else:
                return await mysql_pool.execute(
                    """
                    SELECT * FROM device_errors
                    WHERE device_id = :device_id
                    ORDER BY created_at DESC
                    """,
                    {"device_id": device_id},
                )

        except Exception as e:
            logger.error(f"Failed to get device errors: {e}")
            return []


# 全局错误服务实例
error_service = ErrorService()


# ==================== 消息处理器 ====================


async def handle_device_error(message: Dict[str, Any], conn) -> None:
    """
    处理设备错误上报消息

    Args:
        message: 消息字典
        conn: TCP连接对象
    """
    from app.core.security.checksum import verify_checksum
    from app.core.security.nonce import nonce_manager
    from app.config.settings import settings

    device_id = message.get("device_id")
    data = message.get("data", {})

    error_type = data.get("error_type")
    error_level = data.get("error_level")
    error_code = data.get("error_code")
    error_message = data.get("error_message")
    extra_data = data.get("extra_data")

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

    # 创建设备错误记录
    await error_service.create_error(
        device_id=device_id,
        error_type=error_type,
        error_level=error_level,
        error_code=error_code,
        error_message=error_message,
        extra_data=extra_data,
    )

    logger.warning(
        f"Device error processed: device={device_id}, "
        f"type={error_type}, code={error_code}, message={error_message}"
    )
