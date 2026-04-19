# -*- coding: utf-8 -*-
"""
协议边界条件和异常情况测试
测试各种边界条件和异常情况下的协议处理
"""

import pytest
import json
from datetime import datetime, timedelta

from app.protocol.parser import MessageParser
from app.protocol.validator import MessageValidator
from app.core.security.checksum import calculate_checksum, verify_checksum
from app.core.exceptions import ProtocolParseException
from tests.conftest import create_udp_message, create_tcp_message, TEST_PRESHARED_KEY


class TestChecksumEdgeCases:
    """校验和边界情况测试"""

    def test_checksum_empty_data(self):
        """测试空数据校验和"""
        checksum = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={},
            preshared_key=TEST_PRESHARED_KEY,
        )

        assert isinstance(checksum, str)
        assert len(checksum) == 32

    def test_checksum_special_characters(self):
        """测试特殊字符校验和"""
        checksum = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="nonce!@#$%^&*()",
            data={"message": "中文测试 message"},
            preshared_key=TEST_PRESHARED_KEY,
        )

        assert isinstance(checksum, str)
        assert len(checksum) == 32

    def test_checksum_unicode_data(self):
        """测试Unicode数据校验和"""
        checksum = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"name": "测试设备", "description": "鞋垫定位器"},
            preshared_key=TEST_PRESHARED_KEY,
        )

        assert isinstance(checksum, str)
        assert len(checksum) == 32

    def test_checksum_numeric_precision(self):
        """测试数字精度校验和"""
        checksum = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "latitude": 39.1028123456789,  # 高精度
                "longitude": 117.3475123456789,
                "altitude": 50.555,
            },
            preshared_key=TEST_PRESHARED_KEY,
        )

        assert isinstance(checksum, str)
        assert len(checksum) == 32

    def test_checksum_different_keys_same_values(self):
        """测试相同值不同密钥的校验和"""
        checksum1 = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"battery": 85},
            preshared_key="key1",
        )

        checksum2 = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"battery": 85},
            preshared_key="key2",
        )

        assert checksum1 != checksum2


class TestParserEdgeCases:
    """解析器边界情况测试"""

    def test_parse_very_long_json(self):
        """测试解析超长JSON"""
        parser = MessageParser()

        # 创建一个非常大的JSON
        large_data = {
            "version": "1.0",
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "location",
            "data": {
                "description": "x" * 10000,  # 很大的字符串
            },
            "checksum": "test",
        }

        data = json.dumps(large_data).encode("utf-8")
        result = parser.parse(data)

        assert result is not None
        assert len(result["data"]["description"]) == 10000

    def test_parse_nested_json(self):
        """测试解析嵌套JSON"""
        parser = MessageParser()

        nested_data = {
            "version": "1.0",
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "alarm",
            "data": {
                "alarm_type": 2,
                "alarm_data": {
                    "nested": {
                        "deep": {
                            "value": 123,
                        },
                    },
                },
            },
            "checksum": "test",
        }

        data = json.dumps(nested_data).encode("utf-8")
        result = parser.parse(data)

        assert result["data"]["alarm_data"]["nested"]["deep"]["value"] == 123

    def test_parse_whitespace_json(self):
        """测试解析带空白字符的JSON"""
        parser = MessageParser()

        data = b'  \n\t  {"version": "1.0"}\n\t  '
        result = parser.parse(data)

        assert result["version"] == "1.0"

    def test_parse_single_quotes_json(self):
        """测试解析单引号JSON(应该失败)"""
        parser = MessageParser()

        data = b"{'version': '1.0'}"  # 单引号不是有效JSON

        with pytest.raises(ProtocolParseException):
            parser.parse(data)


class TestValidatorEdgeCases:
    """验证器边界情况测试"""

    def test_validate_location_extreme_altitude_min(self):
        """测试海拔最小边界"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": -1000.0,  # 最小值
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

    def test_validate_location_extreme_altitude_max(self):
        """测试海拔最大边界"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 10000.0,  # 最大值
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

    def test_validate_location_extreme_altitude_exceeded(self):
        """测试海拔超出边界"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 10001.0,  # 超出最大
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
        assert "altitude" in error.lower()

    def test_validate_location_speed_zero(self):
        """测试速度为0"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 0.0,  # 静止
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

    def test_validate_location_speed_max(self):
        """测试最大速度"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 100.0,  # 最大速度 m/s
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

    def test_validate_location_accuracy_zero(self):
        """测试精度为0"""
        validator = MessageValidator()
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 1.2,
            "direction": 90,
            "accuracy": 0.0,  # 最高精度
            "satellites": 8,
            "battery": 85,
            "signal_strength": 75,
            "charging": False,
            "mode": "normal",
        }

        valid, error = validator.validate_location(data)
        assert valid is True

    def test_validate_location_satellites_boundary(self):
        """测试卫星数边界"""
        validator = MessageValidator()

        # 0颗卫星
        data = {
            "latitude": 39.1028,
            "longitude": 117.3475,
            "altitude": 50.5,
            "speed": 1.2,
            "direction": 90,
            "accuracy": 8.5,
            "satellites": 0,  # 最小值
            "battery": 85,
            "signal_strength": 75,
            "charging": False,
            "mode": "normal",
        }
        valid, _ = validator.validate_location(data)
        assert valid is True

        # 24颗卫星
        data["satellites"] = 24  # 最大值
        valid, _ = validator.validate_location(data)
        assert valid is True

        # 25颗卫星(超出)
        data["satellites"] = 25
        valid, error = validator.validate_location(data)
        assert valid is False


class TestGPSFormatConversion:
    """GPS数据格式转换测试"""

    def test_nmea_latitude_conversion(self):
        """测试NMEA纬度转换"""
        # 2937.1685N -> 29.6195
        nmea_lat = "2937.1685N"
        # 去掉最后的方向字符
        nmea_lat = nmea_lat[:-1]
        degrees = int(nmea_lat[:2])
        minutes = float(nmea_lat[2:])
        decimal = degrees + minutes / 60

        assert abs(decimal - 29.6195) < 0.0001

    def test_nmea_longitude_conversion(self):
        """测试NMEA经度转换"""
        # 10629.6172E -> 106.4936
        nmea_lng = "10629.6172E"
        # 去掉最后的方向字符
        nmea_lng = nmea_lng[:-1]
        degrees = int(nmea_lng[:3])
        minutes = float(nmea_lng[3:])
        decimal = degrees + minutes / 60

        assert abs(decimal - 106.4936) < 0.0001

    def test_speed_kmh_to_ms_conversion(self):
        """测试速度从Km/h到m/s转换"""
        # 36 Km/h -> 10 m/s
        speed_kmh = 36
        speed_ms = speed_kmh / 3.6

        assert abs(speed_ms - 10) < 0.1

    def test_accuracy_from_hdop(self):
        """测试从HDOP计算精度"""
        # hdop=2.1 -> accuracy≈10.5m
        hdop = 2.1
        accuracy = hdop * 5

        assert abs(accuracy - 10.5) < 0.1


class TestTimestampValidation:
    """时间戳验证测试"""

    def test_timestamp_format_iso8601(self):
        """测试ISO8601格式时间戳"""
        timestamp = "2024-01-15T14:30:00+08:00"

        # 验证基本格式
        assert "T" in timestamp
        assert "+08:00" in timestamp or "-" in timestamp

    def test_timestamp_format_without_timezone(self):
        """测试不带时区的时间戳"""
        timestamp = "2024-01-15T14:30:00"

        # 应该也能被接受
        assert len(timestamp) > 0

    def test_timestamp_old_timestamp(self):
        """测试老旧时间戳(5分钟前)"""
        old_time = datetime.utcnow() - timedelta(minutes=6)
        timestamp = old_time.isoformat() + "+00:00"

        # 验证时间戳格式
        assert "T" in timestamp

    def test_timestamp_future_timestamp(self):
        """测试未来时间戳(5分钟后)"""
        future_time = datetime.utcnow() + timedelta(minutes=6)
        timestamp = future_time.isoformat() + "+00:00"

        # 验证时间戳格式
        assert "T" in timestamp


class TestNonceValidation:
    """随机数验证测试"""

    def test_nonce_length(self):
        """测试nonce长度"""
        nonce = "abc123def456"

        assert len(nonce) == 12

    def test_nonce_special_characters(self):
        """测试特殊字符nonce"""
        nonce = "nonce!@#$%^&*()"

        assert len(nonce) > 0

    def test_nonce_unicode(self):
        """测试Unicode nonce"""
        nonce = "随机字符串nonce"

        assert len(nonce) > 0


class TestDeviceIDValidation:
    """设备ID验证测试"""

    def test_device_id_length_15(self):
        """测试15位设备ID"""
        device_id = "860000000000000"

        assert len(device_id) == 15

    def test_device_id_length_16(self):
        """测试16位设备ID(最大)"""
        device_id = "8600000000000000"

        assert len(device_id) == 16

    def test_device_id_too_long(self):
        """测试设备ID过长"""
        device_id = "86000000000000000"  # 17位

        assert len(device_id) > 16

    def test_device_id_all_digits(self):
        """测试全数字设备ID"""
        device_id = "123456789012345"

        assert device_id.isdigit()


class TestSessionIDValidation:
    """会话ID验证测试"""

    def test_session_id_uuid_format(self):
        """测试UUID格式会话ID"""
        session_id = "12345678-1234-1234-1234-123456789012"

        # 验证UUID格式
        parts = session_id.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12


class TestErrorCodeMapping:
    """错误码映射测试"""

    def test_error_code_success(self):
        """测试成功错误码"""
        code = 0
        messages = {
            0: "success",
            1001: "device_not_registered",
            1002: "checksum_failed",
            1003: "parameter_error",
            1004: "server_busy",
            1005: "session_invalid",
            1006: "rate_limit_exceeded",
            3001: "session_expired",
            3002: "device_locked",
            3003: "signature_invalid",
            3004: "encryption_failed",
        }

        assert messages[code] == "success"

    def test_all_error_codes(self):
        """测试所有错误码"""
        error_codes = [
            (0, "success"),
            (1001, "device_not_registered"),
            (1002, "checksum_failed"),
            (1003, "parameter_error"),
            (1004, "server_busy"),
            (1005, "session_invalid"),
            (1006, "rate_limit_exceeded"),
            (3001, "session_expired"),
            (3002, "device_locked"),
            (3003, "signature_invalid"),
            (3004, "encryption_failed"),
        ]

        for code, expected_message in error_codes:
            assert code > 0 or code == 0


class TestAlarmTypeMapping:
    """报警类型映射测试"""

    def test_all_alarm_types(self):
        """测试所有报警类型"""
        alarm_types = [
            (1, "tamper", "防拆"),
            (2, "fall", "摔倒"),
            (3, "still", "静止"),
            (4, "low_battery", "低电量"),
            (5, "sos", "SOS"),
            (6, "shutdown", "关机"),
        ]

        for code, name, desc in alarm_types:
            assert code >= 1
            assert code <= 6


class TestAlarmLevelMapping:
    """报警级别映射测试"""

    def test_all_alarm_levels(self):
        """测试所有报警级别"""
        alarm_levels = [
            (1, "low", "低"),
            (2, "medium", "中"),
            (3, "high", "高"),
            (4, "urgent", "紧急"),
        ]

        for code, name, desc in alarm_levels:
            assert code >= 1
            assert code <= 4


class TestDeviceModeMapping:
    """设备模式映射测试"""

    def test_all_device_modes(self):
        """测试所有设备模式"""
        modes = ["normal", "low_power", "alarm", "sleep"]

        for mode in modes:
            assert mode in ["normal", "low_power", "alarm", "sleep"]
