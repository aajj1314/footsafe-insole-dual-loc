# -*- coding: utf-8 -*-
"""
数据编解码模块
"""

import json
from typing import Optional, Any, Dict
from datetime import datetime

from app.core.exceptions import ProtocolParseException


class Codec:
    """数据编解码器"""

    @staticmethod
    def encode(data: Dict[str, Any]) -> bytes:
        """
        编码为JSON字节

        Args:
            data: 数据字典

        Returns:
            JSON字节
        """
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    @staticmethod
    def decode(data: bytes) -> Optional[Dict[str, Any]]:
        """
        解码JSON字节

        Args:
            data: JSON字节

        Returns:
            数据字典或None
        """
        try:
            return json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ProtocolParseException(
                message=f"Failed to decode JSON: {e}",
                details={"data_preview": data[:100]},
            )

    @staticmethod
    def encode_response(code: int, message: str, data: Optional[Dict] = None) -> bytes:
        """
        编码响应报文

        Args:
            code: 错误码
            message: 消息
            data: 数据

        Returns:
            响应JSON字节
        """
        response = {
            "code": code,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat() + "+08:00",
        }
        return Codec.encode(response)

    @staticmethod
    def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
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

    @staticmethod
    def format_timestamp(dt: Optional[datetime] = None) -> str:
        """
        格式化为ISO 8601时间戳

        Args:
            dt: datetime对象，None则使用当前时间

        Returns:
            ISO 8601时间戳字符串
        """
        if dt is None:
            dt = datetime.utcnow()
        return dt.isoformat() + "+08:00"
