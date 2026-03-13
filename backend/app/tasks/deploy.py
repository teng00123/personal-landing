"""
deploy.py — Iteration 3
Celery 自动部署任务：git clone / pull → 框架识别 → 安装依赖 → 构建 → 启动进程
"""

import os
import re
import signal
import socket
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from celery import Task
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.project import Project
from app.tasks.celery_app import celery_app

# ── 工具函数 ───────────────────────────────────────────────


def _find_free_port(start: int = None, end: int = 9000) -> int:
    start = start or settings.DEPLOY_BASE_PORT
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise RuntimeError("没有可用端口")


def _detect_framework(proj_dir: Path) -> str:
    """自动识别项目框架"""
    # Docker 优先
    if (proj_dir / "Dockerfile").exists():
        return "docker"

    pkg = proj_dir / "package.json"
    req = proj_dir / "requirements.txt"

    if pkg.exists():
        content = pkg.read_text(errors="replace")
        if "next" in content:
            return "nextjs"
        if '"build"' in content:
            return "vue-react"  # Vue / React / 其他有 build 脚本的 SPA
        return "nodejs"

    if req.exists():
        content = req.read_text(errors="replace").lower()
        if "fastapi" in content or "uvicorn" in content:
            return "fastapi"
        if "flask" in content:
            return "flask"
        if "django" in content:
            return "django"

    # manage.py → Django
    if (proj_dir / "manage.py").exists():
        return "django"
    # app.py / main.py → 猜 Flask
    if (proj_dir / "app.py").exists() or (proj_dir / "main.py").exists():
        return "flask"

    # 纯静态
    if (proj_dir / "index.html").exists():
        return "static"

    return "unknown"


def _run(cmd: str, cwd: Path, log_cb, timeout: int = 300) -> bool:
    """执行 shell 命令，把输出回调给 log_cb，返回是否成功"""
    log_cb(f"$ {cmd}\n")
    proc = subprocess.Popen(
        cmd,
        shell=True,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    try:
        for line in proc.stdout:
            log_cb(line)
        proc.wait(timeout=timeout)
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        proc.kill()
        log_cb(f"\n[TIMEOUT] 命令执行超过 {timeout}s，已终止\n")
        return False


def _write_pid(proj_dir: Path, pid: int):
    (proj_dir / ".deploy.pid").write_text(str(pid))


def _read_pid(proj_dir: Path) -> int | None:
    f = proj_dir / ".deploy.pid"
    if f.exists():
        try:
            return int(f.read_text().strip())
        except ValueError:
            pass
    return None


def _kill_process(proj_dir: Path):
    pid = _read_pid(proj_dir)
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass


# ── 数据库更新辅助 ─────────────────────────────────────────


def _update_project(project_id: int, **kwargs):
    db: Session = SessionLocal()
    try:
        p = db.get(Project, project_id)
        if p:
            for k, v in kwargs.items():
                setattr(p, k, v)
            db.commit()
    finally:
        db.close()


def _append_log(project_id: int, text: str):
    db: Session = SessionLocal()
    try:
        p = db.get(Project, project_id)
        if p:
            p.deploy_log = (p.deploy_log or "") + text
            db.commit()
    finally:
        db.close()


# ── Celery Tasks ───────────────────────────────────────────


@celery_app.task(name="deploy_project", bind=True)
def deploy_project(self: Task, project_id: int):
    """
    全流程部署：
    1. git clone / pull
    2. 框架识别
    3. 安装依赖
    4. 构建
    5. 启动进程（后台）
    """
    # 清空旧日志，状态→deploying
    _update_project(project_id, deploy_status="deploying", deploy_log="[deploy] 开始部署...\n")

    def log(text: str):
        _append_log(project_id, text)

    # 拉取项目信息
    db: Session = SessionLocal()
    try:
        p = db.get(Project, project_id)
        if not p:
            return
        github_url = p.github_url
        branch = p.deploy_branch or "main"
        custom_cmd = p.deploy_command
        project_name = re.sub(r"[^\w-]", "_", p.name)
    finally:
        db.close()

    base_dir = Path(settings.DEPLOY_BASE_DIR)
    proj_dir = base_dir / f"proj_{project_id}_{project_name}"
    base_dir.mkdir(parents=True, exist_ok=True)

    try:
        # ── Step 1: clone / pull ──────────────────────────
        if proj_dir.exists():
            log(f"[git] 目录已存在，执行 git pull (branch: {branch})\n")
            _kill_process(proj_dir)
            ok = _run(
                f"git fetch origin && git checkout {branch} && git reset --hard origin/{branch}",
                proj_dir,
                log,
            )
        else:
            log(f"[git] clone {github_url} (branch: {branch})\n")
            ok = _run(
                f"git clone --depth=1 --branch {branch} {github_url} {proj_dir}", base_dir, log
            )

        if not ok:
            raise RuntimeError("git clone/pull 失败")

        # ── Step 2: 框架识别 ──────────────────────────────
        fw = _detect_framework(proj_dir)
        log(f"[detect] 框架识别: {fw}\n")
        _update_project(project_id, framework=fw)

        # ── Step 3 & 4: 安装 + 构建 ──────────────────────
        if fw in ("vue-react",):
            if not _run("npm install --prefer-offline", proj_dir, log):
                raise RuntimeError("npm install 失败")
            if not _run("npm run build", proj_dir, log):
                raise RuntimeError("npm run build 失败")

        elif fw == "nextjs":
            if not _run("npm install --prefer-offline", proj_dir, log):
                raise RuntimeError("npm install 失败")
            if not _run("npm run build", proj_dir, log):
                raise RuntimeError("npm run build 失败")

        elif fw == "nodejs":
            if not _run("npm install --prefer-offline", proj_dir, log):
                raise RuntimeError("npm install 失败")

        elif fw in ("fastapi", "flask", "django"):
            venv = proj_dir / ".venv"
            if not venv.exists():
                if not _run("python3 -m venv .venv", proj_dir, log):
                    raise RuntimeError("创建 venv 失败")
            pip = venv / "bin" / "pip"
            req_file = proj_dir / "requirements.txt"
            if req_file.exists():
                if not _run(f"{pip} install -r requirements.txt -q", proj_dir, log):
                    raise RuntimeError("pip install 失败")

        elif fw == "docker":
            tag = f"personal_landing_{project_id}"
            if not _run(f"docker build -t {tag} .", proj_dir, log):
                raise RuntimeError("docker build 失败")

        # ── Step 5: 分配端口 & 启动 ───────────────────────
        port = _find_free_port()
        log(f"[port] 分配端口: {port}\n")

        if custom_cmd:
            start_cmd = custom_cmd.replace("{PORT}", str(port))
        elif fw == "vue-react":
            dist = "dist"
            for candidate in ("dist", "build", "out", ".output/public"):
                if (proj_dir / candidate).exists():
                    dist = candidate
                    break
            start_cmd = f"serve -s {dist} -l {port}"
        elif fw == "nextjs":
            start_cmd = f"PORT={port} npm start"
        elif fw == "nodejs":
            entry = "index.js" if (proj_dir / "index.js").exists() else "app.js"
            start_cmd = f"PORT={port} node {entry}"
        elif fw == "fastapi":
            venv_python = str(proj_dir / ".venv" / "bin" / "python")
            main_file = "main:app" if (proj_dir / "main.py").exists() else "app.main:app"
            start_cmd = f"{venv_python} -m uvicorn {main_file} --host 0.0.0.0 --port {port}"
        elif fw == "flask":
            venv_python = str(proj_dir / ".venv" / "bin" / "python")
            app_file = "app.py" if (proj_dir / "app.py").exists() else "main.py"
            start_cmd = f"FLASK_APP={app_file} FLASK_ENV=production {venv_python} -m flask run --host 0.0.0.0 --port {port}"
        elif fw == "django":
            venv_python = str(proj_dir / ".venv" / "bin" / "python")
            start_cmd = f"{venv_python} manage.py runserver 0.0.0.0:{port}"
        elif fw == "static":
            start_cmd = f"serve -s . -l {port}"
        elif fw == "docker":
            tag = f"personal_landing_{project_id}"
            start_cmd = f"docker run -d -p {port}:{port} --name {tag} {tag}"
        else:
            raise RuntimeError(f"无法识别框架 '{fw}'，请在项目中填写自定义启动命令")

        log(f"[start] {start_cmd}\n")

        # 后台启动进程（不阻塞 Celery worker）
        proc = subprocess.Popen(
            start_cmd,
            shell=True,
            cwd=str(proj_dir),
            stdout=open(proj_dir / "stdout.log", "w"),
            stderr=open(proj_dir / "stderr.log", "w"),
            preexec_fn=os.setsid,  # 独立进程组，防止 worker 退出时被 kill
        )
        _write_pid(proj_dir, proc.pid)

        deploy_url = f"{settings.DEPLOY_BASE_URL}:{port}"
        log(f"[done] 部署成功！访问: {deploy_url}\n")

        _update_project(
            project_id,
            deploy_status="running",
            deploy_port=port,
            deploy_url=deploy_url,
            last_deployed_at=datetime.now(UTC),
        )

    except Exception as exc:
        log(f"\n[ERROR] {exc}\n")
        _update_project(project_id, deploy_status="failed")
        raise


@celery_app.task(name="stop_project")
def stop_project(project_id: int):
    """停止已部署的项目进程"""
    db: Session = SessionLocal()
    try:
        p = db.get(Project, project_id)
        if not p:
            return
        project_name = re.sub(r"[^\w-]", "_", p.name)
    finally:
        db.close()

    proj_dir = Path(settings.DEPLOY_BASE_DIR) / f"proj_{project_id}_{project_name}"
    _kill_process(proj_dir)
    _update_project(project_id, deploy_status="stopped", deploy_port=None, deploy_url=None)
