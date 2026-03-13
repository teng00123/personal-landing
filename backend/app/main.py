import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.articles import router as articles_router
from app.api.projects import router as projects_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时确保上传目录存在
    os.makedirs("./uploads/covers", exist_ok=True)
    os.makedirs("./deploy_workspace", exist_ok=True)
    yield


app = FastAPI(
    title="Personal Landing API",
    description="个人主页后端接口 — 简历 / 文章 / 项目自动部署",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files ───────────────────────────────────────────
os.makedirs("./uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")

# ── Routers ────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(auth_router, prefix=PREFIX)
app.include_router(profile_router, prefix=PREFIX)
app.include_router(articles_router, prefix=PREFIX)
app.include_router(projects_router, prefix=PREFIX)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "version": app.version}
