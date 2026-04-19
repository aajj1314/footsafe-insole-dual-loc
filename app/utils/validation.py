# -*- coding: utf-8 -*-
"""
验证工具模块
"""

import re
from typing import Optional


def validate_imei(imei: str) -> bool:
    """
    验证IMEI格式

    Args:
        imei: IMEI字符串

    Returns:
        是否有效
    """
    if not imei or not isinstance(imei, str):
        return False

    # IMEI应为15位数字
    return bool(re.match(r"^\d{15}$", imei))


def validate_iccid(iccid: str) -> bool:
    """
    验证ICCID格式

    Args:
        iccid: ICCID字符串

    Returns:
        是否有效
    """
    if not iccid or not isinstance(iccid, str):
        return False

    # ICCID应为20位数字
    return bool(re.match(r"^\d{20}$", iccid))


def validate_version(version: str) -> bool:
    """
    验证版本号格式

    Args:
        version: 版本号字符串

    Returns:
        是否有效
    """
    if not version or not isinstance(version, str):
        return False

    # 版本号格式应为 x.y.z
    return bool(re.match(r"^\d+\.\d+\.\d+$", version))


def validate_uuid(uuid_str: str) -> bool:
    """
    验证UUID格式

    Args:
        uuid_str: UUID字符串

    Returns:
        是否有效
    """
    if not uuid_str or not isinstance(uuid_str, str):
        return False

    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(pattern, uuid_str.lower()))


def validate_latitude(lat: float) -> bool:
    """
    验证纬度值

    Args:
        lat: 纬度值

    Returns:
        是否有效
    """
    return -90.0 <= lat <= 90.0


def validate_longitude(lng: float) -> bool:
    """
    验证经度值

    Args:
        lng: 经度值

    Returns:
        是否有效
    """
    return -180.0 <= lng <= 180.0
