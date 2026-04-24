# -*- coding: utf-8 -*-
"""
速率限制工具模块
"""

import time
from collections import defaultdict
from typing import Dict, List


class TokenBucket:
    """令牌桶算法实现"""

    def __init__(self, rate: float, capacity: int):
        """
        初始化令牌桶

        Args:
            rate: 令牌生成速率（个/秒）
            capacity: 桶容量
        """
        self.rate = rate
        self.capacity = capacity
        self._tokens = capacity
        self._last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """
        消费令牌

        Args:
            tokens: 需要消费的令牌数

        Returns:
            是否消费成功
        """
        self._refill()

        if self._tokens >= tokens:
            self._tokens -= tokens
            return True

        return False

    def _refill(self) -> None:
        """重新填充令牌"""
        now = time.time()
        elapsed = now - self._last_update

        self._tokens = min(
            self.capacity,
            self._tokens + elapsed * self.rate
        )
        self._last_update = now


class SlidingWindowCounter:
    """滑动窗口计数器"""

    def __init__(self, window_size: int, max_requests: int):
        """
        初始化滑动窗口计数器

        Args:
            window_size: 窗口大小（秒）
            max_requests: 最大请求数
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """
        检查是否允许请求

        Args:
            key: 限流键

        Returns:
            是否允许
        """
        now = time.time()
        window_start = now - self.window_size

        # 清理过期记录
        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]

        # 检查是否超过限制
        if len(self._requests[key]) >= self.max_requests:
            return False

        # 记录请求
        self._requests[key].append(now)
        return True

    def get_count(self, key: str) -> int:
        """
        获取当前窗口内的请求数

        Args:
            key: 限流键

        Returns:
            请求数
        """
        now = time.time()
        window_start = now - self.window_size

        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]

        return len(self._requests[key])
