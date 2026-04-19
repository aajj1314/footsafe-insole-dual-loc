# -*- coding: utf-8 -*-
"""
内存管理模块单元测试
"""

import pytest
from app.core.memory.object_pool import ObjectPool
from app.core.memory.cache import LRUCache


class TestObjectPool:
    """对象池测试"""

    @pytest.mark.asyncio
    async def test_acquire_release(self):
        """测试对象获取和释放"""
        pool = ObjectPool(factory=lambda: {"data": "test"}, max_size=10)

        obj = await pool.acquire()
        assert obj == {"data": "test"}

        await pool.release(obj)

        stats = pool.get_stats()
        assert stats["pool_size"] == 1
        assert stats["in_use"] == 0

    @pytest.mark.asyncio
    async def test_max_size(self):
        """测试最大容量"""
        pool = ObjectPool(factory=lambda: "test", max_size=2)

        obj1 = await pool.acquire()
        obj2 = await pool.acquire()
        obj3 = await pool.acquire()

        assert obj1 is not None
        assert obj2 is not None
        assert obj3 is not None

        stats = pool.get_stats()
        assert stats["max_size"] == 2


class TestLRUCache:
    """LRU缓存测试"""

    @pytest.mark.asyncio
    async def test_set_get(self):
        """测试设置和获取"""
        cache = LRUCache(max_size=100, ttl=60)

        await cache.set("key1", "value1")
        result = await cache.get("key1")

        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self):
        """测试获取不存在的键"""
        cache = LRUCache(max_size=100, ttl=60)

        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self):
        """测试删除"""
        cache = LRUCache(max_size=100, ttl=60)

        await cache.set("key1", "value1")
        result = await cache.delete("key1")

        assert result is True
        assert await cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self):
        """测试LRU淘汰"""
        cache = LRUCache(max_size=3, ttl=60)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")
        await cache.set("key4", "value4")

        # key1应该被淘汰
        assert await cache.get("key1") is None
        assert await cache.get("key4") == "value4"
