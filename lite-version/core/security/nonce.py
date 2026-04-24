# -*- coding: utf-8 -*-
"""
防重放攻击模块
与硬件端nonce.c完全一致
"""

import time
from typing import Set, Optional
import asyncio

from app.config.limits import NONCE_EXPIRE_SECONDS
from app.core.logger import logger


class NonceManager:
    """Nonce管理器 - 用于防止重放攻击"""

    def __init__(self, cleanup_interval: int = 600):
        """
        初始化Nonce管理器

        Args:
            cleanup_interval: 清理过期nonce的间隔(秒)
        """
        self._nonce_set: Set[str] = set()
        self._nonce_timestamps: dict = {}
        self._lock = asyncio.Lock()
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()

    async def is_nonce_valid(self, nonce: str, timestamp: str) -> bool:
        """
        验证nonce是否有效

        验证规则:
        1. nonce在300秒内未被使用过
        2. timestamp在300秒内

        Args:
            nonce: 随机字符串(12位)
            timestamp: ISO 8601时间戳

        Returns:
            nonce是否有效
        """
        async with self._lock:
            # 检查nonce是否已使用
            if nonce in self._nonce_set:
                logger.warning(f"Nonce already used: {nonce}")
                return False

            # 检查时间戳是否过期
            if not self._check_timestamp(timestamp):
                logger.warning(f"Timestamp expired: {timestamp}")
                return False

            # 标记nonce为已使用
            self._nonce_set.add(nonce)
            self._nonce_timestamps[nonce] = time.time()

            # 异步清理过期nonce
            await self._cleanup_if_needed()

            return True

    async def add_nonce(self, nonce: str) -> None:
        """
        添加nonce到已使用集合

        Args:
            nonce: 随机字符串
        """
        async with self._lock:
            self._nonce_set.add(nonce)
            self._nonce_timestamps[nonce] = time.time()

    def _check_timestamp(self, timestamp: str) -> bool:
        """
        检查时间戳是否在有效期内

        Args:
            timestamp: ISO 8601时间戳

        Returns:
            时间戳是否有效
        """
        from datetime import datetime, timezone

        try:
            # 解析ISO 8601时间戳
            if timestamp.endswith("Z"):
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                dt = datetime.fromisoformat(timestamp)

            # 计算时间差
            now = datetime.now(timezone.utc)
            diff = abs((now - dt).total_seconds())

            return diff <= NONCE_EXPIRE_SECONDS
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to parse timestamp: {timestamp}, error: {e}")
            return False

    async def _cleanup_if_needed(self) -> None:
        """清理过期的nonce"""
        now = time.time()

        if now - self._last_cleanup < self._cleanup_interval:
            return

        await self._cleanup_expired_nonces()
        self._last_cleanup = now

    async def _cleanup_expired_nonces(self) -> None:
        """清理所有过期的nonce"""
        async with self._lock:
            now = time.time()
            expired_nonces = [
                nonce
                for nonce, timestamp in self._nonce_timestamps.items()
                if now - timestamp > NONCE_EXPIRE_SECONDS
            ]

            for nonce in expired_nonces:
                self._nonce_set.discard(nonce)
                self._nonce_timestamps.pop(nonce, None)

            if expired_nonces:
                logger.info(f"Cleaned up {len(expired_nonces)} expired nonces")

    async def clear(self) -> None:
        """清空所有nonce"""
        async with self._lock:
            self._nonce_set.clear()
            self._nonce_timestamps.clear()


# 全局Nonce管理器实例
nonce_manager = NonceManager()
