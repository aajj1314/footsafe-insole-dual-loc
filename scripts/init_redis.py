#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis初始化脚本
用于初始化Redis缓存数据
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def init_redis():
    """初始化Redis数据"""
    from app.core.database.redis import redis_pool
    from app.core.logger import logger

    logger.info("Initializing Redis...")

    try:
        # 初始化连接
        await redis_pool.initialize()

        # 清空现有数据（可选）
        # await redis_pool.flushdb()

        # 创建默认配置
        await redis_pool.set_json(
            "config:system:version",
            {"version": "2.1.0", "updated_at": "2026-04-19"},
        )

        logger.info("Redis initialization completed")

    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        raise
    finally:
        await redis_pool.close()


if __name__ == "__main__":
    asyncio.run(init_redis())
