from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_mfa_token,
    decode_mfa_token,
    decode_token,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    LoginRequest,
    MfaChallenge,
    MfaVerify,
    Token,
    UserOut,
)
from app.utils.mfa import (
    generate_totp_secret,
    get_totp_qr_base64,
    verify_totp,
)
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=False)


# ── 依赖注入：解析 JWT ──────────────────────────────────────


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if not creds:
        raise HTTPException(401, "未提供 Token")
    user_id = decode_token(creds.credentials)
    if user_id is None:
        raise HTTPException(401, "Token 无效或已过期")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(401, "用户不存在或已禁用")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    return user


# ── 登录 ───────────────────────────────────────────────────


@router.post("/login", summary="登录获取 Token（支持 MFA 二步验证）")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or body.password != user.hashed_password:
        raise HTTPException(401, "用户名或密码错误")

    # 未启用 MFA：直接返回 Token
    if not user.mfa_enabled:
        token = create_access_token(user.id)
        return Token(access_token=token, user=UserOut.model_validate(user))

    # 已启用 MFA，本次请求携带了 mfa_code → 直接完成验证
    if body.mfa_code:
        if not verify_totp(user.mfa_secret, body.mfa_code):
            raise HTTPException(401, "验证码错误或已过期")
        token = create_access_token(user.id)
        return Token(access_token=token, user=UserOut.model_validate(user))

    # 已启用 MFA，但没带 code → 返回 MFA challenge（HTTP 202）
    mfa_token = create_mfa_token(user.id)
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=202,
        content=MfaChallenge(mfa_required=True, mfa_token=mfa_token).model_dump(),
    )


@router.post("/login/mfa", response_model=Token, summary="MFA 二步验证完成登录")
def login_mfa(body: MfaVerify, db: Session = Depends(get_db)):
    """第二步：校验 TOTP 码，返回正式 Token"""
    user_id = decode_mfa_token(body.mfa_token)
    if user_id is None:
        raise HTTPException(401, "MFA token 无效或已过期（5 分钟内有效）")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(401, "用户不存在或已禁用")
    if not verify_totp(user.mfa_secret, body.code):
        raise HTTPException(401, "验证码错误或已过期")
    token = create_access_token(user.id)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut, summary="获取当前用户信息")
def me(user: User = Depends(get_current_user)):
    return user


# ── MFA 管理接口 ────────────────────────────────────────────


class MfaCodeBody(BaseModel):
    code: str


@router.post("/security/mfa/setup", summary="生成 MFA 绑定二维码（第一步）")
def mfa_setup(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """生成新的 TOTP Secret 并返回 QR 码，尚未正式启用（需 confirm 步骤）"""
    secret = generate_totp_secret()
    user.mfa_pending_secret = secret
    db.commit()
    qr = get_totp_qr_base64(secret, user.username)
    return {"secret": secret, "qr_code": qr}


@router.post("/security/mfa/confirm", summary="验证 TOTP 码并启用 MFA（第二步）")
def mfa_confirm(
    body: MfaCodeBody,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not user.mfa_pending_secret:
        raise HTTPException(400, "请先调用 /setup 获取二维码")
    if not verify_totp(user.mfa_pending_secret, body.code):
        raise HTTPException(400, "验证码错误，请重试")
    user.mfa_secret          = user.mfa_pending_secret
    user.mfa_pending_secret  = None
    user.mfa_enabled         = True
    db.commit()
    return {"message": "MFA 已成功启用"}


@router.post("/security/mfa/disable", summary="关闭 MFA（需验证当前 TOTP 码）")
def mfa_disable(
    body: MfaCodeBody,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not user.mfa_enabled:
        raise HTTPException(400, "MFA 未启用")
    if not verify_totp(user.mfa_secret, body.code):
        raise HTTPException(400, "验证码错误")
    user.mfa_enabled        = False
    user.mfa_secret         = None
    user.mfa_pending_secret = None
    db.commit()
    return {"message": "MFA 已关闭"}


@router.get("/security/mfa/status", summary="查询 MFA 启用状态")
def mfa_status(user: User = Depends(require_admin)):
    return {"mfa_enabled": user.mfa_enabled}
