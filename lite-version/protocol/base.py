# -*- coding: utf-8 -*-
"""
基础协议类
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseProtocol(ABC):
    """基础协议类"""

    def __init__(self):
        """初始化基础协议"""
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """初始化协议处理器"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """关闭协议处理器"""
        pass

    @abstractmethod
    async def handle_message(
        self,
        message: Dict[str, Any],
        remote_addr: Optional[tuple] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        处理消息

        Args:
            message: 消息字典
            remote_addr: 远程地址

        Returns:
            响应字典或None
        """
        pass

    def validate_message(self, message: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        验证消息格式

        Args:
            message: 消息字典

        Returns:
            (是否有效, 错误信息)
        """
        required_fields = ["version", "device_id", "timestamp", "nonce", "type", "data", "checksum"]

        for field in required_fields:
            if field not in message:
                return False, f"Missing required field: {field}"

        return True, None
