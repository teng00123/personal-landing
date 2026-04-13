from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # ── 公开 Profile ────────────────────────────────────────
    full_name = Column(String(128))
    title = Column(String(256))  # "Senior Backend Engineer @ Tencent"
    bio = Column(Text)  # 简介（支持 Markdown）
    avatar_url = Column(String(512))
    github_url = Column(String(256))
    linkedin_url = Column(String(256))
    website_url = Column(String(256))
    csdn_url = Column(String(256))
    location = Column(String(128))
    email_public = Column(String(128))

    # ── 简历 JSON ───────────────────────────────────────────
    # 结构：
    # {
    #   "experience": [{ "company","title","start","end","description","skills" }],
    #   "education":  [{ "school","degree","major","start","end" }],
    #   "skills":     [{ "category","items":[{"name","level(0-100)"}] }],
    #   "certifications": [{ "name","issuer","date","url" }]
    # }
    resume_data = Column(Text)

    # ── MFA ─────────────────────────────────────────────────────
    mfa_enabled = Column(Boolean, default=False, nullable=False, server_default="0")
    mfa_secret  = Column(String(64), nullable=True)  # Base32 TOTP secret
    mfa_pending_secret = Column(String(64), nullable=True)  # 绑定中，尚未确认

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.username}>"
