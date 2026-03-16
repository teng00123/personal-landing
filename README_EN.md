# 🚀 Personal Landing

<div align="center">

**Full Stack Personal Homepage / Portfolio Platform**

**[🇨🇳 中文](README.md)** | **[🇺🇸 English](README_EN.md)**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org)
[![Vite](https://img.shields.io/badge/Vite-5.x-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/teng00123/personal-landing)](https://github.com/teng00123/personal-landing/releases)

</div>

---

## 📋 Project Overview

Personal Landing is an **enterprise-grade full-stack personal homepage/portfolio platform** built through 8 iterative development cycles, featuring:

- 🎨 Modern Vue 3 frontend (theme switching, full-text search, real-time notifications, PWA)
- ⚡ High-performance FastAPI backend (Redis caching, Prometheus monitoring, async tasks)
- 🔐 Comprehensive security (MFA, RBAC, rate limiting, audit logging)
- 🤖 AI features (intelligent chat assistant, code execution sandbox)
- 🚀 Full DevOps stack (CI/CD, blue-green deployment, Terraform, Kubernetes, Ansible)

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Vue 3 · Vite 5 · Element Plus · Pinia · Vue Router · Vue I18n · Monaco Editor |
| **Backend** | Python 3.11 · FastAPI · SQLAlchemy · Alembic · Celery · PyJWT |
| **Storage** | MySQL 8.0 · Redis 7 |
| **Monitoring** | Prometheus · Grafana · Alertmanager · node_exporter · redis_exporter |
| **Security** | bcrypt · TOTP MFA · RBAC · Sliding window rate limit · OWASP ZAP |
| **DevOps** | Docker · GitHub Actions · Terraform · Ansible · Kubernetes · Nginx |

---

## ✨ Feature Overview

### Core Features
| Feature | Description |
|---------|-------------|
| 👤 Resume Display | Online resume, skills, work experience |
| 📝 Article Management | Markdown upload/edit/publish, auto title & tag extraction |
| 🚀 Project Deployment | GitHub one-click import, supports Vue/React/FastAPI/Flask/Django/Docker |
| 📊 Real-time Logs | WebSocket-powered deployment log streaming |
| 🌍 Internationalization | Full zh/en bilingual support, frontend & backend |

### Advanced Features (Iter 5-8)
| Feature | Description |
|---------|-------------|
| 🌙 Theme System | Dark / Light / Auto modes, follows system preference |
| 🔍 Full-text Search | ⌘K shortcut, 280ms debounce, keyword highlighting |
| 🔔 Real-time Notifications | WebSocket auto-reconnect, deploy/system event push |
| 💬 Social Features | Article likes (IP dedup), nested comments, XSS filtering |
| 🤖 AI Assistant | Intelligent chat with context awareness |
| 🖥️ Code Sandbox | Monaco Editor, multi-language online execution |
| 🔐 MFA Authentication | TOTP + QR code scanning |
| 📈 Prometheus Monitoring | 8-panel Grafana dashboard, 7 alert rules |

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- MySQL 8.0+
- Redis 7+
- Docker & Docker Compose (recommended)

### 🐳 Docker One-Click Start (Recommended)

```bash
git clone https://github.com/teng00123/personal-landing.git
cd personal-landing

# Copy and configure environment variables
cp backend/.env.example backend/.env
# Edit backend/.env — fill in SECRET_KEY, database password, etc.

docker compose up -d
```

After startup:
| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### 🔧 Local Development

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### 📊 Start Monitoring Stack

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | — |
| Alertmanager | http://localhost:9093 | — |

---

## 🗂️ Project Structure

```
personal-landing/
├── frontend/                  # Vue 3 frontend
│   ├── src/
│   │   ├── api/               # HTTP client
│   │   ├── components/        # Shared components
│   │   ├── composables/       # Vue Composables
│   │   ├── layouts/           # Layout components
│   │   ├── locales/           # i18n locale files
│   │   ├── router/            # Route configuration
│   │   ├── store/             # Pinia state management
│   │   └── views/             # Page views
│   └── vite.config.js
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── api/               # Route handlers
│   │   ├── core/              # Config, security, dependencies
│   │   ├── db/                # Database & models
│   │   ├── tasks/             # Celery tasks
│   │   └── utils/             # Utilities (cache/metrics/logging/security)
│   ├── alembic/               # Database migrations
│   └── requirements.txt
├── infra/                     # Infrastructure as Code
│   ├── terraform/             # AWS EC2 + SG + EIP
│   ├── ansible/               # Server configuration management
│   └── k8s/                   # Kubernetes manifests
├── monitoring/                # Monitoring configuration
│   ├── prometheus/            # Scrape config + alert rules
│   ├── alertmanager/          # Alert routing
│   └── grafana/               # Datasources + dashboards
├── nginx/                     # Nginx production config
├── scripts/                   # Ops scripts (backup/healthcheck)
├── docker-compose.yml         # Development environment
├── docker-compose.staging.yml # Staging environment
├── docker-compose.prod.yml    # Production environment
└── docker-compose.monitoring.yml
```

---

## 🚢 Deployment

### Staging

```bash
docker compose -f docker-compose.staging.yml up -d
```

### Production (Blue-Green Deployment)

Push a `v*.*.*` tag to trigger automated blue-green deployment via GitHub Actions:

```bash
git tag v1.0.0 && git push origin v1.0.0
```

Flow: new slot start → health check (12×5s) → Nginx hot-swap → old slot stop

### Kubernetes

```bash
kubectl apply -k infra/k8s/overlays/production
```

HPA configured for CPU 70% / Memory 80%, auto-scales 2–10 replicas.

---

## 💻 Development Guide

### Code Standards

```bash
# Backend lint
cd backend && ruff check . && ruff format .

# Backend type check
mypy app/

# Frontend lint
cd frontend && npm run lint
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
alembic downgrade -1   # rollback one step
```

### Testing

```bash
# Backend
cd backend && pytest tests/ -v --cov=app

# Frontend
cd frontend && npm run test
```

### Celery Task Queue

```bash
# Worker
celery -A app.tasks.celery_app:celery_app worker --loglevel=info --pool=solo

# Beat (scheduled tasks)
celery -A app.tasks.celery_app:celery_app beat --loglevel=info

# Flower monitoring dashboard
celery -A app.tasks.celery_app:celery_app flower
```

---

## 🔧 Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `Unknown system variable 'query_cache_type'` | Removed in MySQL 8.0 | Fixed in latest version |
| `monacoEditorPlugin is not a function` | CJS/ESM export compatibility | Fixed with `.default \|\|` fallback |
| `npm install` 404 `@monaco-editor/vite-plugin` | Wrong package name | Correct package: `vite-plugin-monaco-editor` |
| Frontend `Unexpected "type"` | TypeScript syntax in `.js` files | Removed TS type annotations |
| Database connection timeout | Connection pool exhausted | Tune `pool_size` / `max_overflow` |

For more issues, please submit an [Issue](https://github.com/teng00123/personal-landing/issues).

---

## 🤝 Contributing

1. Fork this project
2. Create a feature branch: `git checkout -b feat/new-feature`
3. Commit (following [Conventional Commits](https://conventionalcommits.org/)): `git commit -m 'feat: add new feature'`
4. Push: `git push origin feat/new-feature`
5. Create a Pull Request

All PRs must pass CI (Ruff · Bandit · Trivy · OWASP ZAP).

---

## 📄 License

MIT © [teng00123](https://github.com/teng00123)

---

<div align="center">

⭐ If this project helps you, please give it a star!

</div>
