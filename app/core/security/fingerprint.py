# -*- coding: utf-8 -*-
"""
设备指纹验证模块
与硬件端fingerprint.c完全一致
"""

import hashlib
from typing import Optional


def generate_fingerprint(
    imei: str,
    iccid: str,
    firmware_version: str,
    hardware_version: str,
) -> str:
    """
    生成设备指纹

    设备指纹组成: SHA256(IMEI + ICCID + firmware_version + hardware_version)

    Args:
        imei: 设备IMEI号
        iccid: SIM卡ICCID
        firmware_version: 固件版本号
        hardware_version: 硬件版本号

    Returns:
        设备指纹字符串(64位十六进制)
    """
    concat = imei + iccid + firmware_version + hardware_version
    return hashlib.sha256(concat.encode("utf-8")).hexdigest()


def verify_fingerprint(
    device_id: str,
    iccid: str,
    firmware_version: str,
    hardware_version: str,
    expected_fingerprint: str,
) -> bool:
    """
    验证设备指纹

    Args:
        device_id: 设备IMEI号
        iccid: SIM卡ICCID
        firmware_version: 固件版本号
        hardware_version: 硬件版本号
        expected_fingerprint: 期望的指纹值

    Returns:
        指纹是否匹配
    """
    actual_fingerprint = generate_fingerprint(
        device_id, iccid, firmware_version, hardware_version
    )
    return actual_fingerprint.lower() == expected_fingerprint.lower()


def extract_device_info_from_fingerprint(fingerprint: str) -> dict:
    """
    从指纹中提取设备信息（用于调试）

    注意：这是单向的，只能提取部分信息

    Args:
        fingerprint: 设备指纹

    Returns:
        设备信息字典
    """
    # 指纹本身不包含设备信息，这里返回原始指纹
    return {
        "fingerprint": fingerprint,
        "note": "Fingerprint is one-way hash, cannot extract original data",
    }
