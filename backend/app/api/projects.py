"""
项目 CRUD + 部署 API — Iteration 3
新增：
  POST /projects/{id}/deploy    触发 Celery 部署
  POST /projects/{id}/stop      停止运行中的项目
  POST /projects/{id}/redeploy  重新部署
  GET  /projects/{id}/logs      获取部署日志（支持 offset 参数）
  POST /projects/{id}/cover     上传封面图
  PUT  /projects/{id}/stars     同步 GitHub stars/forks
"""
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectPage
from app.api.auth import require_admin

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
        .offset((page - 1) * page_size).limit(page_size).all()
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
        .offset((page - 1) * page_size).limit(page_size).all()
    )
    return ProjectPage(total=total, page=page, page_size=page_size, items=items)


@router.post("", response_model=ProjectOut, status_code=201, summary="新建项目（自动触发部署）")
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
        deploy_log="[待部署] 项目已创建，点击「部署」开始自动部署。\n",
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # 自动触发部署
    try:
        from app.tasks.deploy import deploy_project
        deploy_project.delay(project.id)
        project.deploy_status = "deploying"
        db.commit()
        db.refresh(project)
    except Exception:
        pass  # Celery 不可用时不影响创建

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
    # 停止进程
    try:
        from app.tasks.deploy import stop_project
        stop_project.delay(project_id)
    except Exception:
        pass
    db.delete(p)
    db.commit()


# ── 部署操作 ───────────────────────────────────────────────

@router.post("/{project_id}/deploy", response_model=ProjectOut, summary="触发部署")
def trigger_deploy(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "项目不存在")
    if p.deploy_status == "deploying":
        raise HTTPException(409, "项目正在部署中")

    from app.tasks.deploy import deploy_project
    p.deploy_status = "deploying"
    p.deploy_log = "[deploy] 手动触发部署...\n"
    db.commit()
    db.refresh(p)
    deploy_project.delay(project_id)
    return p


@router.post("/{project_id}/redeploy", response_model=ProjectOut, summary="重新部署")
def redeploy(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "项目不存在")

    from app.tasks.deploy import stop_project, deploy_project
    stop_project.delay(project_id)

    p.deploy_status = "deploying"
    p.deploy_log = "[redeploy] 重新部署中...\n"
    db.commit()
    db.refresh(p)
    deploy_project.apply_async((project_id,), countdown=3)
    return p


@router.post("/{project_id}/stop", response_model=ProjectOut, summary="停止项目")
def stop(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "项目不存在")

    from app.tasks.deploy import stop_project
    stop_project.delay(project_id)

    p.deploy_status = "stopped"
    db.commit()
    db.refresh(p)
    return p


@router.get("/{project_id}/logs", summary="获取部署日志")
def get_logs(
    project_id: int,
    offset: int = Query(0, ge=0, description="从第几个字符开始返回（用于增量轮询）"),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "项目不存在")
    log = p.deploy_log or ""
    return {
        "project_id": project_id,
        "status": p.deploy_status,
        "log": log[offset:],
        "total_length": len(log),
        "deploy_url": p.deploy_url,
    }


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
