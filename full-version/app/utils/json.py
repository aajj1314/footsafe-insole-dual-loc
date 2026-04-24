# -*- coding: utf-8 -*-
"""
JSON工具模块
"""

import json
from typing import Any, Optional, Dict


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    安全解析JSON

    Args:
        data: JSON字符串
        default: 默认值

    Returns:
        解析后的对象或默认值
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    安全序列化为JSON

    Args:
        data: 待序列化对象
        default: 默认值

    Returns:
        JSON字符串或默认值
    """
    try:
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError):
        return default


def merge_dict(base: Dict, update: Dict) -> Dict:
    """
    合并字典

    Args:
        base: 基础字典
        update: 更新字典

    Returns:
        合并后的字典
    """
    result = base.copy()
    result.update(update)
    return result
