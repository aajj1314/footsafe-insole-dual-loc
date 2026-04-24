# -*- coding: utf-8 -*-
"""
本地内存缓存模块
L1缓存，使用LRU算法
"""

import asyncio
import time
from typing import Optional, Any, Dict, OrderedDict
from collections import OrderedDict as OD

from app.config.limits import LOCAL_CACHE_MAX_SIZE, LOCAL_CACHE_TTL
from app.core.logger import logger


class LRUCache:
    """
    LRU (Least Recently Used) 缓存

    用于缓存热点数据，减少数据库访问
    """

    def __init__(self, max_size: int = LOCAL_CACHE_MAX_SIZE, ttl: int = LOCAL_CACHE_TTL):
        """
        初始化LRU缓存

        Args:
            max_size: 最大缓存条目数
            ttl: 缓存过期时间(秒)
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OD = OD()
        self._timestamps: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值或None
        """
        async with self._lock:
            if key not in self._cache:
                return None

            # 检查是否过期
            if key in self._timestamps:
                if time.time() - self._timestamps[key] > self.ttl:
                    # 已过期，删除
                    self._cache.pop(key, None)
                    self._timestamps.pop(key, None)
                    return None

            # 移到末尾（最近使用）
            self._cache.move_to_end(key)
            return self._cache[key]

    async def set(self, key: str, value: Any) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
        """
        async with self._lock:
            # 如果key存在，先删除
            if key in self._cache:
                self._cache.pop(key)

            # 如果缓存已满，删除最旧的
            while len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                self._cache.pop(oldest_key)
                self._timestamps.pop(oldest_key, None)

            # 添加新值
            self._cache[key] = value
            self._timestamps[key] = time.time()

    async def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        async with self._lock:
            if key in self._cache:
                self._cache.pop(key)
                self._timestamps.pop(key, None)
                return True
            return False

    async def clear(self) -> None:
        """清空所有缓存"""
        async with self._lock:
            self._cache.clear()
            self._timestamps.clear()

    async def cleanup_expired(self) -> int:
        """
        清理过期缓存

        Returns:
            清理的条目数
        """
        async with self._lock:
            now = time.time()
            expired_keys = [
                key
                for key, timestamp in self._timestamps.items()
                if now - timestamp > self.ttl
            ]

            for key in expired_keys:
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

            return len(expired_keys)

    def get_stats(self) -> dict:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "utilization": len(self._cache) / self.max_size if self.max_size > 0 else 0,
        }


class DeviceInfoCache(LRUCache):
    """设备信息缓存"""

    def __init__(self):
        super().__init__(max_size=LOCAL_CACHE_MAX_SIZE, ttl=LOCAL_CACHE_TTL)

    async def get_device(self, device_id: str) -> Optional[dict]:
        """获取设备信息"""
        return await self.get(f"device:{device_id}")

    async def set_device(self, device_id: str, device_info: dict) -> None:
        """设置设备信息"""
        await self.set(f"device:{device_id}", device_info)

    async def delete_device(self, device_id: str) -> bool:
        """删除设备信息"""
        return await self.delete(f"device:{device_id}")


# 全局缓存实例
device_info_cache = DeviceInfoCache()
