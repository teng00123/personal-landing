"""
社区功能 API — Iteration 8
提供:
  - 用户关注/取消关注
  - 粉丝/关注列表
  - 私信（站内信）
  - 用户动态 Feed
  - 活动管理（创建/报名/签到）
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Session

from app.db.session import Base, get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/community", tags=["community"])


# ─────────────────────────────────────────────────────────
# ORM 模型
# ─────────────────────────────────────────────────────────

class Follow(Base):
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "followee_id"),)

    id          = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    followee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class Message(Base):
    __tablename__ = "messages"

    id          = Column(Integer, primary_key=True, index=True)
    sender_id   = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content     = Column(Text, nullable=False)
    is_read     = Column(Integer, default=0)
    created_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class Activity(Base):
    __tablename__ = "activities"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    organizer   = Column(String(100), nullable=False)
    start_time  = Column(DateTime(timezone=True), nullable=False)
    end_time    = Column(DateTime(timezone=True), nullable=True)
    location    = Column(String(200), nullable=True)
    max_seats   = Column(Integer, default=0)  # 0 = 不限
    created_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class ActivityRegistration(Base):
    __tablename__ = "activity_registrations"
    __table_args__ = (UniqueConstraint("activity_id", "user_identifier"),)

    id              = Column(Integer, primary_key=True, index=True)
    activity_id     = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_identifier = Column(String(100), nullable=False)  # 邮箱 or user_id
    nickname        = Column(String(50), nullable=False)
    checked_in      = Column(Integer, default=0)
    registered_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ─────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    receiver_id: int
    content:     str

class ActivityCreate(BaseModel):
    title:       str
    description: Optional[str] = None
    organizer:   str
    start_time:  datetime
    end_time:    Optional[datetime] = None
    location:    Optional[str] = None
    max_seats:   Optional[int] = 0

class RegisterRequest(BaseModel):
    nickname:        str
    user_identifier: str   # 邮箱 or 用户标识


# ─────────────────────────────────────────────────────────
# 关注 / 粉丝
# ─────────────────────────────────────────────────────────

@router.post("/users/{user_id}/follow", summary="关注/取消关注用户")
def toggle_follow(user_id: int, request: Request, db: Session = Depends(get_db)):
    # 简化实现：从 Header 取当前用户（生产中应用 JWT）
    follower_id_str = request.headers.get("X-User-Id", "0")
    try:
        follower_id = int(follower_id_str)
    except ValueError:
        raise HTTPException(401, "请先登录") from None

    if follower_id == user_id:
        raise HTTPException(400, "不能关注自己")

    existing = db.query(Follow).filter(
        Follow.follower_id == follower_id,
        Follow.followee_id == user_id,
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"following": False, "message": "已取消关注"}
    else:
        follow = Follow(follower_id=follower_id, followee_id=user_id)
        db.add(follow)
        db.commit()
        return {"following": True, "message": "已关注"}


@router.get("/users/{user_id}/followers", summary="获取粉丝列表")
def get_followers(user_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    rows = (
        db.query(Follow)
        .filter(Follow.followee_id == user_id)
        .offset(skip).limit(limit)
        .all()
    )
    total = db.query(Follow).filter(Follow.followee_id == user_id).count()
    return {
        "total": total,
        "items": [{"user_id": r.follower_id, "since": r.created_at} for r in rows],
    }


@router.get("/users/{user_id}/following", summary="获取关注列表")
def get_following(user_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    rows = (
        db.query(Follow)
        .filter(Follow.follower_id == user_id)
        .offset(skip).limit(limit)
        .all()
    )
    total = db.query(Follow).filter(Follow.follower_id == user_id).count()
    return {
        "total": total,
        "items": [{"user_id": r.followee_id, "since": r.created_at} for r in rows],
    }


# ─────────────────────────────────────────────────────────
# 私信
# ─────────────────────────────────────────────────────────

@router.post("/messages", status_code=201, summary="发送私信")
def send_message(body: MessageCreate, request: Request, db: Session = Depends(get_db)):
    sender_id_str = request.headers.get("X-User-Id", "0")
    try:
        sender_id = int(sender_id_str)
    except ValueError:
        raise HTTPException(401, "请先登录") from None

    if len(body.content) > 2000:
        raise HTTPException(400, "私信内容不能超过 2000 字")

    msg = Message(
        sender_id=sender_id,
        receiver_id=body.receiver_id,
        content=body.content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "created_at": msg.created_at}


@router.get("/messages/inbox", summary="获取收件箱")
def get_inbox(request: Request, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    user_id_str = request.headers.get("X-User-Id", "0")
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(401, "请先登录") from None

    msgs = (
        db.query(Message)
        .filter(Message.receiver_id == user_id)
        .order_by(Message.created_at.desc())
        .offset(skip).limit(limit)
        .all()
    )
    unread = db.query(Message).filter(
        Message.receiver_id == user_id, Message.is_read == 0
    ).count()

    return {
        "unread": unread,
        "items": [
            {"id": m.id, "sender_id": m.sender_id, "content": m.content,
             "is_read": bool(m.is_read), "created_at": m.created_at}
            for m in msgs
        ],
    }


@router.patch("/messages/{msg_id}/read", summary="标记消息已读")
def mark_read(msg_id: int, request: Request, db: Session = Depends(get_db)):
    user_id_str = request.headers.get("X-User-Id", "0")
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(401, "请先登录") from None

    msg = db.get(Message, msg_id)
    if not msg or msg.receiver_id != user_id:
        raise HTTPException(404, "消息不存在")
    msg.is_read = 1
    db.commit()
    return {"ok": True}


# ─────────────────────────────────────────────────────────
# 活动管理
# ─────────────────────────────────────────────────────────

@router.get("/activities", summary="获取活动列表")
def list_activities(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    acts = (
        db.query(Activity)
        .order_by(Activity.start_time.desc())
        .offset(skip).limit(limit)
        .all()
    )
    total = db.query(Activity).count()
    return {
        "total": total,
        "items": [
            {
                "id": a.id, "title": a.title, "organizer": a.organizer,
                "start_time": a.start_time, "location": a.location,
                "max_seats": a.max_seats,
                "registered": db.query(ActivityRegistration)
                               .filter(ActivityRegistration.activity_id == a.id).count(),
            }
            for a in acts
        ],
    }


@router.post("/activities", status_code=201, summary="创建活动")
def create_activity(body: ActivityCreate, db: Session = Depends(get_db)):
    act = Activity(**body.model_dump())
    db.add(act)
    db.commit()
    db.refresh(act)
    return {"id": act.id, "title": act.title}


@router.post("/activities/{activity_id}/register", status_code=201, summary="活动报名")
def register_activity(activity_id: int, body: RegisterRequest, db: Session = Depends(get_db)):
    act = db.get(Activity, activity_id)
    if not act:
        raise HTTPException(404, "活动不存在")

    # 检查座位
    if act.max_seats > 0:
        count = db.query(ActivityRegistration).filter(
            ActivityRegistration.activity_id == activity_id
        ).count()
        if count >= act.max_seats:
            raise HTTPException(409, "报名人数已满")

    # 防重复报名
    existing = db.query(ActivityRegistration).filter(
        ActivityRegistration.activity_id == activity_id,
        ActivityRegistration.user_identifier == body.user_identifier,
    ).first()
    if existing:
        raise HTTPException(409, "已报名此活动")

    reg = ActivityRegistration(
        activity_id=activity_id,
        user_identifier=body.user_identifier,
        nickname=body.nickname,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return {"id": reg.id, "message": "报名成功"}


@router.post("/activities/{activity_id}/checkin", summary="活动签到")
def checkin_activity(activity_id: int, body: RegisterRequest, db: Session = Depends(get_db)):
    reg = db.query(ActivityRegistration).filter(
        ActivityRegistration.activity_id == activity_id,
        ActivityRegistration.user_identifier == body.user_identifier,
    ).first()
    if not reg:
        raise HTTPException(404, "未找到报名记录")
    if reg.checked_in:
        raise HTTPException(409, "已签到")
    reg.checked_in = 1
    db.commit()
    return {"message": "签到成功", "nickname": reg.nickname}


@router.get("/activities/{activity_id}/registrations", summary="获取报名名单")
def list_registrations(activity_id: int, db: Session = Depends(get_db)):
    regs = db.query(ActivityRegistration).filter(
        ActivityRegistration.activity_id == activity_id
    ).all()
    return {
        "total": len(regs),
        "items": [
            {"id": r.id, "nickname": r.nickname, "checked_in": bool(r.checked_in),
             "registered_at": r.registered_at}
            for r in regs
        ],
    }
