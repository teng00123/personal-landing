from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    slug = Column(String(300), unique=True, index=True, nullable=False)
    summary = Column(String(512))
    content = Column(Text(length=16_777_215), nullable=False)  # MEDIUMTEXT
    cover_image = Column(String(512))
    tags = Column(String(256))  # 逗号分隔，如 "Python,Backend,API"
    is_published = Column(Boolean, default=False, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", backref="articles")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Article {self.slug}>"
