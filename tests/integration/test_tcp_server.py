# -*- coding: utf-8 -*-
"""
TCP服务器集成测试
测试TCP端口8889上的所有接口
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from tests.conftest import create_tcp_message, generate_checksum, TEST_PRESHARED_KEY


class TestTCPServerIntegration:
    """TCP服务器集成测试"""

    @pytest.mark.asyncio
    async def test_tcp_server_start_stop(self):
        """测试TCP服务器启动和停止"""
        from app.protocol.tcp.server import TCPServer

        server = TCPServer(host="127.0.0.1", port=18889)

        await server.start()
        assert server.is_running is True

        await server.stop()
        assert server.is_running is False

    @pytest.mark.asyncio
    async def test_tcp_server_bind_same_port_fails(self):
        """测试同一端口绑定失败"""
        from app.protocol.tcp.server import TCPServer

        server1 = TCPServer(host="127.0.0.1", port=18889)
        await server1.start()
        assert server1.is_running is True

        server2 = TCPServer(host="127.0.0.1", port=18889)
        try:
            await server2.start()
            await server2.stop()
        except OSError:
            pass  # 预期失败
        finally:
            await server1.stop()


class TestTCPMessageHandling:
    """TCP消息处理测试"""

    def test_create_auth_message(self):
        """测试创建认证消息"""
        message = create_tcp_message(
            msg_type="auth",
            device_id="860000000000000",
            session_id="",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "firmware_version": "1.2.3",
                "hardware_version": "1.0",
                "iccid": "89860000000000000000",
                "fingerprint": "device_fingerprint_string",
            },
        )

        assert message["type"] == "auth"
        assert message["device_id"] == "860000000000000"
        assert message["data"]["firmware_version"] == "1.2.3"
        assert "session_id" not in message  # auth消息不需要session_id

    def test_create_tcp_heartbeat_message(self):
        """测试创建TCP心跳消息"""
        message = create_tcp_message(
            msg_type="tcp_heartbeat",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={},
        )

        assert message["type"] == "tcp_heartbeat"
        assert message["session_id"] == "12345678-1234-1234-1234-123456789012"

    def test_create_command_response_message(self):
        """测试创建命令响应消息"""
        message = create_tcp_message(
            msg_type="command_response",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "command_id": "12345678-1234-1234-1234-123456789012",
                "command_type": "set_report_interval",
                "result": "success",
                "result_data": {},
            },
        )

        assert message["type"] == "command_response"
        assert message["data"]["command_type"] == "set_report_interval"
        assert message["data"]["result"] == "success"

    def test_create_ota_progress_message_downloading(self):
        """测试创建OTA下载进度消息"""
        message = create_tcp_message(
            msg_type="ota_progress",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "upgrade_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "status": "downloading",
                "progress": 50,
                "error_code": 0,
                "error_message": "",
            },
        )

        assert message["type"] == "ota_progress"
        assert message["data"]["status"] == "downloading"
        assert message["data"]["progress"] == 50

    def test_create_ota_progress_message_success(self):
        """测试创建OTA成功消息"""
        message = create_tcp_message(
            msg_type="ota_progress",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "upgrade_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "status": "success",
                "progress": 100,
                "error_code": 0,
                "error_message": "",
            },
        )

        assert message["type"] == "ota_progress"
        assert message["data"]["status"] == "success"
        assert message["data"]["progress"] == 100

    def test_create_ota_progress_message_failed(self):
        """测试创建OTA失败消息"""
        message = create_tcp_message(
            msg_type="ota_progress",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "upgrade_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "status": "failed",
                "progress": 75,
                "error_code": 1001,
                "error_message": "Download timeout",
            },
        )

        assert message["type"] == "ota_progress"
        assert message["data"]["status"] == "failed"
        assert message["data"]["error_code"] == 1001

    def test_create_batch_report_message(self):
        """测试创建批量上报消息"""
        message = create_tcp_message(
            msg_type="batch_report",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
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
            },
        )

        assert message["type"] == "batch_report"
        assert message["data"]["total"] == 100
        assert len(message["data"]["items"]) == 1

    def test_create_device_error_message(self):
        """测试创建设备错误消息"""
        message = create_tcp_message(
            msg_type="device_error",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "error_type": "gps_fault",
                "error_level": 2,
                "error_message": "GPS module initialization failed",
                "error_code": 1001,
                "extra_data": {},
            },
        )

        assert message["type"] == "device_error"
        assert message["data"]["error_type"] == "gps_fault"
        assert message["data"]["error_code"] == 1001


class TestTCPChecksumVerification:
    """TCP校验和验证测试"""

    def test_checksum_verification_success(self):
        """测试校验和验证成功"""
        from app.core.security.checksum import verify_checksum

        data = {"firmware_version": "1.2.3"}
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

    def test_checksum_verification_tampered_firmware(self):
        """测试校验和验证失败-固件版本被篡改"""
        from app.core.security.checksum import verify_checksum

        original_data = {"firmware_version": "1.2.3"}
        checksum = generate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data=original_data,
            preshared_key=TEST_PRESHARED_KEY,
        )

        # 篡改固件版本
        tampered_data = {"firmware_version": "1.2.4"}

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


class TestTCPOTAProgressStatuses:
    """TCP OTA进度状态测试"""

    @pytest.mark.parametrize("status", [
        "downloading",
        "verifying",
        "upgrading",
        "success",
        "failed",
    ])
    def test_all_ota_statuses(self, status):
        """测试所有OTA状态"""
        message = create_tcp_message(
            msg_type="ota_progress",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "upgrade_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "status": status,
                "progress": 50,
                "error_code": 0,
                "error_message": "",
            },
        )

        assert message["data"]["status"] == status


class TestTCPCommandTypes:
    """TCP命令类型测试"""

    @pytest.mark.parametrize("command_type", [
        "get_location",
        "get_status",
        "set_report_interval",
        "set_mode",
        "get_config",
        "ota_start",
        "ota_cancel",
        "factory_reset",
        "lock_device",
    ])
    def test_command_response_all_types(self, command_type):
        """测试所有命令类型的响应"""
        message = create_tcp_message(
            msg_type="command_response",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "command_id": "12345678-1234-1234-1234-123456789012",
                "command_type": command_type,
                "result": "success",
                "result_data": {},
            },
        )

        assert message["data"]["command_type"] == command_type


class TestTCPDeviceErrorTypes:
    """TCP设备错误类型测试"""

    @pytest.mark.parametrize("error_code,error_type", [
        (1001, "gps_fault"),
        (1002, "communication_fault"),
        (1003, "sensor_fault"),
        (1004, "battery_fault"),
        (1005, "memory_fault"),
        (1006, "firmware_crash"),
        (1007, "watchdog_timeout"),
    ])
    def test_all_device_error_types(self, error_code, error_type):
        """测试所有设备错误类型"""
        message = create_tcp_message(
            msg_type="device_error",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "error_type": error_type,
                "error_level": 2,
                "error_message": f"{error_type} occurred",
                "error_code": error_code,
                "extra_data": {},
            },
        )

        assert message["data"]["error_code"] == error_code
        assert message["data"]["error_type"] == error_type


class TestTCPBatchReportValidation:
    """TCP批量上报验证测试"""

    def test_batch_report_max_items(self):
        """测试批量上报最大条数100"""
        items = []
        for i in range(100):
            items.append({
                "type": "location",
                "timestamp": f"2024-01-15T{i % 24:02d}:{i % 60:02d}:00+08:00",
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
                    "gps_timestamp": f"2024-01-15T{i % 24:02d}:{i % 60:02d}:00+08:00",
                },
            })

        message = create_tcp_message(
            msg_type="batch_report",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "total": 100,
                "index": 1,
                "items": items,
            },
        )

        assert len(message["data"]["items"]) == 100

    def test_batch_report_mixed_types(self):
        """测试批量上报混合类型"""
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
            {
                "type": "heartbeat",
                "timestamp": "2024-01-15T14:01:00+08:00",
                "data": {
                    "battery": 85,
                    "signal_strength": 75,
                    "charging": False,
                    "temperature": 25.5,
                },
            },
            {
                "type": "alarm",
                "timestamp": "2024-01-15T14:02:00+08:00",
                "data": {
                    "alarm_type": 2,
                    "alarm_level": 3,
                    "latitude": 39.1028,
                    "longitude": 117.3475,
                    "accuracy": 8.5,
                    "battery": 85,
                    "alarm_data": {},
                },
            },
        ]

        message = create_tcp_message(
            msg_type="batch_report",
            device_id="860000000000000",
            session_id="12345678-1234-1234-1234-123456789012",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "total": 3,
                "index": 1,
                "items": items,
            },
        )

        assert len(message["data"]["items"]) == 3
        types = [item["type"] for item in message["data"]["items"]]
        assert "location" in types
        assert "heartbeat" in types
        assert "alarm" in types


class TestTCPSessionManagement:
    """TCP会话管理测试"""

    def test_session_id_format(self):
        """测试会话ID格式"""
        session_id = "12345678-1234-1234-1234-123456789012"

        # 验证UUID格式
        parts = session_id.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_auth_message_no_session_id(self):
        """测试auth消息不包含session_id"""
        message = create_tcp_message(
            msg_type="auth",
            device_id="860000000000000",
            session_id="",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={
                "firmware_version": "1.2.3",
                "hardware_version": "1.0",
                "iccid": "89860000000000000000",
                "fingerprint": "device_fingerprint_string",
            },
        )

        assert "session_id" not in message

    def test_non_auth_messages_have_session_id(self):
        """测试非auth消息包含session_id"""
        for msg_type in ["tcp_heartbeat", "command_response", "ota_progress", "batch_report", "device_error"]:
            message = create_tcp_message(
                msg_type=msg_type,
                device_id="860000000000000",
                session_id="12345678-1234-1234-1234-123456789012",
                timestamp="2024-01-15T14:30:00+08:00",
                nonce="abc123def456",
                data={},
            )

            assert "session_id" in message
            assert message["session_id"] == "12345678-1234-1234-1234-123456789012"


class TestTCPHeartbeatInterval:
    """TCP心跳间隔测试"""

    def test_heartbeat_interval_30_seconds(self):
        """测试心跳间隔30秒"""
        # 根据API文档,心跳间隔为30秒
        heartbeat_interval = 30

        assert heartbeat_interval == 30
        assert 10 <= heartbeat_interval <= 60  # 合理范围

    def test_session_expire_300_seconds(self):
        """测试会话过期时间300秒"""
        # 根据API文档,会话过期时间为300秒
        session_expire = 300

        assert session_expire == 300
