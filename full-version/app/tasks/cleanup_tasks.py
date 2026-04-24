# -*- coding: utf-8 -*-
"""
清理任务模块
"""

import asyncio
from app.core.logger import logger


async def cleanup_expired_sessions():
    """清理过期会话"""
    from app.protocol.tcp.session import tcp_session_manager

    while True:
        try:
            count = await tcp_session_manager.cleanup_expired()
            if count > 0:
                logger.info(f"Cleaned up {count} expired sessions")
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")

        await asyncio.sleep(60)  # 每分钟执行一次


async def cleanup_expired_nonces():
    """清理过期的nonce"""
    from app.core.security.nonce import nonce_manager

    while True:
        try:
            await nonce_manager._cleanup_if_needed()
        except Exception as e:
            logger.error(f"Error cleaning up nonces: {e}")

        await asyncio.sleep(600)  # 每10分钟执行一次


async def cleanup_expired_cache():
    """清理过期的本地缓存"""
    from app.core.memory.cache import device_info_cache

    while True:
        try:
            count = await device_info_cache.cleanup_expired()
            if count > 0:
                logger.info(f"Cleaned up {count} expired cache entries")
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")

        await asyncio.sleep(300)  # 每5分钟执行一次


async def cleanup_closed_connections():
    """清理已关闭的TCP连接"""
    from app.protocol.tcp.connection import tcp_connection_manager

    while True:
        try:
            count = await tcp_connection_manager.cleanup_closed()
            if count > 0:
                logger.info(f"Cleaned up {count} closed connections")
        except Exception as e:
            logger.error(f"Error cleaning up connections: {e}")

        await asyncio.sleep(30)  # 每30秒执行一次


def start_cleanup_tasks():
    """启动所有清理任务"""
    tasks = [
        asyncio.create_task(cleanup_expired_sessions()),
        asyncio.create_task(cleanup_expired_nonces()),
        asyncio.create_task(cleanup_expired_cache()),
        asyncio.create_task(cleanup_closed_connections()),
    ]

    logger.info(f"Started {len(tasks)} cleanup tasks")

    return tasks
