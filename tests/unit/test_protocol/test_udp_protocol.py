# -*- coding: utf-8 -*-
"""
UDP协议接口单元测试
覆盖:
- 位置上报 (location)
- 报警事件上报 (alarm)
- 设备心跳 (heartbeat)
- 指令响应 (command_response)
"""

import pytest
import json
from datetime import datetime

from app.protocol.parser import MessageParser
from app.protocol.validator import MessageValidator
from app.core.security.checksum import calculate_checksum, verify_checksum
from app.core.exceptions import ProtocolParseException
from tests.conftest import create_udp_message, TEST_PRESHARED_KEY


class TestUDPParser:
    """UDP报文解析器测试"""

    def test_parse_valid_location_message(self):
        """测试解析有效位置消息"""
        parser = MessageParser()
        data = json.dumps({
            "version": "1.0",
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "location",
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
                "gps_timestamp": "2024-01-15T14:30:00+08:00",
            },
            "checksum": "test",
        }).encode("utf-8")

        result = parser.parse(data)

        assert result["version"] == "1.0"
        assert result["device_id"] == "860000000000000"
        assert result["type"] == "location"
        assert result["data"]["latitude"] == 39.1028

    def test_parse_invalid_json(self):
        """测试解析无效JSON"""
        parser = MessageParser()
        data = b"invalid json"

        with pytest.raises(ProtocolParseException):
            parser.parse(data)

    def test_parse_empty_data(self):
        """测试解析空数据"""
        parser = MessageParser()
        data = b""

        with pytest.raises(ProtocolParseException):
            parser.parse(data)

    def test_parse_unicode_data(self):
        """测试解析Unicode数据"""
        parser = MessageParser()
        data = json.dumps({
            "version": "1.0",
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123中文nonce",
            "type": "location",
            "data": {"latitude": 39.1028, "longitude": 117.3475},
            "checksum": "test",
        }).encode("utf-8")

        result = parser.parse(data)
        assert "abc123中文nonce" in result["nonce"]


class TestUDPValidator:
    """UDP报文验证器测试"""

    def test_validate_base_valid(self):
        """测试基础验证通过"""
        validator = MessageValidator()
        message = {
            "version": "1.0",
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "location",
            "data": {},
            "checksum": "abc123",
        }

        valid, error = validator.validate_base(message)
        assert valid is True
        assert error is None

    def test_validate_base_invalid_version(self):
        """测试基础验证失败-版本错误"""
        validator = MessageValidator()
        message = {
            "version": "2.0",
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "location",
            "data": {},
            "checksum": "abc123",
        }

        valid, error = validator.validate_base(message)
        assert valid is False
        assert "version" in error.lower()

    def test_validate_base_missing_device_id(self):
        """测试基础验证失败-缺少device_id"""
        validator = MessageValidator()
        message = {
            "version": "1.0",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "location",
            "data": {},
            "checksum": "abc123",
        }

        valid, error = validator.validate_base(message)
        assert valid is False
        assert "device_id" in error.lower()

    def test_validate_base_invalid_device_id_too_long(self):
        """测试基础验证失败-device_id过长"""
        validator = MessageValidator()
        message = {
            "version": "1.0",
            "device_id": "860000000000000000",  # 18位, 超过16位
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "location",
            "data": {},
            "checksum": "abc123",
        }

        valid, error = validator.validate_base(message)
        assert valid is False
        assert "device_id" in error.lower()

    def test_validate_base_invalid_message_type(self):
        """测试基础验证失败-无效消息类型"""
        validator = MessageValidator()
        message = {
            "version": "1.0",
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "invalid_type",
            "data": {},
            "checksum": "abc123",
        }

        valid, error = validator.validate_base(message)
        assert valid is False
        assert "message type" in error.lower()


class TestLocationValidation:
    """位置数据验证测试"""

    def test_validate_location_valid(self, mock_location_data):
        """测试位置数据验证通过"""
        validator = MessageValidator()
        valid, error = validator.validate_location(mock_location_data)
        assert valid is True
        assert error is None

    def test_validate_location_boundary_latitude_max(self):
        """测试纬度边界值-最大值90"""
        validator = MessageValidator()
        data = {
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
        }
        valid, error = validator.validate_location(data)
        assert valid is True

    def test_validate_location_boundary_latitude_min(self):
        """测试纬度边界值-最小值-90"""
        validator = MessageValidator()
        data = {
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
        }
        valid, error = validator.validate_location(data)
        assert valid is True

    def test_validate_location_boundary_latitude_exceeded(self):
        """测试纬度边界值-超过90"""
        validator = MessageValidator()
        data = {
            "latitude": 91.0,
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
        }
        valid, error = validator.validate_location(data)
        assert valid is False
        assert "latitude" in error.lower()

    def test_validate_location_boundary_longitude_max(self):
        """测试经度边界值-最大值180"""
        validator = MessageValidator()
        data = {
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
        }
        valid, error = validator.validate_location(data)
        assert valid is True

    def test_validate_location_boundary_longitude_min(self):
        """测试经度边界值-最小值-180"""
        validator = MessageValidator()
        data = {
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
        }
        valid, error = validator.validate_location(data)
        assert valid is True

    def test_validate_location_boundary_longitude_exceeded(self):
        """测试经度边界值-超过180"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 181.0,
            "altitude": 50.5,
            "speed": 1.2,
            "direction": 90,
            "accuracy": 8.5,
            "satellites": 8,
            "battery": 85,
            "signal_strength": 75,
            "charging": False,
            "mode": "normal",
        }
        valid, error = validator.validate_location(data)
        assert valid is False
        assert "longitude" in error.lower()

    def test_validate_location_boundary_battery_zero(self):
        """测试电量边界值-0"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 1.2,
            "direction": 90,
            "accuracy": 8.5,
            "satellites": 8,
            "battery": 0,
            "signal_strength": 75,
            "charging": False,
            "mode": "normal",
        }
        valid, error = validator.validate_location(data)
        assert valid is True

    def test_validate_location_boundary_battery_100(self):
        """测试电量边界值-100"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 1.2,
            "direction": 90,
            "accuracy": 8.5,
            "satellites": 8,
            "battery": 100,
            "signal_strength": 75,
            "charging": False,
            "mode": "normal",
        }
        valid, error = validator.validate_location(data)
        assert valid is True

    def test_validate_location_boundary_battery_exceeded(self):
        """测试电量边界值-超过100"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 1.2,
            "direction": 90,
            "accuracy": 8.5,
            "satellites": 8,
            "battery": 101,
            "signal_strength": 75,
            "charging": False,
            "mode": "normal",
        }
        valid, error = validator.validate_location(data)
        assert valid is False
        assert "battery" in error.lower()

    def test_validate_location_boundary_direction_0(self):
        """测试方向边界值-0度"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 1.2,
            "direction": 0,
            "accuracy": 8.5,
            "satellites": 8,
            "battery": 85,
            "signal_strength": 75,
            "charging": False,
            "mode": "normal",
        }
        valid, error = validator.validate_location(data)
        assert valid is True

    def test_validate_location_boundary_direction_359(self):
        """测试方向边界值-359度"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 1.2,
            "direction": 359,
            "accuracy": 8.5,
            "satellites": 8,
            "battery": 85,
            "signal_strength": 75,
            "charging": False,
            "mode": "normal",
        }
        valid, error = validator.validate_location(data)
        assert valid is True

    def test_validate_location_invalid_direction(self):
        """测试方向无效值"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 1.2,
            "direction": 360,
            "accuracy": 8.5,
            "satellites": 8,
            "battery": 85,
            "signal_strength": 75,
            "charging": False,
            "mode": "normal",
        }
        valid, error = validator.validate_location(data)
        assert valid is False
        assert "direction" in error.lower()

    def test_validate_location_invalid_mode(self):
        """测试无效工作模式"""
        validator = MessageValidator()
        data = {
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
            "mode": "invalid_mode",
        }
        valid, error = validator.validate_location(data)
        assert valid is False
        assert "mode" in error.lower()

    def test_validate_location_all_modes(self):
        """测试所有有效工作模式"""
        validator = MessageValidator()
        modes = ["normal", "low_power", "alarm", "sleep"]

        for mode in modes:
            data = {
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
            }
            valid, error = validator.validate_location(data)
            assert valid is True, f"Mode {mode} should be valid"


class TestAlarmValidation:
    """报警数据验证测试"""

    def test_validate_alarm_valid_tamper(self):
        """测试防拆报警验证"""
        validator = MessageValidator()
        data = {
            "alarm_type": 1,
            "alarm_level": 2,
            "latitude": 39.1028,
            "longitude": 117.3475,
            "accuracy": 8.5,
            "battery": 85,
            "alarm_data": {"detect_method": "switch"},
        }
        valid, error = validator.validate_alarm(data)
        assert valid is True

    def test_validate_alarm_valid_fall(self):
        """测试摔倒报警验证"""
        validator = MessageValidator()
        data = {
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
        valid, error = validator.validate_alarm(data)
        assert valid is True

    def test_validate_alarm_valid_still(self):
        """测试静止报警验证"""
        validator = MessageValidator()
        data = {
            "alarm_type": 3,
            "alarm_level": 2,
            "latitude": 39.1028,
            "longitude": 117.3475,
            "accuracy": 8.5,
            "battery": 85,
            "alarm_data": {"still_duration": 1800},
        }
        valid, error = validator.validate_alarm(data)
        assert valid is True

    def test_validate_alarm_valid_low_battery(self):
        """测试低电量报警验证"""
        validator = MessageValidator()
        data = {
            "alarm_type": 4,
            "alarm_level": 1,
            "latitude": 39.1028,
            "longitude": 117.3475,
            "accuracy": 8.5,
            "battery": 15,
            "alarm_data": {"battery": 15},
        }
        valid, error = validator.validate_alarm(data)
        assert valid is True

    def test_validate_alarm_valid_sos(self):
        """测试SOS报警验证"""
        validator = MessageValidator()
        data = {
            "alarm_type": 5,
            "alarm_level": 4,
            "latitude": 39.1028,
            "longitude": 117.3475,
            "accuracy": 8.5,
            "battery": 85,
            "alarm_data": {"button_press_duration": 3.2},
        }
        valid, error = validator.validate_alarm(data)
        assert valid is True

    def test_validate_alarm_valid_shutdown(self):
        """测试关机报警验证"""
        validator = MessageValidator()
        data = {
            "alarm_type": 6,
            "alarm_level": 4,
            "latitude": 39.1028,
            "longitude": 117.3475,
            "accuracy": 8.5,
            "battery": 85,
            "alarm_data": {"power_off_reason": 0},
        }
        valid, error = validator.validate_alarm(data)
        assert valid is True

    def test_validate_alarm_invalid_type(self):
        """测试无效报警类型"""
        validator = MessageValidator()
        data = {
            "alarm_type": 99,
            "alarm_level": 3,
            "latitude": 39.1028,
            "longitude": 117.3475,
            "accuracy": 8.5,
            "battery": 85,
            "alarm_data": {},
        }
        valid, error = validator.validate_alarm(data)
        assert valid is False
        assert "alarm_type" in error.lower()

    def test_validate_alarm_invalid_level(self):
        """测试无效报警级别"""
        validator = MessageValidator()
        data = {
            "alarm_type": 2,
            "alarm_level": 5,
            "latitude": 39.1028,
            "longitude": 117.3475,
            "accuracy": 8.5,
            "battery": 85,
            "alarm_data": {},
        }
        valid, error = validator.validate_alarm(data)
        assert valid is False
        assert "alarm_level" in error.lower()

    def test_validate_alarm_all_types(self):
        """测试所有有效报警类型"""
        validator = MessageValidator()
        for alarm_type in range(1, 7):
            data = {
                "alarm_type": alarm_type,
                "alarm_level": 3,
                "latitude": 39.1028,
                "longitude": 117.3475,
                "accuracy": 8.5,
                "battery": 85,
                "alarm_data": {},
            }
            valid, error = validator.validate_alarm(data)
            assert valid is True, f"Alarm type {alarm_type} should be valid"


class TestHeartbeatValidation:
    """心跳数据验证测试"""

    def test_validate_heartbeat_valid(self, mock_heartbeat_data):
        """测试心跳数据验证通过"""
        validator = MessageValidator()
        valid, error = validator.validate_heartbeat(mock_heartbeat_data)
        assert valid is True
        assert error is None

    def test_validate_heartbeat_boundary_battery_zero(self):
        """测试电量边界值-0"""
        validator = MessageValidator()
        data = {
            "battery": 0,
            "signal_strength": 75,
            "charging": False,
            "temperature": 25.5,
        }
        valid, error = validator.validate_heartbeat(data)
        assert valid is True

    def test_validate_heartbeat_boundary_battery_100(self):
        """测试电量边界值-100"""
        validator = MessageValidator()
        data = {
            "battery": 100,
            "signal_strength": 75,
            "charging": False,
            "temperature": 25.5,
        }
        valid, error = validator.validate_heartbeat(data)
        assert valid is True

    def test_validate_heartbeat_boundary_temperature_min(self):
        """测试温度边界值-最低-40"""
        validator = MessageValidator()
        data = {
            "battery": 85,
            "signal_strength": 75,
            "charging": False,
            "temperature": -40.0,
        }
        valid, error = validator.validate_heartbeat(data)
        assert valid is True

    def test_validate_heartbeat_boundary_temperature_max(self):
        """测试温度边界值-最高85"""
        validator = MessageValidator()
        data = {
            "battery": 85,
            "signal_strength": 75,
            "charging": False,
            "temperature": 85.0,
        }
        valid, error = validator.validate_heartbeat(data)
        assert valid is True

    def test_validate_heartbeat_boundary_temperature_exceeded(self):
        """测试温度边界值-超过85"""
        validator = MessageValidator()
        data = {
            "battery": 85,
            "signal_strength": 75,
            "charging": False,
            "temperature": 86.0,
        }
        valid, error = validator.validate_heartbeat(data)
        assert valid is False
        assert "temperature" in error.lower()

    def test_validate_heartbeat_invalid_charging_type(self):
        """测试充电状态类型错误"""
        validator = MessageValidator()
        data = {
            "battery": 85,
            "signal_strength": 75,
            "charging": 1,  # 应该是bool
            "temperature": 25.5,
        }
        valid, error = validator.validate_heartbeat(data)
        assert valid is False
        assert "charging" in error.lower()


class TestUDPChecksum:
    """UDP校验和测试"""

    def test_calculate_checksum(self):
        """测试校验和计算"""
        checksum = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"battery": 85},
            preshared_key=TEST_PRESHARED_KEY,
        )

        assert isinstance(checksum, str)
        assert len(checksum) == 32

    def test_verify_checksum_success(self):
        """测试校验和验证成功"""
        checksum = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"battery": 85},
            preshared_key=TEST_PRESHARED_KEY,
        )

        result = verify_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"battery": 85},
            checksum=checksum,
            preshared_key=TEST_PRESHARED_KEY,
        )
        assert result is True

    def test_verify_checksum_failed(self):
        """测试校验和验证失败"""
        result = verify_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"battery": 85},
            checksum="invalid_checksum",
            preshared_key=TEST_PRESHARED_KEY,
        )
        assert result is False

    def test_checksum_case_insensitive(self):
        """测试校验和大小写不敏感"""
        checksum = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"battery": 85},
            preshared_key=TEST_PRESHARED_KEY,
        )

        result = verify_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"battery": 85},
            checksum=checksum.upper(),
            preshared_key=TEST_PRESHARED_KEY,
        )
        assert result is True


class TestUDPMessageFactory:
    """UDP消息工厂测试"""

    def test_create_location_message(self, location_message_factory):
        """测试创建位置消息"""
        message = location_message_factory()

        assert message["version"] == "1.0"
        assert message["type"] == "location"
        assert message["device_id"] == "860000000000000"
        assert "checksum" in message
        assert len(message["checksum"]) == 32

    def test_create_alarm_message(self, alarm_message_factory):
        """测试创建报警消息"""
        message = alarm_message_factory(alarm_type=5, alarm_level=4)

        assert message["type"] == "alarm"
        assert message["data"]["alarm_type"] == 5
        assert message["data"]["alarm_level"] == 4

    def test_create_heartbeat_message(self, heartbeat_message_factory):
        """测试创建心跳消息"""
        message = heartbeat_message_factory(battery=50, signal_strength=60)

        assert message["type"] == "heartbeat"
        assert message["data"]["battery"] == 50
        assert message["data"]["signal_strength"] == 60

    def test_create_location_message_custom_device(self):
        """测试创建自定义设备ID的位置消息"""
        message = create_udp_message(
            msg_type="location",
            device_id="869595050000001",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="customnonce123",
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
            },
        )

        assert message["device_id"] == "869595050000001"
        assert message["nonce"] == "customnonce123"
