import os
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.articles import router as articles_router
from app.api.projects import router as projects_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("./uploads/covers", exist_ok=True)
    os.makedirs("./deploy_workspace", exist_ok=True)
    logger.info("personal-landing API started")
    yield
    logger.info("personal-landing API shutdown")


app = FastAPI(
    title="Personal Landing API",
    description="个人主页后端接口 — 简历 / 文章 / 项目自动部署",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ─────────────────────────────────────────────

app.add_middleware(GZipMiddleware, minimum_size=1024)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(
        "%s %s %d %.0fms",
        request.method, request.url.path,
        response.status_code, duration,
    )
    return response


# ── Global exception handlers ──────────────────────────────

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "资源不存在"})


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.exception("未处理异常: %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误，请稍后重试"})


# ── Static files ───────────────────────────────────────────

os.makedirs("./uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")

# ── Routers ────────────────────────────────────────────────

PREFIX = "/api/v1"
app.include_router(auth_router,     prefix=PREFIX)
app.include_router(profile_router,  prefix=PREFIX)
app.include_router(articles_router, prefix=PREFIX)
app.include_router(projects_router, prefix=PREFIX)


@app.get("/health", tags=["health"], summary="健康检查")
def health():
    return {"status": "ok", "version": app.version}
