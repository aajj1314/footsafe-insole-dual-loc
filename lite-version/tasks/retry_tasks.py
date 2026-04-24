# -*- coding: utf-8 -*-
"""
重试任务模块
"""

import asyncio
from typing import Optional

from app.core.logger import logger
from app.config.limits import ALARM_RETRY_COUNT, ALARM_RETRY_INTERVAL_MS


class RetryTasks:
    """重试任务"""

    @staticmethod
    async def retry_alarm_push(
        alarm_id: str,
        device_id: str,
        alarm_data: dict,
        max_retries: int = ALARM_RETRY_COUNT,
    ) -> bool:
        """
        重试报警推送

        Args:
            alarm_id: 报警ID
            device_id: 设备ID
            alarm_data: 报警数据
            max_retries: 最大重试次数

        Returns:
            是否推送成功
        """
        from app.services.push_service import push_service
        from app.services.alarm_service import alarm_service

        for attempt in range(max_retries):
            try:
                # 推送报警
                await push_service.push_alarm(
                    device_id,
                    alarm_id,
                    alarm_data,
                    alarm_data.get("alarm_type"),
                    alarm_data.get("alarm_level"),
                )

                # 更新推送状态
                await alarm_service.update_alarm_status(
                    alarm_id,
                    "pushed",
                    push_count=attempt + 1,
                )

                logger.info(
                    f"Alarm push succeeded after {attempt + 1} attempts: {alarm_id}"
                )
                return True

            except Exception as e:
                logger.error(
                    f"Alarm push attempt {attempt + 1} failed: {alarm_id}, error: {e}"
                )

                if attempt < max_retries - 1:
                    await asyncio.sleep(ALARM_RETRY_INTERVAL_MS / 1000)

        logger.error(f"Alarm push failed after {max_retries} attempts: {alarm_id}")
        return False

    @staticmethod
    async def retry_command(
        command_id: str,
        device_id: str,
        command_type: str,
        command_data: dict,
        max_retries: int = 3,
    ) -> bool:
        """
        重试命令下发

        Args:
            command_id: 命令ID
            device_id: 设备ID
            command_type: 命令类型
            command_data: 命令数据
            max_retries: 最大重试次数

        Returns:
            是否发送成功
        """
        from app.protocol.tcp.sender import TCPSender
        from app.protocol.tcp.connection import tcp_connection_manager

        sender = TCPSender(tcp_connection_manager)

        for attempt in range(max_retries):
            try:
                success = await sender.send_command(
                    device_id,
                    command_type,
                    command_data,
                )

                if success:
                    logger.info(
                        f"Command sent after {attempt + 1} attempts: {command_id}"
                    )
                    return True

            except Exception as e:
                logger.error(
                    f"Command attempt {attempt + 1} failed: {command_id}, error: {e}"
                )

                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # 1秒后重试

        logger.error(f"Command failed after {max_retries} attempts: {command_id}")
        return False
