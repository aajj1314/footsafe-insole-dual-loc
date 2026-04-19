# -*- coding: utf-8 -*-
"""
安全模块单元测试
"""

import pytest
from app.core.security.checksum import calculate_checksum, verify_checksum
from app.core.security.fingerprint import generate_fingerprint, verify_fingerprint


class TestChecksum:
    """MD5校验和测试"""

    def test_calculate_checksum(self):
        """测试校验和计算"""
        checksum = calculate_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"battery": 85},
            preshared_key="test_key",
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
            preshared_key="test_key",
        )

        result = verify_checksum(
            version="1.0",
            device_id="860000000000000",
            timestamp="2024-01-15T14:30:00+08:00",
            nonce="abc123def456",
            data={"battery": 85},
            checksum=checksum,
            preshared_key="test_key",
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
            preshared_key="test_key",
        )

        assert result is False


class TestFingerprint:
    """设备指纹测试"""

    def test_generate_fingerprint(self):
        """测试指纹生成"""
        fingerprint = generate_fingerprint(
            imei="860000000000000",
            iccid="89860000000000000000",
            firmware_version="1.2.3",
            hardware_version="1.0",
        )

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64

    def test_verify_fingerprint_success(self):
        """测试指纹验证成功"""
        fingerprint = generate_fingerprint(
            imei="860000000000000",
            iccid="89860000000000000000",
            firmware_version="1.2.3",
            hardware_version="1.0",
        )

        result = verify_fingerprint(
            device_id="860000000000000",
            iccid="89860000000000000000",
            firmware_version="1.2.3",
            hardware_version="1.0",
            expected_fingerprint=fingerprint,
        )

        assert result is True

    def test_verify_fingerprint_failed(self):
        """测试指纹验证失败"""
        result = verify_fingerprint(
            device_id="860000000000000",
            iccid="89860000000000000000",
            firmware_version="1.2.3",
            hardware_version="1.0",
            expected_fingerprint="invalid_fingerprint",
        )

        assert result is False
