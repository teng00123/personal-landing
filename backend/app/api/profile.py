from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import PublicProfileOut, UserOut, UserProfileUpdate
from app.api.auth import require_admin

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=PublicProfileOut, summary="获取公开 Profile（首页用）")
def get_profile(db: Session = Depends(get_db)):
    """返回第一个管理员的公开信息，用于首页展示简历。不包含密码等敏感字段。"""
    user = db.query(User).filter(User.is_admin == True, User.is_active == True).first()
    if not user:
        raise HTTPException(404, "Profile 未配置")
    return user


@router.put("", response_model=UserOut, summary="更新 Profile（管理员）")
def update_profile(
    body: UserProfileUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(admin, field, value)
    db.commit()
    db.refresh(admin)
    return admin
