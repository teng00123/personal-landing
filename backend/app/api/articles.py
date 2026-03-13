"""
文章 CRUD API — Iteration 2
新增：
  POST /articles/upload-md        上传 .md 文件，解析标题/标签，返回草稿
  POST /articles/{id}/cover       上传封面图
  GET  /articles/admin            管理员列表（含草稿）
  全部原有 CRUD 保持不变
"""

import os
import re
import uuid
from datetime import UTC, datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from python_slugify import slugify
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

router = APIRouter(prefix="/articles", tags=["articles"])

UPLOAD_DIR = "./uploads/covers"
ALLOWED_IMG = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMG_SIZE = 5 * 1024 * 1024  # 5 MB


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

    # 提取第一个 # 标题
    for line in lines:
        m = re.match(r"^#\s+(.+)", line.strip())
        if m:
            title = m.group(1).strip()
            break

    # 提取 front-matter 风格的 tags（如果有）: `tags: vue, python`
    for line in lines[:20]:
        m = re.match(r"^(?:tags|标签)\s*[:：]\s*(.+)", line, re.IGNORECASE)
        if m:
            tags = m.group(1).strip()
            break

    # 生成摘要：第一段非标题文字，最多 200 字
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


# ── Public ─────────────────────────────────────────────────


@router.get("", response_model=ArticlePage, summary="文章列表（公开已发布）")
def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    tag: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
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
    return article


@router.post("", response_model=ArticleOut, status_code=201, summary="新建文章")
def create_article(
    body: ArticleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
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
    if body.is_published is True and not a.published_at:
        a.published_at = datetime.now(UTC)
    elif body.is_published is False:
        a.published_at = None
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
    # 删除封面图文件
    if a.cover_image and a.cover_image.startswith("/uploads/"):
        path = "." + a.cover_image
        if os.path.exists(path):
            os.remove(path)
    db.delete(a)
    db.commit()


@router.post("/{article_id}/cover", response_model=ArticleOut, summary="上传封面图")
async def upload_cover(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
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

    # 删除旧封面
    if a.cover_image and a.cover_image.startswith("/uploads/"):
        old = "." + a.cover_image
        if os.path.exists(old):
            os.remove(old)

    a.cover_image = f"/uploads/covers/{filename}"
    db.commit()
    db.refresh(a)
    return a
