from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ArticleBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    cover_image: Optional[str] = None
    tags: Optional[str] = None
    is_published: bool = False


class ArticleCreate(ArticleBase):
    slug: Optional[str] = None  # 不填则自动生成


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[str] = None
    is_published: Optional[bool] = None


class ArticleOut(ArticleBase):
    id: int
    slug: str
    view_count: int
    author_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ArticleListItem(BaseModel):
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[str] = None
    is_published: bool
    view_count: int
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ArticlePage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ArticleListItem]
