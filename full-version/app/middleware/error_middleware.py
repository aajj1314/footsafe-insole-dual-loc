# -*- coding: utf-8 -*-
"""
错误处理中间件
"""

from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logger import logger
from app.core.exceptions import BaseServiceException


class ErrorMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""

    async def dispatch(self, request: Request, call_next: Callable):
        """
        处理请求

        Args:
            request: HTTP请求
            call_next: 下一个处理器

        Returns:
            HTTP响应
        """
        try:
            return await call_next(request)

        except BaseServiceException as e:
            logger.error(f"Service exception: {e.code} - {e.message}")
            return JSONResponse(
                status_code=400,
                content={
                    "code": e.code,
                    "message": e.message,
                    "details": e.details,
                },
            )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "code": 5000,
                    "message": "internal_server_error",
                    "details": {},
                },
            )
