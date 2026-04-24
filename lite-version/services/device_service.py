# -*- coding: utf-8 -*-
"""
设备服务模块
"""

import asyncio
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.database.mysql import mysql_pool
from app.core.database.redis import redis_pool, DeviceStateCache
from app.core.memory.cache import device_info_cache
from app.core.logger import logger
from app.config.constants import (
    ERROR_SUCCESS,
    ERROR_DEVICE_NOT_REGISTERED,
    ERROR_SESSION_INVALID,
    DEVICE_STATUS_ONLINE,
    DEVICE_STATUS_OFFLINE,
)
from app.protocol.serializer import ResponseSerializer


class DeviceService:
    """设备服务"""

    def __init__(self):
        """初始化设备服务"""
        self.device_cache = DeviceStateCache(redis_pool)

    async def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        获取设备信息

        Args:
            device_id: 设备IMEI

        Returns:
            设备信息字典或None
        """
        # 先从本地缓存获取
        cached = await device_info_cache.get_device(device_id)
        if cached:
            return cached

        # 从Redis获取
        redis_device = await self.device_cache.get_device_state(device_id)
        if redis_device:
            # 写入本地缓存
            await device_info_cache.set_device(device_id, redis_device)
            return redis_device

        # 从MySQL获取
        try:
            result = await mysql_pool.execute_one(
                "SELECT * FROM devices WHERE imei = :imei",
                {"imei": device_id},
            )

            if result:
                # 写入缓存
                await self.device_cache.set_device_state(device_id, result)
                await device_info_cache.set_device(device_id, result)
                return result

        except Exception as e:
            logger.error(f"Failed to get device from database: {e}")

        return None

    async def register_device(
        self,
        device_id: str,
        iccid: Optional[str] = None,
        firmware_version: Optional[str] = None,
        hardware_version: Optional[str] = None,
    ) -> bool:
        """
        注册设备

        Args:
            device_id: 设备IMEI
            iccid: SIM卡ICCID
            firmware_version: 固件版本
            hardware_version: 硬件版本

        Returns:
            是否注册成功
        """
        try:
            # 检查是否已存在
            existing = await self.get_device(device_id)
            if existing:
                return True

            # 插入新设备
            await mysql_pool.execute_write(
                """
                INSERT INTO devices (imei, iccid, firmware_version, hardware_version, status, created_at, updated_at)
                VALUES (:imei, :iccid, :firmware_version, :hardware_version, :status, NOW(), NOW())
                """,
                {
                    "imei": device_id,
                    "iccid": iccid,
                    "firmware_version": firmware_version,
                    "hardware_version": hardware_version,
                    "status": DEVICE_STATUS_OFFLINE,
                },
            )

            logger.info(f"Device registered: {device_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to register device: {e}")
            return False

    async def update_device(self, device_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新设备信息

        Args:
            device_id: 设备IMEI
            updates: 更新字段字典

        Returns:
            是否更新成功
        """
        try:
            # 构建更新SQL
            set_clauses = []
            params = {"imei": device_id}

            for key, value in updates.items():
                set_clauses.append(f"{key} = :{key}")
                params[key] = value

            set_clauses.append("updated_at = NOW()")

            sql = f"UPDATE devices SET {', '.join(set_clauses)} WHERE imei = :imei"
            await mysql_pool.execute_write(sql, params)

            # 清除缓存
            await self.device_cache.delete_device_state(device_id)
            await device_info_cache.delete_device(device_id)

            return True

        except Exception as e:
            logger.error(f"Failed to update device: {e}")
            return False

    async def update_location(
        self,
        device_id: str,
        latitude: float,
        longitude: float,
        battery: int,
        signal_strength: int,
        mode: str,
    ) -> bool:
        """
        更新设备位置

        Args:
            device_id: 设备IMEI
            latitude: 纬度
            longitude: 经度
            battery: 电量
            signal_strength: 信号强度
            mode: 工作模式

        Returns:
            是否更新成功
        """
        return await self.update_device(
            device_id,
            {
                "last_location_lat": str(latitude),
                "last_location_lng": str(longitude),
                "last_location_time": datetime.utcnow(),
                "battery": battery,
                "signal_strength": signal_strength,
                "mode": mode,
                "status": DEVICE_STATUS_ONLINE,
                "last_seen": datetime.utcnow(),
            },
        )

    async def update_status(self, device_id: str, status: str) -> bool:
        """
        更新设备状态

        Args:
            device_id: 设备IMEI
            status: 状态

        Returns:
            是否更新成功
        """
        return await self.update_device(
            device_id, {"status": status, "last_seen": datetime.utcnow()}
        )

    async def update_session(self, device_id: str, session_id: str) -> bool:
        """
        更新设备会话

        Args:
            device_id: 设备IMEI
            session_id: 会话ID

        Returns:
            是否更新成功
        """
        return await self.update_device(device_id, {"session_id": session_id})


# 全局设备服务实例
device_service = DeviceService()


# ==================== 消息处理器 ====================


async def handle_heartbeat(message: Dict[str, Any], remote_addr: tuple) -> None:
    """
    处理心跳消息

    Args:
        message: 消息字典
        remote_addr: 远程地址
    """
    from app.core.security.checksum import verify_checksum
    from app.core.security.nonce import nonce_manager
    from app.config.settings import settings
    from app.protocol.validator import message_validator

    device_id = message.get("device_id")
    data = message.get("data", {})

    # 验证消息格式
    valid, error = message_validator.validate_base(message)
    if not valid:
        logger.warning(f"Invalid heartbeat message: {error}")
        return

    # 验证数据
    valid, error = message_validator.validate_heartbeat(data)
    if not valid:
        logger.warning(f"Invalid heartbeat data: {error}")
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

    # 更新设备状态
    await device_service.update_device(
        device_id,
        {
            "battery": data.get("battery"),
            "signal_strength": data.get("signal_strength"),
            "status": DEVICE_STATUS_ONLINE,
            "last_seen": datetime.utcnow(),
        },
    )

    # 更新Redis心跳
    from app.protocol.tcp.session import tcp_session_manager
    await tcp_session_manager.update_session(device_id)

    logger.debug(f"Heartbeat processed for device: {device_id}")
