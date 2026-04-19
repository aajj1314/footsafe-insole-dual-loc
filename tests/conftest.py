# -*- coding: utf-8 -*-
"""
测试配置和fixtures
"""

import pytest
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, Any

# 测试用预共享密钥
TEST_PRESHARED_KEY = "test_preshared_key_12345"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_device_id() -> str:
    """模拟设备ID"""
    return "860000000000000"


@pytest.fixture
def mock_session_id() -> str:
    """模拟会话ID"""
    return "12345678-1234-1234-1234-123456789012"


@pytest.fixture
def mock_timestamp() -> str:
    """模拟时间戳"""
    return datetime.utcnow().isoformat() + "+08:00"


@pytest.fixture
def mock_nonce() -> str:
    """模拟随机字符串"""
    return "abc123def456"


@pytest.fixture
def mock_location_data() -> dict:
    """模拟位置数据"""
    return {
        "latitude": 39.1028,
        "longitude": 117.3475,
        "altitude": 50.5,
        "speed": 1.2,
        "direction": 90,
        "accuracy": 8.5,
        "satellites": 8,
        "battery": 85,
        "signal_strength": 75,
        "charging": False,
        "mode": "normal",
        "gps_timestamp": "2024-01-15T14:30:00+08:00",
    }


@pytest.fixture
def mock_alarm_data() -> dict:
    """模拟报警数据"""
    return {
        "alarm_type": 2,
        "alarm_level": 3,
        "latitude": 39.1028,
        "longitude": 117.3475,
        "accuracy": 8.5,
        "battery": 85,
        "alarm_data": {
            "fall_height": 0.8,
            "impact_force": 12.5,
            "duration": 2.3,
        },
    }


@pytest.fixture
def mock_heartbeat_data() -> dict:
    """模拟心跳数据"""
    return {
        "battery": 85,
        "signal_strength": 75,
        "charging": False,
        "temperature": 25.5,
    }


@pytest.fixture
def mock_auth_data() -> dict:
    """模拟认证数据"""
    return {
        "firmware_version": "1.2.3",
        "hardware_version": "1.0",
        "iccid": "89860000000000000000",
        "fingerprint": "device_fingerprint_string",
    }


@pytest.fixture
def mock_ota_progress_data() -> dict:
    """模拟OTA进度数据"""
    return {
        "upgrade_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "status": "downloading",
        "progress": 50,
        "error_code": 0,
        "error_message": "",
    }


@pytest.fixture
def mock_device_error_data() -> dict:
    """模拟设备错误数据"""
    return {
        "error_type": "gps_fault",
        "error_level": 2,
        "error_message": "GPS module initialization failed",
        "error_code": 1001,
        "extra_data": {},
    }


@pytest.fixture
def mock_batch_report_data(mock_location_data, mock_heartbeat_data, mock_alarm_data) -> dict:
    """模拟批量上报数据"""
    return {
        "total": 100,
        "index": 1,
        "items": [
            {
                "type": "location",
                "timestamp": "2024-01-15T14:00:00+08:00",
                "data": mock_location_data,
            },
            {
                "type": "heartbeat",
                "timestamp": "2024-01-15T14:01:00+08:00",
                "data": mock_heartbeat_data,
            },
            {
                "type": "alarm",
                "timestamp": "2024-01-15T14:02:00+08:00",
                "data": mock_alarm_data,
            },
        ],
    }


def generate_checksum(
    version: str,
    device_id: str,
    timestamp: str,
    nonce: str,
    data: dict,
    preshared_key: str = TEST_PRESHARED_KEY,
) -> str:
    """生成校验和"""
    from app.core.security.checksum import calculate_checksum
    return calculate_checksum(version, device_id, timestamp, nonce, data, preshared_key)


def create_udp_message(
    msg_type: str,
    device_id: str,
    timestamp: str,
    nonce: str,
    data: dict,
    preshared_key: str = TEST_PRESHARED_KEY,
) -> dict:
    """创建UDP报文"""
    version = "1.0"
    checksum = generate_checksum(version, device_id, timestamp, nonce, data, preshared_key)
    return {
        "version": version,
        "device_id": device_id,
        "timestamp": timestamp,
        "nonce": nonce,
        "type": msg_type,
        "data": data,
        "checksum": checksum,
    }


def create_tcp_message(
    msg_type: str,
    device_id: str,
    session_id: str,
    timestamp: str,
    nonce: str,
    data: dict,
    preshared_key: str = TEST_PRESHARED_KEY,
) -> dict:
    """创建TCP报文"""
    version = "1.0"
    checksum = generate_checksum(version, device_id, timestamp, nonce, data, preshared_key)
    message = {
        "version": version,
        "device_id": device_id,
        "timestamp": timestamp,
        "nonce": nonce,
        "type": msg_type,
        "data": data,
        "checksum": checksum,
    }
    if msg_type != "auth":
        message["session_id"] = session_id
    return message


@pytest.fixture
def location_message_factory():
    """位置消息工厂"""
    def _create(
        device_id: str = "860000000000000",
        timestamp: str = None,
        nonce: str = None,
        data: dict = None,
    ):
        ts = timestamp or datetime.utcnow().isoformat() + "+08:00"
        nn = nonce or "abc123def456"
        loc_data = data or {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 1.2,
            "direction": 90,
            "accuracy": 8.5,
            "satellites": 8,
            "battery": 85,
            "signal_strength": 75,
            "charging": False,
            "mode": "normal",
            "gps_timestamp": "2024-01-15T14:30:00+08:00",
        }
        return create_udp_message("location", device_id, ts, nn, loc_data)
    return _create


@pytest.fixture
def alarm_message_factory():
    """报警消息工厂"""
    def _create(
        device_id: str = "860000000000000",
        alarm_type: int = 2,
        alarm_level: int = 3,
        timestamp: str = None,
        nonce: str = None,
    ):
        ts = timestamp or datetime.utcnow().isoformat() + "+08:00"
        nn = nonce or "abc123def456"
        alarm_data = {
            "alarm_type": alarm_type,
            "alarm_level": alarm_level,
            "latitude": 39.1028,
            "longitude": 117.3475,
            "accuracy": 8.5,
            "battery": 85,
            "alarm_data": {
                "fall_height": 0.8,
                "impact_force": 12.5,
                "duration": 2.3,
            },
        }
        return create_udp_message("alarm", device_id, ts, nn, alarm_data)
    return _create


@pytest.fixture
def heartbeat_message_factory():
    """心跳消息工厂"""
    def _create(
        device_id: str = "860000000000000",
        timestamp: str = None,
        nonce: str = None,
        battery: int = 85,
        signal_strength: int = 75,
    ):
        ts = timestamp or datetime.utcnow().isoformat() + "+08:00"
        nn = nonce or "abc123def456"
        hb_data = {
            "battery": battery,
            "signal_strength": signal_strength,
            "charging": False,
            "temperature": 25.5,
        }
        return create_udp_message("heartbeat", device_id, ts, nn, hb_data)
    return _create


@pytest.fixture
def auth_message_factory():
    """认证消息工厂"""
    def _create(
        device_id: str = "860000000000000",
        timestamp: str = None,
        nonce: str = None,
        firmware_version: str = "1.2.3",
        hardware_version: str = "1.0",
    ):
        ts = timestamp or datetime.utcnow().isoformat() + "+08:00"
        nn = nonce or "abc123def456"
        auth_data = {
            "firmware_version": firmware_version,
            "hardware_version": hardware_version,
            "iccid": "89860000000000000000",
            "fingerprint": "device_fingerprint_string",
        }
        return create_tcp_message("auth", device_id, "", ts, nn, auth_data)
    return _create


@pytest.fixture
def tcp_heartbeat_message_factory():
    """TCP心跳消息工厂"""
    def _create(
        device_id: str = "860000000000000",
        session_id: str = "12345678-1234-1234-1234-123456789012",
        timestamp: str = None,
        nonce: str = None,
    ):
        ts = timestamp or datetime.utcnow().isoformat() + "+08:00"
        nn = nonce or "abc123def456"
        return create_tcp_message("tcp_heartbeat", device_id, session_id, ts, nn, {})
    return _create


@pytest.fixture
def command_response_message_factory():
    """命令响应消息工厂"""
    def _create(
        device_id: str = "860000000000000",
        session_id: str = "12345678-1234-1234-1234-123456789012",
        command_id: str = None,
        command_type: str = "get_location",
        result: str = "success",
        timestamp: str = None,
        nonce: str = None,
    ):
        ts = timestamp or datetime.utcnow().isoformat() + "+08:00"
        nn = nonce or "abc123def456"
        cmd_data = {
            "command_id": command_id or str(uuid.uuid4()),
            "command_type": command_type,
            "result": result,
            "result_data": {"latitude": 39.1028, "longitude": 117.3475} if result == "success" else {},
        }
        return create_tcp_message("command_response", device_id, session_id, ts, nn, cmd_data)
    return _create


@pytest.fixture
def ota_progress_message_factory():
    """OTA进度消息工厂"""
    def _create(
        device_id: str = "860000000000000",
        session_id: str = "12345678-1234-1234-1234-123456789012",
        upgrade_id: str = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        status: str = "downloading",
        progress: int = 50,
        timestamp: str = None,
        nonce: str = None,
    ):
        ts = timestamp or datetime.utcnow().isoformat() + "+08:00"
        nn = nonce or "abc123def456"
        ota_data = {
            "upgrade_id": upgrade_id,
            "status": status,
            "progress": progress,
            "error_code": 0,
            "error_message": "",
        }
        return create_tcp_message("ota_progress", device_id, session_id, ts, nn, ota_data)
    return _create


@pytest.fixture
def batch_report_message_factory():
    """批量上报消息工厂"""
    def _create(
        device_id: str = "860000000000000",
        session_id: str = "12345678-1234-1234-1234-123456789012",
        timestamp: str = None,
        nonce: str = None,
        total: int = 100,
        index: int = 1,
        items: list = None,
    ):
        ts = timestamp or datetime.utcnow().isoformat() + "+08:00"
        nn = nonce or "abc123def456"

        if items is None:
            items = [
                {
                    "type": "location",
                    "timestamp": "2024-01-15T14:00:00+08:00",
                    "data": {
                        "latitude": 39.1028,
                        "longitude": 117.3475,
                        "altitude": 50.5,
                        "speed": 1.2,
                        "direction": 90,
                        "accuracy": 8.5,
                        "satellites": 8,
                        "battery": 85,
                        "signal_strength": 75,
                        "charging": False,
                        "mode": "normal",
                        "gps_timestamp": "2024-01-15T14:00:00+08:00",
                    },
                },
            ]

        batch_data = {
            "total": total,
            "index": index,
            "items": items,
        }
        return create_tcp_message("batch_report", device_id, session_id, ts, nn, batch_data)
    return _create


@pytest.fixture
def device_error_message_factory():
    """设备错误消息工厂"""
    def _create(
        device_id: str = "860000000000000",
        session_id: str = "12345678-1234-1234-1234-123456789012",
        error_type: str = "gps_fault",
        error_level: int = 2,
        error_code: int = 1001,
        timestamp: str = None,
        nonce: str = None,
    ):
        ts = timestamp or datetime.utcnow().isoformat() + "+08:00"
        nn = nonce or "abc123def456"
        error_data = {
            "error_type": error_type,
            "error_level": error_level,
            "error_message": "GPS module initialization failed",
            "error_code": error_code,
            "extra_data": {},
        }
        return create_tcp_message("device_error", device_id, session_id, ts, nn, error_data)
    return _create
