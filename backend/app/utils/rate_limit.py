"""
API 限流中间件 — Iteration 6
基于 Redis 滑动窗口算法
支持:
  - 全局速率限制
  - 路由级别精细控制
  - IP 黑名单/白名单
  - 限流触发后返回标准 429 + Retry-After
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# 路由级别限流规则: path_prefix → (max_requests, window_seconds)
ROUTE_LIMITS: dict[str, tuple[int, int]] = {
    "/api/v1/auth/login": (10, 60),  # 登录：60s 内最多 10 次
    "/api/v1/auth/mfa": (20, 60),  # MFA：60s 内最多 20 次
    "/api/v1/search": (60, 60),  # 搜索：60s 内最多 60 次
    "/api/v1/social": (100, 60),  # 社交：60s 内最多 100 次
    "/api/v1/": (300, 60),  # 全局 API：60s 内最多 300 次
}

# IP 永久白名单（内网）
IP_WHITELIST = {"127.0.0.1", "::1"}


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """滑动窗口限流（需 Redis）"""

    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.enabled:
            return await call_next(request)

        ip = _get_client_ip(request)
        if ip in IP_WHITELIST:
            return await call_next(request)

        path = request.url.path
        limit, window = self._get_limit(path)

        # 检查 IP 黑名单
        if await self._is_blacklisted(ip):
            return JSONResponse(
                status_code=403,
                content={"detail": "IP 已被封禁，请联系管理员"},
            )

        # 限流检查
        allowed, remaining, retry_after = await self._check_rate(ip, path, limit, window)
        if not allowed:
            logger.warning("Rate limit exceeded: ip=%s path=%s", ip, path)
            return JSONResponse(
                status_code=429,
                content={"detail": f"请求过于频繁，请 {retry_after} 秒后重试"},
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    def _get_limit(self, path: str) -> tuple[int, int]:
        # 精确匹配 → 前缀匹配
        for prefix, rule in sorted(ROUTE_LIMITS.items(), key=lambda x: -len(x[0])):
            if path.startswith(prefix):
                return rule
        return (500, 60)  # 默认

    async def _is_blacklisted(self, ip: str) -> bool:
        try:
            from app.utils.cache import get_redis

            r = get_redis()
            return bool(await r.sismember("pl:ip:blacklist", ip))
        except Exception:
            return False

    async def _check_rate(
        self, ip: str, path: str, limit: int, window: int
    ) -> tuple[bool, int, int]:
        """滑动窗口计数，返回 (allowed, remaining, retry_after)"""
        try:
            from app.utils.cache import get_redis

            r = get_redis()
            key = f"pl:rl:{ip}:{path[:40]}"
            now = int(time.time())
            window_start = now - window

            pipe = r.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(now * 1000): now})
            pipe.zcard(key)
            pipe.expire(key, window)
            results = await pipe.execute()

            count = results[2]
            if count > limit:
                oldest = await r.zrange(key, 0, 0, withscores=True)
                retry = window - (now - int(oldest[0][1])) if oldest else window
                return False, 0, max(1, retry)
            return True, limit - count, 0
        except Exception:
            return True, limit, 0  # Redis 不可用时放行


class IPBlocklistManager:
    """IP 黑名单管理工具"""

    @staticmethod
    async def block(ip: str, reason: str = "manual"):
        from app.utils.cache import get_redis

        r = get_redis()
        await r.sadd("pl:ip:blacklist", ip)
        await r.hset("pl:ip:blacklist:reasons", ip, reason)
        logger.info("IP blocked: %s reason=%s", ip, reason)

    @staticmethod
    async def unblock(ip: str):
        from app.utils.cache import get_redis

        r = get_redis()
        await r.srem("pl:ip:blacklist", ip)
        await r.hdel("pl:ip:blacklist:reasons", ip)

    @staticmethod
    async def list_blocked() -> list[dict]:
        from app.utils.cache import get_redis

        r = get_redis()
        ips = await r.smembers("pl:ip:blacklist")
        reasons = await r.hgetall("pl:ip:blacklist:reasons")
        return [{"ip": ip, "reason": reasons.get(ip, "unknown")} for ip in ips]

    @staticmethod
    async def auto_block_brute_force(ip: str, threshold: int = 20, window: int = 300):
        """登录失败超过阈值时自动封禁"""
        from app.utils.cache import get_redis

        r = get_redis()
        key = f"pl:login:fail:{ip}"
        count = await r.incr(key)
        await r.expire(key, window)
        if count >= threshold:
            await IPBlocklistManager.block(ip, f"brute_force:{count}_attempts")
            return True
        return False
