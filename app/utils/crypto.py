# -*- coding: utf-8 -*-
"""
加密工具模块
"""

import hashlib
import hmac
from typing import Optional


def md5(data: str) -> str:
    """
    计算MD5哈希

    Args:
        data: 待哈希数据

    Returns:
        十六进制哈希字符串
    """
    return hashlib.md5(data.encode("utf-8")).hexdigest()


def sha256(data: str) -> str:
    """
    计算SHA256哈希

    Args:
        data: 待哈希数据

    Returns:
        十六进制哈希字符串
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def sha512(data: str) -> str:
    """
    计算SHA512哈希

    Args:
        data: 待哈希数据

    Returns:
        十六进制哈希字符串
    """
    return hashlib.sha512(data.encode("utf-8")).hexdigest()


def hmac_sha256(key: str, data: str) -> str:
    """
    计算HMAC-SHA256

    Args:
        key: 密钥
        data: 数据

    Returns:
        十六进制哈希字符串
    """
    return hmac.new(
        key.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def generate_random_string(length: int = 16) -> str:
    """
    生成随机字符串

    Args:
        length: 长度

    Returns:
        随机字符串
    """
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_random_hex(length: int = 32) -> str:
    """
    生成随机十六进制字符串

    Args:
        length: 长度

    Returns:
        随机十六进制字符串
    """
    import secrets
    return secrets.token_hex(length // 2)
