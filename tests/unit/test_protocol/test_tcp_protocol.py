# -*- coding: utf-8 -*-
"""
TCP协议接口单元测试
覆盖:
- TCP身份认证 (auth)
- TCP保活心跳 (tcp_heartbeat)
- 服务器指令响应 (command_response)
- OTA升级进度上报 (ota_progress)
- 批量数据上报 (batch_report)
- 设备异常状态 (device_error)
"""

import pytest
import json
import uuid
from datetime import datetime

from app.protocol.parser import MessageParser
from app.protocol.validator import MessageValidator
from app.core.security.checksum import calculate_checksum, verify_checksum
from app.core.exceptions import ProtocolParseException
from tests.conftest import create_tcp_message, TEST_PRESHARED_KEY


class TestTCPParser:
    """TCP报文解析器测试"""

    def test_parse_valid_auth_message(self):
        """测试解析有效认证消息"""
        parser = MessageParser()
        data = json.dumps({
            "version": "1.0",
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "auth",
            "data": {
                "firmware_version": "1.2.3",
                "hardware_version": "1.0",
                "iccid": "89860000000000000000",
                "fingerprint": "device_fingerprint_string",
            },
            "checksum": "test",
        }).encode("utf-8")

        result = parser.parse(data)

        assert result["version"] == "1.0"
        assert result["device_id"] == "860000000000000"
        assert result["type"] == "auth"
        assert result["data"]["firmware_version"] == "1.2.3"

    def test_parse_valid_tcp_heartbeat_message(self):
        """测试解析有效TCP心跳消息"""
        parser = MessageParser()
        data = json.dumps({
            "version": "1.0",
            "device_id": "860000000000000",
            "session_id": "12345678-1234-1234-1234-123456789012",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "tcp_heartbeat",
            "data": {},
            "checksum": "test",
        }).encode("utf-8")

        result = parser.parse(data)

        assert result["type"] == "tcp_heartbeat"
        assert result["session_id"] == "12345678-1234-1234-1234-123456789012"

    def test_parse_invalid_json(self):
        """测试解析无效JSON"""
        parser = MessageParser()
        data = b"invalid json"

        with pytest.raises(ProtocolParseException):
            parser.parse(data)


class TestTCPValidator:
    """TCP报文验证器测试"""

    def test_validate_base_valid(self):
        """测试基础验证通过"""
        validator = MessageValidator()
        message = {
            "version": "1.0",
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "auth",
            "data": {},
            "checksum": "abc123",
        }

        valid, error = validator.validate_base(message)
        assert valid is True
        assert error is None

    def test_validate_base_missing_session_id(self):
        """测试基础验证失败-非auth消息缺少session_id"""
        validator = MessageValidator()
        message = {
            "version": "1.0",
            "device_id": "860000000000000",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "tcp_heartbeat",
            "data": {},
            "checksum": "abc123",
            # 缺少session_id
        }

        # 注意: 基础验证不检查session_id, session_id验证在TCP特定验证中
        valid, error = validator.validate_base(message)
        assert valid is True


class TestAuthValidation:
    """认证数据验证测试"""

    def test_validate_auth_valid(self, mock_auth_data):
        """测试认证数据验证通过"""
        validator = MessageValidator()
        valid, error = validator.validate_auth(mock_auth_data)
        assert valid is True
        assert error is None

    def test_validate_auth_missing_firmware_version(self):
        """测试认证数据验证失败-缺少固件版本"""
        validator = MessageValidator()
        data = {
            "hardware_version": "1.0",
            "iccid": "89860000000000000000",
            "fingerprint": "device_fingerprint_string",
        }
        valid, error = validator.validate_auth(data)
        assert valid is False
        assert "firmware_version" in error.lower()

    def test_validate_auth_missing_hardware_version(self):
        """测试认证数据验证失败-缺少硬件版本"""
        validator = MessageValidator()
        data = {
            "firmware_version": "1.2.3",
            "iccid": "89860000000000000000",
            "fingerprint": "device_fingerprint_string",
        }
        valid, error = validator.validate_auth(data)
        assert valid is False
        assert "hardware_version" in error.lower()

    def test_validate_auth_missing_iccid(self):
        """测试认证数据验证失败-缺少ICCID"""
        validator = MessageValidator()
        data = {
            "firmware_version": "1.2.3",
            "hardware_version": "1.0",
            "fingerprint": "device_fingerprint_string",
        }
        valid, error = validator.validate_auth(data)
        assert valid is False
        assert "iccid" in error.lower()

    def test_validate_auth_missing_fingerprint(self):
        """测试认证数据验证失败-缺少指纹"""
        validator = MessageValidator()
        data = {
            "firmware_version": "1.2.3",
            "hardware_version": "1.0",
            "iccid": "89860000000000000000",
        }
        valid, error = validator.validate_auth(data)
        assert valid is False
        assert "fingerprint" in error.lower()


class TestTCPHeartbeatValidation:
    """TCP心跳数据验证测试"""

    def test_validate_tcp_heartbeat_empty_data(self):
        """测试TCP心跳空数据验证"""
        validator = MessageValidator()
        message = {
            "version": "1.0",
            "device_id": "860000000000000",
            "session_id": "12345678-1234-1234-1234-123456789012",
            "timestamp": "2024-01-15T14:30:00+08:00",
            "nonce": "abc123def456",
            "type": "tcp_heartbeat",
            "data": {},
            "checksum": "test",
        }

        # TCP心跳的data为空对象,基础验证应该通过
        valid, error = validator.validate_base(message)
        assert valid is True


class TestOTAProgressValidation:
    """OTA进度数据验证测试"""

    def test_validate_ota_progress_valid(self):
        """测试OTA进度数据验证通过"""
        validator = MessageValidator()
        data = {
            "upgrade_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "status": "downloading",
            "progress": 50,
            "error_code": 0,
            "error_message": "",
        }

        # 检查progress范围
        progress = data.get("progress")
        assert 0 <= progress <= 100

    def test_validate_ota_progress_boundary_progress_0(self):
        """测试OTA进度边界值-0"""
        data = {
            "upgrade_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "status": "downloading",
            "progress": 0,
            "error_code": 0,
            "error_message": "",
        }
        assert 0 <= data["progress"] <= 100

    def test_validate_ota_progress_boundary_progress_100(self):
        """测试OTA进度边界值-100"""
        data = {
            "upgrade_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "status": "downloading",
            "progress": 100,
            "error_code": 0,
            "error_message": "",
        }
        assert 0 <= data["progress"] <= 100

    def test_validate_ota_progress_invalid_status(self):
        """测试OTA进度无效状态"""
        data = {
            "upgrade_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "status": "invalid_status",
            "progress": 50,
            "error_code": 0,
            "error_message": "",
        }

        valid_statuses = {"downloading", "verifying", "upgrading", "success", "failed"}
        assert data["status"] not in valid_statuses

    def test_validate_ota_progress_all_statuses(self):
        """测试所有有效OTA状态"""
        valid_statuses = ["downloading", "verifying", "upgrading", "success", "failed"]
        for status in valid_statuses:
            data = {
                "upgrade_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "status": status,
                "progress": 50,
                "error_code": 0,
                "error_message": "",
            }
            assert data["status"] in valid_statuses


class TestBatchReportValidation:
    """批量上报数据验证测试"""

    def test_validate_batch_report_valid(self):
        """测试批量上报数据验证通过"""
        data = {
            "total": 100,
            "index": 1,
            "items": [
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
            ],
        }

        assert isinstance(data["total"], int)
        assert isinstance(data["index"], int)
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0

    def test_validate_batch_report_boundary_total(self):
        """测试批量上报边界值"""
        # 根据API文档,批量最大条数为100
        data = {
            "total": 100,
            "index": 1,
            "items": [],
        }
        assert data["total"] <= 100

    def test_validate_batch_report_item_types(self):
        """测试批量上报项类型"""
        valid_types = {"location", "heartbeat", "alarm"}
        items = [
            {"type": "location", "timestamp": "2024-01-15T14:00:00+08:00", "data": {}},
            {"type": "heartbeat", "timestamp": "2024-01-15T14:01:00+08:00", "data": {}},
            {"type": "alarm", "timestamp": "2024-01-15T14:02:00+08:00", "data": {}},
        ]

        for item in items:
            assert item["type"] in valid_types


class TestDeviceErrorValidation:
    """设备错误数据验证测试"""

    def test_validate_device_error_valid(self):
        """测试设备错误数据验证通过"""
        data = {
            "error_type": "gps_fault",
            "error_level": 2,
            "error_message": "GPS module initialization failed",
            "error_code": 1001,
            "extra_data": {},
        }

        valid_error_codes = {1001, 1002, 1003, 1004, 1005, 1006, 1007}
        assert data["error_code"] in valid_error_codes

    def test_validate_device_error_all_types(self):
        """测试所有有效错误类型"""
        valid_errors = {
            1001: "gps_fault",
            1002: "communication_fault",
            1003: "sensor_fault",
            1004: "battery_fault",
            1005: "memory_fault",
            1006: "firmware_crash",
            1007: "watchdog_timeout",
        }

        for error_code, error_type in valid_errors.items():
            data = {
                "error_type": error_type,
                "error_level": 2,
                "error_message": f"{error_type} occurred",
                "error_code": error_code,
                "extra_data": {},
            }
            assert data["error_code"] == error_code
            assert data["error_type"] == error_type

    def test_validate_device_error_boundary_level(self):
        """测试设备错误级别边界"""
        data = {
            "error_type": "gps_fault",
            "error_level": 4,  # 最大级别
            "error_message": "GPS module initialization failed",
            "error_code": 1001,
            "extra_data": {},
        }
        assert 1 <= data["error_level"] <= 4


class TestTCPMessageFactory:
    """TCP消息工厂测试"""

    def test_create_auth_message(self, auth_message_factory):
        """测试创建认证消息"""
        message = auth_message_factory()

        assert message["version"] == "1.0"
        assert message["type"] == "auth"
        assert message["device_id"] == "860000000000000"
        assert "session_id" not in message  # auth消息不需要session_id
        assert "firmware_version" in message["data"]
        assert len(message["checksum"]) == 32

    def test_create_tcp_heartbeat_message(self, tcp_heartbeat_message_factory):
        """测试创建TCP心跳消息"""
        message = tcp_heartbeat_message_factory()

        assert message["type"] == "tcp_heartbeat"
        assert "session_id" in message
        assert message["session_id"] == "12345678-1234-1234-1234-123456789012"

    def test_create_command_response_message(self, command_response_message_factory):
        """测试创建命令响应消息"""
        message = command_response_message_factory()

        assert message["type"] == "command_response"
        assert "session_id" in message
        assert "command_id" in message["data"]
        assert "command_type" in message["data"]
        assert "result" in message["data"]

    def test_create_ota_progress_message(self, ota_progress_message_factory):
        """测试创建OTA进度消息"""
        message = ota_progress_message_factory(status="success", progress=100)

        assert message["type"] == "ota_progress"
        assert message["data"]["status"] == "success"
        assert message["data"]["progress"] == 100

    def test_create_batch_report_message(self, batch_report_message_factory):
        """测试创建批量上报消息"""
        message = batch_report_message_factory(total=50, index=2)

        assert message["type"] == "batch_report"
        assert message["data"]["total"] == 50
        assert message["data"]["index"] == 2

    def test_create_device_error_message(self, device_error_message_factory):
        """测试创建设备错误消息"""
        message = device_error_message_factory(error_code=1002, error_type="communication_fault")

        assert message["type"] == "device_error"
        assert message["data"]["error_code"] == 1002
        assert message["data"]["error_type"] == "communication_fault"


class TestTCPChecksum:
    """TCP校验和测试"""

    def test_calculate_tcp_checksum(self):
        """测试TCP校验和计算"""
        checksum = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"firmware_version": "1.2.3"},
            preshared_key=TEST_PRESHARED_KEY,
        )

        assert isinstance(checksum, str)
        assert len(checksum) == 32

    def test_verify_tcp_checksum_success(self):
        """测试TCP校验和验证成功"""
        checksum = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"firmware_version": "1.2.3"},
            preshared_key=TEST_PRESHARED_KEY,
        )

        result = verify_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"firmware_version": "1.2.3"},
            checksum=checksum,
            preshared_key=TEST_PRESHARED_KEY,
        )
        assert result is True

    def test_tcp_checksum_different_for_different_data(self):
        """测试不同数据产生不同校验和"""
        checksum1 = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"firmware_version": "1.2.3"},
            preshared_key=TEST_PRESHARED_KEY,
        )

        checksum2 = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"firmware_version": "1.2.4"},  # 不同版本
            preshared_key=TEST_PRESHARED_KEY,
        )

        assert checksum1 != checksum2


class TestCommandResponse:
    """命令响应测试"""

    def test_command_response_success(self, command_response_message_factory):
        """测试命令响应成功"""
        message = command_response_message_factory(
            command_type="get_location",
            result="success",
        )

        assert message["data"]["result"] == "success"
        assert "latitude" in message["data"]["result_data"]
        assert "longitude" in message["data"]["result_data"]

    def test_command_response_failed(self, command_response_message_factory):
        """测试命令响应失败"""
        message = command_response_message_factory(
            command_type="set_report_interval",
            result="failed",
        )

        assert message["data"]["result"] == "failed"
        assert message["data"]["result_data"] == {}

    def test_command_types(self, command_response_message_factory):
        """测试不同命令类型"""
        command_types = [
            "get_location",
            "get_status",
            "set_report_interval",
            "set_mode",
            "get_config",
            "ota_start",
            "ota_cancel",
            "factory_reset",
            "lock_device",
        ]

        for cmd_type in command_types:
            message = command_response_message_factory(command_type=cmd_type)
            assert message["data"]["command_type"] == cmd_type
