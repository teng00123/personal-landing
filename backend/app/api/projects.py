"""
项目 CRUD + GitHub README API
"""

import os
import re
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.auth import require_admin
from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectOut, ProjectPage, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])

UPLOAD_DIR = "./uploads/covers"
ALLOWED_IMG = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMG_SIZE = 5 * 1024 * 1024


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
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(Project)
    if q:
        query = query.filter(Project.name.ilike(f"%{q}%"))
    total = query.count()
    items = (
        query.order_by(Project.sort_order.asc(), desc(Project.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ProjectPage(total=total, page=page, page_size=page_size, items=items)


@router.post("", response_model=ProjectOut, status_code=201, summary="新建项目")
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
        deploy_log="[待部署] 项目已创建。\n",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
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


# ── GitHub README ──────────────────────────────────────────


@router.get("/{project_id}/readme", summary="拉取 GitHub README")
async def fetch_readme(project_id: int, db: Session = Depends(get_db)):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "项目不存在")
    if not p.github_url:
        return {"project_id": project_id, "readme": None, "error": "未设置 GitHub URL"}

    repo = _parse_repo(p.github_url)
    if not repo:
        return {"project_id": project_id, "readme": None, "error": "无法解析 GitHub 仓库地址"}

    import httpx
    for branch in ["main", "master"]:
        url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return {"project_id": project_id, "readme": resp.text, "readme_url": url}
        except Exception:
            continue

    return {"project_id": project_id, "readme": None, "error": "README 获取失败"}


# ── 封面图上传 ─────────────────────────────────────────────


@router.post("/{project_id}/cover", response_model=ProjectOut, summary="上传封面图")
async def upload_cover(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "项目不存在")
    if file.content_type not in ALLOWED_IMG:
        raise HTTPException(400, f"不支持的图片类型: {file.content_type}")
    raw = await file.read()
    if len(raw) > MAX_IMG_SIZE:
        raise HTTPException(413, "图片不能超过 5MB")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
        f.write(raw)

    if p.cover_image and p.cover_image.startswith("/uploads/"):
        old = "." + p.cover_image
        if os.path.exists(old):
            os.remove(old)

    p.cover_image = f"/uploads/covers/{filename}"
    db.commit()
    db.refresh(p)
    return p
