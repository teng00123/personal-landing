"""
项目 CRUD API
迭代一：基础骨架（list / get / create / update / delete）
迭代三：新增 Celery 自动部署 / 部署日志 / 重新部署
"""
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectPage
from app.api.auth import require_admin

router = APIRouter(prefix="/projects", tags=["projects"])


def _parse_repo(github_url: str) -> Optional[str]:
    m = re.search(r"github\.com/([^/]+/[^/]+?)(?:\.git)?(?:[/?#]|$)", github_url)
    return m.group(1) if m else None


# ── Public ─────────────────────────────────────────────────

@router.get("", response_model=ProjectPage, summary="项目列表（公开）")
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = db.query(Project).filter(Project.is_published == True)
    total = q.count()
    items = (
        q.order_by(Project.sort_order.asc(), desc(Project.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ProjectPage(total=total, page=page, page_size=page_size, items=items)


@router.get("/public/{project_id}", response_model=ProjectOut, summary="项目详情（公开）")
def get_project_public(project_id: int, db: Session = Depends(get_db)):
    p = db.get(Project, project_id)
    if not p or not p.is_published:
        raise HTTPException(404, "项目不存在")
    return p


# ── Admin ──────────────────────────────────────────────────

@router.get("/admin", response_model=ProjectPage, summary="项目列表（管理员）")
def admin_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    total = db.query(Project).count()
    items = (
        db.query(Project)
        .order_by(Project.sort_order.asc(), desc(Project.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ProjectPage(total=total, page=page, page_size=page_size, items=items)


@router.post("", response_model=ProjectOut, status_code=201, summary="新建项目（触发部署在迭代三实现）")
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    github_repo = _parse_repo(body.github_url)
    project = Project(
        **body.model_dump(),
        github_repo=github_repo,
        owner_id=admin.id,
        deploy_status="pending",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    # 迭代三：在这里调用 deploy_project.delay(project.id)
    return project


@router.get("/{project_id}", response_model=ProjectOut, summary="项目详情（管理员）")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "项目不存在")
    return p


@router.put("/{project_id}", response_model=ProjectOut, summary="更新项目信息")
def update_project(
    project_id: int,
    body: ProjectUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "项目不存在")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(p, field, value)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{project_id}", status_code=204, summary="删除项目")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "项目不存在")
    db.delete(p)
    db.commit()
