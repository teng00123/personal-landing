from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token, decode_token
from app.schemas.user import LoginRequest, Token, UserOut

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


# ── 路由 ───────────────────────────────────────────────────

@router.post("/login", response_model=Token, summary="登录获取 Token")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "用户名或密码错误")
    token = create_access_token(user.id)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut, summary="获取当前用户信息")
def me(user: User = Depends(get_current_user)):
    return user
