# -*- coding: utf-8 -*-
"""
Redis连接池与操作模块
"""

import json
import asyncio
from typing import Optional, Any, Dict, List
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from app.config.settings import settings
from app.config.limits import REDIS_CACHE_TTL
from app.core.logger import logger


class RedisPool:
    """Redis连接池管理器"""

    _instance: Optional["RedisPool"] = None

    def __init__(self):
        """初始化Redis连接池"""
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[Redis] = None

    @classmethod
    def get_instance(cls) -> "RedisPool":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self) -> None:
        """初始化连接池"""
        if self._client is not None:
            return

        # 创建连接池
        self._pool = ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            max_connections=settings.REDIS_POOL_SIZE,
            decode_responses=True,
        )

        # 创建客户端
        self._client = Redis(connection_pool=self._pool)

        # 测试连接
        await self._client.ping()

        logger.info(
            f"Redis connection pool initialized: "
            f"{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        )

    async def close(self) -> None:
        """关闭连接池"""
        if self._client:
            await self._client.close()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        logger.info("Redis connection pool closed")

    @property
    def client(self) -> Redis:
        """获取Redis客户端"""
        if not self._client:
            raise RuntimeError("Redis pool not initialized")
        return self._client

    # ==================== 基础操作 ====================

    async def get(self, key: str) -> Optional[str]:
        """获取值"""
        return await self._client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None,
    ) -> bool:
        """设置值"""
        return await self._client.set(key, value, ex=ex)

    async def delete(self, key: str) -> int:
        """删除键"""
        return await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self._client.exists(key) > 0

    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        return await self._client.expire(key, seconds)

    # ==================== JSON操作 ====================

    async def get_json(self, key: str) -> Optional[Any]:
        """获取JSON值"""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
    ) -> bool:
        """设置JSON值"""
        return await self.set(key, json.dumps(value), ex=ex)

    # ==================== 哈希操作 ====================

    async def hget(self, key: str, field: str) -> Optional[str]:
        """获取哈希字段值"""
        return await self._client.hget(key, field)

    async def hset(self, key: str, field: str, value: str) -> int:
        """设置哈希字段值"""
        return await self._client.hset(key, field, value)

    async def hgetall(self, key: str) -> Dict[str, str]:
        """获取哈希所有字段"""
        return await self._client.hgetall(key)

    async def hmset(self, key: str, mapping: Dict[str, str]) -> bool:
        """批量设置哈希字段"""
        return await self._client.hmset(key, mapping)

    async def hdel(self, key: str, *fields: str) -> int:
        """删除哈希字段"""
        return await self._client.hdel(key, *fields)

    # ==================== 集合操作 ====================

    async def sadd(self, key: str, *values: str) -> int:
        """添加到集合"""
        return await self._client.sadd(key, *values)

    async def smembers(self, key: str) -> set:
        """获取集合所有成员"""
        return await self._client.smembers(key)

    async def sismember(self, key: str, value: str) -> bool:
        """检查值是否在集合中"""
        return await self._client.sismember(key, value)

    async def srem(self, key: str, *values: str) -> int:
        """从集合移除值"""
        return await self._client.srem(key, *values)

    # ==================== 有序集合操作 ====================

    async def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        """添加到有序集合"""
        return await self._client.zadd(key, mapping)

    async def zrange(
        self,
        key: str,
        start: int,
        end: int,
        withscores: bool = False,
    ) -> List[Any]:
        """获取有序集合范围内的成员"""
        return await self._client.zrange(key, start, end, withscores=withscores)

    async def zrangebyscore(
        self,
        key: str,
        min_score: float,
        max_score: float,
    ) -> List[str]:
        """按分数范围获取成员"""
        return await self._client.zrangebyscore(key, min_score, max_score)

    async def zremrangebyscore(
        self,
        key: str,
        min_score: float,
        max_score: float,
    ) -> int:
        """按分数范围删除成员"""
        return await self._client.zremrangebyscore(key, min_score, max_score)

    # ==================== 列表操作 ====================

    async def lpush(self, key: str, *values: str) -> int:
        """添加到列表头部"""
        return await self._client.lpush(key, *values)

    async def rpush(self, key: str, *values: str) -> int:
        """添加到列表尾部"""
        return await self._client.rpush(key, *values)

    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """获取列表范围内的元素"""
        return await self._client.lrange(key, start, end)

    async def lpop(self, key: str) -> Optional[str]:
        """从列表头部弹出元素"""
        return await self._client.lpop(key)

    async def rpop(self, key: str) -> Optional[str]:
        """从列表尾部弹出元素"""
        return await self._client.rpop(key)

    # ==================== 发布订阅 ====================

    async def publish(self, channel: str, message: str) -> int:
        """发布消息"""
        return await self._client.publish(channel, message)

    # ==================== 键操作 ====================

    async def keys(self, pattern: str) -> List[str]:
        """获取匹配的所有键"""
        return await self._client.keys(pattern)

    async def flushdb(self) -> bool:
        """清空当前数据库"""
        return await self._client.flushdb()


# ==================== 会话管理 ====================


class SessionManager:
    """会话管理器"""

    SESSION_PREFIX = "session:"
    DEVICE_SESSION_PREFIX = "device_session:"
    HEARTBEAT_PREFIX = "heartbeat:"

    def __init__(self, redis_pool: RedisPool):
        """初始化会话管理器"""
        self.redis = redis_pool

    async def create_session(
        self,
        session_id: str,
        device_id: str,
        ttl: int = settings.SESSION_EXPIRE_SECONDS,
    ) -> bool:
        """
        创建会话

        Args:
            session_id: 会话ID
            device_id: 设备ID
            ttl: 过期时间(秒)

        Returns:
            是否创建成功
        """
        session_key = f"{self.SESSION_PREFIX}{session_id}"
        device_key = f"{self.DEVICE_SESSION_PREFIX}{device_id}"

        # 存储会话信息
        session_data = {
            "session_id": session_id,
            "device_id": device_id,
        }

        # 设置会话
        await self.redis.set_json(session_key, session_data, ex=ttl)

        # 设备关联会话
        await self.redis.set(device_key, session_id, ex=ttl)

        return True

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        session_key = f"{self.SESSION_PREFIX}{session_id}"
        return await self.redis.get_json(session_key)

    async def get_session_by_device(self, device_id: str) -> Optional[str]:
        """获取设备对应的会话ID"""
        device_key = f"{self.DEVICE_SESSION_PREFIX}{device_id}"
        return await self.redis.get(device_key)

    async def delete_session(self, session_id: str) -> None:
        """删除会话"""
        session_key = f"{self.SESSION_PREFIX}{session_id}"
        session = await self.get_session(session_id)

        if session:
            device_key = f"{self.DEVICE_SESSION_PREFIX}{session['device_id']}"
            await self.redis.delete(device_key)

        await self.redis.delete(session_key)

    async def update_session_ttl(
        self,
        session_id: str,
        ttl: int = settings.SESSION_EXPIRE_SECONDS,
    ) -> bool:
        """更新会话过期时间"""
        session_key = f"{self.SESSION_PREFIX}{session_id}"
        session = await self.get_session(session_id)

        if not session:
            return False

        # 更新会话过期时间
        await self.redis.expire(session_key, ttl)

        # 更新设备会话映射过期时间
        device_key = f"{self.DEVICE_SESSION_PREFIX}{session['device_id']}"
        await self.redis.expire(device_key, ttl)

        return True

    async def update_heartbeat(self, device_id: str) -> None:
        """更新心跳时间"""
        heartbeat_key = f"{self.HEARTBEAT_PREFIX}{device_id}"
        import time
        await self.redis.set(heartbeat_key, str(time.time()), ex=settings.HEARTBEAT_EXPIRE_SECONDS)

    async def get_last_heartbeat(self, device_id: str) -> Optional[float]:
        """获取最后心跳时间"""
        heartbeat_key = f"{self.HEARTBEAT_PREFIX}{device_id}"
        value = await self.redis.get(heartbeat_key)
        if value:
            return float(value)
        return None


# ==================== 设备状态缓存 ====================


class DeviceStateCache:
    """设备状态缓存"""

    DEVICE_STATE_PREFIX = "device_state:"

    def __init__(self, redis_pool: RedisPool):
        """初始化设备状态缓存"""
        self.redis = redis_pool

    async def set_device_state(
        self,
        device_id: str,
        state: Dict[str, Any],
        ttl: int = REDIS_CACHE_TTL,
    ) -> None:
        """
        设置设备状态

        Args:
            device_id: 设备ID
            state: 设备状态
            ttl: 过期时间(秒)
        """
        key = f"{self.DEVICE_STATE_PREFIX}{device_id}"
        await self.redis.set_json(key, state, ex=ttl)

    async def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """获取设备状态"""
        key = f"{self.DEVICE_STATE_PREFIX}{device_id}"
        return await self.redis.get_json(key)

    async def delete_device_state(self, device_id: str) -> None:
        """删除设备状态"""
        key = f"{self.DEVICE_STATE_PREFIX}{device_id}"
        await self.redis.delete(key)


# 全局Redis连接池实例
redis_pool = RedisPool.get_instance()
