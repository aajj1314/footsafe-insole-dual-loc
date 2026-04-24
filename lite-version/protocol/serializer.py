# -*- coding: utf-8 -*-
"""
响应序列化器
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.network.codec import Codec


class ResponseSerializer:
    """响应序列化器"""

    @staticmethod
    def serialize(
        code: int,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        序列化响应报文

        Args:
            code: 错误码
            message: 消息
            data: 数据

        Returns:
            JSON字节
        """
        response = {
            "code": code,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat() + "+08:00",
        }
        return Codec.encode(response)

    @staticmethod
    def serialize_error(code: int, message: str) -> bytes:
        """
        序列化错误响应

        Args:
            code: 错误码
            message: 错误消息

        Returns:
            JSON字节
        """
        return ResponseSerializer.serialize(code, message, {})

    @staticmethod
    def serialize_success(
        data: Optional[Dict[str, Any]] = None,
        message: str = "success",
    ) -> bytes:
        """
        序列化成功响应

        Args:
            data: 数据
            message: 消息

        Returns:
            JSON字节
        """
        from app.config.constants import ERROR_SUCCESS
        return ResponseSerializer.serialize(ERROR_SUCCESS, message, data)

    @staticmethod
    def serialize_auth_response(
        session_id: str,
        heartbeat_interval: int,
        key_version: int = 1,
    ) -> bytes:
        """
        序列化认证响应

        Args:
            session_id: 会话ID
            heartbeat_interval: 心跳间隔
            key_version: 密钥版本

        Returns:
            JSON字节
        """
        from app.config.constants import ERROR_SUCCESS
        data = {
            "session_id": session_id,
            "heartbeat_interval": heartbeat_interval,
            "server_time": datetime.utcnow().isoformat() + "+08:00",
            "key_version": key_version,
        }
        return ResponseSerializer.serialize(ERROR_SUCCESS, "success", data)

    @staticmethod
    def serialize_batch_response(
        success_count: int,
        failed_indexes: list,
    ) -> bytes:
        """
        序列化批量处理响应

        Args:
            success_count: 成功数量
            failed_indexes: 失败索引列表

        Returns:
            JSON字节
        """
        from app.config.constants import ERROR_SUCCESS
        data = {
            "success_count": success_count,
            "failed_indexes": failed_indexes,
        }
        return ResponseSerializer.serialize(ERROR_SUCCESS, "success", data)
