# -*- coding: utf-8 -*-
"""
位置服务模块
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database.influxdb import influxdb_pool
from app.core.database.redis import redis_pool, DeviceStateCache
from app.core.logger import logger
from app.services.device_service import device_service
from app.services.push_service import push_service


class LocationService:
    """位置服务"""

    def __init__(self):
        """初始化位置服务"""
        self.device_cache = DeviceStateCache(redis_pool)

    async def save_location(
        self,
        device_id: str,
        latitude: float,
        longitude: float,
        altitude: float,
        speed: float,
        direction: int,
        accuracy: float,
        satellites: int,
        battery: int,
        signal_strength: int,
        charging: bool,
        mode: str,
        gps_timestamp: str,
    ) -> bool:
        """
        保存位置数据

        Args:
            device_id: 设备IMEI
            latitude: 纬度
            longitude: 经度
            altitude: 海拔高度
            speed: 移动速度
            direction: 移动方向
            accuracy: 定位精度
            satellites: 卫星数量
            battery: 电量百分比
            signal_strength: 信号强度
            charging: 是否充电
            mode: 设备模式
            gps_timestamp: GPS时间戳

        Returns:
            是否保存成功
        """
        try:
            # 写入InfluxDB
            await influxdb_pool.write_location_data(
                device_id=device_id,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                speed=speed,
                direction=direction,
                accuracy=accuracy,
                satellites=satellites,
                battery=battery,
                signal_strength=signal_strength,
                charging=charging,
                mode=mode,
                gps_timestamp=gps_timestamp,
            )

            # 更新Redis缓存
            await self.device_cache.set_device_state(
                device_id,
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": altitude,
                    "speed": speed,
                    "direction": direction,
                    "accuracy": accuracy,
                    "battery": battery,
                    "signal_strength": signal_strength,
                    "mode": mode,
                    "gps_timestamp": gps_timestamp,
                    "updated_at": datetime.utcnow().isoformat(),
                },
            )

            # 更新MySQL设备信息
            await device_service.update_location(
                device_id,
                latitude,
                longitude,
                battery,
                signal_strength,
                mode,
            )

            logger.debug(
                f"Location saved for device: {device_id}, "
                f"lat: {latitude}, lng: {longitude}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to save location: {e}")
            return False

    async def get_latest_location(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        获取设备最新位置

        Args:
            device_id: 设备IMEI

        Returns:
            位置信息字典或None
        """
        # 先从Redis缓存获取
        cached = await self.device_cache.get_device_state(device_id)
        if cached and "latitude" in cached:
            return cached

        # 从InfluxDB获取
        return await influxdb_pool.query_latest_location(device_id)

    async def get_location_history(
        self,
        device_id: str,
        start_time: str,
        end_time: str,
        limit: int = 1000,
    ) -> list:
        """
        获取位置历史

        Args:
            device_id: 设备IMEI
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回条数限制

        Returns:
            位置历史列表
        """
        return await influxdb_pool.query_location_history(
            device_id, start_time, end_time, limit
        )


# 全局位置服务实例
location_service = LocationService()


# ==================== 消息处理器 ====================


async def handle_location(message: Dict[str, Any], remote_addr: tuple) -> None:
    """
    处理位置上报消息

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
        logger.warning(f"Invalid location message: {error}")
        return

    # 验证位置数据
    valid, error = message_validator.validate_location(data)
    if not valid:
        logger.warning(f"Invalid location data: {error}")
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

    # 保存位置数据
    await location_service.save_location(
        device_id=device_id,
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        altitude=data.get("altitude"),
        speed=data.get("speed"),
        direction=data.get("direction"),
        accuracy=data.get("accuracy"),
        satellites=data.get("satellites"),
        battery=data.get("battery"),
        signal_strength=data.get("signal_strength"),
        charging=data.get("charging"),
        mode=data.get("mode"),
        gps_timestamp=data.get("gps_timestamp"),
    )

    # 推送位置给绑定用户
    await push_service.push_location(device_id, data)

    logger.debug(f"Location processed for device: {device_id}")
