# -*- coding: utf-8 -*-
"""
UDP报文分发模块
"""

from typing import Dict, Any, Optional, Callable
import asyncio

from app.core.logger import logger
from app.config.constants import (
    MESSAGE_TYPE_LOCATION,
    MESSAGE_TYPE_ALARM,
    MESSAGE_TYPE_HEARTBEAT,
    MESSAGE_TYPE_COMMAND_RESPONSE,
)


class UDPHandler:
    """UDP报文分发处理器"""

    def __init__(self):
        """初始化UDP处理器"""
        self._handlers: Dict[str, Callable] = {}
        self._lock = asyncio.Lock()

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """
        注册消息处理器

        Args:
            message_type: 消息类型
            handler: 处理函数
        """
        self._handlers[message_type] = handler
        logger.debug(f"Registered UDP handler for: {message_type}")

    async def handle(
        self,
        message: Dict[str, Any],
        remote_addr: tuple,
    ) -> None:
        """
        处理UDP消息

        Args:
            message: 消息字典
            remote_addr: 远程地址
        """
        msg_type = message.get("type")

        handler = self._handlers.get(msg_type)
        if not handler:
            logger.warning(f"No handler for UDP message type: {msg_type}")
            return

        try:
            await handler(message, remote_addr)
        except Exception as e:
            logger.error(f"Error handling UDP message {msg_type}: {e}")

    def get_registered_types(self) -> list:
        """获取已注册的消息类型"""
        return list(self._handlers.keys())


# 全局UDP处理器实例
udp_handler = UDPHandler()
