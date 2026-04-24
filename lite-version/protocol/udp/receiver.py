# -*- coding: utf-8 -*-
"""
UDP数据接收模块
"""

import asyncio
from typing import Tuple

from app.core.logger import logger
from app.core.network.buffer import Buffer


class UDPReceiver:
    """UDP数据接收器"""

    def __init__(self, buffer_size: int = 512):
        """
        初始化UDP接收器

        Args:
            buffer_size: 缓冲区大小
        """
        self.buffer_size = buffer_size

    async def receive(
        self,
        sock: asyncio.DatagramProtocol,
    ) -> Tuple[bytes, Tuple[str, int]]:
        """
        接收UDP数据

        Args:
            sock: UDP socket

        Returns:
            (数据, (地址, 端口))
        """
        try:
            data, addr = await asyncio.wait_for(
                sock.recvfrom(self.buffer_size),
                timeout=1.0,
            )
            return data, addr
        except asyncio.TimeoutError:
            return b"", ("", 0)
        except Exception as e:
            logger.error(f"UDP receive error: {e}")
            return b"", ("", 0)

    async def receive_loop(
        self,
        sock: asyncio.DatagramProtocol,
        handler: callable,
    ) -> None:
        """
        UDP接收循环

        Args:
            sock: UDP socket
            handler: 数据处理函数
        """
        logger.info("UDP receiver started")

        while True:
            try:
                data, addr = await self.receive(sock)

                if data:
                    logger.debug(f"UDP packet received from {addr}, size: {len(data)}")
                    await handler(data, addr)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in UDP receive loop: {e}")
                await asyncio.sleep(0.1)

        logger.info("UDP receiver stopped")
