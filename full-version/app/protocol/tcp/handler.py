# -*- coding: utf-8 -*-
"""
TCP报文分发模块
"""

from typing import Dict, Any, Callable

from app.core.logger import logger
from app.config.constants import (
    MESSAGE_TYPE_AUTH,
    MESSAGE_TYPE_TCP_HEARTBEAT,
    MESSAGE_TYPE_COMMAND_RESPONSE,
    MESSAGE_TYPE_OTA_PROGRESS,
    MESSAGE_TYPE_BATCH_REPORT,
    MESSAGE_TYPE_DEVICE_ERROR,
)


class TCPHandler:
    """TCP报文分发处理器"""

    def __init__(self):
        """初始化TCP处理器"""
        self._handlers: Dict[str, Callable] = {}

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """
        注册消息处理器

        Args:
            message_type: 消息类型
            handler: 处理函数
        """
        self._handlers[message_type] = handler
        logger.debug(f"Registered TCP handler for: {message_type}")

    async def handle(
        self,
        message: Dict[str, Any],
        conn_id: str,
    ) -> Any:
        """
        处理TCP消息

        Args:
            message: 消息字典
            conn_id: 连接ID

        Returns:
            响应数据
        """
        msg_type = message.get("type")

        handler = self._handlers.get(msg_type)
        if not handler:
            logger.warning(f"No handler for TCP message type: {msg_type}")
            return None

        try:
            return await handler(message, conn_id)
        except Exception as e:
            logger.error(f"Error handling TCP message {msg_type}: {e}")
            raise

    def get_registered_types(self) -> list:
        """获取已注册的消息类型"""
        return list(self._handlers.keys())


# 全局TCP处理器实例
tcp_handler = TCPHandler()
