"""
Prometheus 指标收集器 — Iteration 4
暴露 /metrics 端点供 Prometheus 抓取
"""

import logging
import time
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

logger = logging.getLogger(__name__)

# ── 业务指标定义 ──────────────────────────────────────────

# HTTP 请求计数
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP request count",
    ["method", "endpoint", "status_code"],
)

# HTTP 请求耗时
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# 当前活跃请求数
HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"],
)

# 文章相关
ARTICLES_TOTAL = Gauge("articles_total", "Total number of articles", ["status"])
ARTICLE_VIEWS_TOTAL = Counter("article_views_total", "Total article view count")

# 项目相关
PROJECTS_TOTAL = Gauge("projects_total", "Total number of projects", ["status"])
DEPLOY_JOBS_TOTAL = Counter(
    "deploy_jobs_total",
    "Total deployment job count",
    ["result"],  # success / failure
)

# 缓存命中
CACHE_HITS_TOTAL = Counter("cache_hits_total", "Cache hit count", ["cache_name"])
CACHE_MISSES_TOTAL = Counter("cache_misses_total", "Cache miss count", ["cache_name"])

# 系统信息
APP_INFO = Info("app_info", "Application version and environment")
APP_INFO.info({"version": "1.0.0", "environment": "production"})


# ── 中间件 ────────────────────────────────────────────────

IGNORED_PATHS = {"/metrics", "/health", "/docs", "/redoc", "/openapi.json"}


async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    """记录每次 HTTP 请求的耗时和状态码"""
    path = request.url.path
    method = request.method

    # 跳过内部路径
    if path in IGNORED_PATHS:
        return await call_next(request)

    HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).inc()
    start = time.perf_counter()

    try:
        response: Response = await call_next(request)
        status = response.status_code
    except Exception as exc:
        status = 500
        raise exc
    finally:
        duration = time.perf_counter() - start
        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=path, status_code=str(status)).inc()
        HTTP_REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)
        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).dec()

    return response


# ── /metrics 端点 ─────────────────────────────────────────


def metrics_endpoint():
    """返回 Prometheus 格式的指标数据"""
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


# ── 注册到 FastAPI ─────────────────────────────────────────


def setup_metrics(app: FastAPI) -> None:
    """在 app 启动时注册中间件和 /metrics 路由"""
    app.middleware("http")(metrics_middleware)
    app.add_route("/metrics", lambda _: metrics_endpoint(), methods=["GET"])
    logger.info("Prometheus metrics enabled at /metrics")
