"""
安全审计日志 — Iteration 6
记录所有敏感操作到数据库
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Optional

from fastapi import Request
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Session

from app.db.session import Base

logger = logging.getLogger(__name__)


class AuditLog(Base):
    """安全审计日志表"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # None = 匿名
    username = Column(String(64), nullable=True)
    action = Column(String(64), nullable=False, index=True)  # login/logout/create/update/delete
    resource = Column(String(64), nullable=True)  # article/project/user
    resource_id = Column(Integer, nullable=True)
    detail = Column(Text, nullable=True)  # JSON 额外信息
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(256), nullable=True)
    status = Column(String(16), default="success")  # success/failed/blocked
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)


def _get_ip(request: Optional[Request]) -> str:
    if not request:
        return "internal"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def record_audit(
    db: Session,
    action: str,
    resource: str = None,
    resource_id: int = None,
    user_id: int = None,
    username: str = None,
    detail: str = None,
    status: str = "success",
    request: Request = None,
):
    """同步写入审计日志"""
    try:
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource=resource,
            resource_id=resource_id,
            detail=detail,
            ip_address=_get_ip(request),
            user_agent=request.headers.get("user-agent", "")[:256] if request else None,
            status=status,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error("Audit log write failed: %s", e)
        db.rollback()


async def record_audit_async(
    action: str,
    resource: str = None,
    resource_id: int = None,
    user_id: int = None,
    username: str = None,
    detail: str = None,
    status: str = "success",
    request: Request = None,
):
    """异步写入审计日志（无 DB session，用 Redis 队列中转）"""
    import json

    try:
        from app.utils.cache import get_redis

        r = get_redis()
        entry = {
            "user_id": user_id,
            "username": username,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "detail": detail,
            "ip": _get_ip(request),
            "ua": request.headers.get("user-agent", "")[:256] if request else None,
            "status": status,
            "ts": datetime.now(UTC).isoformat(),
        }
        await r.lpush("pl:audit:queue", json.dumps(entry))
        await r.ltrim("pl:audit:queue", 0, 9999)  # 最多保留 10000 条待写入
    except Exception as e:
        logger.error("Async audit enqueue failed: %s", e)
