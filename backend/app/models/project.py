from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    github_url = Column(String(512), nullable=False)
    github_repo = Column(String(256))       # owner/repo
    cover_image = Column(String(512))
    tags = Column(String(256))              # 逗号分隔
    tech_stack = Column(String(512))        # 逗号分隔技术标签
    is_published = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)

    # ── 部署信息 ────────────────────────────────────────────
    # deploy_status: pending | deploying | running | failed | stopped
    deploy_status = Column(String(32), default="pending", nullable=False)
    deploy_port = Column(Integer)
    deploy_url = Column(String(256))
    deploy_log = Column(Text)               # 实时部署日志
    deploy_branch = Column(String(64), default="main")
    deploy_command = Column(String(512))    # 自定义启动命令（可选）
    framework = Column(String(64))          # 自动检测：vue/react/fastapi/…

    last_deployed_at = Column(DateTime(timezone=True))

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", backref="projects")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Project {self.name} [{self.deploy_status}]>"
