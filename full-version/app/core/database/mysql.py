# -*- coding: utf-8 -*-
"""
MySQL连接池模块
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


class MySQLPool:
    """MySQL连接池管理器"""

    _instance: Optional["MySQLPool"] = None

    def __init__(self):
        """初始化MySQL连接池"""
        self._engine = None
        self._session_factory = None

    @classmethod
    def get_instance(cls) -> "MySQLPool":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self) -> None:
        """初始化连接池"""
        if self._engine is not None:
            return

        # 构建数据库URL
        database_url = (
            f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
            f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
        )

        # 创建异步引擎
        self._engine = create_async_engine(
            database_url,
            pool_size=settings.MYSQL_POOL_SIZE,
            max_overflow=settings.MYSQL_POOL_MAX_OVERFLOW,
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
            f"MySQL connection pool initialized: "
            f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
        )

    async def close(self) -> None:
        """关闭连接池"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("MySQL connection pool closed")

    @asynccontextmanager
    async def get_session(self):
        """获取数据库会话"""
        if not self._session_factory:
            raise RuntimeError("MySQL pool not initialized")

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


# 全局MySQL连接池实例
mysql_pool = MySQLPool.get_instance()
