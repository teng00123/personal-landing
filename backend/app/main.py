"""
FastAPI 入口 — Iteration 4 (性能优化 + 监控)
新增:
  - 结构化 JSON 日志 (logging_config)
  - Prometheus 指标中间件 + /metrics 端点
  - GZip 压缩最小阈值调整
  - /health 增加 Redis 存活检测
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.articles import router as articles_router
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.projects import router as projects_router
from app.core.config import settings
from app.utils.i18n import i18n
from app.utils.logging_config import setup_logging
from app.utils.metrics import setup_metrics

# ── 日志初始化（最先执行）─────────────────────────────────
setup_logging(
    level="DEBUG" if settings.DEBUG else "INFO",
    json_logs=not settings.DEBUG,   # 生产输出 JSON，开发输出可读格式
)

import logging
logger = logging.getLogger("app")


# ── Lifespan ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("./uploads/covers", exist_ok=True)
    os.makedirs("./deploy_workspace", exist_ok=True)
    logger.info("personal-landing API started", extra={"version": "1.0.0"})
    yield
    logger.info("personal-landing API shutdown")


# ── App 实例 ──────────────────────────────────────────────

app = FastAPI(
    title="Personal Landing API",
    description="个人主页后端接口 — 简历 / 文章 / 项目自动部署",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ─────────────────────────────────────────────

# Prometheus 指标（最外层，覆盖所有路由）
setup_metrics(app)

# Gzip 压缩（1KB 以上响应才压缩）
app.add_middleware(GZipMiddleware, minimum_size=1024)

# CORS
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
app.include_router(auth_router,     prefix=PREFIX)
app.include_router(profile_router,  prefix=PREFIX)
app.include_router(articles_router, prefix=PREFIX)
app.include_router(projects_router, prefix=PREFIX)


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
