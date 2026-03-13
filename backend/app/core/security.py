from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def _pre_hash(plain: str) -> str:
    """
    bcrypt 原生最多处理 72 字节，超长密码会被截断或抛异常。
    用 SHA-256 做预处理：输出固定 64 hex 字符（64 bytes），
    既解决长度限制，也不损失任何安全性。
    """
    return sha256(plain.encode("utf-8")).hexdigest()


def hash_password(plain: str) -> str:
    return _pwd.hash(_pre_hash(plain))


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(_pre_hash(plain), hashed)


def create_access_token(subject: int, expires_minutes: Optional[int] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": str(subject), "exp": expire},
        settings.APP_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> Optional[int]:
    """Returns user_id (int) or None."""
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None
