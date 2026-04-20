# -*- coding: utf-8 -*-
"""
MariaDB连接池模块
"""

import asyncio
from typing import Optional, Any, Dict, List
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.config.settings import settings
from app.core.logger import logger


class MariaDBPool:
    """MariaDB连接池管理器"""

    _instance: Optional["MariaDBPool"] = None

    def __init__(self):
        """初始化MariaDB连接池"""
        self._engine = None
        self._session_factory = None

    @classmethod
    def get_instance(cls) -> "MariaDBPool":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self) -> None:
        """初始化连接池"""
        if self._engine is not None:
            return

        # 优先使用MariaDB配置，若无则回退到MySQL配置
        host = getattr(settings, 'MARIADB_HOST', settings.MYSQL_HOST)
        port = getattr(settings, 'MARIADB_PORT', settings.MYSQL_PORT)
        database = getattr(settings, 'MARIADB_DATABASE', settings.MYSQL_DATABASE)
        user = getattr(settings, 'MARIADB_USER', settings.MYSQL_USER)
        password = getattr(settings, 'MARIADB_PASSWORD', settings.MYSQL_PASSWORD)
        pool_size = getattr(settings, 'MARIADB_POOL_SIZE', settings.MYSQL_POOL_SIZE)
        pool_max_overflow = getattr(settings, 'MARIADB_POOL_MAX_OVERFLOW', settings.MYSQL_POOL_MAX_OVERFLOW)

        # 构建数据库URL（MariaDB与MySQL兼容，使用相同的驱动）
        database_url = (
            f"mysql+aiomysql://{user}:{password}"
            f"@{host}:{port}/{database}"
        )

        # 创建异步引擎
        self._engine = create_async_engine(
            database_url,
            pool_size=pool_size,
            max_overflow=pool_max_overflow,
            poolclass=AsyncAdaptedQueuePool,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG,
        )

        # 创建会话工厂
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        logger.info(
            f"MariaDB connection pool initialized: "
            f"{host}:{port}/{database}"
        )

    async def close(self) -> None:
        """关闭连接池"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("MariaDB connection pool closed")

    @asynccontextmanager
    async def get_session(self):
        """获取数据库会话"""
        if not self._session_factory:
            raise RuntimeError("MariaDB pool not initialized")

        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        执行SQL查询

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            查询结果列表
        """
        async with self.get_session() as session:
            result = await session.execute(text(query), params or {})
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def execute_one(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        执行SQL查询，返回单条结果

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            查询结果或None
        """
        async with self.get_session() as session:
            result = await session.execute(text(query), params or {})
            row = result.fetchone()
            return dict(row._mapping) if row else None

    async def execute_write(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        执行写操作SQL

        Args:
            query: SQL语句
            params: 参数

        Returns:
            影响行数
        """
        async with self.get_session() as session:
            result = await session.execute(text(query), params or {})
            await session.commit()
            return result.rowcount

    @property
    def engine(self):
        """获取引擎"""
        return self._engine


# 全局MariaDB连接池实例
mariadb_pool = MariaDBPool.get_instance()

# 为了向后兼容，保留MySQLPool作为别名
class MySQLPool(MariaDBPool):
    """MySQL连接池管理器（向后兼容别名）"""

mysql_pool = mariadb_pool  # 向后兼容别名
