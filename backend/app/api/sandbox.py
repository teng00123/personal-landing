"""
代码沙箱 API — Iteration 8 (rev: real-exec)
提供:
  - 多语言代码执行（优先 Docker 隔离；无 Docker 时本地沙箱执行）
  - 代码片段保存/分享（Redis 缓存，7 天有效）
  - 语言列表
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import resource
import secrets
import sys
import tempfile
import time
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.utils.cache import CacheManager, get_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sandbox", tags=["sandbox"])

# ── 运行时探测 ────────────────────────────────────────────

def _which(cmd: str) -> str | None:
    import shutil
    return shutil.which(cmd)

RUNTIME_PYTHON = _which("python3") or _which("python")
RUNTIME_NODE   = _which("node") or _which("nodejs")
RUNTIME_BASH   = _which("bash")
DOCKER_SOCK    = os.path.exists("/var/run/docker.sock")

# ── 支持的语言 ────────────────────────────────────────────

LANGUAGES: dict[str, dict] = {
    "python": {
        "name": "Python 3",
        "image": "python:3.12-alpine",
        "docker_cmd": ["python3", "-c", "{code}"],
        "local_runtime": RUNTIME_PYTHON,
        "local_mode": "inline",          # 直接 -c 执行
        "file_ext": ".py",
        "timeout": 10,
    },
    "javascript": {
        "name": "Node.js",
        "image": "node:20-alpine",
        "docker_cmd": ["node", "-e", "{code}"],
        "local_runtime": RUNTIME_NODE,
        "local_mode": "inline",
        "file_ext": ".js",
        "timeout": 10,
    },
    "bash": {
        "name": "Bash",
        "image": "bash:5-alpine3.18",
        "docker_cmd": ["bash", "-c", "{code}"],
        "local_runtime": RUNTIME_BASH,
        "local_mode": "inline",
        "file_ext": ".sh",
        "timeout": 5,
    },
    "go": {
        "name": "Go",
        "image": "golang:1.22-alpine",
        "docker_cmd": None,
        "local_runtime": _which("go"),
        "local_mode": "file",            # 写文件再 go run
        "file_ext": ".go",
        "timeout": 15,
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
    engine: str = "local"   # "docker" | "local" | "mock"


class SnippetSave(BaseModel):
    language: str
    code: str
    title: Optional[str] = "Untitled"


# ── 主路由 ────────────────────────────────────────────────

@router.get("/languages", summary="获取支持的语言列表")
def list_languages():
    result = []
    for k, v in LANGUAGES.items():
        available = DOCKER_SOCK or bool(v.get("local_runtime"))
        result.append({
            "id": k,
            "name": v["name"],
            "available": available,
        })
    return {"languages": result}


@router.post("/run", response_model=RunResult, summary="执行代码")
async def run_code(req: RunRequest, cache: CacheManager = Depends(get_cache)):
    if req.language not in LANGUAGES:
        raise HTTPException(400, f"不支持的语言，可选: {list(LANGUAGES)}")
    if len(req.code) > 10_000:
        raise HTTPException(400, "代码长度不能超过 10,000 字符")

    # 缓存（相同代码 30s 内不重复执行）
    cache_key = f"sandbox:{req.language}:{hashlib.sha256(req.code.encode()).hexdigest()[:16]}"
    if cached := await cache.get(cache_key):
        import json
        return RunResult(**json.loads(cached))

    lang = LANGUAGES[req.language]
    start = time.monotonic()

    if DOCKER_SOCK:
        result = await _docker_run(req, lang, start)
    elif lang.get("local_runtime"):
        result = await _local_run(req, lang, start)
    else:
        result = RunResult(
            stdout="",
            stderr=f"语言 {lang['name']} 在当前环境不可用（未安装运行时）",
            exit_code=127,
            duration_ms=int((time.monotonic() - start) * 1000),
            language=req.language,
            engine="mock",
        )

    import json
    await cache.set(cache_key, json.dumps(result.model_dump()), ttl=30)
    return result


# ── 本地沙箱执行 ──────────────────────────────────────────

def _set_limits():
    """子进程 preexec_fn：设置资源限制"""
    # CPU 时间上限 12s（配合 asyncio timeout 10s）
    resource.setrlimit(resource.RLIMIT_CPU, (12, 12))
    # 虚拟内存 256MB
    try:
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
    except ValueError:
        pass  # 某些系统不支持 AS 限制
    # 文件大小 4MB
    resource.setrlimit(resource.RLIMIT_FSIZE, (4 * 1024 * 1024, 4 * 1024 * 1024))
    # 禁止 fork 新进程（nproc=1）— 只限制额外子进程
    try:
        resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    except (ValueError, AttributeError):
        pass


async def _local_run(req: RunRequest, lang: dict, start: float) -> RunResult:
    """本地沙箱执行（无 Docker）"""
    timeout = lang.get("timeout", 10)
    runtime = lang["local_runtime"]
    mode    = lang.get("local_mode", "inline")

    try:
        if mode == "file":
            result = await _run_via_file(req, lang, runtime, timeout, start)
        else:
            result = await _run_inline(req, lang, runtime, timeout, start)
    except Exception as e:
        logger.exception("local_run error: %s", e)
        result = RunResult(
            stdout="",
            stderr=f"执行失败: {e}",
            exit_code=-1,
            duration_ms=int((time.monotonic() - start) * 1000),
            language=req.language,
            engine="local",
        )
    return result


async def _run_inline(
    req: RunRequest, lang: dict, runtime: str, timeout: int, start: float
) -> RunResult:
    """直接通过 -c / -e 执行代码字符串"""
    ext = lang["file_ext"]

    # Node 和 bash 也用 inline，但 python 支持 -c；
    # 统一写临时文件以避免 shell 转义问题
    with tempfile.NamedTemporaryFile(suffix=ext, mode="w", delete=False) as f:
        f.write(req.code)
        tmp_path = f.name

    try:
        cmd = _build_file_cmd(runtime, lang["name"], tmp_path)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if req.stdin else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=_set_limits,
        )
        stdin_data = req.stdin.encode() if req.stdin else None
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=stdin_data), timeout=timeout
            )
        except TimeoutError:
            proc.kill()
            await proc.communicate()
            return RunResult(
                stdout="",
                stderr=f"执行超时（{timeout}s 限制）",
                exit_code=124,
                duration_ms=int((time.monotonic() - start) * 1000),
                language=req.language,
                engine="local",
            )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    return RunResult(
        stdout=stdout.decode("utf-8", errors="replace")[:8192],
        stderr=stderr.decode("utf-8", errors="replace")[:2048],
        exit_code=proc.returncode or 0,
        duration_ms=int((time.monotonic() - start) * 1000),
        language=req.language,
        engine="local",
    )


async def _run_via_file(
    req: RunRequest, lang: dict, runtime: str, timeout: int, start: float
) -> RunResult:
    """写临时文件后执行（Go 等需要文件的语言）"""
    ext = lang["file_ext"]
    with tempfile.NamedTemporaryFile(suffix=ext, mode="w", delete=False) as f:
        f.write(req.code)
        tmp_path = f.name
    try:
        cmd = [runtime, "run", tmp_path]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if req.stdin else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdin_data = req.stdin.encode() if req.stdin else None
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=stdin_data), timeout=timeout
            )
        except TimeoutError:
            proc.kill()
            await proc.communicate()
            return RunResult(
                stdout="",
                stderr=f"执行超时（{timeout}s 限制）",
                exit_code=124,
                duration_ms=int((time.monotonic() - start) * 1000),
                language=req.language,
                engine="local",
            )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    return RunResult(
        stdout=stdout.decode("utf-8", errors="replace")[:8192],
        stderr=stderr.decode("utf-8", errors="replace")[:2048],
        exit_code=proc.returncode or 0,
        duration_ms=int((time.monotonic() - start) * 1000),
        language=req.language,
        engine="local",
    )


def _build_file_cmd(runtime: str, lang_name: str, path: str) -> list[str]:
    """根据语言构建执行命令"""
    name = lang_name.lower()
    if "python" in name:
        return [runtime, path]
    if "node" in name:
        return [runtime, path]
    if "bash" in name:
        return [runtime, path]
    # 默认直接运行
    return [runtime, path]


# ── Docker 执行（有 docker.sock 时） ──────────────────────

async def _docker_run(req: RunRequest, lang: dict, start: float) -> RunResult:
    """通过 docker run 执行代码（完全隔离沙箱）"""
    if lang.get("docker_cmd") is None:
        # Go 等需要 volume mount，降级到本地执行
        if lang.get("local_runtime"):
            return await _local_run(req, lang, start)
        return RunResult(
            stdout="",
            stderr=f"{lang['name']} 需要 Docker volume mount，当前不支持",
            exit_code=1,
            duration_ms=0,
            language=req.language,
            engine="mock",
        )

    container_name = f"sandbox-{uuid.uuid4().hex[:8]}"
    timeout = lang.get("timeout", 10)
    inner_cmd = lang["docker_cmd"][:]
    inner_cmd[-1] = inner_cmd[-1].replace("{code}", req.code)

    docker_cmd = [
        "docker", "run", "--rm",
        "--name", container_name,
        "--network", "none",
        "--memory", "64m",
        "--cpus", "0.5",
        "--read-only",
        "--security-opt", "no-new-privileges",
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
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=stdin_data), timeout=timeout + 2
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
                engine="docker",
            )
    except Exception as e:
        logger.error("Docker run failed: %s", e)
        return RunResult(
            stdout="",
            stderr=f"沙箱执行失败: {e}",
            exit_code=-1,
            duration_ms=0,
            language=req.language,
            engine="docker",
        )

    return RunResult(
        stdout=stdout.decode("utf-8", errors="replace")[:8192],
        stderr=stderr.decode("utf-8", errors="replace")[:2048],
        exit_code=proc.returncode or 0,
        duration_ms=int((time.monotonic() - start) * 1000),
        language=req.language,
        engine="docker",
    )


# ── 代码片段保存/分享 ─────────────────────────────────────

@router.post("/snippets", summary="保存代码片段（生成分享链接）")
async def save_snippet(req: SnippetSave, cache: CacheManager = Depends(get_cache)):
    if req.language not in LANGUAGES:
        raise HTTPException(400, "不支持的语言")
    if len(req.code) > 10_000:
        raise HTTPException(400, "代码过长")

    snippet_id = secrets.token_urlsafe(8)
    import json
    data = json.dumps({
        "id": snippet_id,
        "language": req.language,
        "title": req.title,
        "code": req.code,
    }, ensure_ascii=False)
    await cache.set(f"snippet:{snippet_id}", data, ttl=86400 * 7)
    return {"id": snippet_id, "share_url": f"/playground?snippet={snippet_id}"}


@router.get("/snippets/{snippet_id}", summary="获取代码片段")
async def get_snippet(snippet_id: str, cache: CacheManager = Depends(get_cache)):
    import json
    data = await cache.get(f"snippet:{snippet_id}")
    if not data:
        raise HTTPException(404, "片段不存在或已过期")
    return json.loads(data)
