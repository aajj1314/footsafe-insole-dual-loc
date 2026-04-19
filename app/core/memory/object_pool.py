# -*- coding: utf-8 -*-
"""
对象池实现模块
用于复用高频创建的对象，减少内存分配开销
"""

import asyncio
import time
from typing import TypeVar, Generic, Optional, Callable, Any
from collections import deque

T = TypeVar("T")


class ObjectPool(Generic[T]):
    """
    异步对象池

    用于复用高频创建的对象，如报文解析器、加密对象等
    """

    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 1000,
        idle_timeout: int = 300,
    ):
        """
        初始化对象池

        Args:
            factory: 对象工厂函数
            max_size: 对象池最大容量
            idle_timeout: 空闲对象超时时间(秒)
        """
        self.factory = factory
        self.max_size = max_size
        self.idle_timeout = idle_timeout

        self._pool: deque = deque()
        self._in_use: set = set()
        self._last_used: dict = {}
        self._lock = asyncio.Lock()

    async def acquire(self) -> T:
        """
        获取对象

        Returns:
            对象实例
        """
        async with self._lock:
            # 尝试从池中获取
            while self._pool:
                obj = self._pool.popleft()
                obj_id = id(obj)

                # 检查是否过期
                if obj_id in self._last_used:
                    last_time = self._last_used[obj_id]
                    if time.time() - last_time <= self.idle_timeout:
                        self._in_use.add(obj_id)
                        self._last_used.pop(obj_id, None)
                        return obj

            # 池为空，创建新对象
            obj = self.factory()
            self._in_use.add(id(obj))
            return obj

    async def release(self, obj: T) -> None:
        """
        释放对象回池

        Args:
            obj: 对象实例
        """
        async with self._lock:
            obj_id = id(obj)

            if obj_id not in self._in_use:
                return

            self._in_use.discard(obj_id)

            # 如果池未满，放回池中
            if len(self._pool) < self.max_size:
                self._pool.append(obj)
                self._last_used[obj_id] = time.time()

    async def cleanup(self) -> int:
        """
        清理过期对象

        Returns:
            清理的对象数量
        """
        async with self._lock:
            now = time.time()
            expired_ids = set()

            # 找出所有过期对象
            for obj_id, last_time in self._last_used.items():
                if now - last_time > self.idle_timeout:
                    expired_ids.add(obj_id)

            # 从池中移除过期对象
            original_len = len(self._pool)
            self._pool = deque(
                [obj for obj in self._pool if id(obj) not in expired_ids]
            )

            # 清理时间戳记录
            for obj_id in expired_ids:
                self._last_used.pop(obj_id, None)

            return original_len - len(self._pool)

    def get_stats(self) -> dict:
        """
        获取池统计信息

        Returns:
            统计信息字典
        """
        return {
            "pool_size": len(self._pool),
            "in_use": len(self._in_use),
            "max_size": self.max_size,
            "total_capacity": self.max_size,
            "utilization": len(self._in_use) / self.max_size if self.max_size > 0 else 0,
        }


# ==================== 预定义对象池 ====================


class ParserPool(ObjectPool):
    """报文解析器对象池"""

    def __init__(self):
        from app.protocol.parser import MessageParser
        super().__init__(
            factory=lambda: MessageParser(),
            max_size=1000,
            idle_timeout=300,
        )


class SerializerPool(ObjectPool):
    """响应序列化器对象池"""

    def __init__(self):
        from app.protocol.serializer import ResponseSerializer
        super().__init__(
            factory=lambda: ResponseSerializer(),
            max_size=1000,
            idle_timeout=300,
        )


# 全局对象池实例
parser_pool = ParserPool()
serializer_pool = SerializerPool()
