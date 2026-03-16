# 🚀 Personal Landing - 全栈个人主页/作品集应用

<div align="center">

**[🇺🇸 English Version](README_EN.md)** | **[🇨🇳 中文版本](README.md)**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Vue](https://img.shields.io/badge/Vue-3.x-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

---

## 📋 项目概述

一个现代化的全栈个人主页/作品集应用，集成了简历展示、博客管理和项目部署功能。

### 🛠️ 技术栈

| 组件 | 技术选型 |
|------|----------|
| **后端** | Python 3.11+ + FastAPI + SQLAlchemy + MySQL + Redis + Celery |
| **前端** | Vue 3 + Vite + Element Plus |
| **部署** | Docker + Docker Compose |
| **任务队列** | Celery + Redis |

### ✨ 核心功能

- 📄 **简历展示** - 在线简历和个人介绍
- 📝 **Markdown文章管理** - 支持上传、编辑、发布
- 🚀 **GitHub项目自动部署** - 一键部署多种框架项目
- 📊 **实时日志查看** - 部署过程透明化
- 🔐 **JWT身份认证** - 安全的用户管理系统

---

## ⚡ 快速开始

### 📦 环境要求

- Python 3.11+
- Node.js 20+
- MySQL 8.0+
- Redis 7+
- Docker & Docker Compose

### 🔧 安装步骤

#### 1️⃣ 克隆项目
```bash
git clone https://github.com/teng00123/personal-landing.git
cd personal-landing
```

#### 2️⃣ 后端设置
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息
```

#### 3️⃣ 前端设置
```bash
cd frontend
npm install
cp .env.example .env
```

#### 4️⃣ 启动服务

**🐳 Docker方式（推荐）**
```bash
docker compose up -d
```

**🔧 手动方式**
```bash
# 后端服务
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端服务
cd frontend
npm run dev

# 确保 MySQL 和 Redis 正在运行
```

### 📚 API文档

启动后访问以下地址：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎯 主要功能详解

### 🔐 用户认证系统
- ✅ JWT Token 认证机制
- 👑 管理员权限精细控制
- 🔒 密码加密存储 (bcrypt + SHA-256 pre-hash)

### 📝 文章管理系统
- 📤 Markdown 文件上传
- 🏷️ 自动提取标题和标签
- 📅 发布状态管理
- 📈 阅读统计分析

### 🚀 项目部署系统
- 🔗 GitHub 项目导入
- ⚡ 自动部署（支持多种框架）
- 📋 实时日志查看
- 🎲 端口自动分配 (8100-9000)

**支持的部署框架：**
- Vue/React/Next.js 项目构建
- FastAPI/Flask/Django 项目部署
- 静态网站托管
- Docker 容器部署

---

## ⚙️ Celery 任务队列

### 🐳 Docker 方式（推荐）
```bash
# 启动 Celery Worker（处理部署任务）
docker-compose up -d celery

# 查看 Celery 日志
docker-compose logs -f celery

# 启动 Celery Beat（定时任务）
docker-compose up -d celery-beat
```

### 💻 本地开发方式
```bash
cd backend

# 启动 Celery Worker
celery -A app.tasks.celery_app:celery_app worker --loglevel=info --pool=solo

# 启动 Celery Beat（定时任务）
celery -A app.tasks.celery_app:celery_app beat --loglevel=info

# 监控任务状态（Flower）
celery -A app.tasks.celery_app:celery_app flower
```

### 🔧 常用 Celery 命令
```bash
# 查看活跃任务
celery -A app.tasks.celery_app:celery_app inspect active

# 查看注册任务
celery -A app.tasks.celery_app:celery_app inspect registered

# 清空任务队列
celery -A app.tasks.celery_app:celery_app purge
```

---

## 💻 开发指南

### 📏 代码规范
- 📝 使用 [Conventional Commits](https://conventionalcommits.org/) 提交规范
- 🐍 后端: ruff 格式化 + mypy 类型检查
- ⚡ 前端: ESLint + Prettier
- ✅ 所有 PR 必须通过 CI 检查

### 🧪 测试
```bash
# 后端测试
cd backend
pytest tests/ -v

# 前端测试
cd frontend
npm run test
```

### 🗄️ 数据库迁移
```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head
```

---

## 🚢 部署

### 🐳 Docker 部署
```bash
docker compose up -d
```

### 🏭 生产环境配置
- 🌐 使用 Nginx 反向代理
- 🔐 配置 SSL 证书
- 🛡️ 设置防火墙规则
- 💾 定期备份数据库

---

## 🔧 故障排除

常见问题及解决方案请参考本文件或提交 Issue。

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. 🍴 Fork 本项目
2. 🌿 创建功能分支 (`git checkout -b feat/新功能`)
3. ✨ 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 📤 推送分支 (`git push origin feat/新功能`)
5. 🔄 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👤 联系方式

- **作者**: teng00123
- **GitHub**: [@teng00123](https://github.com/teng00123)
- **邮箱**: teng00123@github.com

---

<div align="center">

⭐ 如果这个项目对您有帮助，请给它一个星标！

</div>