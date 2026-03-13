# 统一导出，alembic env.py 只需 import app.models
from app.models.article import Article
from app.models.project import Project
from app.models.user import User

__all__ = ["User", "Article", "Project"]
