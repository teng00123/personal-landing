# 迭代计划 · Personal Landing

> GitHub: https://github.com/teng00123/personal-landing

---

## 迭代总览

| 迭代 | 主题 | 状态 |
|------|------|------|
| **Iter 1** | 项目骨架 + 后端核心 + 可运行环境 | ✅ 完成 |
| **Iter 2** | 文章系统（上传 .md / 编辑 / 渲染） | 🔜 计划中 |
| **Iter 3** | 项目展示 + Celery 自动部署 | 🔜 计划中 |

---

## Iteration 1 — 项目骨架（已完成）

### 目标
搭建可一键启动的全栈骨架，后端 API 全部通，前端路由全部可访问。

### 交付物
- Docker Compose 一键启动（MySQL 8 / Redis 7 / FastAPI / Celery / Vue 3 Dev Server）
- 后端全套 API（认证、Profile、文章 CRUD、项目 CRUD）
- Alembic 迁移框架
- 前端完整路由体系 + 暗色主题 UI
- 首页简历展示（工作经历时间轴、技能进度条、教育背景）
- 文章列表 + 文章详情（Markdown 渲染，含语法高亮）
- 项目列表（展示部署状态）
- 管理后台骨架（个人资料编辑）

### 技术栈
```
Backend  : Python 3.11 · FastAPI · SQLAlchemy 2.0 · Alembic
Database : MySQL 8.0 · Redis 7
Auth     : JWT (python-jose) · bcrypt
Task     : Celery 5 (broker=Redis)

Frontend : Vue 3 · Vite · Element Plus · Pinia · Vue Router 4
MD       : marked · highlight.js · DOMPurify
```

### 快速启动
```bash
# 1. 复制环境变量
cp backend/.env.example backend/.env

# 2. 启动所有服务
docker compose up -d

# 3. 初始化数据库 & 创建管理员
docker compose exec backend python -m app.init_db

# 4. 访问
#    主页：http://localhost:5173
#    API文档：http://localhost:8000/docs
#    后台：http://localhost:5173/login  (admin / Admin@123456)
```

---

## Iteration 2 — 文章系统（计划）

### 目标
管理员可通过后台上传 / 编辑 Markdown 文章，访客可浏览并阅读渲染效果。

### 计划功能
- [ ] 后台文章列表：可搜索、分页、切换发布状态
- [ ] 上传 `.md` 文件（自动提取 `# 标题`、生成 slug）
- [ ] 在线 Markdown 编辑器（基于 CodeMirror 或 textarea + 实时预览）
- [ ] 封面图上传（multipart/form-data → OSS 或本地 /uploads）
- [ ] 标签管理（逗号分隔，支持筛选）
- [ ] 草稿 / 发布状态切换
- [ ] 文章阅读量统计

### API 扩展
```
POST /api/v1/articles/upload-md   上传 .md 文件，返回解析后草稿
POST /api/v1/articles/{id}/cover  上传封面图
```

---

## Iteration 3 — 项目自动部署（计划）

### 目标
管理员输入 GitHub 仓库 URL，系统自动 clone、识别框架、安装依赖、启动服务，访客可直接通过独立端口访问已部署的项目。

### 计划功能
- [ ] 后台项目管理：录入 GitHub URL、branch、自定义命令
- [ ] Celery Task：`deploy_project` 全流程
  - git clone / git pull
  - 框架自动识别（Vue/React/Next.js/Node/FastAPI/Flask/Django/Static/Docker）
  - 安装依赖（npm install / pip install）
  - 构建（npm run build）
  - 端口分配（8100~9000 自动扫描空闲端口）
  - 进程启动（serve / uvicorn / flask / gunicorn）
- [ ] 部署日志实时回显（SSE 或轮询 `/projects/{id}/logs`）
- [ ] 部署状态：pending → deploying → running / failed
- [ ] 停止 / 重新部署操作
- [ ] 前端项目卡片展示：运行状态绿点 + "访问" 按钮

### 支持框架矩阵
| 框架 | 识别特征 | 运行方式 |
|------|----------|----------|
| Vue/React | `package.json` + build script | `npm run build` → `serve -s dist` |
| Next.js | `next` in deps | `npm run build` → `npm start` |
| Node.js | `package.json` (no build) | `node index.js` / `npm start` |
| FastAPI | `main.py` + `fastapi` in requirements | `uvicorn main:app` |
| Flask | `app.py` + `flask` in requirements | `flask run` |
| Django | `manage.py` | `python manage.py runserver` |
| Static | `index.html` only | `serve .` |
| Docker | `Dockerfile` | `docker build + run` |
