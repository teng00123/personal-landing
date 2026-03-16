"""
Redis 缓存管理器 — Iteration 4
支持:
  - 装饰器缓存 @cache(ttl=60)
  - 手动 get/set/delete/clear_pattern
  - 键前缀命名空间
"""
import functools
import json
import logging
from typing import Any, Callable, Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── 全局异步连接池 ─────────────────────────────────────────

_pool: Optional[Redis] = None


def get_redis() -> Redis:
    global _pool
    if _pool is None:
        _pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return _pool


# ── CacheManager ──────────────────────────────────────────

class CacheManager:
    PREFIX = "pl:"  # personal-landing 命名空间

    def __init__(self, redis: Redis):
        self.r = redis

    def _key(self, key: str) -> str:
        return f"{self.PREFIX}{key}"

    async def get(self, key: str) -> Optional[Any]:
        try:
            raw = await self.r.get(self._key(key))
            return json.loads(raw) if raw is not None else None
        except Exception as e:
            logger.warning("cache get error: %s", e)
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        try:
            await self.r.setex(self._key(key), ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.warning("cache set error: %s", e)
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self.r.delete(self._key(key))
            return True
        except Exception as e:
            logger.warning("cache delete error: %s", e)
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """删除匹配 pattern 的所有 key，如 'articles:*'"""
        try:
            keys = await self.r.keys(self._key(pattern))
            if keys:
                return await self.r.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("cache clear_pattern error: %s", e)
            return 0

    async def exists(self, key: str) -> bool:
        try:
            return bool(await self.r.exists(self._key(key)))
        except Exception:
            return False

    async def ttl(self, key: str) -> int:
        try:
            return await self.r.ttl(self._key(key))
        except Exception:
            return -1


# ── 便捷依赖注入 ──────────────────────────────────────────

async def get_cache() -> CacheManager:
    return CacheManager(get_redis())


# ── 缓存装饰器 ────────────────────────────────────────────

def cache(ttl: int = 300, key_prefix: str = ""):
    """
    缓存装饰器，用于异步函数
    用法:
        @cache(ttl=60, key_prefix="articles")
        async def get_articles(page: int) -> list:
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 构建缓存 key
            cache_key = key_prefix or func.__name__
            if args:
                cache_key += ":" + ":".join(str(a) for a in args)
            if kwargs:
                cache_key += ":" + ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

            cm = CacheManager(get_redis())
            cached = await cm.get(cache_key)
            if cached is not None:
                logger.debug("cache hit: %s", cache_key)
                return cached

            result = await func(*args, **kwargs)
            await cm.set(cache_key, result, ttl)
            logger.debug("cache set: %s (ttl=%ds)", cache_key, ttl)
            return result
        return wrapper
    return decorator