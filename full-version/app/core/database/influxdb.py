# -*- coding: utf-8 -*-
"""
InfluxDB连接池模块
用于存储时序数据（位置数据）
"""

import asyncio
from typing import Optional, Any, Dict, List
from datetime import datetime

from influxdb_client import InfluxDBClient
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client.rest import ApiException

from app.config.settings import settings
from app.core.logger import logger


class InfluxDBPool:
    """InfluxDB连接池管理器"""

    _instance: Optional["InfluxDBPool"] = None

    def __init__(self):
        """初始化InfluxDB连接池"""
        self._client: Optional[InfluxDBClientAsync] = None
        self._write_api = None
        self._query_api = None

    @classmethod
    def get_instance(cls) -> "InfluxDBPool":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self) -> None:
        """初始化连接池"""
        if self._client is not None:
            return

        # 创建异步客户端
        self._client = InfluxDBClientAsync(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG,
            timeout=30000,
        )

        # 获取写入和查询API
        self._write_api = self._client.write_api()
        self._query_api = self._client.query_api()

        logger.info(
            f"InfluxDB connection initialized: {settings.INFLUXDB_URL}, "
            f"org: {settings.INFLUXDB_ORG}, bucket: {settings.INFLUXDB_BUCKET}"
        )

    async def close(self) -> None:
        """关闭连接池"""
        if self._client:
            await self._client.close()
            self._client = None
            self._write_api = None
            self._query_api = None
            logger.info("InfluxDB connection closed")

    @property
    def client(self) -> InfluxDBClientAsync:
        """获取客户端"""
        if not self._client:
            raise RuntimeError("InfluxDB pool not initialized")
        return self._client

    @property
    def write_api(self):
        """获取写入API"""
        if not self._write_api:
            raise RuntimeError("InfluxDB pool not initialized")
        return self._write_api

    @property
    def query_api(self):
        """获取查询API"""
        if not self._query_api:
            raise RuntimeError("InfluxDB pool not initialized")
        return self._query_api

    async def write_location_data(
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
        写入位置数据

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
            是否写入成功
        """
        from influxdb_client import Point

        try:
            point = (
                Point("location")
                .tag("device_id", device_id)
                .tag("mode", mode)
                .field("latitude", latitude)
                .field("longitude", longitude)
                .field("altitude", altitude)
                .field("speed", speed)
                .field("direction", direction)
                .field("accuracy", accuracy)
                .field("satellites", satellites)
                .field("battery", battery)
                .field("signal_strength", signal_strength)
                .field("charging", charging)
                .time(gps_timestamp)
            )

            await self.write_api.write(
                bucket=settings.INFLUXDB_BUCKET,
                org=settings.INFLUXDB_ORG,
                record=point,
            )

            logger.debug(f"Location data written for device {device_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to write location data: {e}")
            return False

    async def query_location_history(
        self,
        device_id: str,
        start_time: str,
        end_time: str,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        查询位置历史

        Args:
            device_id: 设备IMEI
            start_time: 开始时间(ISO 8601)
            end_time: 结束时间(ISO 8601)
            limit: 返回条数限制

        Returns:
            位置数据列表
        """
        query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
            |> range(start: {start_time}, stop: {end_time})
            |> filter(fn: (r) => r["device_id"] == "{device_id}")
            |> sort(columns: ["_time"], desc: true)
            |> limit(n: {limit})
        '''

        try:
            result = await self.query_api.query(query)

            locations = []
            for table in result:
                for record in table.records:
                    locations.append({
                        "time": record.get_time(),
                        "latitude": record.values.get("latitude"),
                        "longitude": record.values.get("longitude"),
                        "altitude": record.values.get("altitude"),
                        "speed": record.values.get("speed"),
                        "direction": record.values.get("direction"),
                        "accuracy": record.values.get("accuracy"),
                        "mode": record.values.get("mode"),
                    })

            return locations

        except Exception as e:
            logger.error(f"Failed to query location history: {e}")
            return []

    async def query_latest_location(
        self,
        device_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        查询最新位置

        Args:
            device_id: 设备IMEI

        Returns:
            最新位置数据或None
        """
        query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
            |> range(start: -24h)
            |> filter(fn: (r) => r["device_id"] == "{device_id}")
            |> sort(columns: ["_time"], desc: true)
            |> limit(n: 1)
        '''

        try:
            result = await self.query_api.query(query)

            for table in result:
                for record in table.records:
                    return {
                        "time": record.get_time(),
                        "latitude": record.values.get("latitude"),
                        "longitude": record.values.get("longitude"),
                        "altitude": record.values.get("altitude"),
                        "speed": record.values.get("speed"),
                        "direction": record.values.get("direction"),
                        "accuracy": record.values.get("accuracy"),
                        "mode": record.values.get("mode"),
                    }

            return None

        except Exception as e:
            logger.error(f"Failed to query latest location: {e}")
            return None


# 全局InfluxDB连接池实例
influxdb_pool = InfluxDBPool.get_instance()
