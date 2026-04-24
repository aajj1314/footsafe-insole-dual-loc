# -*- coding: utf-8 -*-
"""
零拷贝缓冲区模块
"""

import asyncio
from typing import Optional
from dataclasses import dataclass


@dataclass
class Buffer:
    """网络缓冲区"""

    data: bytearray
    offset: int = 0
    length: int = 0

    def __post_init__(self):
        if self.length == 0:
            self.length = len(self.data)

    @classmethod
    def create(cls, size: int = 1024) -> "Buffer":
        """创建缓冲区"""
        return cls(data=bytearray(size))

    def write(self, data: bytes) -> int:
        """
        写入数据

        Args:
            data: 待写入数据

        Returns:
            写入字节数
        """
        available = len(self.data) - self.offset
        write_size = min(len(data), available)

        self.data[self.offset : self.offset + write_size] = data[:write_size]
        self.offset += write_size
        self.length = self.offset

        return write_size

    def read(self, size: int = -1) -> bytes:
        """
        读取数据

        Args:
            size: 读取字节数，-1表示读取全部

        Returns:
            读取的数据
        """
        if size < 0:
            size = self.length

        data = bytes(self.data[:size])
        return data

    def clear(self) -> None:
        """清空缓冲区"""
        self.data.clear()
        self.offset = 0
        self.length = 0

    def compact(self) -> None:
        """压缩缓冲区，将未读数据移到开头"""
        if self.offset > 0:
            self.data[: self.length - self.offset] = self.data[self.offset : self.length]
            self.length -= self.offset
            self.offset = 0


class BufferPool:
    """缓冲区池"""

    def __init__(self, pool_size: int = 100):
        """
        初始化缓冲区池

        Args:
            pool_size: 池大小
        """
        self.pool_size = pool_size
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=pool_size)
        self._lock = asyncio.Lock()

        # 预创建缓冲区
        for _ in range(pool_size // 2):
            self._pool.put_nowait(Buffer.create())

    async def acquire(self, size: int = 1024) -> Buffer:
        """
        获取缓冲区

        Args:
            size: 缓冲区大小

        Returns:
            缓冲区对象
        """
        try:
            buffer = self._pool.get_nowait()
            # 如果请求的大小大于现有缓冲区，创建新的
            if len(buffer.data) < size:
                buffer = Buffer.create(size)
            return buffer
        except asyncio.QueueEmpty:
            return Buffer.create(size)

    async def release(self, buffer: Buffer) -> None:
        """
        释放缓冲区回池

        Args:
            buffer: 缓冲区对象
        """
        buffer.clear()
        try:
            self._pool.put_nowait(buffer)
        except asyncio.QueueFull:
            # 池已满，丢弃
            pass

    def get_stats(self) -> dict:
        """获取池统计信息"""
        return {
            "pool_size": self.pool_size,
            "available": self._pool.qsize(),
        }


# 全局缓冲区池实例
buffer_pool = BufferPool()
