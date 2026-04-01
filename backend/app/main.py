"""
FastAPI 入口 — Iteration 4 (性能优化 + 监控) + Iteration 5 (UX)
新增 (Iter 5):
  - 搜索 API /api/v1/search
  - 社交互动 API /api/v1/social (点赞/评论)
  - WebSocket 实时通知 /api/v1/ws/notifications
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.ai import router as ai_router
from app.api.articles import router as articles_router
from app.api.auth import router as auth_router
from app.api.community import router as community_router
from app.api.profile import router as profile_router
from app.api.projects import router as projects_router
from app.api.sandbox import router as sandbox_router
from app.api.search import router as search_router
from app.api.security import router as security_router
from app.api.social import router as social_router
from app.api.websocket import router as ws_router
from app.core.config import settings
from app.utils.i18n import i18n
from app.utils.logging_config import setup_logging
from app.utils.metrics import setup_metrics
from app.utils.rate_limit import RateLimitMiddleware

# ── 日志初始化 ────────────────────────────────────────────
setup_logging(
    level="DEBUG" if settings.DEBUG else "INFO",
    json_logs=not settings.DEBUG,
)

logger = logging.getLogger("app")


# ── Lifespan ──────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("./uploads/covers", exist_ok=True)
    os.makedirs("./deploy_workspace", exist_ok=True)
    # 确保审计日志表存在
    try:
        from app.api.community import Activity, ActivityRegistration, Follow, Message
        from app.api.social import Comment
        from app.db.session import Base, engine
        from app.utils.audit import AuditLog

        Base.metadata.create_all(
            bind=engine,
            tables=[
                Comment.__table__,
                AuditLog.__table__,
                Follow.__table__,
                Message.__table__,
                Activity.__table__,
                ActivityRegistration.__table__,
            ],
        )
    except Exception as e:
        logger.warning("table init skipped: %s", e)
    logger.info("personal-landing API started", extra={"version": "1.0.0"})
    yield
    logger.info("personal-landing API shutdown")


# ── App ───────────────────────────────────────────────────

app = FastAPI(
    title="Personal Landing API",
    description="个人主页后端接口 — 简历 / 文章 / 项目自动部署",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ─────────────────────────────────────────────

setup_metrics(app)
app.add_middleware(RateLimitMiddleware, enabled=not settings.DEBUG)  # Iter 6: 限流
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception Handlers ─────────────────────────────────────


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": i18n.t("errors.article_not_found")})


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.exception("未处理异常: %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": i18n.t("errors.internal_server_error")})


# ── Static Files ───────────────────────────────────────────

os.makedirs("./uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")

# ── Routers ────────────────────────────────────────────────

PREFIX = "/api/v1"
app.include_router(auth_router, prefix=PREFIX)
app.include_router(profile_router, prefix=PREFIX)
app.include_router(articles_router, prefix=PREFIX)
app.include_router(projects_router, prefix=PREFIX)
app.include_router(search_router, prefix=PREFIX)  # Iter 5
app.include_router(social_router, prefix=PREFIX)  # Iter 5
app.include_router(ws_router, prefix=PREFIX)  # Iter 5
app.include_router(security_router, prefix=PREFIX)  # Iter 6
app.include_router(ai_router, prefix=PREFIX)  # Iter 8
app.include_router(sandbox_router, prefix=PREFIX)  # Iter 8
app.include_router(community_router, prefix=PREFIX)  # Iter 8


# ── Health Check ──────────────────────────────────────────


@app.get("/health", tags=["ops"], summary="健康检查")
async def health():
    from app.utils.cache import get_redis

    redis_ok = False
    try:
        redis_ok = await get_redis().ping()
    except Exception:
        pass
    return {
        "status": "ok" if redis_ok else "degraded",
        "version": app.version,
        "redis": "ok" if redis_ok else "unavailable",
    }
