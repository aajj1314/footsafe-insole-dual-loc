# -*- coding: utf-8 -*-
"""
通用报文解析器
"""

import json
from typing import Optional, Dict, Any

from app.core.exceptions import ProtocolParseException
from app.core.logger import logger


class MessageParser:
    """报文解析器"""

    def __init__(self):
        """初始化报文解析器"""
        self._buffer = ""

    def parse(self, data: bytes) -> Optional[Dict[str, Any]]:
        """
        解析报文

        Args:
            data: 原始字节数据

        Returns:
            解析后的字典或None
        """
        try:
            # 解码为字符串
            json_str = data.decode("utf-8").strip()

            # 尝试解析JSON
            message = json.loads(json_str)

            # 验证基本结构
            if not isinstance(message, dict):
                raise ProtocolParseException(message="Message is not a dictionary")

            return message

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {e}, data: {data[:100]}")
            raise ProtocolParseException(
                message=f"JSON parse error: {e}",
                details={"data_preview": data[:100].decode("utf-8", errors="replace")},
            )
        except UnicodeDecodeError as e:
            logger.warning(f"Unicode decode error: {e}")
            raise ProtocolParseException(
                message=f"Unicode decode error: {e}",
                details={"data_preview": data[:100].decode("utf-8", errors="replace")},
            )

    def parse_batch(self, data: bytes) -> list:
        """
        解析批量报文

        Args:
            data: 原始字节数据

        Returns:
            报文列表
        """
        try:
            json_str = data.decode("utf-8").strip()
            messages = json.loads(json_str)

            if not isinstance(messages, list):
                raise ProtocolParseException(message="Batch message is not a list")

            return messages

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Batch parse error: {e}")
            raise ProtocolParseException(
                message=f"Batch parse error: {e}",
                details={"data_preview": data[:100].decode("utf-8", errors="replace")},
            )

    def reset(self) -> None:
        """重置解析器状态"""
        self._buffer = ""
