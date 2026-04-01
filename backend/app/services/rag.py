"""
RAG 服务 — 简历问答引擎
职责：
  1. 把 profile / articles / projects 向量化存入 ChromaDB
  2. 每次问答：检索最相关 K 条上下文 → 构建 prompt → LangChain 流式输出
  3. 支持增量重建（新文章发布后自动触发）
"""
from __future__ import annotations

import json
import logging
import os
from typing import AsyncIterator

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── 懒加载：避免无 API Key 时启动报错 ────────────────────


def _build_embeddings():
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_API_BASE,
    )


def _build_llm():
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_API_BASE,
        temperature=0.7,
        streaming=True,
    )


def _build_vectorstore(embeddings):
    from chromadb import PersistentClient
    from langchain_community.vectorstores import Chroma

    persist_dir = os.path.abspath(settings.CHROMA_PERSIST_DIR)
    os.makedirs(persist_dir, exist_ok=True)

    return Chroma(
        collection_name="resume_knowledge",
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )


# ── 知识库构建 ────────────────────────────────────────────


def build_documents(profile_data: dict, articles: list[dict], projects: list[dict]) -> list:
    """把结构化数据转换为 LangChain Document 列表"""
    from langchain.schema import Document

    docs: list[Document] = []

    # 1. Profile 基本信息
    resume = {}
    try:
        resume = json.loads(profile_data.get("resume_data") or "{}")
    except Exception:
        pass

    bio_parts = [
        f"姓名：{profile_data.get('full_name', '')}",
        f"职位：{profile_data.get('title', '')}",
        f"简介：{profile_data.get('bio', '')}",
    ]
    if resume.get("skills"):
        skill_str = "、".join(
            s.get("name", "") for s in resume["skills"] if s.get("name")
        )
        bio_parts.append(f"技能：{skill_str}")
    docs.append(
        Document(
            page_content="\n".join(bio_parts),
            metadata={"source": "profile", "type": "bio"},
        )
    )

    # 2. 工作经历
    for exp in resume.get("experience", []):
        content = (
            f"公司：{exp.get('company', '')}\n"
            f"职位：{exp.get('position', '')}\n"
            f"时间：{exp.get('start_date', '')} ~ {exp.get('end_date', '至今')}\n"
            f"描述：{exp.get('description', '')}"
        )
        docs.append(
            Document(
                page_content=content,
                metadata={"source": "experience", "company": exp.get("company", "")},
            )
        )

    # 3. 教育背景
    for edu in resume.get("education", []):
        content = (
            f"学校：{edu.get('school', '')}\n"
            f"专业：{edu.get('major', '')}\n"
            f"学历：{edu.get('degree', '')}\n"
            f"时间：{edu.get('start_date', '')} ~ {edu.get('end_date', '')}"
        )
        docs.append(
            Document(
                page_content=content,
                metadata={"source": "education", "school": edu.get("school", "")},
            )
        )

    # 4. 文章摘要（只用 title + summary + tags，不放全文避免过长）
    for art in articles:
        content = (
            f"文章标题：{art.get('title', '')}\n"
            f"摘要：{art.get('summary', '')}\n"
            f"标签：{art.get('tags', '')}"
        )
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": "article",
                    "article_id": str(art.get("id", "")),
                    "slug": art.get("slug", ""),
                },
            )
        )

    # 5. 项目
    for proj in projects:
        content = (
            f"项目名称：{proj.get('name', '')}\n"
            f"描述：{proj.get('description', '')}\n"
            f"技术栈：{proj.get('tech_stack', '')}\n"
            f"标签：{proj.get('tags', '')}\n"
            f"GitHub：{proj.get('github_url', '')}"
        )
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": "project",
                    "project_id": str(proj.get("id", "")),
                    "name": proj.get("name", ""),
                },
            )
        )

    return docs


async def rebuild_index(profile_data: dict, articles: list[dict], projects: list[dict]) -> int:
    """重建向量索引，返回写入文档数"""
    try:
        embeddings = _build_embeddings()
        vs = _build_vectorstore(embeddings)

        # 清空旧数据
        try:
            vs.delete_collection()
        except Exception:
            pass

        # 重新构建
        from chromadb import PersistentClient
        from langchain_community.vectorstores import Chroma

        persist_dir = os.path.abspath(settings.CHROMA_PERSIST_DIR)
        docs = build_documents(profile_data, articles, projects)
        if not docs:
            return 0

        Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name="resume_knowledge",
            persist_directory=persist_dir,
        )
        logger.info("RAG index rebuilt: %d docs", len(docs))
        return len(docs)
    except Exception as e:
        logger.error("RAG rebuild failed: %s", e)
        raise


# ── 问答流式生成 ──────────────────────────────────────────

SYSTEM_PROMPT_WITH_CONTEXT = """你是一个专业的个人简历问答助手。
你代表简历主人回答访客的问题，语气自然、简洁、专业。
严格基于以下「个人资料上下文」回答，不要编造不存在的信息。
如果问题超出提供的上下文范围，礼貌地说明无法回答。
回答使用中文，控制在 200 字以内。

个人资料上下文：
{context}
"""

SYSTEM_PROMPT_DIRECT = """你是一个专业的个人简历问答助手，代表这个个人主页的博主回答访客的问题。
语气自然、简洁、专业。如果不清楚具体信息，礼貌地引导访客查看主页相关页面。
回答使用中文，控制在 200 字以内。
"""


def _has_vector_index() -> bool:
    """检查 ChromaDB 索引是否已构建"""
    try:
        import chromadb
        persist_dir = os.path.abspath(settings.CHROMA_PERSIST_DIR)
        if not os.path.exists(persist_dir):
            return False
        client = chromadb.PersistentClient(path=persist_dir)
        col = client.get_or_create_collection("resume_knowledge")
        return col.count() > 0
    except Exception:
        return False


async def stream_answer(question: str) -> AsyncIterator[str]:
    """
    流式问答主入口：
    - 有向量索引 → RAG 检索上下文 + LangChain ChatOpenAI 流式输出
    - 无向量索引 → 直接用 LangChain ChatOpenAI 流式输出（降级模式）
    每次 yield 一个 str chunk
    """
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    llm = _build_llm()

    # ── 尝试 RAG 检索上下文 ────────────────────────────────
    context: str | None = None
    if _has_vector_index():
        try:
            embeddings = _build_embeddings()
            vs = _build_vectorstore(embeddings)
            retriever = vs.as_retriever(search_kwargs={"k": 5})
            relevant_docs = retriever.get_relevant_documents(question)
            if relevant_docs:
                context = "\n\n---\n\n".join(d.page_content for d in relevant_docs)
                logger.info("RAG retrieved %d docs for question", len(relevant_docs))
        except Exception as e:
            logger.warning("RAG retrieval failed, falling back to direct mode: %s", e)

    # ── 构建 LangChain Chain ───────────────────────────────
    if context:
        # RAG 模式：注入检索到的上下文
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_WITH_CONTEXT.format(context=context)),
            ("human", "{question}"),
        ])
    else:
        # 直接模式：不依赖向量库，LangChain 直接调用
        logger.info("No vector index found, using direct LangChain mode")
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_DIRECT),
            ("human", "{question}"),
        ])

    chain = prompt | llm | StrOutputParser()

    async for chunk in chain.astream({"question": question}):
        yield chunk
