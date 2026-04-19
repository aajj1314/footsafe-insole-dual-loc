# -*- coding: utf-8 -*-
"""
垃圾回收管理器模块
"""

import gc
import asyncio
from typing import Optional

from app.core.logger import logger


class GarbageCollectorManager:
    """垃圾回收管理器"""

    def __init__(self):
        """初始化垃圾回收管理器"""
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._interval = 60  # 默认60秒执行一次

    def start(self, interval: int = 60) -> None:
        """
        启动垃圾回收

        Args:
            interval: 执行间隔(秒)
        """
        if self._running:
            return

        self._running = True
        self._interval = interval
        self._task = asyncio.create_task(self._run())
        logger.info(f"Garbage collector started, interval: {interval}s")

    def stop(self) -> None:
        """停止垃圾回收"""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Garbage collector stopped")

    async def _run(self) -> None:
        """运行垃圾回收循环"""
        while self._running:
            try:
                await asyncio.sleep(self._interval)
                self.collect()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in garbage collector: {e}")

    def collect(self) -> dict:
        """
        执行垃圾回收

        Returns:
            回收统计信息
        """
        before = gc.mem_alloc() if hasattr(gc, "mem_alloc") else 0

        # 执行垃圾回收
        collected = gc.collect()

        after = gc.mem_alloc() if hasattr(gc, "mem_alloc") else 0

        stats = {
            "collected": collected,
            "before_bytes": before,
            "after_bytes": after,
            "freed_bytes": before - after,
        }

        if collected > 0:
            logger.debug(f"GC collected {collected} objects, freed {before - after} bytes")

        return stats

    def enable(self) -> None:
        """启用自动垃圾回收"""
        gc.enable()

    def disable(self) -> None:
        """禁用自动垃圾回收"""
        gc.disable()

    def is_enabled(self) -> bool:
        """检查是否启用"""
        return gc.isenabled()


# 全局垃圾回收管理器实例
gc_manager = GarbageCollectorManager()
