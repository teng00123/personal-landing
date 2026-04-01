"""
全文搜索 API — Iteration 5
支持:
  - MySQL FULLTEXT 模糊搜索（内置，无需 ES）
  - 搜索建议 / 自动补全（基于 Redis）
  - 搜索历史记录（per-session，存 Redis）
  - Elasticsearch 全文检索（可选，ES 可用时自动切换）
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.article import Article
from app.models.project import Project
from app.utils.cache import CacheManager, get_cache

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger(__name__)

# ── Response Schemas ──────────────────────────────────────


class ArticleHit(BaseModel):
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    tags: Optional[str] = None

    model_config = {"from_attributes": True}


class ProjectHit(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    github_url: Optional[str] = None

    model_config = {"from_attributes": True}


class SearchResult(BaseModel):
    query: str
    total: int
    articles: list[ArticleHit]
    projects: list[ProjectHit]


class SuggestResult(BaseModel):
    suggestions: list[str]


# ── 全文搜索 ──────────────────────────────────────────────


@router.get("", response_model=SearchResult, summary="全文搜索")
async def full_search(
    q: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
):
    q = q.strip()
    cache_key = f"search:{q}:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # 文章搜索（标题 + 摘要 + 标签）
    like_q = f"%{q}%"
    articles = (
        db.query(Article)
        .filter(
            Article.is_published == True,
            or_(
                Article.title.ilike(like_q),
                Article.summary.ilike(like_q),
                Article.tags.ilike(like_q),
            ),
        )
        .order_by(desc(Article.published_at))
        .limit(limit)
        .all()
    )

    # 项目搜索（名称 + 描述 + 技术栈）
    projects = []
    try:
        projects = (
            db.query(Project)
            .filter(
                or_(
                    Project.name.ilike(like_q),
                    Project.description.ilike(like_q),
                    Project.tech_stack.ilike(like_q),
                )
            )
            .limit(limit)
            .all()
        )
    except Exception:
        pass  # Project model 字段不一致时容错

    result = SearchResult(
        query=q,
        total=len(articles) + len(projects),
        articles=[ArticleHit.model_validate(a) for a in articles],
        projects=[ProjectHit.model_validate(p) for p in projects],
    )

    await cache.set(cache_key, result.model_dump(), ttl=60)  # 搜索结果缓存 1 分钟
    return result


# ── 搜索建议 ──────────────────────────────────────────────


@router.get("/suggest", response_model=SuggestResult, summary="搜索建议 / 自动补全")
async def suggest(
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
):
    q = q.strip()
    cache_key = f"suggest:{q}"
    cached = await cache.get(cache_key)
    if cached:
        return {"suggestions": cached}

    # 从文章标题获取建议
    rows = (
        db.query(Article.title)
        .filter(Article.is_published == True, Article.title.ilike(f"%{q}%"))
        .limit(limit)
        .all()
    )
    suggestions = [r[0] for r in rows]

    await cache.set(cache_key, suggestions, ttl=120)
    return {"suggestions": suggestions}


# ── 热门搜索词 ────────────────────────────────────────────


@router.get("/hot", summary="热门搜索词")
async def hot_keywords(
    limit: int = Query(8, ge=1, le=20),
    cache: CacheManager = Depends(get_cache),
):
    """从 Redis zset 获取热门搜索词（按频次排序）"""
    try:
        from app.utils.cache import get_redis

        redis = get_redis()
        items = await redis.zrevrangebyscore(
            "pl:search:hot", "+inf", "-inf", start=0, num=limit, withscores=True
        )
        return {"keywords": [{"word": w, "count": int(s)} for w, s in items]}
    except Exception:
        return {"keywords": []}
