"""
代码沙箱 API — Iteration 8
提供:
  - 多语言代码执行（Docker 隔离沙箱）
  - 代码片段保存/分享
  - 语言列表
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import secrets
import time
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.utils.cache import CacheManager, get_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sandbox", tags=["sandbox"])

# ── 支持的语言 ───────────────────────────────────────────

LANGUAGES: dict[str, dict] = {
    "python": {
        "name": "Python 3",
        "image": "python:3.12-alpine",
        "cmd": ["python3", "-c", "{code}"],
        "file_ext": ".py",
        "timeout": 10,
    },
    "javascript": {
        "name": "Node.js",
        "image": "node:20-alpine",
        "cmd": ["node", "-e", "{code}"],
        "file_ext": ".js",
        "timeout": 10,
    },
    "bash": {
        "name": "Bash",
        "image": "bash:5-alpine3.18",
        "cmd": ["bash", "-c", "{code}"],
        "file_ext": ".sh",
        "timeout": 5,
    },
    "go": {
        "name": "Go",
        "image": "golang:1.22-alpine",
        "file_ext": ".go",
        "timeout": 15,
        "via_file": True,  # Go 需要写文件再运行
    },
}

# ── Schemas ───────────────────────────────────────────────


class RunRequest(BaseModel):
    language: str
    code: str
    stdin: Optional[str] = None


class RunResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    language: str


class SnippetSave(BaseModel):
    language: str
    code: str
    title: Optional[str] = "Untitled"


# ── 代码执行（Docker 沙箱）────────────────────────────────


@router.get("/languages", summary="获取支持的语言列表")
def list_languages():
    return {"languages": [{"id": k, "name": v["name"]} for k, v in LANGUAGES.items()]}


@router.post("/run", response_model=RunResult, summary="执行代码（Docker 沙箱）")
async def run_code(req: RunRequest, cache: CacheManager = Depends(get_cache)):
    if req.language not in LANGUAGES:
        raise HTTPException(400, f"不支持的语言，可选: {list(LANGUAGES)}")
    if len(req.code) > 10_000:
        raise HTTPException(400, "代码长度不能超过 10,000 字符")

    # 同一代码片段缓存 30s（避免重复执行）
    cache_key = f"sandbox:{req.language}:{hashlib.sha256(req.code.encode()).hexdigest()[:16]}"
    if cached := await cache.get(cache_key):
        import json

        return RunResult(**json.loads(cached))

    lang = LANGUAGES[req.language]
    start = time.monotonic()

    # ── 检查 Docker 是否可用 ──────────────────────────────
    docker_available = os.path.exists("/var/run/docker.sock")
    if not docker_available:
        # 开发模式：Python Mock 执行
        return await _mock_run(req, lang, start)

    try:
        result = await _docker_run(req, lang, start)
    except Exception as e:
        logger.error("Docker run failed: %s", e)
        result = RunResult(
            stdout="",
            stderr=f"沙箱执行失败: {e}",
            exit_code=-1,
            duration_ms=0,
            language=req.language,
        )

    import json

    await cache.set(cache_key, json.dumps(result.model_dump()), ttl=30)
    return result


async def _docker_run(req: RunRequest, lang: dict, start: float) -> RunResult:
    """通过 docker run 执行代码（隔离沙箱）"""
    container_name = f"sandbox-{uuid.uuid4().hex[:8]}"
    timeout = lang.get("timeout", 10)

    # 构建命令
    if lang.get("via_file"):
        # 需要文件执行（如 Go）— 简化为 mock
        return await _mock_run(
            req, lang, start, note="Go file-based execution requires volume mount; using mock in CI"
        )

    inner_cmd = lang["cmd"][:]
    inner_cmd[-1] = inner_cmd[-1].replace("{code}", req.code)

    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "--name",
        container_name,
        "--network",
        "none",  # 禁止网络
        "--memory",
        "64m",  # 内存限制
        "--cpus",
        "0.5",  # CPU 限制
        "--read-only",  # 只读文件系统
        "--security-opt",
        "no-new-privileges",
        lang["image"],
    ] + inner_cmd

    try:
        proc = await asyncio.create_subprocess_exec(
            *docker_cmd,
            stdin=asyncio.subprocess.PIPE if req.stdin else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdin_data = req.stdin.encode() if req.stdin else None
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=stdin_data),
            timeout=timeout + 2,
        )
    except TimeoutError:
        try:
            await asyncio.create_subprocess_exec("docker", "kill", container_name)
        except Exception:
            pass
        return RunResult(
            stdout="",
            stderr=f"执行超时（{timeout}s）",
            exit_code=124,
            duration_ms=int((time.monotonic() - start) * 1000),
            language=req.language,
        )

    return RunResult(
        stdout=stdout.decode("utf-8", errors="replace")[:8192],
        stderr=stderr.decode("utf-8", errors="replace")[:2048],
        exit_code=proc.returncode or 0,
        duration_ms=int((time.monotonic() - start) * 1000),
        language=req.language,
    )


async def _mock_run(req: RunRequest, lang: dict, start: float, note: str = "") -> RunResult:
    """Docker 不可用时的 Mock 响应（仅用于开发）"""
    await asyncio.sleep(0.05)  # 模拟执行延迟
    line_count = len(req.code.splitlines())
    mock_out = (
        f"[Mock Sandbox — {lang['name']}]\n"
        f"代码行数: {line_count}\n"
        f"代码 SHA: {hashlib.sha256(req.code.encode()).hexdigest()[:12]}\n"
    )
    if note:
        mock_out += f"注: {note}\n"
    mock_out += "（配置 Docker 后将真实执行代码）"
    return RunResult(
        stdout=mock_out,
        stderr="",
        exit_code=0,
        duration_ms=int((time.monotonic() - start) * 1000),
        language=req.language,
    )


# ── 代码片段保存/分享 ────────────────────────────────────


@router.post("/snippets", summary="保存代码片段（生成分享链接）")
async def save_snippet(req: SnippetSave, cache: CacheManager = Depends(get_cache)):
    if req.language not in LANGUAGES:
        raise HTTPException(400, "不支持的语言")
    if len(req.code) > 10_000:
        raise HTTPException(400, "代码过长")

    snippet_id = secrets.token_urlsafe(8)
    import json

    data = json.dumps(
        {
            "id": snippet_id,
            "language": req.language,
            "title": req.title,
            "code": req.code,
        },
        ensure_ascii=False,
    )
    await cache.set(f"snippet:{snippet_id}", data, ttl=86400 * 7)  # 保存 7 天
    return {"id": snippet_id, "share_url": f"/playground?snippet={snippet_id}"}


@router.get("/snippets/{snippet_id}", summary="获取代码片段")
async def get_snippet(snippet_id: str, cache: CacheManager = Depends(get_cache)):
    import json

    data = await cache.get(f"snippet:{snippet_id}")
    if not data:
        raise HTTPException(404, "片段不存在或已过期")
    return json.loads(data)
