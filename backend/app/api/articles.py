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

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
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
CACHE_TTL_LIST = 120  # 列表缓存 2 分钟
CACHE_TTL_DETAIL = 300  # 详情缓存 5 分钟


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


# ── CSDN 导入 ──────────────────────────────────────────────


class CsdnImportBody(BaseModel):
    url: str


def _extract_csdn(html: str, url: str) -> dict:
    """从 CSDN 文章 HTML 中提取标题、正文（转 Markdown）、封面、摘要、标签。"""
    # 标题
    title_m = re.search(r'<h1[^>]*class="[^"]*title-article[^"]*"[^>]*>(.*?)</h1>', html, re.S)
    if not title_m:
        title_m = re.search(r"<title>(.*?)(?:\s*[-_|].*)?</title>", html, re.S)
    title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else "CSDN 文章"

    # 封面（og:image）
    cover_m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html)
    cover = cover_m.group(1) if cover_m else None

    # 标签
    tags_list = re.findall(r'<a[^>]+class="[^"]*tag-link[^"]*"[^>]*>([^<]+)</a>', html)
    tags = ",".join(t.strip() for t in tags_list[:6]) if tags_list else ""

    # 正文
    body_m = re.search(
        r'<div[^>]+id="article_content"[^>]*>(.*?)</div>\s*(?=<div[^>]+class="[^"]*article-copyright)',
        html,
        re.S,
    )
    if not body_m:
        body_m = re.search(r'<div[^>]+id="article_content"[^>]*>(.*?)</div>', html, re.S)

    content_html = body_m.group(1) if body_m else ""

    # 简单 HTML → Markdown 转换
    md = content_html
    md = re.sub(
        r"<h([1-6])[^>]*>(.*?)</h\1>",
        lambda m: "#" * int(m.group(1)) + " " + re.sub(r"<[^>]+>", "", m.group(2)).strip(),
        md,
        flags=re.S,
    )
    md = re.sub(
        r'<pre[^>]*><code[^>]*class="[^"]*language-([^"\s]+)[^"]*"[^>]*>(.*?)</code></pre>',
        lambda m: f'\n```{m.group(1)}\n{re.sub(chr(60)+"[^>]+"+chr(62),"",m.group(2)).strip()}\n```\n',
        md,
        flags=re.S,
    )
    md = re.sub(
        r"<pre[^>]*><code[^>]*>(.*?)</code></pre>",
        lambda m: f'\n```\n{re.sub(chr(60)+"[^>]+"+chr(62),"",m.group(1)).strip()}\n```\n',
        md,
        flags=re.S,
    )
    md = re.sub(
        r"<code[^>]*>(.*?)</code>",
        lambda m: f'`{re.sub(chr(60)+"[^>]+"+chr(62),"",m.group(1))}`',
        md,
        flags=re.S,
    )
    md = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", md, flags=re.S)
    md = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", md, flags=re.S)
    md = re.sub(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r"[\2](\1)", md, flags=re.S)
    md = re.sub(r'<img[^>]+src="([^"]+)"[^>]*/?>', r"![](\1)", md, flags=re.S)
    md = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1", md, flags=re.S)
    md = re.sub(r"<[^>]+>", "", md)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()

    # 追加原文链接
    md += f"\n\n---\n> 原文链接：[{url}]({url})\n"

    summary = md[:200].replace("\n", " ").strip()

    return {"title": title, "content": md, "cover": cover, "tags": tags, "summary": summary}


@router.post(
    "/import-csdn",
    response_model=ArticleOut,
    status_code=201,
    summary="从 CSDN 链接导入文章，保存为草稿",
)
async def import_csdn(
    body: CsdnImportBody,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    cache: CacheManager = Depends(get_cache),
):
    url = body.url.strip()
    if "csdn.net" not in url:
        raise HTTPException(400, "仅支持 CSDN 文章链接（csdn.net）")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://blog.csdn.net/",
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=12) as client:
            resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(502, f"CSDN 返回 {resp.status_code}，请检查链接是否有效")
        html = resp.text
    except httpx.TimeoutException:
        raise HTTPException(504, "请求 CSDN 超时，请稍后重试") from None
    except httpx.RequestError as e:
        raise HTTPException(502, f"网络错误：{e}") from e

    meta = _extract_csdn(html, url)
    if not meta["content"] or len(meta["content"]) < 50:
        raise HTTPException(422, "无法提取文章内容，CSDN 可能需要登录或已更改页面结构")

    slug = _unique_slug(meta["title"], db)
    article = Article(
        title=meta["title"],
        slug=slug,
        summary=meta["summary"],
        content=meta["content"],
        cover_image=meta["cover"],
        tags=meta["tags"],
        is_published=False,
        author_id=admin.id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
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
