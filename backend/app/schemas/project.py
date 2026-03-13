from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    github_url: str
    cover_image: Optional[str] = None
    tags: Optional[str] = None
    tech_stack: Optional[str] = None
    is_published: bool = True
    sort_order: int = 0
    deploy_branch: str = "main"
    deploy_command: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[str] = None
    tech_stack: Optional[str] = None
    is_published: Optional[bool] = None
    sort_order: Optional[int] = None
    deploy_branch: Optional[str] = None
    deploy_command: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    github_url: str
    github_repo: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[str] = None
    tech_stack: Optional[str] = None
    is_published: bool
    sort_order: int
    stars: int
    forks: int
    deploy_status: str
    deploy_port: Optional[int] = None
    deploy_url: Optional[str] = None
    deploy_log: Optional[str] = None
    deploy_branch: str
    deploy_command: Optional[str] = None
    framework: Optional[str] = None
    last_deployed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProjectPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ProjectOut]
