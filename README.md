# 🚀 Personal Landing

<div align="center">

**全栈个人主页 / 作品集平台**

**[🇺🇸 English](README_EN.md)** | **[🇨🇳 中文](README.md)**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org)
[![Vite](https://img.shields.io/badge/Vite-5.x-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/teng00123/personal-landing)](https://github.com/teng00123/personal-landing/releases)

</div>

---

## 📋 项目概述

Personal Landing 是一个**企业级全栈个人主页/作品集平台**，从零到生产经历 8+ 次迭代，涵盖：

- 🎨 现代化 Vue 3 前端（主题切换、全文搜索、实时通知、PWA）
- ⚡ 高性能 FastAPI 后端（Redis 缓存、Prometheus 监控、异步任务）
- 🔐 完整安全体系（**TOTP MFA 双因子认证**、RBAC、速率限制、审计日志）
- 🤖 AI 功能（智能对话助手 + 错误降级、**真实代码沙箱**）
- 🚀 DevOps 全套（CI/CD、蓝绿部署、Terraform、Kubernetes、Ansible）

---

## ✨ 最新亮点

| 功能 | 说明 | 版本 |
|------|------|------|
| 🔐 **TOTP MFA** | 双因子认证，TOTP 二步验证，扫码绑定 Google Authenticator | v0.8.1 |
| 🖥️ **代码沙箱真实执行** | Python / Node / Bash 本地沙箱，resource 限制 CPU/内存，无 Docker 时自动降级 | v0.8.2 |
| 🤖 **VisitorChat 错误处理** | 区分网络/OpenAI 不可用/通用错误，降级提示 + 一键重试 | v0.8.3 |
| ⚙️ **Admin Playground 快捷入口** | 管理员后台侧边栏直达代码运行页面 | v0.8.4 |

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 · Vite 5 · Element Plus · Pinia · Vue Router · Vue I18n · Monaco Editor |
| **后端** | Python 3.11 · FastAPI · SQLAlchemy · Alembic · Celery · PyJWT · pyotp |
| **存储** | MySQL 8.0 · Redis 7 |
| **监控** | Prometheus · Grafana · Alertmanager · node_exporter · redis_exporter |
| **安全** | bcrypt · **TOTP MFA** · RBAC · 滑动窗口限流 · OWASP ZAP |
| **DevOps** | Docker · GitHub Actions · Terraform · Ansible · Kubernetes · Nginx |

---

## ✨ 功能一览

### 核心功能
| 功能 | 说明 |
|------|------|
| 👤 个人简历展示 | 在线简历、技能、工作经历 |
| 📝 文章管理 | Markdown 上传/编辑/发布，自动提取标题标签 |
| 🚀 项目部署 | GitHub 一键导入，支持 Vue/React/FastAPI/Flask/Django/Docker |
| 📊 实时日志 | WebSocket 推送部署过程日志 |
| 🌍 国际化 | 中/英双语，前后端全覆盖 |

### 进阶功能（Iter 5-8+）
| 功能 | 说明 |
|------|------|
| 🌙 主题系统 | Dark / Light / Auto 三模式，跟随系统偏好 |
| 🔍 全文搜索 | ⌘K 唤起，280ms 防抖，关键词高亮 |
| 🔔 实时通知 | WebSocket 自动重连，部署/系统事件推送 |
| 💬 社交功能 | 文章点赞（IP 去重）、嵌套评论、XSS 过滤 |
| 🤖 AI 助手 | 智能对话，上下文感知，**错误降级 + 重试** |
| 🖥️ 代码沙箱 | Monaco Editor，Python/Node/Bash **真实执行**，resource 限制 |
| 🔐 **MFA 双因子认证** | **TOTP + QR 码扫描，5 分钟 challenge token** |
| 📈 Prometheus 监控 | 8 面板 Grafana 大盘，7 条告警规则 |

---

## ⚡ 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- MySQL 8.0+
- Redis 7+
- Docker & Docker Compose（推荐）

### 🐳 Docker 一键启动（推荐）

```bash
git clone https://github.com/teng00123/personal-landing.git
cd personal-landing

# 复制并配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，填写 SECRET_KEY、数据库密码等

docker compose up -d
```

服务启动后：
| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

**默认管理员账号：**
```
用户名：admin
密码：  admin123
```

### 🔧 本地开发

```bash
# 1. 后端
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 编辑 .env 填写配置

# 2. 数据库初始化（自动创建表 + 管理员账号）
python -m app.init_db           # 仅初始化
python -m app.init_db --seed    # 初始化 + 示例文章/项目

# 3. 数据库迁移（如有新字段）
alembic upgrade head

# 4. 启动后端
uvicorn app.main:app --reload --port 8000

# 5. 前端（新终端）
cd frontend
npm install
npm run dev
```

**默认管理员账号：**
- 用户名：`admin`
- 密码：`admin123`

> 首次登录后，建议立即在「个人资料 → 账号安全」中**启用 MFA** 双因子认证。

### 📊 启动监控栈

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

| 服务 | 地址 | 默认账号 |
|------|------|----------|
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | — |
| Alertmanager | http://localhost:9093 | — |

---

## 🗂️ 项目结构

```
personal-landing/
├── frontend/                  # Vue 3 前端
│   ├── src/
│   │   ├── api/               # HTTP 客户端
│   │   ├── components/        # 公共组件（MFASetup、VisitorChat、CodePlayground）
│   │   ├── composables/       # Vue Composables
│   │   ├── layouts/           # 布局组件
│   │   ├── locales/           # i18n 语言包
│   │   ├── router/            # 路由配置
│   │   ├── store/             # Pinia 状态管理
│   │   └── views/             # 页面视图
│   └── vite.config.js
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── api/               # 路由处理器（auth.py 含 MFA 路由）
│   │   ├── core/              # 配置、安全（TOTP token）、依赖
│   │   ├── db/                # 数据库 & 模型
│   │   ├── tasks/             # Celery 任务
│   │   ├── utils/             # 工具类（缓存/监控/日志/安全/MFA）
│   │   ├── init_db.py         # ✨ 数据库初始化脚本
│   │   └── main.py
│   ├── alembic/               # 数据库迁移
│   └── requirements.txt
├── infra/                     # 基础设施即代码
│   ├── terraform/             # AWS EC2 + SG + EIP
│   ├── ansible/               # 服务器配置管理
│   └── k8s/                   # Kubernetes 清单
├── monitoring/                # 监控配置
│   ├── prometheus/            # 抓取配置 + 告警规则
│   ├── alertmanager/          # 告警路由
│   └── grafana/               # 数据源 + 仪表盘
├── nginx/                     # Nginx 生产配置
├── scripts/                   # 运维脚本（备份/健康检查）
├── docker-compose.yml         # 开发环境
├── docker-compose.staging.yml # 预发布环境
├── docker-compose.prod.yml    # 生产环境
└── docker-compose.monitoring.yml
```

---

## 🚢 部署

### 预发布环境

```bash
docker compose -f docker-compose.staging.yml up -d
```

### 生产环境（蓝绿部署）

推送 `v*.*.*` 标签自动触发 GitHub Actions 蓝绿部署流水线：

```bash
git tag v1.0.0 && git push origin v1.0.0
```

流程：新槽启动 → 健康检查（12×5s）→ Nginx 热切换 → 旧槽停止

### Kubernetes

```bash
kubectl apply -k infra/k8s/overlays/production
```

配置了 HPA（CPU 70% / 内存 80%），自动扩缩 2-10 副本。

---

## 💻 开发指南

### 代码规范

```bash
# 后端 lint
cd backend && ruff check . && ruff format .

# 后端类型检查
mypy app/

# 前端 lint
cd frontend && npm run lint
```

### 数据库迁移

```bash
cd backend

# 生成迁移
alembic revision --autogenerate -m "描述变更"

# 执行迁移
alembic upgrade head

# 回滚一步
alembic downgrade -1
```

### 初始化数据库

```bash
cd backend

# 基础初始化：创建表 + 管理员账号
python -m app.init_db

# 包含示例数据：文章 + 项目
python -m app.init_db --seed

# 危险：重置所有表（删除后重建）
python -m app.init_db --reset
```

**init_db 功能：**
1. 等待 MySQL 就绪（自动重试）
2. 自动创建数据库（如不存在）
3. 创建所有表（idempotent，已存在则跳过）
4. 创建管理员账号（配置来自 `.env`）
5. 可选：写入 3 篇示例文章 + 1 个示例项目

### 测试

```bash
# 后端
cd backend && pytest tests/ -v --cov=app

# 前端
cd frontend && npm run test
```

### Celery 任务队列

```bash
# Worker
celery -A app.tasks.celery_app:celery_app worker --loglevel=info --pool=solo

# Beat（定时任务）
celery -A app.tasks.celery_app:celery_app beat --loglevel=info

# Flower 监控面板
celery -A app.tasks.celery_app:celery_app flower
```

---

## 🔧 故障排除

| 问题 | 原因 | 解决 |
|------|------|------|
| `Unknown system variable 'query_cache_type'` | MySQL 8.0 已移除该变量 | 升级到最新版本，已修复 |
| `monacoEditorPlugin is not a function` | CJS/ESM 导出兼容问题 | 已修复，使用 `.default ||` 兼容 |
| `npm install` 404 `@monaco-editor/vite-plugin` | 包名错误 | 正确包名为 `vite-plugin-monaco-editor` |
| 前端 `Unexpected "type"` | JS 文件含 TypeScript 语法 | 已移除 TS 类型标注 |
| 数据库连接超时 | 连接池耗尽 | 调整 `pool_size` / `max_overflow` |
| **Alembic `Multiple head revisions`** | 迁移链路不连续 | 检查 `down_revision`，确保线性链路 |
| **MFA 验证码始终错误** | 手机时间不同步 | 确保设备时间与服务器误差 < 30s |

更多问题请提交 [Issue](https://github.com/teng00123/personal-landing/issues)。

---

## 🔐 安全特性

| 特性 | 说明 |
|------|------|
| **TOTP MFA** | RFC 6238 双因子认证，5 分钟 challenge token，防暴力破解 |
| bcrypt | 密码哈希，成本因子 12 |
| JWT | 签名 Token，可配置过期时间 |
| RBAC | 基于角色的访问控制 |
| 速率限制 | 滑动窗口算法，防 DDoS |
| OWASP ZAP | CI 自动扫描 SQL 注入 / XSS |
| Trivy | Docker 镜像漏洞扫描 |
| Bandit | Python 代码安全审计 |

---

## 🤝 贡献指南

1. Fork 本项目
2. 创建功能分支：`git checkout -b feat/新功能`
3. 提交（遵循 [Conventional Commits](https://conventionalcommits.org/)）：`git commit -m 'feat: 添加新功能'`
4. 推送：`git push origin feat/新功能`
5. 创建 Pull Request

所有 PR 需通过 CI（Ruff · Bandit · Trivy · OWASP ZAP）。

---

## 📄 许可证

MIT © [teng00123](https://github.com/teng00123)

---

<div align="center">

⭐ 如果这个项目对你有帮助，欢迎 Star！

</div>
