# -*- coding: utf-8 -*-
"""
TCP指令下发模块
"""

import asyncio
import time
import random
import string
import uuid
from typing import Tuple, Optional

from app.core.logger import logger
from app.core.network.codec import Codec
from app.config.constants import PROTOCOL_VERSION
from app.protocol.tcp.connection import TCPConnectionManager


class TCPSender:
    """TCP指令下发器"""

    def __init__(self, connection_manager: TCPConnectionManager):
        """
        初始化TCP发送器

        Args:
            connection_manager: 连接管理器
        """
        self.connection_manager = connection_manager

    async def send_command(
        self,
        device_id: str,
        command_type: str,
        data: dict,
        session_id: Optional[str] = None,
    ) -> bool:
        """
        发送TCP指令到设备

        Args:
            device_id: 设备ID
            command_type: 命令类型
            data: 命令数据
            session_id: 会话ID

        Returns:
            是否发送成功
        """
        # 获取设备连接
        conn = await self.connection_manager.get_connection_by_device(device_id)
        if not conn:
            logger.warning(f"No TCP connection for device: {device_id}")
            return False

        # 生成随机nonce
        nonce = "".join(random.choices(string.ascii_letters + string.digits, k=12))

        # 构建指令报文
        message = {
            "version": PROTOCOL_VERSION,
            "device_id": device_id,
            "session_id": session_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "nonce": nonce,
            "type": "server_command",
            "data": {
                "command_id": str(uuid.uuid4()),
                "command_type": command_type,
                **data,
            },
            "checksum": "",  # 简化版本，实际应该计算校验和
        }

        try:
            data_bytes = Codec.encode(message)
            await conn.send(data_bytes)
            logger.info(
                f"TCP command sent to device: {device_id}, type: {command_type}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send TCP command: {e}")
            return False

    async def send_set_report_interval(
        self,
        device_id: str,
        interval: int,
        session_id: Optional[str] = None,
    ) -> bool:
        """发送设置上报间隔指令"""
        return await self.send_command(
            device_id,
            "set_report_interval",
            {"interval": interval},
            session_id,
        )

    async def send_set_mode(
        self,
        device_id: str,
        mode: str,
        session_id: Optional[str] = None,
    ) -> bool:
        """发送设置工作模式指令"""
        return await self.send_command(
            device_id,
            "set_mode",
            {"mode": mode},
            session_id,
        )

    async def send_get_config(
        self,
        device_id: str,
        session_id: Optional[str] = None,
    ) -> bool:
        """发送获取配置指令"""
        return await self.send_command(
            device_id,
            "get_config",
            {},
            session_id,
        )

    async def send_ota_start(
        self,
        device_id: str,
        upgrade_id: str,
        url: str,
        version: str,
        size: int,
        checksum: str,
        session_id: Optional[str] = None,
    ) -> bool:
        """发送OTA开始升级指令"""
        return await self.send_command(
            device_id,
            "ota_start",
            {
                "upgrade_id": upgrade_id,
                "url": url,
                "version": version,
                "size": size,
                "checksum": checksum,
            },
            session_id,
        )

    async def send_ota_cancel(
        self,
        device_id: str,
        upgrade_id: str,
        session_id: Optional[str] = None,
    ) -> bool:
        """发送OTA取消升级指令"""
        return await self.send_command(
            device_id,
            "ota_cancel",
            {"upgrade_id": upgrade_id},
            session_id,
        )

    async def send_factory_reset(
        self,
        device_id: str,
        session_id: Optional[str] = None,
    ) -> bool:
        """发送恢复出厂设置指令"""
        return await self.send_command(
            device_id,
            "factory_reset",
            {},
            session_id,
        )

    async def send_lock_device(
        self,
        device_id: str,
        lock_time: int,
        session_id: Optional[str] = None,
    ) -> bool:
        """发送锁定设备指令"""
        return await self.send_command(
            device_id,
            "lock_device",
            {"lock_time": lock_time},
            session_id,
        )
