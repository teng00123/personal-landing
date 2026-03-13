# personal-landing

> 高端个人主页 | 简历展示 + 文章 + GitHub 项目自动部署

## 技术栈

| 层 | 技术 |
|---|---|
| 后端框架 | FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL 8 |
| 缓存 | Redis 7 |
| 异步任务 | Celery 5 |
| 鉴权 | JWT (python-jose) |
| 前端 | Vue 3 + Vite |
| UI | Element Plus |
| Markdown | marked + highlight.js |

## 迭代计划

- **迭代一（当前）** — 项目骨架、后端核心、Docker 环境、前端脚手架
- **迭代二** — 文章系统（上传 .md / 编辑器 / 渲染展示）
- **迭代三** — 项目展示 + Celery 自动部署

## 快速启动

```bash
# 1. 复制环境变量
cp backend/.env.example backend/.env

# 2. 启动所有服务（MySQL / Redis / Backend / Celery / Frontend）
docker-compose up -d

# 3. 初始化数据库 & 默认管理员
docker-compose exec backend python -m app.init_db

# 4. 访问
#   前端主页:  http://localhost:5173
#   后端 API:  http://localhost:8000/docs
```

## 本地开发

```bash
# 后端
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 编辑 .env
alembic upgrade head
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```
