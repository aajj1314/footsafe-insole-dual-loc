# -*- coding: utf-8 -*-
"""
日志中间件
"""

import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求

        Args:
            request: HTTP请求
            call_next: 下一个处理器

        Returns:
            HTTP响应
        """
        start_time = time.time()

        # 记录请求
        logger.info(f"Request: {request.method} {request.url.path}")

        try:
            response = await call_next(request)

            # 记录响应
            duration = time.time() - start_time
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"status={response.status_code} duration={duration:.3f}s"
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"error={str(e)} duration={duration:.3f}s"
            )
            raise
