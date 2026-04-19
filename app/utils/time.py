# -*- coding: utf-8 -*-
"""
时间工具模块
"""

from datetime import datetime, timezone, timedelta
from typing import Optional


def get_current_timestamp() -> str:
    """
    获取当前时间戳（ISO 8601格式）

    Returns:
        ISO 8601时间戳字符串
    """
    return datetime.now(timezone.utc).isoformat()


def get_current_timestamp_with_offset(offset: int = 8) -> str:
    """
    获取带时区偏移的时间戳

    Args:
        offset: 时区偏移（小时）

    Returns:
        ISO 8601时间戳字符串
    """
    tz = timezone(timedelta(hours=offset))
    return datetime.now(tz).isoformat()


def parse_iso8601(timestamp_str: str) -> Optional[datetime]:
    """
    解析ISO 8601时间戳

    Args:
        timestamp_str: 时间戳字符串

    Returns:
        datetime对象或None
    """
    try:
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str.replace("Z", "+00:00")
        return datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError):
        return None


def timestamp_to_utc(timestamp_str: str) -> Optional[datetime]:
    """
    转换时间戳为UTC datetime

    Args:
        timestamp_str: ISO 8601时间戳

    Returns:
        UTC datetime对象或None
    """
    dt = parse_iso8601(timestamp_str)
    if dt:
        return dt.astimezone(timezone.utc)
    return None


def get_timestamp_diff_seconds(timestamp1: str, timestamp2: str) -> Optional[float]:
    """
    计算两个时间戳的差值（秒）

    Args:
        timestamp1: 时间戳1
        timestamp2: 时间戳2

    Returns:
        差值秒数或None
    """
    dt1 = parse_iso8601(timestamp1)
    dt2 = parse_iso8601(timestamp2)

    if dt1 and dt2:
        delta = dt1 - dt2
        return abs(delta.total_seconds())

    return None


def is_timestamp_expired(timestamp_str: str, expire_seconds: int) -> bool:
    """
    检查时间戳是否过期

    Args:
        timestamp_str: ISO 8601时间戳
        expire_seconds: 过期秒数

    Returns:
        是否过期
    """
    dt = parse_iso8601(timestamp_str)
    if not dt:
        return True

    now = datetime.now(timezone.utc)
    dt_utc = dt.astimezone(timezone.utc)

    return (now - dt_utc).total_seconds() > expire_seconds
