"""
社交互动 API — Iteration 5
支持:
  - 文章点赞 / 取消点赞（Redis 计数，IP 去重）
  - 评论系统（匿名 + 楼层结构）
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, constr
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Session, relationship

from app.db.session import Base, get_db
from app.utils.cache import get_cache, CacheManager

router = APIRouter(prefix="/social", tags=["social"])
logger = logging.getLogger(__name__)


# ── 评论模型 ──────────────────────────────────────────────

class Comment(Base):
    __tablename__ = "comments"

    id         = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id  = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    nickname   = Column(String(50), nullable=False)
    email      = Column(String(120), nullable=True)
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    replies = relationship("Comment", backref="parent", remote_side=[id], lazy="select")


# ── Schemas ───────────────────────────────────────────────

class CommentCreate(BaseModel):
    article_id: int
    parent_id:  Optional[int] = None
    nickname:   constr(min_length=1, max_length=50)
    email:      Optional[str] = None
    content:    constr(min_length=1, max_length=2000)


class CommentOut(BaseModel):
    id:         int
    article_id: int
    parent_id:  Optional[int] = None
    nickname:   str
    content:    str
    created_at: datetime
    replies:    list["CommentOut"] = []

    model_config = {"from_attributes": True}


# ── 点赞 ──────────────────────────────────────────────────

@router.post("/articles/{article_id}/like", summary="点赞/取消点赞")
async def toggle_like(
    article_id: int,
    request: Request,
    cache: CacheManager = Depends(get_cache),
):
    """用 Redis set 做 IP 去重，保证每个 IP 只能点一次"""
    ip = request.client.host or "unknown"
    ip_set_key = f"likes:ips:{article_id}"
    count_key  = f"likes:count:{article_id}"

    from app.utils.cache import get_redis
    redis = get_redis()

    already = await redis.sismember(f"pl:{ip_set_key}", ip)
    if already:
        # 取消点赞
        await redis.srem(f"pl:{ip_set_key}", ip)
        count = await redis.decr(f"pl:{count_key}")
        return {"liked": False, "count": max(0, int(count))}
    else:
        # 点赞
        await redis.sadd(f"pl:{ip_set_key}", ip)
        count = await redis.incr(f"pl:{count_key}")
        return {"liked": True, "count": int(count)}


@router.get("/articles/{article_id}/like", summary="获取点赞数")
async def get_likes(article_id: int):
    from app.utils.cache import get_redis
    redis = get_redis()
    count = await redis.get(f"pl:likes:count:{article_id}") or 0
    return {"article_id": article_id, "count": int(count)}


# ── 评论 ──────────────────────────────────────────────────

@router.get("/articles/{article_id}/comments", response_model=list[CommentOut], summary="获取文章评论")
def list_comments(article_id: int, db: Session = Depends(get_db)):
    # 只返回顶层评论（含嵌套 replies）
    top = (
        db.query(Comment)
        .filter(Comment.article_id == article_id, Comment.parent_id == None)
        .order_by(Comment.created_at)
        .all()
    )
    return top


@router.post("/articles/{article_id}/comments", response_model=CommentOut, status_code=201, summary="发表评论")
def create_comment(
    article_id: int,
    body: CommentCreate,
    db: Session = Depends(get_db),
):
    if body.article_id != article_id:
        raise HTTPException(400, "article_id 不匹配")
    if body.parent_id:
        parent = db.get(Comment, body.parent_id)
        if not parent or parent.article_id != article_id:
            raise HTTPException(404, "父评论不存在")

    # 简单内容过滤（生产中应接入内容安全 API）
    blocked = ["<script", "javascript:", "data:text"]
    for b in blocked:
        if b.lower() in body.content.lower():
            raise HTTPException(400, "评论内容含有不允许的内容")

    comment = Comment(
        article_id=article_id,
        parent_id=body.parent_id,
        nickname=body.nickname,
        email=body.email,
        content=body.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
