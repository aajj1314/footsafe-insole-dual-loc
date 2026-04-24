# -*- coding: utf-8 -*-
"""
限流中间件
"""

import time
from typing import Dict, Optional
from collections import defaultdict

from app.config.limits import MAX_REQUESTS_PER_SECOND, NONCE_EXPIRE_SECONDS
from app.core.logger import logger


class RateLimiter:
    """速率限制器"""

    def __init__(self, max_requests: int = MAX_REQUESTS_PER_SECOND, window: int = 1):
        """
        初始化限流器

        Args:
            max_requests: 最大请求数
            window: 时间窗口(秒)
        """
        self.max_requests = max_requests
        self.window = window
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = False

    def is_allowed(self, key: str) -> bool:
        """
        检查是否允许请求

        Args:
            key: 限流键（如设备ID、IP等）

        Returns:
            是否允许
        """
        now = time.time()
        window_start = now - self.window

        # 清理过期的请求记录
        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]

        # 检查是否超过限制
        if len(self._requests[key]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for key: {key}")
            return False

        # 记录请求
        self._requests[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        """
        获取剩余请求数

        Args:
            key: 限流键

        Returns:
            剩余请求数
        """
        now = time.time()
        window_start = now - self.window

        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]

        return max(0, self.max_requests - len(self._requests[key]))


# 全局限流器
device_rate_limiter = RateLimiter()
ip_rate_limiter = RateLimiter(max_requests=100, window=1)  # IP级别更宽松
