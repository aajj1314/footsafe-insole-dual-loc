# -*- coding: utf-8 -*-
"""
足安智能防走失系统主入口
"""

import asyncio
import signal
import sys
import multiprocessing
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_http_api():
    """运行HTTP API服务（独立进程）"""
    import uvicorn
    from app.api import app
    from app.config.settings import settings

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.HTTP_API_PORT,
        log_level="info",
    )


async def shutdown(signal_obj, loop, udp_server, tcp_server, memory_monitor, http_process=None):
    """
    优雅关闭服务

    Args:
        signal_obj: 信号对象
        loop: 事件循环
        udp_server: UDP服务器
        tcp_server: TCP服务器
        memory_monitor: 内存监控器
        http_process: HTTP API进程
    """
    from app.core.logger import logger
    from app.core.database.session import close_all_databases
    from app.core.memory.gc_manager import gc_manager

    logger.info(f"Received exit signal {signal_obj.name}...")

    # 停止HTTP API进程
    if http_process and http_process.is_alive():
        http_process.terminate()
        http_process.join(timeout=5)

    # 停止服务器
    await udp_server.stop()
    await tcp_server.stop()

    # 停止内存监控
    memory_monitor.stop()

    # 停止垃圾回收
    gc_manager.stop()

    # 关闭数据库连接
    await close_all_databases()

    # 取消所有任务
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    logger.info("Service shutdown complete")


async def main():
    """主函数"""
    from app.core.logger import logger
    from app.core.database.session import init_all_databases
    from app.core.memory.monitor import memory_monitor
    from app.core.memory.gc_manager import gc_manager
    from app.core.security.audit import SecurityAuditor
    from app.protocol.udp.server import UDPServer
    from app.protocol.tcp.server import TCPServer
    from app.tasks.cleanup_tasks import start_cleanup_tasks
    from app.tasks.monitor_tasks import start_monitor_tasks
    from app.core.database.redis import redis_pool, SessionManager
    from app.protocol.tcp.session import tcp_session_manager
    from app.config.settings import settings

    logger.info("=" * 50)
    logger.info("足安智能防走失系统启动中 (v2.1)...")
    logger.info("=" * 50)

    # 初始化数据库
    try:
        await init_all_databases()
        logger.info("All databases initialized")
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        sys.exit(1)

    # 初始化安全审计器
    security_auditor = SecurityAuditor()
    security_auditor.start()
    logger.info("Security auditor started")

    # 初始化内存监控
    memory_monitor = memory_monitor
    memory_monitor.start()
    logger.info("Memory monitor started")

    # 初始化垃圾回收
    gc_manager.start()
    logger.info("Garbage collector started")

    # 初始化会话管理器（设置Redis）
    redis_session_manager = SessionManager(redis_pool)
    tcp_session_manager.set_redis_session_manager(redis_session_manager)

    # 创建UDP服务器
    udp_server = UDPServer(
        host=settings.HOST,
        port=settings.UDP_PORT,
        security_auditor=security_auditor,
    )
    await udp_server.start()
    logger.info(f"UDP server started on {settings.HOST}:{settings.UDP_PORT}")

    # 创建TCP服务器
    tcp_server = TCPServer(
        host=settings.HOST,
        port=settings.TCP_PORT,
        security_auditor=security_auditor,
    )
    await tcp_server.start()
    logger.info(f"TCP server started on {settings.HOST}:{settings.TCP_PORT}")

    # 启动HTTP API服务（独立进程）
    http_process = None
    try:
        http_process = multiprocessing.Process(target=run_http_api, daemon=True)
        http_process.start()
        logger.info(f"HTTP API server started on {settings.HOST}:{settings.HTTP_API_PORT}")
    except Exception as e:
        logger.warning(f"Failed to start HTTP API server: {e}")

    # 启动清理任务
    start_cleanup_tasks()
    logger.info("Background cleanup tasks started")

    # 启动监控任务
    start_monitor_tasks()
    logger.info("Background monitor tasks started")

    # 设置信号处理
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(
                shutdown(s, loop, udp_server, tcp_server, memory_monitor, http_process)
            ),
        )

    logger.info("=" * 50)
    logger.info("Service is running...")
    logger.info(f"  - UDP Protocol Server: {settings.HOST}:{settings.UDP_PORT}")
    logger.info(f"  - TCP Protocol Server: {settings.HOST}:{settings.TCP_PORT}")
    logger.info(f"  - HTTP API Server: {settings.HOST}:{settings.HTTP_API_PORT}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 50)

    # 保持运行
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
