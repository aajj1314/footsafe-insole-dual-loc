# -*- coding: utf-8 -*-
"""
安全中间件
"""

import asyncio
from typing import Optional

from app.core.logger import logger
from app.core.security.checksum import verify_checksum
from app.core.security.nonce import nonce_manager
from app.config.settings import settings


class SecurityMiddleware:
    """安全中间件"""

    def __init__(self):
        """初始化安全中间件"""
        self._enabled = True

    async def verify_request(
        self,
        message: dict,
        preshared_key: Optional[str] = None,
    ) -> tuple:
        """
        验证请求的安全性

        Args:
            message: 消息字典
            preshared_key: 预共享密钥

        Returns:
            (是否通过, 错误码, 错误信息)
        """
        if not self._enabled:
            return True, 0, ""

        device_id = message.get("device_id")
        nonce = message.get("nonce")
        timestamp = message.get("timestamp")
        checksum = message.get("checksum")
        data = message.get("data", {})

        # 验证nonce
        if not await nonce_manager.is_nonce_valid(nonce, timestamp):
            return False, 1002, "checksum_failed"

        # 验证校验和
        key = preshared_key or settings.DEVICE_PRESHARED_KEY
        if not verify_checksum(
            message["version"],
            device_id,
            timestamp,
            nonce,
            data,
            checksum,
            key,
        ):
            return False, 1002, "checksum_failed"

        return True, 0, ""


# 全局安全中间件实例
security_middleware = SecurityMiddleware()
