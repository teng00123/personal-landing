from datetime import UTC, datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(subject: int, expires_minutes: Optional[int] = None) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": str(subject), "exp": expire},
        settings.APP_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_mfa_token(user_id: int) -> str:
    """MFA 中间凭证，5 分钟有效，仅用于完成 MFA 验证"""
    expire = datetime.now(UTC) + timedelta(minutes=5)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "scope": "mfa"},
        settings.APP_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_mfa_token(token: str) -> Optional[int]:
    """Returns user_id or None. Only accepts tokens with scope=mfa."""
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("scope") != "mfa":
            return None
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


def decode_token(token: str) -> Optional[int]:
    """Returns user_id (int) or None."""
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None
