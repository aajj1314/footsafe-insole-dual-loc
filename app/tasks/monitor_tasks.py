# -*- coding: utf-8 -*-
"""
监控任务模块
"""

import asyncio
from app.core.logger import logger


async def monitor_memory():
    """监控内存使用"""
    from app.core.memory.monitor import memory_monitor

    while True:
        try:
            stats = memory_monitor.get_memory_stats()
            logger.debug(
                f"Memory stats: "
                f"process={stats['system']['process_rss_mb']:.2f}MB, "
                f"system={stats['system']['percent']:.1f}%"
            )
        except Exception as e:
            logger.error(f"Error monitoring memory: {e}")

        await asyncio.sleep(60)  # 每分钟执行一次


async def monitor_connections():
    """监控连接状态"""
    from app.protocol.tcp.connection import tcp_connection_manager
    from app.protocol.tcp.session import tcp_session_manager

    while True:
        try:
            conn_stats = tcp_connection_manager.get_stats()
            session_stats = tcp_session_manager.get_stats()

            logger.debug(
                f"Connections: {conn_stats['total_connections']}, "
                f"Devices: {conn_stats['unique_devices']}, "
                f"Sessions: {session_stats['total_sessions']}"
            )
        except Exception as e:
            logger.error(f"Error monitoring connections: {e}")

        await asyncio.sleep(30)  # 每30秒执行一次


async def monitor_object_pools():
    """监控对象池"""
    from app.core.memory.object_pool import parser_pool, serializer_pool

    while True:
        try:
            parser_stats = parser_pool.get_stats()
            serializer_stats = serializer_pool.get_stats()

            logger.debug(
                f"Parser pool: {parser_stats['pool_size']}/{parser_stats['max_size']}, "
                f"Serializer pool: {serializer_stats['pool_size']}/{serializer_stats['max_size']}"
            )
        except Exception as e:
            logger.error(f"Error monitoring object pools: {e}")

        await asyncio.sleep(60)  # 每分钟执行一次


def start_monitor_tasks():
    """启动所有监控任务"""
    tasks = [
        asyncio.create_task(monitor_memory()),
        asyncio.create_task(monitor_connections()),
        asyncio.create_task(monitor_object_pools()),
    ]

    logger.info(f"Started {len(tasks)} monitor tasks")

    return tasks
