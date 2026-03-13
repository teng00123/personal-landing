# 迭代计划 · Personal Landing

> GitHub: https://github.com/teng00123/personal-landing

---

## 迭代总览

| 迭代 | 主题 | 状态 |
|------|------|------|
| **Iter 1** | 项目骨架 + 后端核心 + 可运行环境 | ✅ 完成 |
| **Iter 2** | 文章系统（上传 .md / 编辑器 / 渲染） | ✅ 完成 |
| **Iter 3** | 项目展示 + Celery 自动部署 | ✅ 完成 |

---

## Iteration 1 — 项目骨架（已完成）

### 交付物
- Docker Compose 一键启动（MySQL 8 / Redis 7 / FastAPI / Celery / Vue 3）
- 后端全套 API（认证、Profile、文章 CRUD、项目 CRUD）
- Alembic 迁移框架 + `init_db.py`
- 前端完整路由 + 暗色主题 UI
- 首页简历（工作经历时间轴、技能进度条、教育背景）
- 文章列表 + 详情（Markdown 渲染 + 语法高亮）
- 管理后台骨架

---

## Iteration 2 — 文章系统（已完成）

### 新增接口
| 接口 | 说明 |
|------|------|
| `POST /api/v1/articles/upload-md` | 上传 `.md`，自动解析标题/摘要/标签，存为草稿 |
| `POST /api/v1/articles/{id}/cover` | 上传封面图（JPEG/PNG/WebP ≤5MB） |

### 新增前端
- **ArticleManager** — 搜索/筛选/上传 .md/发布 Switch/编辑/删除
- **ArticleEditor** — 左右分栏编辑器（Markdown + 实时预览 + 工具栏 + 封面上传）

---

## Iteration 3 — 项目自动部署（已完成）

### 新增接口
| 接口 | 说明 |
|------|------|
| `POST /api/v1/projects` | 创建项目，自动触发 Celery 部署 |
| `POST /api/v1/projects/{id}/deploy` | 手动触发部署 |
| `POST /api/v1/projects/{id}/redeploy` | 停止后重新部署 |
| `POST /api/v1/projects/{id}/stop` | 停止运行中的项目 |
| `GET  /api/v1/projects/{id}/logs` | 增量获取部署日志（offset 参数支持轮询） |
| `POST /api/v1/projects/{id}/cover` | 上传项目封面图 |

### Celery Task：`deploy_project`
```
git clone / pull
    ↓
框架自动识别
    ↓
安装依赖（npm install / pip install）
    ↓
构建（npm run build）
    ↓
端口分配（8100~9000 自动扫描）
    ↓
后台启动进程（独立进程组）
    ↓
更新 deploy_status = running，写入 deploy_url
```

### 支持框架
| 框架 | 识别方式 | 启动方式 |
|------|----------|----------|
| Vue / React | `package.json` + build script | `serve -s dist -l {PORT}` |
| Next.js | `next` in package.json | `PORT={PORT} npm start` |
| Node.js | `package.json`（无 build） | `node index.js` |
| FastAPI | `requirements.txt` + fastapi | `uvicorn main:app --port {PORT}` |
| Flask | `requirements.txt` + flask | `flask run --port {PORT}` |
| Django | `manage.py` | `python manage.py runserver 0.0.0.0:{PORT}` |
| Static | `index.html` only | `serve -s . -l {PORT}` |
| Docker | `Dockerfile` | `docker build + run -p {PORT}` |

### 新增前端
- **ProjectManager** — 卡片 grid，实时部署状态，操作按钮（部署/重部署/停止/删除）
- **日志 Drawer** — 部署日志实时滚动，2s 增量轮询，自动停止
- **ProjectsView（公开）** — 运行状态绿点 + "🚀 访问" 按钮，自动轮询部署中的项目

### 快速启动
```bash
git clone https://github.com/teng00123/personal-landing.git
cd personal-landing
cp backend/.env.example backend/.env
docker compose up -d
docker compose exec backend python -m app.init_db

# 主页:    http://localhost:5173
# 后台:    http://localhost:5173/login   admin / Admin@123456
# API 文档: http://localhost:8000/docs
```
