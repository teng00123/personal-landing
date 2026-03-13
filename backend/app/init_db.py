"""
init_db.py — 数据库初始化
功能：
  1. 等待 MySQL 就绪
  2. 自动创建数据库（如不存在）
  3. CREATE TABLE（idempotent，已存在则跳过）
  4. 创建 admin 账号（已存在则跳过）
  5. 写入示例文章 & 项目（--seed 或 SEED_DEMO=1 时）

用法：
  python -m app.init_db            # 建表 + admin，不写示例数据
  python -m app.init_db --seed     # 建表 + admin + 示例数据
  python -m app.init_db --reset    # ⚠️  删除所有表后重建（危险！）
"""
import json
import sys
from datetime import datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.db.session import engine, Base
from app.models import User, Article, Project  # noqa — 注册模型到 metadata
from app.core.security import hash_password
from app.core.config import settings


# ── 示例数据 ───────────────────────────────────────────────

SAMPLE_RESUME = json.dumps({
    "experience": [
        {
            "company": "示例科技有限公司",
            "title": "高级全栈工程师",
            "start": "2022-01",
            "end": "",
            "description": "负责核心交易系统架构设计与性能优化，QPS 提升 300%，主导微服务改造。",
            "skills": "Python,FastAPI,Vue3,MySQL,Redis,Celery"
        },
        {
            "company": "前一家公司",
            "title": "后端工程师",
            "start": "2020-06",
            "end": "2021-12",
            "description": "参与微服务拆分，维护 CI/CD 流水线，改善部署效率 50%。",
            "skills": "Go,Docker,Kubernetes,gRPC"
        }
    ],
    "education": [
        {
            "school": "某某大学",
            "degree": "本科",
            "major": "计算机科学与技术",
            "start": "2016-09",
            "end": "2020-06"
        }
    ],
    "skills": [
        {
            "category": "后端",
            "items": [
                {"name": "Python / FastAPI", "level": 95},
                {"name": "Go",              "level": 75},
                {"name": "MySQL / Redis",   "level": 90}
            ]
        },
        {
            "category": "前端",
            "items": [
                {"name": "Vue 3 / Vite",   "level": 82},
                {"name": "TypeScript",     "level": 72}
            ]
        },
        {
            "category": "运维 / 基础设施",
            "items": [
                {"name": "Docker / K8s",   "level": 84},
                {"name": "Linux / Bash",   "level": 88},
                {"name": "Celery / MQ",    "level": 80}
            ]
        }
    ],
    "certifications": []
}, ensure_ascii=False)

SAMPLE_ARTICLES = [
    {
        "title": "用 FastAPI + Celery 实现 GitHub 项目自动部署",
        "slug": "fastapi-celery-auto-deploy",
        "summary": "本文介绍如何通过 Celery 异步任务队列实现 GitHub 项目的全自动 clone、构建、部署流程，支持 Vue/React/Next.js/FastAPI 等主流框架。",
        "content": """# 用 FastAPI + Celery 实现 GitHub 项目自动部署

## 背景

每次手动 `git pull && npm run build && pm2 restart` 太繁琐？本文带你用 **Celery** 实现一键自动部署。

## 架构概览

```
前端触发 → FastAPI 接收请求 → Celery Task 异步执行
                                   ↓
                          git clone / pull
                                   ↓
                          框架识别（package.json / requirements.txt）
                                   ↓
                          安装依赖 + 构建
                                   ↓
                          端口分配 + 后台启动进程
```

## 框架识别逻辑

```python
def detect_framework(proj_dir: Path) -> str:
    if (proj_dir / "Dockerfile").exists():
        return "docker"
    pkg = proj_dir / "package.json"
    if pkg.exists():
        content = pkg.read_text()
        if "next" in content:
            return "nextjs"
        if '"build"' in content:
            return "vue-react"
        return "nodejs"
    req = proj_dir / "requirements.txt"
    if req.exists():
        content = req.read_text().lower()
        if "fastapi" in content:
            return "fastapi"
        if "flask" in content:
            return "flask"
    return "static"
```

## 端口自动分配

```python
def find_free_port(start=8100, end=9000) -> int:
    for port in range(start, end):
        with socket.socket() as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise RuntimeError("没有可用端口")
```

## 增量日志

部署日志实时追加到数据库，前端通过 `?offset=N` 实现增量轮询，避免重复传输大日志。

## 总结

整套方案无需 Jenkins/GitHub Actions，纯 Python 实现，适合个人项目和小团队快速部署。
""",
        "tags": "Python,FastAPI,Celery,DevOps,部署",
        "is_published": True,
    },
    {
        "title": "Vue 3 + Element Plus 打造暗色主题个人主页",
        "slug": "vue3-dark-theme-portfolio",
        "summary": "从零搭建一个支持暗色主题、Markdown 渲染、实时预览的个人技术主页，包含简历展示、文章系统和项目管理。",
        "content": """# Vue 3 + Element Plus 打造暗色主题个人主页

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端框架 | Vue 3 + Vite |
| UI 组件库 | Element Plus |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| Markdown | marked + highlight.js + DOMPurify |

## CSS 变量暗色主题

```css
:root {
  --bg-primary:   #0f172a;
  --bg-card:      #1e293b;
  --text-primary: #f1f5f9;
  --text-muted:   #64748b;
  --accent:       #60a5fa;
  --success:      #10b981;
}
```

## Markdown 实时预览

```js
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'

marked.use(markedHighlight({
  highlight(code, lang) {
    const l = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language: l }).value
  }
}))

const previewHtml = computed(() =>
  DOMPurify.sanitize(marked.parse(form.value.content))
)
```

## 分栏编辑器

左栏 Markdown 编辑，右栏实时预览，工具栏支持加粗、斜体、代码块、链接等快捷插入。

```
┌─────────────────┬─────────────────┐
│  ✏️ Markdown 编辑  │   👁 实时预览     │
│                 │                 │
│  # 标题          │  <h1>标题</h1>  │
│  **加粗**        │  <strong>加粗</strong> │
└─────────────────┴─────────────────┘
```

## 总结

整套方案开箱即用，配合后端 FastAPI 接口，支持 .md 文件上传、封面图管理、发布控制。
""",
        "tags": "Vue3,前端,Element Plus,暗色主题",
        "is_published": True,
    },
    {
        "title": "SQLAlchemy 2.0 + Alembic 数据库迁移最佳实践",
        "slug": "sqlalchemy2-alembic-migration",
        "summary": "介绍 SQLAlchemy 2.0 新风格（DeclarativeBase）与 Alembic 迁移工作流，以及在 Docker 环境中自动执行迁移的实践。",
        "content": """# SQLAlchemy 2.0 + Alembic 数据库迁移最佳实践

## SQLAlchemy 2.0 新风格

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id:       Mapped[int]  = mapped_column(primary_key=True)
    username: Mapped[str]  = mapped_column(String(64), unique=True)
    email:    Mapped[str]  = mapped_column(String(256), unique=True)
```

## Alembic 工作流

```bash
# 初始化
alembic init alembic

# 生成迁移
alembic revision --autogenerate -m "add users table"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## Docker 自动迁移

在 `docker-compose.yml` 中为 backend 服务配置启动命令：

```yaml
command: >
  sh -c "python -m app.wait_for_db &&
         alembic upgrade head &&
         python -m app.init_db &&
         uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

## 生产环境注意事项

1. 迁移脚本纳入版本控制
2. 每次部署前备份数据库
3. 避免在同一迁移中同时 DROP 和 ADD 列（分两步）
4. 使用 `--autogenerate` 后务必人工 review 生成的脚本
""",
        "tags": "Python,SQLAlchemy,Alembic,数据库",
        "is_published": False,  # 草稿
    },
]

SAMPLE_PROJECTS = [
    {
        "name": "Personal Landing",
        "description": "本项目——基于 FastAPI + Vue 3 的个人主页，含博客、简历展示和 GitHub 项目自动部署。",
        "github_url": "https://github.com/teng00123/personal-landing",
        "github_repo": "teng00123/personal-landing",
        "tech_stack": "FastAPI,Vue3,MySQL,Redis,Celery,Docker",
        "deploy_branch": "main",
        "deploy_status": "pending",
        "is_published": True,
        "sort_order": 0,
    },
]


# ── 数据库自动创建 ──────────────────────────────────────────

def ensure_database_exists():
    """连接到 MySQL server（不指定库名），自动创建数据库（若不存在）"""
    # 去掉 URL 中的数据库名，连接到 server 级别
    server_url = (
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}?charset=utf8mb4"
    )
    server_engine = create_engine(server_url, pool_pre_ping=True)
    db_name = settings.DB_NAME
    try:
        with server_engine.connect() as conn:
            conn.execute(text(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            ))
            conn.commit()
        print(f"  ✓ 数据库 `{db_name}` 已就绪")
    except Exception as e:
        print(f"  ⚠️  自动建库失败（可能权限不足，请手动创建）: {e}")
    finally:
        server_engine.dispose()


# ── 建表 ───────────────────────────────────────────────────

def create_tables(reset: bool = False):
    if reset:
        print("  ⚠️  --reset 模式：删除所有表...")
        Base.metadata.drop_all(bind=engine)
        print("  ✓ 所有表已删除")
    print("▶ 创建数据库表（已存在则跳过）...")
    Base.metadata.create_all(bind=engine)
    tables = list(Base.metadata.tables.keys())
    print(f"  ✓ 表已就绪: {', '.join(tables)}")


# ── 管理员账号 ─────────────────────────────────────────────

def create_admin(db: Session) -> User:
    existing = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
    if existing:
        print(f"  ℹ  管理员 '{settings.ADMIN_USERNAME}' 已存在，跳过")
        return existing

    admin = User(
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
        is_admin=True,
        full_name="Your Name",
        title="Senior Full Stack Engineer",
        bio="热爱技术，专注于构建高性能、高可用的软件系统。\n喜欢开源，持续学习。",
        location="深圳，中国",
        github_url="https://github.com/teng00123",
        resume_data=SAMPLE_RESUME,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"  ✓ 管理员已创建：{settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}")
    return admin


# ── 示例数据 ───────────────────────────────────────────────

def seed_articles(db: Session, admin: User):
    for data in SAMPLE_ARTICLES:
        exists = db.query(Article).filter(Article.slug == data["slug"]).first()
        if exists:
            print(f"  ℹ  文章 '{data['slug']}' 已存在，跳过")
            continue
        article = Article(
            **data,
            author_id=admin.id,
            published_at=datetime.now(timezone.utc) if data["is_published"] else None,
        )
        db.add(article)
    db.commit()
    count = len(SAMPLE_ARTICLES)
    print(f"  ✓ 写入示例文章 {count} 篇")


def seed_projects(db: Session, admin: User):
    for data in SAMPLE_PROJECTS:
        exists = db.query(Project).filter(Project.github_url == data["github_url"]).first()
        if exists:
            print(f"  ℹ  项目 '{data['name']}' 已存在，跳过")
            continue
        project = Project(**data, owner_id=admin.id)
        db.add(project)
    db.commit()
    count = len(SAMPLE_PROJECTS)
    print(f"  ✓ 写入示例项目 {count} 个")


# ── 主流程 ─────────────────────────────────────────────────

def init(seed: bool = False, reset: bool = False):
    print("=" * 50)
    print("  personal-landing · 数据库初始化")
    print("=" * 50)

    # 1. 等待 DB 就绪
    from app.wait_for_db import wait
    wait()

    # 2. 自动建库
    print("▶ 检查数据库...")
    ensure_database_exists()

    # 3. 建表
    create_tables(reset=reset)

    # 4. 管理员账号
    print("▶ 初始化管理员账号...")
    with Session(engine) as db:
        admin = create_admin(db)

        # 5. 示例数据（可选）
        if seed:
            print("▶ 写入示例数据...")
            seed_articles(db, admin)
            seed_projects(db, admin)

    print()
    print("✅ 初始化完成！")
    print()
    print("  访问地址：")
    print("    主页     http://localhost:5173")
    print("    后台     http://localhost:5173/login")
    print("    API 文档  http://localhost:8000/docs")
    print()
    print(f"  管理员账号：{settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}")
    print("=" * 50)


if __name__ == "__main__":
    _seed  = "--seed"  in sys.argv
    _reset = "--reset" in sys.argv

    if _reset:
        confirm = input("⚠️  --reset 将删除所有数据，确认请输入 yes: ").strip()
        if confirm != "yes":
            print("已取消")
            sys.exit(0)

    init(seed=_seed, reset=_reset)
