# -*- coding: utf-8 -*-
"""
MD5校验和计算模块
与硬件端checksum.c完全一致
"""

import hashlib
from typing import Optional


def calculate_checksum(
    version: str,
    device_id: str,
    timestamp: str,
    nonce: str,
    data: dict,
    preshared_key: str,
) -> str:
    """
    计算MD5校验值

    计算公式: checksum = MD5(version + device_id + timestamp + nonce + JSON(data) + 预共享密钥)

    Args:
        version: 协议版本
        device_id: 设备IMEI号
        timestamp: 时间戳
        nonce: 随机字符串(12位)
        data: 数据体字典
        preshared_key: 预共享密钥

    Returns:
        MD5校验值(32位十六进制字符串)
    """
    import json

    # 按照指定顺序拼接字符串
    data_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    concat_str = version + device_id + timestamp + nonce + data_str + preshared_key

    # 计算MD5
    md5_hash = hashlib.md5(concat_str.encode("utf-8"))
    return md5_hash.hexdigest()


def verify_checksum(
    version: str,
    device_id: str,
    timestamp: str,
    nonce: str,
    data: dict,
    checksum: str,
    preshared_key: str,
) -> bool:
    """
    验证MD5校验值

    Args:
        version: 协议版本
        device_id: 设备IMEI号
        timestamp: 时间戳
        nonce: 随机字符串(12位)
        data: 数据体字典
        checksum: 待验证的校验值
        preshared_key: 预共享密钥

    Returns:
        校验是否通过
    """
    expected_checksum = calculate_checksum(
        version, device_id, timestamp, nonce, data, preshared_key
    )
    return expected_checksum.lower() == checksum.lower()
