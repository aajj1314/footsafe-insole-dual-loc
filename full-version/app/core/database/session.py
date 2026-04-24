# -*- coding: utf-8 -*-
"""
数据库会话管理
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config.settings import settings

# 创建全局Base
Base = declarative_base()

# 根据数据库类型决定是否使用连接池参数
is_sqlite = "sqlite" in settings.DATABASE_URL

if is_sqlite:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
    )

# 创建会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_all_databases():
    """初始化所有数据库连接"""
    async with engine.begin() as conn:
        # 导入所有模型以确保它们被注册
        from app.models.orm import user, device, user_device

        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

    # 初始化演示账号
    async with async_session_factory() as session:
        from app.services.user_service import UserService
        user_service = UserService(session)
        await user_service.ensure_demo_user("admin", "admin")


async def close_all_databases():
    """关闭所有数据库连接"""
    await engine.dispose()
