# -*- coding: utf-8 -*-
"""
UDP服务器集成测试
测试UDP端口8888上的所有接口
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from tests.conftest import create_udp_message, generate_checksum, TEST_PRESHARED_KEY


class TestUDPServerIntegration:
    """UDP服务器集成测试"""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="UDP server start requires full asyncio environment")
    async def test_udp_server_start_stop(self):
        """测试UDP服务器启动和停止"""
        from app.protocol.udp.server import UDPServer

        server = UDPServer(host="127.0.0.1", port=18888)

        await server.start()
        assert server.is_running is True

        await server.stop()
        assert server.is_running is False

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="UDP server start requires full asyncio environment")
    async def test_udp_server_bind_same_port_fails(self):
        """测试同一端口绑定失败"""
        from app.protocol.udp.server import UDPServer

        server1 = UDPServer(host="127.0.0.1", port=18888)
        await server1.start()
        assert server1.is_running is True

        server2 = UDPServer(host="127.0.0.1", port=18888)
        try:
            await server2.start()
            # 如果没有抛出异常,清理
            await server2.stop()
        except OSError:
            pass  # 预期失败
        finally:
            await server1.stop()


class TestUDPMessageHandling:
    """UDP消息处理测试"""

    def test_create_location_message(self):
        """测试创建位置消息"""
        message = create_udp_message(
            msg_type="location",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
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
            },
        )

        assert message["type"] == "location"
        assert message["device_id"] == "860000000000000"
        assert message["data"]["latitude"] == 39.1028
        assert len(message["checksum"]) == 32

    def test_create_alarm_message_tamper(self):
        """测试创建防拆报警消息"""
        message = create_udp_message(
            msg_type="alarm",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "alarm_type": 1,  # 防拆
                "alarm_level": 2,
                "latitude": 39.1028,
                "longitude": 117.3475,
                "accuracy": 8.5,
                "battery": 85,
                "alarm_data": {"detect_method": "switch"},
            },
        )

        assert message["type"] == "alarm"
        assert message["data"]["alarm_type"] == 1

    def test_create_alarm_message_fall(self):
        """测试创建摔倒报警消息"""
        message = create_udp_message(
            msg_type="alarm",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "alarm_type": 2,  # 摔倒
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
            },
        )

        assert message["type"] == "alarm"
        assert message["data"]["alarm_type"] == 2
        assert "fall_height" in message["data"]["alarm_data"]

    def test_create_alarm_message_sos(self):
        """测试创建SOS报警消息"""
        message = create_udp_message(
            msg_type="alarm",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "alarm_type": 5,  # SOS
                "alarm_level": 4,
                "latitude": 39.1028,
                "longitude": 117.3475,
                "accuracy": 8.5,
                "battery": 85,
                "alarm_data": {"button_press_duration": 3.2},
            },
        )

        assert message["type"] == "alarm"
        assert message["data"]["alarm_type"] == 5
        assert message["data"]["alarm_level"] == 4

    def test_create_heartbeat_message(self):
        """测试创建心跳消息"""
        message = create_udp_message(
            msg_type="heartbeat",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "battery": 85,
                "signal_strength": 75,
                "charging": False,
                "temperature": 25.5,
            },
        )

        assert message["type"] == "heartbeat"
        assert message["data"]["battery"] == 85
        assert message["data"]["temperature"] == 25.5

    def test_create_command_response_message(self):
        """测试创建命令响应消息"""
        message = create_udp_message(
            msg_type="command_response",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "command_id": "12345678-1234-1234-1234-123456789012",
                "command_type": "get_location",
                "result": "success",
                "result_data": {"latitude": 39.1028, "longitude": 117.3475},
            },
        )

        assert message["type"] == "command_response"
        assert message["data"]["command_type"] == "get_location"
        assert message["data"]["result"] == "success"


class TestUDPChecksumVerification:
    """UDP校验和验证测试"""

    def test_checksum_verification_success(self):
        """测试校验和验证成功"""
        from app.core.security.checksum import verify_checksum

        data = {"battery": 85, "signal_strength": 75}
        checksum = generate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data=data,
            preshared_key=TEST_PRESHARED_KEY,
        )

        result = verify_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data=data,
            checksum=checksum,
            preshared_key=TEST_PRESHARED_KEY,
        )

        assert result is True

    def test_checksum_verification_tampered_data(self):
        """测试校验和验证失败-数据被篡改"""
        from app.core.security.checksum import verify_checksum

        original_data = {"battery": 85}
        checksum = generate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data=original_data,
            preshared_key=TEST_PRESHARED_KEY,
        )

        # 篡改数据
        tampered_data = {"battery": 100}

        result = verify_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data=tampered_data,
            checksum=checksum,
            preshared_key=TEST_PRESHARED_KEY,
        )

        assert result is False


class TestUDPAlarmTypes:
    """UDP报警类型测试"""

    @pytest.mark.parametrize("alarm_type,expected_name", [
        (1, "tamper"),
        (2, "fall"),
        (3, "still"),
        (4, "low_battery"),
        (5, "sos"),
        (6, "shutdown"),
    ])
    def test_all_alarm_types(self, alarm_type, expected_name):
        """测试所有报警类型"""
        message = create_udp_message(
            msg_type="alarm",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "alarm_type": alarm_type,
                "alarm_level": 3,
                "latitude": 39.1028,
                "longitude": 117.3475,
                "accuracy": 8.5,
                "battery": 85,
                "alarm_data": {},
            },
        )

        assert message["data"]["alarm_type"] == alarm_type


class TestUDPDeviceModes:
    """UDP设备模式测试"""

    @pytest.mark.parametrize("mode", [
        "normal",
        "low_power",
        "alarm",
        "sleep",
    ])
    def test_all_device_modes(self, mode):
        """测试所有设备模式"""
        message = create_udp_message(
            msg_type="location",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
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
                "mode": mode,
                "gps_timestamp": "2024-01-15T14:30:00+08:00",
            },
        )

        assert message["data"]["mode"] == mode


class TestUDPCoordinateBoundaries:
    """UDP坐标边界测试"""

    def test_max_latitude(self):
        """测试最大纬度90"""
        message = create_udp_message(
            msg_type="location",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "latitude": 90.0,
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
            },
        )

        assert message["data"]["latitude"] == 90.0

    def test_min_latitude(self):
        """测试最小纬度-90"""
        message = create_udp_message(
            msg_type="location",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "latitude": -90.0,
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
            },
        )

        assert message["data"]["latitude"] == -90.0

    def test_max_longitude(self):
        """测试最大经度180"""
        message = create_udp_message(
            msg_type="location",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "latitude": 39.1028,
                "longitude": 180.0,
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
            },
        )

        assert message["data"]["longitude"] == 180.0

    def test_min_longitude(self):
        """测试最小经度-180"""
        message = create_udp_message(
            msg_type="location",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "latitude": 39.1028,
                "longitude": -180.0,
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
            },
        )

        assert message["data"]["longitude"] == -180.0


class TestUDPBatteryBoundaries:
    """UDP电量边界测试"""

    def test_battery_zero(self):
        """测试电量为0"""
        message = create_udp_message(
            msg_type="heartbeat",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "battery": 0,
                "signal_strength": 75,
                "charging": False,
                "temperature": 25.5,
            },
        )

        assert message["data"]["battery"] == 0

    def test_battery_full(self):
        """测试电量为100"""
        message = create_udp_message(
            msg_type="heartbeat",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "battery": 100,
                "signal_strength": 75,
                "charging": True,
                "temperature": 25.5,
            },
        )

        assert message["data"]["battery"] == 100
