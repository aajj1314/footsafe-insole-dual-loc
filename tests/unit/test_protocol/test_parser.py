# -*- coding: utf-8 -*-
"""
协议处理单元测试
"""

import pytest
from app.protocol.parser import MessageParser
from app.protocol.validator import MessageValidator
from app.protocol.serializer import ResponseSerializer


class TestMessageParser:
    """报文解析器测试"""

    def test_parse_valid_json(self):
        """测试解析有效JSON"""
        parser = MessageParser()
        data = b'{"version": "1.0", "device_id": "860000000000000"}'

        result = parser.parse(data)

        assert result["version"] == "1.0"
        assert result["device_id"] == "860000000000000"

    def test_parse_invalid_json(self):
        """测试解析无效JSON"""
        from app.core.exceptions import ProtocolParseException

        parser = MessageParser()
        data = b"invalid json"

        with pytest.raises(ProtocolParseException):
            parser.parse(data)


class TestMessageValidator:
    """消息验证器测试"""

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
        """测试基础验证失败-版本"""
        validator = MessageValidator()
        message = {
            "version": "2.0",  # 无效版本
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "location",
            "data": {},
            "checksum": "abc123",
        }

        valid, error = validator.validate_base(message)
        assert valid is False
        assert "version" in error

    def test_validate_location_valid(self):
        """测试位置数据验证通过"""
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
            "mode": "normal",
        }

        valid, error = validator.validate_location(data)
        assert valid is True

    def test_validate_location_invalid_latitude(self):
        """测试位置数据验证失败-纬度"""
        validator = MessageValidator()
        data = {
            "latitude": 100.0,  # 无效纬度
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


class TestResponseSerializer:
    """响应序列化器测试"""

    def test_serialize_success(self):
        """测试序列化成功响应"""
        data = ResponseSerializer.serialize_success({"key": "value"})

        assert isinstance(data, bytes)
        assert b'"code":0' in data
        assert b'"message":"success"' in data

    def test_serialize_error(self):
        """测试序列化错误响应"""
        data = ResponseSerializer.serialize_error(1001, "device_not_registered")

        assert isinstance(data, bytes)
        assert b'"code":1001' in data
        assert b'"device_not_registered"' in data

    def test_serialize_auth_response(self):
        """测试序列化认证响应"""
        data = ResponseSerializer.serialize_auth_response(
            session_id="12345678-1234-1234-1234-123456789012",
            heartbeat_interval=30,
        )

        assert isinstance(data, bytes)
        assert b'"session_id"' in data
        assert b'"heartbeat_interval":30' in data
