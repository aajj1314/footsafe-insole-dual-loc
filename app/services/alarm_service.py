# -*- coding: utf-8 -*-
"""
报警服务模块
"""

import uuid
import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database.mysql import mysql_pool
from app.core.logger import logger
from app.services.device_service import device_service
from app.services.push_service import push_service
from app.config.constants import (
    ALARM_TYPE_TAMPER,
    ALARM_TYPE_FALL,
    ALARM_TYPE_STILL,
    ALARM_TYPE_LOW_BATTERY,
    ALARM_TYPE_SOS,
    ALARM_TYPE_SHUTDOWN,
    ALARM_LEVEL_LOW,
    ALARM_LEVEL_MEDIUM,
    ALARM_LEVEL_HIGH,
    ALARM_LEVEL_URGENT,
)


class AlarmService:
    """报警服务"""

    async def create_alarm(
        self,
        device_id: str,
        alarm_type: int,
        alarm_level: int,
        latitude: float,
        longitude: float,
        accuracy: float,
        battery: int,
        alarm_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        创建报警记录

        Args:
            device_id: 设备IMEI
            alarm_type: 报警类型
            alarm_level: 报警级别
            latitude: 纬度
            longitude: 经度
            accuracy: 定位精度
            battery: 电量百分比
            alarm_data: 报警附加数据

        Returns:
            报警ID或None
        """
        alarm_id = str(uuid.uuid4())

        try:
            await mysql_pool.execute_write(
                """
                INSERT INTO alarms (
                    alarm_id, device_id, alarm_type, alarm_level,
                    latitude, longitude, accuracy, battery,
                    alarm_data, status, created_at, updated_at
                )
                VALUES (
                    :alarm_id, :device_id, :alarm_type, :alarm_level,
                    :latitude, :longitude, :accuracy, :battery,
                    :alarm_data, 'pending', NOW(), NOW()
                )
                """,
                {
                    "alarm_id": alarm_id,
                    "device_id": device_id,
                    "alarm_type": alarm_type,
                    "alarm_level": alarm_level,
                    "latitude": str(latitude),
                    "longitude": str(longitude),
                    "accuracy": str(accuracy),
                    "battery": battery,
                    "alarm_data": json.dumps(alarm_data) if alarm_data else None,
                },
            )

            logger.info(
                f"Alarm created: {alarm_id}, device: {device_id}, "
                f"type: {alarm_type}, level: {alarm_level}"
            )

            return alarm_id

        except Exception as e:
            logger.error(f"Failed to create alarm: {e}")
            return None

    async def update_alarm_status(
        self,
        alarm_id: str,
        status: str,
        push_count: Optional[int] = None,
    ) -> bool:
        """
        更新报警状态

        Args:
            alarm_id: 报警ID
            status: 状态
            push_count: 推送次数

        Returns:
            是否更新成功
        """
        try:
            if push_count is not None:
                await mysql_pool.execute_write(
                    """
                    UPDATE alarms
                    SET status = :status, push_count = :push_count, updated_at = NOW()
                    WHERE alarm_id = :alarm_id
                    """,
                    {"alarm_id": alarm_id, "status": status, "push_count": push_count},
                )
            else:
                await mysql_pool.execute_write(
                    """
                    UPDATE alarms
                    SET status = :status, updated_at = NOW()
                    WHERE alarm_id = :alarm_id
                    """,
                    {"alarm_id": alarm_id, "status": status},
                )

            return True

        except Exception as e:
            logger.error(f"Failed to update alarm status: {e}")
            return False

    async def get_device_alarms(
        self,
        device_id: str,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> list:
        """
        获取设备报警列表

        Args:
            device_id: 设备IMEI
            status: 状态过滤
            limit: 返回条数限制

        Returns:
            报警列表
        """
        try:
            if status:
                return await mysql_pool.execute(
                    """
                    SELECT * FROM alarms
                    WHERE device_id = :device_id AND status = :status
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """,
                    {"device_id": device_id, "status": status, "limit": limit},
                )
            else:
                return await mysql_pool.execute(
                    """
                    SELECT * FROM alarms
                    WHERE device_id = :device_id
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """,
                    {"device_id": device_id, "limit": limit},
                )

        except Exception as e:
            logger.error(f"Failed to get device alarms: {e}")
            return []

    def get_alarm_level(self, alarm_type: int) -> int:
        """
        根据报警类型获取报警级别

        Args:
            alarm_type: 报警类型

        Returns:
            报警级别
        """
        alarm_levels = {
            ALARM_TYPE_LOW_BATTERY: ALARM_LEVEL_LOW,
            ALARM_TYPE_STILL: ALARM_LEVEL_MEDIUM,
            ALARM_TYPE_TAMPER: ALARM_LEVEL_MEDIUM,
            ALARM_TYPE_FALL: ALARM_LEVEL_HIGH,
            ALARM_TYPE_SOS: ALARM_LEVEL_URGENT,
            ALARM_TYPE_SHUTDOWN: ALARM_LEVEL_URGENT,
        }
        return alarm_levels.get(alarm_type, ALARM_LEVEL_MEDIUM)


# 全局报警服务实例
alarm_service = AlarmService()


# ==================== 消息处理器 ====================


async def handle_alarm(message: Dict[str, Any], remote_addr: tuple) -> None:
    """
    处理报警上报消息

    Args:
        message: 消息字典
        remote_addr: 远程地址
    """
    from app.core.security.checksum import verify_checksum
    from app.core.security.nonce import nonce_manager
    from app.config.settings import settings
    from app.protocol.validator import message_validator
    from app.core.security.audit import security_auditor

    device_id = message.get("device_id")
    data = message.get("data", {})

    # 验证消息格式
    valid, error = message_validator.validate_base(message)
    if not valid:
        logger.warning(f"Invalid alarm message: {error}")
        return

    # 验证报警数据
    valid, error = message_validator.validate_alarm(data)
    if not valid:
        logger.warning(f"Invalid alarm data: {error}")
        return

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

    alarm_type = data.get("alarm_type")
    alarm_level = data.get("alarm_level")

    # 根据报警类型确定报警级别
    if alarm_level is None:
        alarm_level = alarm_service.get_alarm_level(alarm_type)

    # 创建报警记录
    alarm_id = await alarm_service.create_alarm(
        device_id=device_id,
        alarm_type=alarm_type,
        alarm_level=alarm_level,
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        accuracy=data.get("accuracy"),
        battery=data.get("battery"),
        alarm_data=data.get("alarm_data"),
    )

    if not alarm_id:
        logger.error(f"Failed to create alarm for device: {device_id}")
        return

    # 更新设备状态为报警中
    await device_service.update_status(device_id, "alarm")

    # 记录安全审计日志
    security_auditor.log_alarm_triggered(device_id, alarm_type, alarm_level)

    # 推送报警给用户
    await push_service.push_alarm(device_id, alarm_id, data, alarm_type, alarm_level)

    logger.info(
        f"Alarm processed: device={device_id}, alarm_id={alarm_id}, "
        f"type={alarm_type}, level={alarm_level}"
    )
