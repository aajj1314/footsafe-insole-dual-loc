# -*- coding: utf-8 -*-
"""
演示数据服务
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any


class DemoDataService:
    """演示数据服务"""

    DEMO_USER_ID = 999

    @staticmethod
    def is_demo_user(user_id: int) -> bool:
        """检查是否为演示用户"""
        return user_id == DemoDataService.DEMO_USER_ID

    @staticmethod
    def is_demo_username(username: str) -> bool:
        """检查是否为演示用户名"""
        return username.lower() == "admin"

    @staticmethod
    def get_demo_devices() -> List[Dict[str, Any]]:
        """获取演示设备列表"""
        now = datetime.utcnow()
        return [
            {
                "id": 1,
                "imei": "861234567890001",
                "nickname": "奶奶的智能鞋",
                "relation": "奶奶",
                "iccid": "89860123456789000123",
                "firmware_version": "v2.1.0",
                "hardware_version": "v1.0",
                "battery": 85,
                "signal_strength": 4,
                "mode": "normal",
                "status": "online",
                "last_location_lat": "39.9142",
                "last_location_lng": "116.4074",
                "last_location_time": (now - timedelta(minutes=5)).isoformat(),
                "created_at": (now - timedelta(days=30)).isoformat(),
            },
            {
                "id": 2,
                "imei": "861234567890002",
                "nickname": "爷爷的智能鞋",
                "relation": "爷爷",
                "iccid": "89860123456789000124",
                "firmware_version": "v2.1.0",
                "hardware_version": "v1.0",
                "battery": 62,
                "signal_strength": 3,
                "mode": "normal",
                "status": "online",
                "last_location_lat": "39.9200",
                "last_location_lng": "116.4150",
                "last_location_time": (now - timedelta(minutes=2)).isoformat(),
                "created_at": (now - timedelta(days=15)).isoformat(),
            },
            {
                "id": 3,
                "imei": "861234567890003",
                "nickname": "外婆的智能鞋",
                "relation": "外婆",
                "iccid": "89860123456789000125",
                "firmware_version": "v2.0.8",
                "hardware_version": "v1.0",
                "battery": 23,
                "signal_strength": 2,
                "mode": "low_power",
                "status": "offline",
                "last_location_lat": "39.9080",
                "last_location_lng": "116.4020",
                "last_location_time": (now - timedelta(hours=2)).isoformat(),
                "created_at": (now - timedelta(days=7)).isoformat(),
            },
        ]

    @staticmethod
    def get_demo_alarms() -> List[Dict[str, Any]]:
        """获取演示报警列表"""
        now = datetime.utcnow()
        return [
            {
                "id": 1,
                "alarm_id": "ALM20260419001",
                "device_id": "861234567890001",
                "alarm_type": 5,
                "alarm_level": 4,
                "latitude": "39.9142",
                "longitude": "116.4074",
                "accuracy": "10.5",
                "battery": 85,
                "status": "pending",
                "created_at": (now - timedelta(minutes=15)).isoformat(),
            },
            {
                "id": 2,
                "alarm_id": "ALM20260419002",
                "device_id": "861234567890002",
                "alarm_type": 2,
                "alarm_level": 3,
                "latitude": "39.9200",
                "longitude": "116.4150",
                "accuracy": "8.2",
                "battery": 62,
                "status": "resolved",
                "created_at": (now - timedelta(hours=1)).isoformat(),
            },
            {
                "id": 3,
                "alarm_id": "ALM20260419003",
                "device_id": "861234567890003",
                "alarm_type": 4,
                "alarm_level": 2,
                "latitude": "39.9080",
                "longitude": "116.4020",
                "accuracy": "15.0",
                "battery": 23,
                "status": "pending",
                "created_at": (now - timedelta(hours=2)).isoformat(),
            },
            {
                "id": 4,
                "alarm_id": "ALM20260418004",
                "device_id": "861234567890001",
                "alarm_type": 1,
                "alarm_level": 4,
                "latitude": "39.9145",
                "longitude": "116.4078",
                "accuracy": "5.0",
                "battery": 87,
                "status": "resolved",
                "created_at": (now - timedelta(days=1)).isoformat(),
            },
        ]

    @staticmethod
    def get_demo_fences() -> List[Dict[str, Any]]:
        """获取演示围栏列表"""
        now = datetime.utcnow()
        return [
            {
                "id": 1,
                "device_imei": "861234567890001",
                "name": "小区范围",
                "fence_type": "circle",
                "center_lat": "39.9142",
                "center_lng": "116.4074",
                "radius": "500",
                "enabled": True,
                "alarm_enabled": True,
                "created_at": (now - timedelta(days=20)).isoformat(),
            },
            {
                "id": 2,
                "device_imei": "861234567890002",
                "name": "公园活动区",
                "fence_type": "rectangle",
                "min_lat": "39.9150",
                "max_lat": "39.9250",
                "min_lng": "116.4100",
                "max_lng": "116.4200",
                "enabled": True,
                "alarm_enabled": True,
                "created_at": (now - timedelta(days=10)).isoformat(),
            },
        ]

    @staticmethod
    def get_demo_locations(device_imei: str) -> List[Dict[str, Any]]:
        """获取演示位置历史"""
        now = datetime.utcnow()
        base_lat = 39.9142
        base_lng = 116.4074

        if device_imei == "861234567890002":
            base_lat = 39.9200
            base_lng = 116.4150
        elif device_imei == "861234567890003":
            base_lat = 39.9080
            base_lng = 116.4020

        locations = []
        for i in range(24):
            location_time = now - timedelta(hours=i)
            locations.append({
                "latitude": f"{base_lat + (i % 3) * 0.001}",
                "longitude": f"{base_lng + (i % 5) * 0.001}",
                "altitude": f"{10 + i % 5}",
                "speed": f"{1.0 + (i % 3) * 0.5}",
                "direction": f"{i * 15 % 360}",
                "accuracy": f"{5.0 + (i % 3) * 2}",
                "satellites": 8 + (i % 4),
                "gps_timestamp": location_time.isoformat(),
            })

        return locations


demo_data_service = DemoDataService()
