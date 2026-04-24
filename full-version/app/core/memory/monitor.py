# -*- coding: utf-8 -*-
"""
内存监控模块
"""

import asyncio
import psutil
import os
from typing import Optional, Callable

from app.config.limits import MAX_MEMORY_USAGE, MEMORY_MONITOR_INTERVAL
from app.core.logger import logger
from app.core.memory.gc_manager import gc_manager


class MemoryMonitor:
    """内存监控器"""

    def __init__(
        self,
        max_memory: int = MAX_MEMORY_USAGE,
        monitor_interval: int = MEMORY_MONITOR_INTERVAL,
    ):
        """
        初始化内存监控器

        Args:
            max_memory: 最大允许内存使用(字节)
            monitor_interval: 监控间隔(秒)
        """
        self.max_memory = max_memory
        self.monitor_interval = monitor_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._warning_threshold = 0.8  # 80%警告阈值
        self._critical_threshold = 0.9  # 90%严重阈值
        self._process = psutil.Process(os.getpid())

    def start(self) -> None:
        """启动内存监控"""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info(
            f"Memory monitor started, max: {self.max_memory / 1024 / 1024:.2f}MB, "
            f"interval: {self.monitor_interval}s"
        )

    def stop(self) -> None:
        """停止内存监控"""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Memory monitor stopped")

    async def _run(self) -> None:
        """运行监控循环"""
        while self._running:
            try:
                await asyncio.sleep(self.monitor_interval)
                await self._check_memory()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in memory monitor: {e}")

    async def _check_memory(self) -> None:
        """检查内存使用情况"""
        memory_info = self.get_memory_info()
        usage_percent = memory_info["percent"]

        # 检查是否超过阈值
        if usage_percent >= self._critical_threshold * 100:
            logger.error(
                f"CRITICAL: Memory usage critical: {memory_info['used_mb']:.2f}MB / "
                f"{memory_info['total_mb']:.2f}MB ({usage_percent:.1f}%)"
            )
            # 强制GC
            gc_manager.collect()
            await self._check_memory()  # 再次检查

        elif usage_percent >= self._warning_threshold * 100:
            logger.warning(
                f"WARNING: Memory usage high: {memory_info['used_mb']:.2f}MB / "
                f"{memory_info['total_mb']:.2f}MB ({usage_percent:.1f}%)"
            )

    def get_memory_info(self) -> dict:
        """
        获取内存信息

        Returns:
            内存信息字典
        """
        system_memory = psutil.virtual_memory()
        process_memory = self._process.memory_info()

        return {
            "total_mb": system_memory.total / 1024 / 1024,
            "available_mb": system_memory.available / 1024 / 1024,
            "used_mb": system_memory.used / 1024 / 1024,
            "percent": system_memory.percent,
            "process_rss_mb": process_memory.rss / 1024 / 1024,
            "process_vms_mb": process_memory.vms / 1024 / 1024,
            "process_percent": self._process.memory_percent(),
        }

    def get_memory_stats(self) -> dict:
        """
        获取详细内存统计

        Returns:
            内存统计字典
        """
        memory_info = self.get_memory_info()
        gc_stats = gc_manager.collect() if hasattr(gc_manager, "collect") else {}

        return {
            "system": memory_info,
            "gc": gc_stats,
            "limits": {
                "max_memory_mb": self.max_memory / 1024 / 1024,
                "warning_threshold": self._warning_threshold,
                "critical_threshold": self._critical_threshold,
            },
        }


# 全局内存监控器实例
memory_monitor = MemoryMonitor()
