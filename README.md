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

## Celery 任务队列启动说明

### Docker 方式（推荐）
```bash
# 启动 Celery Worker（处理部署任务）
docker-compose up -d celery

# 查看 Celery 日志
docker-compose logs -f celery

# 启动 Celery Beat（定时任务，如果需要）
docker-compose up -d celery-beat
```

### 本地开发方式
```bash
# 进入后端目录
cd backend

# 启动 Celery Worker
celery -A app.tasks.celery_app:celery_app worker --loglevel=info --pool=solo

# 启动 Celery Beat（定时任务）
celery -A app.tasks.celery_app:celery_app beat --loglevel=info

# 监控任务状态（Flower）
celery -A app.tasks.celery_app:celery_app flower
```

### Celery 任务类型
- **项目部署**: 自动克隆 GitHub 项目并部署
- **支持框架**: Vue/React/Next.js/Node/FastAPI/Flask/Django/Static/Docker
- **端口分配**: 自动扫描 8100-9000 端口范围
- **日志查看**: 通过 API `/projects/{id}/logs` 实时查看部署日志

### 常用 Celery 命令
```bash
# 查看活跃任务
celery -A app.tasks.celery_app:celery_app inspect active

# 查看注册任务
celery -A app.tasks.celery_app:celery_app inspect registered

# 清空任务队列
celery -A app.tasks.celery_app:celery_app purge
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
