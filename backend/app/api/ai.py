"""
AI 功能模块 — Iteration 8
提供:
  - 智能写作助手（文章生成、内容优化、语法检查）
  - 内容智能分析（摘要生成、关键词提取、情感分析）
  - 个性化推荐引擎（协同过滤 + 内容相似度）
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from collections import defaultdict
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.utils.cache import CacheManager, get_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])

# ─────────────────────────────────────────────────────────
# AI Provider 抽象（支持 OpenAI / 本地 Ollama / Mock）
# ─────────────────────────────────────────────────────────


class AIProvider:
    """可替换的 AI 后端封装"""

    def __init__(self):
        import os

        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_base = os.getenv("OPENAI_API_BASE", "")
        self.model = os.getenv("AI_MODEL", "gpt-3.5-turbo")
        self.ollama_url = os.getenv("OLLAMA_URL", "")

    async def chat(self, system: str, user: str, max_tokens: int = 512) -> str:
        """调用 AI 模型，返回文本；无配置时走 Mock"""
        if self.openai_key:
            return await self._openai_chat(system, user, max_tokens)
        if self.ollama_url:
            return await self._ollama_chat(system, user, max_tokens)
        return self._mock_response(user)

    async def _openai_chat(self, system: str, user: str, max_tokens: int) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.openai_base}/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()

    async def _ollama_chat(self, system: str, user: str, max_tokens: int) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"System: {system}\n\nUser: {user}",
                    "stream": False,
                    "options": {"num_predict": max_tokens},
                },
            )
            resp.raise_for_status()
            return resp.json()["response"].strip()

    def _mock_response(self, prompt: str) -> str:
        """开发模式 Mock：返回确定性占位内容"""
        h = hashlib.md5(prompt.encode()).hexdigest()[:8]
        return f"[AI Mock {h}] 这是模拟的 AI 响应，请配置 OPENAI_API_KEY 或 OLLAMA_URL 以启用真实功能。"


_ai = AIProvider()


# ─────────────────────────────────────────────────────────
# 8.1 写作助手
# ─────────────────────────────────────────────────────────


class WriteRequest(BaseModel):
    topic: str
    outline: Optional[str] = None
    length: Optional[str] = "medium"  # short / medium / long
    style: Optional[str] = "technical"  # technical / casual / academic


class OptimizeRequest(BaseModel):
    content: str
    goal: Optional[str] = "clarity"  # clarity / seo / engagement


class GrammarRequest(BaseModel):
    content: str
    lang: Optional[str] = "zh"  # zh / en


@router.post("/write/generate", summary="AI 文章生成")
async def generate_article(req: WriteRequest, cache: CacheManager = Depends(get_cache)):
    cache_key = f"ai:generate:{hashlib.md5((req.topic + str(req.outline) + req.length).encode()).hexdigest()}"
    if cached := await cache.get(cache_key):
        return {"content": cached, "cached": True}

    length_map = {"short": 300, "medium": 600, "long": 1000}
    tokens = length_map.get(req.length, 600)
    system = (
        f"你是一位专业的技术博客作者，风格为 {req.style}。"
        "根据用户提供的主题和大纲，生成结构清晰、内容丰富的 Markdown 格式文章。"
    )
    user = f"主题：{req.topic}"
    if req.outline:
        user += f"\n\n参考大纲：\n{req.outline}"
    user += f"\n\n请生成约 {tokens} 字的文章。"

    try:
        content = await _ai.chat(system, user, max_tokens=tokens * 2)
        await cache.set(cache_key, content, ttl=3600)
        return {"content": content, "cached": False}
    except Exception as e:
        logger.error("AI generate failed: %s", e)
        raise HTTPException(503, "AI 服务暂时不可用") from e


@router.post("/write/optimize", summary="内容优化建议")
async def optimize_content(req: OptimizeRequest, cache: CacheManager = Depends(get_cache)):
    goal_desc = {
        "clarity": "提升表达清晰度和可读性",
        "seo": "优化 SEO 关键词分布和标题结构",
        "engagement": "提升用户参与感和情感共鸣",
    }.get(req.goal, req.goal)

    system = f"你是内容编辑专家，目标：{goal_desc}。给出具体可操作的优化建议，用编号列表输出。"
    user = f"请分析并优化以下内容：\n\n{req.content[:2000]}"

    try:
        suggestions = await _ai.chat(system, user, max_tokens=400)
        return {"suggestions": suggestions, "goal": req.goal}
    except Exception as e:
        logger.error("AI optimize failed: %s", e)
        raise HTTPException(503, "AI 服务暂时不可用") from e


@router.post("/write/grammar", summary="语法检查")
async def check_grammar(req: GrammarRequest, cache: CacheManager = Depends(get_cache)):
    cache_key = f"ai:grammar:{hashlib.md5(req.content.encode()).hexdigest()}"
    if cached := await cache.get(cache_key):
        return json.loads(cached)

    lang_hint = "中文" if req.lang == "zh" else "English"
    system = (
        f"你是 {lang_hint} 语言专家。检查文本中的语法错误、用词不当、标点问题，"
        '以 JSON 格式返回: {{"score": 0-100, "issues": [{{"pos": "...", "issue": "...", "fix": "..."}}]}}'
    )
    user = f"检查以下文本：\n\n{req.content[:1500]}"

    try:
        raw = await _ai.chat(system, user, max_tokens=600)
        # 尝试解析 JSON，失败则包装为纯文本
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {"score": None, "raw": raw, "issues": []}
        await cache.set(cache_key, json.dumps(result, ensure_ascii=False), ttl=1800)
        return result
    except Exception as e:
        logger.error("AI grammar check failed: %s", e)
        raise HTTPException(503, "AI 服务暂时不可用") from e


# ─────────────────────────────────────────────────────────
# 8.2 内容智能分析
# ─────────────────────────────────────────────────────────


class AnalyzeRequest(BaseModel):
    content: str
    title: Optional[str] = None


@router.post("/analyze/summary", summary="自动摘要生成")
async def generate_summary(req: AnalyzeRequest, cache: CacheManager = Depends(get_cache)):
    cache_key = f"ai:summary:{hashlib.md5(req.content[:500].encode()).hexdigest()}"
    if cached := await cache.get(cache_key):
        return {"summary": cached, "cached": True}

    system = "你是专业摘要生成器。将输入文章压缩为 2-3 句话的摘要，保留核心观点，中文输出。"
    user = f"{'标题：' + req.title + chr(10) if req.title else ''}内容：\n{req.content[:3000]}"

    try:
        summary = await _ai.chat(system, user, max_tokens=200)
        await cache.set(cache_key, summary, ttl=86400)
        return {"summary": summary, "cached": False}
    except Exception as e:
        raise HTTPException(503, "AI 服务暂时不可用") from e


@router.post("/analyze/keywords", summary="关键词提取")
async def extract_keywords(req: AnalyzeRequest, cache: CacheManager = Depends(get_cache)):
    cache_key = f"ai:kw:{hashlib.md5(req.content[:500].encode()).hexdigest()}"
    if cached := await cache.get(cache_key):
        return json.loads(cached)

    system = (
        "从文章中提取 5-10 个最重要的关键词/短语，"
        '以 JSON 格式返回：{{"keywords": [{{"word": "...", "weight": 0.0-1.0}}]}}'
    )
    user = f"{req.content[:2000]}"

    try:
        raw = await _ai.chat(system, user, max_tokens=300)
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            # 降级：按空格/逗号分割
            words = [w.strip() for w in raw.replace("，", ",").split(",") if w.strip()]
            result = {"keywords": [{"word": w, "weight": 1.0} for w in words[:10]]}
        await cache.set(cache_key, json.dumps(result, ensure_ascii=False), ttl=86400)
        return result
    except Exception as e:
        raise HTTPException(503, "AI 服务暂时不可用") from e


@router.post("/analyze/sentiment", summary="情感倾向分析")
async def analyze_sentiment(req: AnalyzeRequest, cache: CacheManager = Depends(get_cache)):
    cache_key = f"ai:sentiment:{hashlib.md5(req.content[:300].encode()).hexdigest()}"
    if cached := await cache.get(cache_key):
        return json.loads(cached)

    system = (
        "分析文本情感倾向，以 JSON 返回："
        '{{"sentiment": "positive|neutral|negative", "score": -1.0~1.0, "emotions": ["..."], "reason": "..."}}'
    )
    user = f"{req.content[:1000]}"

    try:
        raw = await _ai.chat(system, user, max_tokens=200)
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {"sentiment": "neutral", "score": 0.0, "emotions": [], "reason": raw}
        await cache.set(cache_key, json.dumps(result, ensure_ascii=False), ttl=3600)
        return result
    except Exception as e:
        raise HTTPException(503, "AI 服务暂时不可用") from e


# ─────────────────────────────────────────────────────────
# 8.3 个性化推荐引擎
# ─────────────────────────────────────────────────────────


class RecommendRequest(BaseModel):
    article_id: Optional[int] = None  # 基于文章的相似推荐
    user_history: Optional[list[int]] = []  # 用户阅读历史 (article_id 列表)
    limit: Optional[int] = 5


def _cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """计算两个 TF-IDF 稀疏向量的余弦相似度"""
    common = set(vec_a) & set(vec_b)
    if not common:
        return 0.0
    dot = sum(vec_a[k] * vec_b[k] for k in common)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _build_tfidf(docs: list[dict]) -> list[dict[str, float]]:
    """轻量 TF-IDF（无需 sklearn）"""
    N = len(docs)
    df: dict[str, int] = defaultdict(int)
    tfs: list[dict[str, int]] = []

    for doc in docs:
        words = (doc.get("title", "") + " " + doc.get("content", "")).lower().split()
        tf: dict[str, int] = defaultdict(int)
        for w in words:
            tf[w] += 1
        tfs.append(tf)
        for w in set(tf):
            df[w] += 1

    vectors = []
    for tf in tfs:
        total = sum(tf.values()) or 1
        vec = {}
        for w, cnt in tf.items():
            idf = math.log((N + 1) / (df[w] + 1)) + 1
            vec[w] = (cnt / total) * idf
        vectors.append(vec)
    return vectors


@router.post("/recommend", summary="个性化文章推荐")
async def recommend_articles(
    req: RecommendRequest,
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
):
    cache_key = f"ai:rec:{req.article_id}:{','.join(str(i) for i in (req.user_history or []))}"
    if cached := await cache.get(cache_key):
        return json.loads(cached)

    # 拉取所有文章（生产中应分批）
    from sqlalchemy import text as sa_text

    rows = db.execute(
        sa_text("SELECT id, title, summary, tags FROM articles WHERE is_published=1 LIMIT 200")
    ).fetchall()

    if not rows:
        return {"recommendations": [], "strategy": "empty"}

    articles = [
        {"id": r[0], "title": r[1] or "", "content": r[2] or "", "tags": r[3] or ""} for r in rows
    ]
    vectors = _build_tfidf(articles)
    id_to_idx = {a["id"]: i for i, a in enumerate(articles)}

    scores: dict[int, float] = defaultdict(float)

    # ── 基于目标文章的内容相似度 ────────────────────────
    if req.article_id and req.article_id in id_to_idx:
        target_vec = vectors[id_to_idx[req.article_id]]
        for i, art in enumerate(articles):
            if art["id"] == req.article_id:
                continue
            scores[art["id"]] += _cosine_similarity(target_vec, vectors[i])

    # ── 基于历史的协同/内容加权 ──────────────────────────
    if req.user_history:
        history_set = set(req.user_history)
        for hist_id in req.user_history:
            if hist_id not in id_to_idx:
                continue
            h_vec = vectors[id_to_idx[hist_id]]
            for i, art in enumerate(articles):
                if art["id"] in history_set:
                    continue
                scores[art["id"]] += _cosine_similarity(h_vec, vectors[i]) * 0.5

    if not scores:
        # 冷启动：返回最新文章
        top = sorted(articles, key=lambda a: a["id"], reverse=True)[: req.limit]
        strategy = "cold_start"
    else:
        sorted_ids = sorted(scores, key=lambda k: scores[k], reverse=True)[: req.limit]
        id_map = {a["id"]: a for a in articles}
        top = [id_map[i] for i in sorted_ids if i in id_map]
        strategy = "content_similarity"

    result = {
        "recommendations": [
            {"id": a["id"], "title": a["title"], "score": round(scores.get(a["id"], 0.0), 4)}
            for a in top
        ],
        "strategy": strategy,
    }
    await cache.set(cache_key, json.dumps(result, ensure_ascii=False), ttl=300)
    return result


# ─────────────────────────────────────────────────────────
# 8.4 通用聊天助手
# ─────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    question: str


@router.post("/chat/ask", summary="通用聊天助手（流式响应）")
async def chat_ask(req: ChatRequest, cache: CacheManager = Depends(get_cache)):
    """通用聊天助手，支持流式响应"""
    cache_key = f"ai:chat:{hashlib.md5(req.question.encode()).hexdigest()}"
    if cached := await cache.get(cache_key):
        # 对于缓存的内容，也返回流式格式
        return StreamingResponse(
            _stream_cached_response(cached),
            media_type="text/plain; charset=utf-8"
        )

    # 构建系统提示词
    system = (
        "你是一位专业的技术助手，专门回答关于这个个人主页的问题。"
        "主页包含技术文章、项目经验和技能介绍。"
        "请用友好、专业的语气回答用户的问题，如果问题超出你的知识范围，请礼貌地说明。"
        "回答要简洁明了，使用Markdown格式增强可读性。"
    )

    try:
        # 使用流式响应
        return StreamingResponse(
            _stream_ai_response(system, req.question),
            media_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        logger.error("AI chat failed: %s", e)
        return StreamingResponse(
            _stream_error_response("AI 服务暂时不可用，请稍后重试"),
            media_type="text/plain; charset=utf-8"
        )


async def _stream_ai_response(system: str, question: str):
    """流式生成AI响应"""
    try:
        # 使用AI提供者生成响应
        response = await _ai.chat(system, question, max_tokens=800)

        # 模拟流式输出（实际生产中应该使用真正的流式API）
        words = response.split()
        buffer = ""

        for word in words:
            buffer += word + " "
            if len(buffer) > 50:  # 每50个字符左右发送一次
                yield f"data: {buffer}\n\n"
                buffer = ""
                # 模拟思考延迟
                import asyncio
                await asyncio.sleep(0.05)

        if buffer:
            yield f"data: {buffer}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: [ERROR]{str(e)}\n\n"


async def _stream_cached_response(cached_content: str):
    """流式输出缓存的内容"""
    words = cached_content.split()
    buffer = ""

    for word in words:
        buffer += word + " "
        if len(buffer) > 50:
            yield f"data: {buffer}\n\n"
            buffer = ""
            import asyncio
            await asyncio.sleep(0.03)  # 缓存内容输出更快

    if buffer:
        yield f"data: {buffer}\n\n"

    yield "data: [DONE]\n\n"


async def _stream_error_response(error_msg: str):
    """流式输出错误信息"""
    yield f"data: [ERROR]{error_msg}\n\n"