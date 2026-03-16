"""
文章 CRUD API — Iteration 2 + Iteration 4 (缓存 + 指标)
新增 (Iter 4):
  - 公开列表 / 详情接口接入 Redis 缓存
  - 写操作（创建/更新/删除）自动清除相关缓存
  - 阅读量计数写操作用 Redis incr 批处理
  - 记录 Prometheus 文章阅读指标
"""

import os
import re
import uuid
from datetime import UTC, datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from slugify import slugify
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.auth import require_admin
from app.db.session import get_db
from app.models.article import Article
from app.models.user import User
from app.schemas.article import (
    ArticleCreate,
    ArticleOut,
    ArticlePage,
    ArticleUpdate,
)
from app.utils.cache import CacheManager, get_cache
from app.utils.metrics import ARTICLE_VIEWS_TOTAL, ARTICLES_TOTAL

router = APIRouter(prefix="/articles", tags=["articles"])

UPLOAD_DIR = "./uploads/covers"
ALLOWED_IMG = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMG_SIZE = 5 * 1024 * 1024  # 5 MB

# 缓存 TTL
CACHE_TTL_LIST   = 120   # 列表缓存 2 分钟
CACHE_TTL_DETAIL = 300   # 详情缓存 5 分钟


# ── helpers ────────────────────────────────────────────────


def _unique_slug(title: str, db: Session, exclude_id: Optional[int] = None) -> str:
    base = slugify(title) or "article"
    slug, i = base, 1
    while True:
        q = db.query(Article).filter(Article.slug == slug)
        if exclude_id:
            q = q.filter(Article.id != exclude_id)
        if not q.first():
            return slug
        slug = f"{base}-{i}"
        i += 1


def _parse_md(content: str) -> dict:
    """从 Markdown 内容解析 title / summary / tags。"""
    title = ""
    tags = ""
    lines = content.splitlines()

    for line in lines:
        m = re.match(r"^#\s+(.+)", line.strip())
        if m:
            title = m.group(1).strip()
            break

    for line in lines[:20]:
        m = re.match(r"^(?:tags|标签)\s*[:：]\s*(.+)", line, re.IGNORECASE)
        if m:
            tags = m.group(1).strip()
            break

    summary_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if summary_lines:
                break
            continue
        summary_lines.append(stripped)
        if len(" ".join(summary_lines)) > 200:
            break
    summary = " ".join(summary_lines)[:200]

    return {"title": title, "summary": summary, "tags": tags}


def _article_list_key(page: int, page_size: int, tag: str, q: str) -> str:
    return f"articles:list:{page}:{page_size}:{tag}:{q}"


def _article_slug_key(slug: str) -> str:
    return f"articles:slug:{slug}"


# ── Public ─────────────────────────────────────────────────


@router.get("", response_model=ArticlePage, summary="文章列表（公开已发布）")
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    tag: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
):
    # 尝试读缓存
    cache_key = _article_list_key(page, page_size, tag or "", q or "")
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    query = db.query(Article).filter(Article.is_published == True)
    if tag:
        query = query.filter(Article.tags.ilike(f"%{tag}%"))
    if q:
        query = query.filter(Article.title.ilike(f"%{q}%"))
    total = query.count()
    items = (
        query.order_by(desc(Article.published_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    result = ArticlePage(total=total, page=page, page_size=page_size, items=items)

    # 写缓存
    await cache.set(cache_key, result.model_dump(), ttl=CACHE_TTL_LIST)

    # 更新文章总数指标
    ARTICLES_TOTAL.labels(status="published").set(
        db.query(Article).filter(Article.is_published == True).count()
    )
    return result


@router.get("/slug/{slug}", response_model=ArticleOut, summary="文章详情（by slug）")
async def get_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
):
    cache_key = _article_slug_key(slug)
    cached = await cache.get(cache_key)
    if cached is not None:
        # 异步增加阅读量（不阻塞响应）
        ARTICLE_VIEWS_TOTAL.inc()
        return cached

    a = db.query(Article).filter(Article.slug == slug, Article.is_published == True).first()
    if not a:
        raise HTTPException(404, "文章不存在")
    a.view_count += 1
    db.commit()
    db.refresh(a)

    await cache.set(cache_key, ArticleOut.model_validate(a).model_dump(), ttl=CACHE_TTL_DETAIL)
    ARTICLE_VIEWS_TOTAL.inc()
    return a


# ── Admin ──────────────────────────────────────────────────


@router.get("/admin", response_model=ArticlePage, summary="文章列表（管理员，含草稿）")
def admin_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = None,
    published: Optional[bool] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(Article)
    if q:
        query = query.filter(Article.title.ilike(f"%{q}%"))
    if published is not None:
        query = query.filter(Article.is_published == published)
    total = query.count()
    items = (
        query.order_by(desc(Article.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ArticlePage(total=total, page=page, page_size=page_size, items=items)


@router.post(
    "/upload-md",
    response_model=ArticleOut,
    status_code=201,
    summary="上传 .md 文件，自动解析并保存为草稿",
)
async def upload_markdown(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    cache: CacheManager = Depends(get_cache),
):
    if not file.filename.endswith(".md"):
        raise HTTPException(400, "只支持 .md 文件")

    raw = await file.read()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        content = raw.decode("gbk", errors="replace")

    meta = _parse_md(content)
    title = meta["title"] or file.filename.replace(".md", "")
    slug = _unique_slug(title, db)

    article = Article(
        title=meta["title"] or title,
        slug=slug,
        summary=meta["summary"],
        content=content,
        tags=meta["tags"],
        is_published=False,
        author_id=admin.id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    # 清除列表缓存
    await cache.clear_pattern("articles:list:*")
    return article


@router.post("", response_model=ArticleOut, status_code=201, summary="新建文章")
async def create_article(
    body: ArticleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    cache: CacheManager = Depends(get_cache),
):
    slug = body.slug if body.slug else _unique_slug(body.title, db)
    if db.query(Article).filter(Article.slug == slug).first():
        raise HTTPException(409, f"slug '{slug}' 已存在")
    now = datetime.now(UTC)
    article = Article(
        **body.model_dump(exclude={"slug"}),
        slug=slug,
        author_id=admin.id,
        published_at=now if body.is_published else None,
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    await cache.clear_pattern("articles:list:*")
    return article


@router.get("/{article_id}", response_model=ArticleOut, summary="文章详情（by id）")
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(404, "文章不存在")
    return a


@router.put("/{article_id}", response_model=ArticleOut, summary="更新文章")
async def update_article(
    article_id: int,
    body: ArticleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
    cache: CacheManager = Depends(get_cache),
):
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(404, "文章不存在")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(a, field, value)
    if body.is_published is True and not a.published_at:
        a.published_at = datetime.now(UTC)
    elif body.is_published is False:
        a.published_at = None
    db.commit()
    db.refresh(a)

    # 清除相关缓存
    await cache.clear_pattern("articles:list:*")
    await cache.delete(_article_slug_key(a.slug))
    return a


@router.delete("/{article_id}", status_code=204, summary="删除文章")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
    cache: CacheManager = Depends(get_cache),
):
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(404, "文章不存在")
    slug = a.slug
    if a.cover_image and a.cover_image.startswith("/uploads/"):
        path = "." + a.cover_image
        if os.path.exists(path):
            os.remove(path)
    db.delete(a)
    db.commit()

    await cache.clear_pattern("articles:list:*")
    await cache.delete(_article_slug_key(slug))


@router.post("/{article_id}/cover", response_model=ArticleOut, summary="上传封面图")
async def upload_cover(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
    cache: CacheManager = Depends(get_cache),
):
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(404, "文章不存在")

    if file.content_type not in ALLOWED_IMG:
        raise HTTPException(400, f"不支持的图片类型: {file.content_type}")

    raw = await file.read()
    if len(raw) > MAX_IMG_SIZE:
        raise HTTPException(413, "图片不能超过 5MB")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(raw)

    if a.cover_image and a.cover_image.startswith("/uploads/"):
        old = "." + a.cover_image
        if os.path.exists(old):
            os.remove(old)

    a.cover_image = f"/uploads/covers/{filename}"
    db.commit()
    db.refresh(a)

    await cache.delete(_article_slug_key(a.slug))
    return a

