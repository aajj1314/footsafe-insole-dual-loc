# -*- coding: utf-8 -*-
"""
UDP指令下发模块
"""

import asyncio
from typing import Tuple, Optional

from app.core.logger import logger
from app.core.network.codec import Codec
from app.config.constants import PROTOCOL_VERSION
import uuid


class UDPSender:
    """UDP指令下发器"""

    def __init__(self, sock: asyncio.DatagramProtocol):
        """
        初始化UDP发送器

        Args:
            sock: UDP socket
        """
        self.sock = sock

    async def send_command(
        self,
        device_id: str,
        command_type: str,
        data: dict,
        remote_addr: Tuple[str, int],
    ) -> bool:
        """
        发送UDP指令到设备

        Args:
            device_id: 设备ID
            command_type: 命令类型
            data: 命令数据
            remote_addr: 设备地址

        Returns:
            是否发送成功
        """
        import time
        import random
        import string

        # 生成随机nonce
        nonce = "".join(random.choices(string.ascii_letters + string.digits, k=12))

        # 构建指令报文
        message = {
            "version": PROTOCOL_VERSION,
            "device_id": device_id,
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
            await self.sock.sendto(data_bytes, remote_addr)
            logger.info(
                f"UDP command sent to {remote_addr}: type={command_type}, device={device_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send UDP command: {e}")
            return False

    async def send_get_location(
        self,
        device_id: str,
        remote_addr: Tuple[str, int],
    ) -> bool:
        """发送获取位置指令"""
        return await self.send_command(
            device_id,
            "get_location",
            {},
            remote_addr,
        )

    async def send_get_status(
        self,
        device_id: str,
        remote_addr: Tuple[str, int],
    ) -> bool:
        """发送获取状态指令"""
        return await self.send_command(
            device_id,
            "get_status",
            {},
            remote_addr,
        )

    async def send_reset(
        self,
        device_id: str,
        remote_addr: Tuple[str, int],
    ) -> bool:
        """发送重启指令"""
        return await self.send_command(
            device_id,
            "reset",
            {},
            remote_addr,
        )
