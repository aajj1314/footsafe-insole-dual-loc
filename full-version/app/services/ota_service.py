# -*- coding: utf-8 -*-
"""
OTA服务模块
"""

import uuid
import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database.mysql import mysql_pool
from app.core.logger import logger
from app.config.constants import (
    OTA_STATUS_DOWNLOADING,
    OTA_STATUS_VERIFYING,
    OTA_STATUS_UPGRADING,
    OTA_STATUS_SUCCESS,
    OTA_STATUS_FAILED,
)


class OTAService:
    """OTA升级服务"""

    async def create_task(
        self,
        device_id: str,
        upgrade_id: str,
        version: str,
        url: str,
        size: int,
        checksum: str,
    ) -> bool:
        """
        创建OTA任务

        Args:
            device_id: 设备IMEI
            upgrade_id: 升级任务ID
            version: 目标版本
            url: 固件URL
            size: 固件大小
            checksum: 校验和

        Returns:
            是否创建成功
        """
        try:
            await mysql_pool.execute_write(
                """
                INSERT INTO ota_tasks (
                    upgrade_id, device_id, version, url, size, checksum,
                    status, progress, created_at, updated_at
                )
                VALUES (
                    :upgrade_id, :device_id, :version, :url, :size, :checksum,
                    'pending', 0, NOW(), NOW()
                )
                """,
                {
                    "upgrade_id": upgrade_id,
                    "device_id": device_id,
                    "version": version,
                    "url": url,
                    "size": size,
                    "checksum": checksum,
                },
            )

            logger.info(
                f"OTA task created: upgrade_id={upgrade_id}, "
                f"device={device_id}, version={version}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to create OTA task: {e}")
            return False

    async def update_progress(
        self,
        upgrade_id: str,
        status: str,
        progress: int,
        error_code: int = 0,
        error_message: str = "",
    ) -> bool:
        """
        更新OTA进度

        Args:
            upgrade_id: 升级任务ID
            status: 状态
            progress: 进度
            error_code: 错误码
            error_message: 错误信息

        Returns:
            是否更新成功
        """
        try:
            updates = {
                "status": status,
                "progress": progress,
                "error_code": error_code,
                "error_message": error_message,
            }

            if status == OTA_STATUS_DOWNLOADING:
                updates["started_at"] = datetime.utcnow()
            elif status in (OTA_STATUS_SUCCESS, OTA_STATUS_FAILED):
                updates["completed_at"] = datetime.utcnow()

            set_clauses = [f"{k} = :{k}" for k in updates.keys()]
            set_clauses.append("updated_at = NOW()")

            sql = f"UPDATE ota_tasks SET {', '.join(set_clauses)} WHERE upgrade_id = :upgrade_id"
            params = {"upgrade_id": upgrade_id, **updates}

            await mysql_pool.execute_write(sql, params)

            logger.info(
                f"OTA progress updated: upgrade_id={upgrade_id}, "
                f"status={status}, progress={progress}%"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to update OTA progress: {e}")
            return False

    async def get_task(self, upgrade_id: str) -> Optional[Dict[str, Any]]:
        """
        获取OTA任务信息

        Args:
            upgrade_id: 升级任务ID

        Returns:
            任务信息或None
        """
        try:
            return await mysql_pool.execute_one(
                "SELECT * FROM ota_tasks WHERE upgrade_id = :upgrade_id",
                {"upgrade_id": upgrade_id},
            )

        except Exception as e:
            logger.error(f"Failed to get OTA task: {e}")
            return None

    async def get_device_tasks(
        self,
        device_id: str,
        status: Optional[str] = None,
    ) -> list:
        """
        获取设备的OTA任务列表

        Args:
            device_id: 设备IMEI
            status: 状态过滤

        Returns:
            任务列表
        """
        try:
            if status:
                return await mysql_pool.execute(
                    """
                    SELECT * FROM ota_tasks
                    WHERE device_id = :device_id AND status = :status
                    ORDER BY created_at DESC
                    """,
                    {"device_id": device_id, "status": status},
                )
            else:
                return await mysql_pool.execute(
                    """
                    SELECT * FROM ota_tasks
                    WHERE device_id = :device_id
                    ORDER BY created_at DESC
                    """,
                    {"device_id": device_id},
                )

        except Exception as e:
            logger.error(f"Failed to get device OTA tasks: {e}")
            return []


# 全局OTA服务实例
ota_service = OTAService()


# ==================== 消息处理器 ====================


async def handle_ota_progress(message: Dict[str, Any], conn) -> None:
    """
    处理OTA进度上报消息

    Args:
        message: 消息字典
        conn: TCP连接对象
    """
    from app.core.security.checksum import verify_checksum
    from app.core.security.nonce import nonce_manager
    from app.config.settings import settings

    device_id = message.get("device_id")
    data = message.get("data", {})

    upgrade_id = data.get("upgrade_id")
    status = data.get("status")
    progress = data.get("progress")
    error_code = data.get("error_code", 0)
    error_message = data.get("error_message", "")

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

    # 更新OTA进度
    await ota_service.update_progress(
        upgrade_id,
        status,
        progress,
        error_code,
        error_message,
    )

    logger.info(
        f"OTA progress processed: upgrade_id={upgrade_id}, "
        f"device={device_id}, status={status}, progress={progress}%"
    )
