# -*- coding: utf-8 -*-
"""
内存监控中间件
"""

import asyncio
import psutil
import os
from typing import Callable

from app.core.logger import logger
from app.config.limits import MAX_MEMORY_USAGE


class MemoryMiddleware:
    """内存监控中间件"""

    def __init__(self, warning_threshold: float = 0.8, critical_threshold: float = 0.9):
        """
        初始化内存监控中间件

        Args:
            warning_threshold: 警告阈值比例
            critical_threshold: 严重阈值比例
        """
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self._process = psutil.Process(os.getpid())

    def get_memory_usage(self) -> float:
        """
        获取当前内存使用比例

        Returns:
            内存使用比例 (0.0 - 1.0)
        """
        memory_info = self._process.memory_info()
        return memory_info.rss / MAX_MEMORY_USAGE

    def check_memory(self) -> tuple:
        """
        检查内存使用状态

        Returns:
            (状态, 消息)
        """
        usage = self.get_memory_usage()

        if usage >= self.critical_threshold:
            return "critical", f"Memory usage critical: {usage * 100:.1f}%"
        elif usage >= self.warning_threshold:
            return "warning", f"Memory usage high: {usage * 100:.1f}%"

        return "normal", f"Memory usage: {usage * 100:.1f}%"

    async def middleware(self, handler: Callable) -> Callable:
        """
        包装处理器，检查内存使用

        Args:
            handler: 处理器函数

        Returns:
            包装后的处理器
        """
        async def wrapped(*args, **kwargs):
            status, message = self.check_memory()

            if status == "critical":
                logger.error(f"MEMORY CRITICAL: {message}")
                # 触发GC
                import gc
                gc.collect()
            elif status == "warning":
                logger.warning(f"MEMORY WARNING: {message}")

            return await handler(*args, **kwargs)

        return wrapped


# 全局内存中间件实例
memory_middleware = MemoryMiddleware()
