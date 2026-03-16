"""
增强认证 API — Iteration 6
新增:
  - MFA TOTP 绑定/验证
  - JWT Refresh Token
  - 登录失败暴力破解防护
  - 密码强度验证
  - 登出（Token 吊销）
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.utils.audit import record_audit
from app.utils.mfa import (
    generate_totp_secret,
    get_totp_qr_base64,
    verify_totp,
)
from app.utils.rate_limit import IPBlocklistManager
from app.utils.security_tools import check_password_strength

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth/security", tags=["security"])
_bearer = HTTPBearer(auto_error=False)

REFRESH_TOKEN_EXPIRE_DAYS = 30
ALGORITHM = "HS256"


# ── Schemas ───────────────────────────────────────────────

class MFASetupResponse(BaseModel):
    qr_code: str        # base64 data URI
    secret: str         # 备用手动输入密钥
    uri: str            # otpauth:// URI


class MFAVerifyRequest(BaseModel):
    code: str           # 6位 TOTP 码


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


# ── 辅助函数 ──────────────────────────────────────────────

def _create_refresh_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "type": "refresh"},
        settings.APP_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def _verify_refresh_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


async def _is_token_revoked(token: str) -> bool:
    """检查 Token 是否已被吊销（Redis 黑名单）"""
    try:
        from app.utils.cache import get_redis
        r = get_redis()
        from app.utils.security_tools import hash_sensitive
        return bool(await r.sismember("pl:token:revoked", hash_sensitive(token)))
    except Exception:
        return False


async def _revoke_token(token: str):
    """将 Token 加入吊销黑名单"""
    try:
        from app.utils.cache import get_redis
        r = get_redis()
        from app.utils.security_tools import hash_sensitive
        key = hash_sensitive(token)
        await r.sadd("pl:token:revoked", key)
        await r.expire("pl:token:revoked", 86400 * REFRESH_TOKEN_EXPIRE_DAYS)
    except Exception:
        pass


# ── MFA 绑定 ──────────────────────────────────────────────

@router.post("/mfa/setup", response_model=MFASetupResponse, summary="生成 MFA 绑定二维码")
async def mfa_setup(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """生成 TOTP 密钥，前端展示 QR 码让用户扫码"""
    secret = generate_totp_secret()
    # 临时存储（绑定确认后才写入 user 表）
    from app.utils.cache import get_redis
    r = get_redis()
    await r.setex(f"pl:mfa:pending:{user.id}", 300, secret)  # 5 分钟有效

    from app.utils.mfa import get_totp_uri
    uri = get_totp_uri(secret, user.username)
    qr  = get_totp_qr_base64(secret, user.username)
    return MFASetupResponse(qr_code=qr, secret=secret, uri=uri)


@router.post("/mfa/confirm", summary="确认绑定 MFA（验证一次 TOTP 码）")
async def mfa_confirm(
    body: MFAVerifyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.utils.cache import get_redis
    r = get_redis()
    pending_secret = await r.get(f"pl:mfa:pending:{user.id}")
    if not pending_secret:
        raise HTTPException(400, "未找到待绑定的 MFA 密钥，请重新发起绑定")

    if not verify_totp(pending_secret, body.code):
        raise HTTPException(400, "TOTP 验证码错误")

    # 写入 user 记录（动态给 User 加字段，生产中应迁移）
    try:
        db.execute(
            __import__("sqlalchemy").text(
                "UPDATE users SET mfa_secret=:s, mfa_enabled=1 WHERE id=:id"
            ),
            {"s": pending_secret, "id": user.id},
        )
        db.commit()
    except Exception:
        # 列不存在时降级记录到 Redis
        await r.set(f"pl:mfa:secret:{user.id}", pending_secret)

    await r.delete(f"pl:mfa:pending:{user.id}")
    record_audit(db, "mfa_bind", user_id=user.id, username=user.username)
    return {"message": "MFA 绑定成功"}


@router.post("/mfa/disable", summary="关闭 MFA")
async def mfa_disable(
    body: MFAVerifyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 验证当前 TOTP 码才允许关闭
    from app.utils.cache import get_redis
    r = get_redis()
    secret = await r.get(f"pl:mfa:secret:{user.id}") or getattr(user, "mfa_secret", None)
    if not secret or not verify_totp(secret, body.code):
        raise HTTPException(400, "TOTP 验证码错误，无法关闭 MFA")

    try:
        db.execute(
            __import__("sqlalchemy").text("UPDATE users SET mfa_enabled=0 WHERE id=:id"),
            {"id": user.id},
        )
        db.commit()
    except Exception:
        await r.delete(f"pl:mfa:secret:{user.id}")

    record_audit(db, "mfa_disable", user_id=user.id, username=user.username)
    return {"message": "MFA 已关闭"}


# ── Token 刷新 ────────────────────────────────────────────

@router.post("/refresh", response_model=TokenPair, summary="刷新 Access Token")
async def refresh_token(
    body: RefreshRequest,
    db: Session = Depends(get_db),
):
    if await _is_token_revoked(body.refresh_token):
        raise HTTPException(401, "Refresh Token 已失效")

    user_id = _verify_refresh_token(body.refresh_token)
    if not user_id:
        raise HTTPException(401, "无效的 Refresh Token")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(401, "用户不存在或已禁用")

    # 吊销旧 refresh token（单次使用）
    await _revoke_token(body.refresh_token)

    access  = create_access_token(user.id)
    refresh = _create_refresh_token(user.id)
    return TokenPair(access_token=access, refresh_token=refresh)


# ── 登出 ──────────────────────────────────────────────────

@router.post("/logout", summary="登出（吊销 Token）")
async def logout(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
):
    if creds:
        await _revoke_token(creds.credentials)
    record_audit(db, "logout", user_id=user.id, username=user.username, request=request)
    return {"message": "已登出"}


# ── 密码修改 ──────────────────────────────────────────────

@router.post("/change-password", summary="修改密码")
async def change_password(
    body: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
):
    # 验证当前密码
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if not pwd_ctx.verify(body.current_password, user.hashed_password):
        raise HTTPException(400, "当前密码错误")

    # 验证新密码强度
    ok, msg = check_password_strength(body.new_password)
    if not ok:
        raise HTTPException(400, msg)

    user.hashed_password = pwd_ctx.hash(body.new_password)
    db.commit()
    record_audit(db, "password_change", user_id=user.id, username=user.username, request=request)
    return {"message": "密码修改成功"}


# ── IP 黑名单管理（管理员）────────────────────────────────

@router.get("/blocklist", summary="查看 IP 黑名单")
async def list_blocklist(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    return await IPBlocklistManager.list_blocked()


@router.post("/blocklist/{ip}", summary="封禁 IP")
async def block_ip(
    ip: str,
    reason: str = "manual",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    await IPBlocklistManager.block(ip, reason)
    record_audit(db, "ip_block", detail=f"ip={ip} reason={reason}", user_id=user.id, username=user.username)
    return {"message": f"IP {ip} 已封禁"}


@router.delete("/blocklist/{ip}", summary="解封 IP")
async def unblock_ip(
    ip: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    await IPBlocklistManager.unblock(ip)
    record_audit(db, "ip_unblock", detail=f"ip={ip}", user_id=user.id, username=user.username)
    return {"message": f"IP {ip} 已解封"}


# ── 安全审计日志查询（管理员）────────────────────────────

@router.get("/audit-logs", summary="查看安全审计日志")
def list_audit_logs(
    page: int = 1,
    size: int = 50,
    action: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    from app.utils.audit import AuditLog
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if action:
        q = q.filter(AuditLog.action == action)
    total = q.count()
    logs  = q.offset((page - 1) * size).limit(size).all()
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": [
            {
                "id":          l.id,
                "user_id":     l.user_id,
                "username":    l.username,
                "action":      l.action,
                "resource":    l.resource,
                "resource_id": l.resource_id,
                "detail":      l.detail,
                "ip_address":  l.ip_address,
                "status":      l.status,
                "created_at":  l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ],
    }
