"""
文章 CRUD API
迭代一：仅包含基础骨架（list / get-by-slug / create / update / delete）
迭代二：新增 Markdown 文件上传、封面图上传
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session
from python_slugify import slugify

from app.db.session import get_db
from app.models.article import Article
from app.models.user import User
from app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleOut, ArticlePage
)
from app.api.auth import get_current_user, require_admin

router = APIRouter(prefix="/articles", tags=["articles"])


# ── helpers ────────────────────────────────────────────────

def _unique_slug(title: str, db: Session, exclude_id: Optional[int] = None) -> str:
    base = slugify(title) or f"article"
    slug, i = base, 1
    while True:
        q = db.query(Article).filter(Article.slug == slug)
        if exclude_id:
            q = q.filter(Article.id != exclude_id)
        if not q.first():
            return slug
        slug = f"{base}-{i}"
        i += 1


# ── Public ─────────────────────────────────────────────────

@router.get("", response_model=ArticlePage, summary="文章列表（公开）")
def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Article).filter(Article.is_published == True)
    if tag:
        q = q.filter(Article.tags.ilike(f"%{tag}%"))
    total = q.count()
    items = (
        q.order_by(desc(Article.published_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ArticlePage(total=total, page=page, page_size=page_size, items=items)


@router.get("/slug/{slug}", response_model=ArticleOut, summary="文章详情（by slug）")
def get_by_slug(slug: str, db: Session = Depends(get_db)):
    a = db.query(Article).filter(Article.slug == slug, Article.is_published == True).first()
    if not a:
        raise HTTPException(404, "文章不存在")
    a.view_count += 1
    db.commit()
    db.refresh(a)
    return a


# ── Admin ──────────────────────────────────────────────────

@router.get("/admin", response_model=ArticlePage, summary="文章列表（管理员）")
def admin_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    total = db.query(Article).count()
    items = (
        db.query(Article)
        .order_by(desc(Article.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ArticlePage(total=total, page=page, page_size=page_size, items=items)


@router.post("", response_model=ArticleOut, status_code=201, summary="新建文章")
def create_article(
    body: ArticleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    slug = body.slug if body.slug else _unique_slug(body.title, db)
    # 检查 slug 唯一性
    if db.query(Article).filter(Article.slug == slug).first():
        raise HTTPException(409, f"slug '{slug}' 已存在")
    now = datetime.now(timezone.utc)
    article = Article(
        **body.model_dump(exclude={"slug"}),
        slug=slug,
        author_id=admin.id,
        published_at=now if body.is_published else None,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.get("/{article_id}", response_model=ArticleOut, summary="文章详情（by id，管理员）")
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
def update_article(
    article_id: int,
    body: ArticleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(404, "文章不存在")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(a, field, value)
    if body.is_published and not a.published_at:
        a.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{article_id}", status_code=204, summary="删除文章")
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(404, "文章不存在")
    db.delete(a)
    db.commit()
