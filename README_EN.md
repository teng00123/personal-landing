# 🚀 Personal Landing - Full Stack Personal Portfolio Application

<div align="center">

**[🇨🇳 中文版本](README.md)** | **[🇺🇸 English Version](README_EN.md)**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Vue](https://img.shields.io/badge/Vue-3.x-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

---

## 📋 Project Overview

A modern full-stack personal homepage/portfolio application integrating resume display, blog management, and automated project deployment.

### 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.11+ + FastAPI + SQLAlchemy + MySQL + Redis + Celery |
| **Frontend** | Vue 3 + Vite + Element Plus |
| **Deployment** | Docker + Docker Compose |
| **Task Queue** | Celery + Redis |

### ✨ Core Features

- 📄 **Resume Display** - Online resume and personal introduction
- 📝 **Markdown Article Management** - Upload, edit, and publish articles
- 🚀 **GitHub Project Auto-Deployment** - One-click deployment for multiple frameworks
- 📊 **Real-time Log Viewing** - Transparent deployment process
- 🔐 **JWT Authentication** - Secure user management system

---

## ⚡ Quick Start

### 📦 Prerequisites

- Python 3.11+
- Node.js 20+
- MySQL 8.0+
- Redis 7+
- Docker & Docker Compose

### 🔧 Installation Steps

#### 1️⃣ Clone Repository
```bash
git clone https://github.com/teng00123/personal-landing.git
cd personal-landing
```

#### 2️⃣ Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env file to configure database and other settings
```

#### 3️⃣ Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
```

#### 4️⃣ Start Services

**🐳 Docker Way (Recommended)**
```bash
docker compose up -d
```

**🔧 Manual Way**
```bash
# Backend service
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend service
cd frontend
npm run dev

# Ensure MySQL and Redis are running
```

### 📚 API Documentation

After startup, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎯 Feature Details

### 🔐 User Authentication System
- ✅ JWT Token authentication mechanism
- 👑 Admin permission fine-grained control
- 🔒 Password encryption storage (bcrypt + SHA-256 pre-hash)

### 📝 Article Management System
- 📤 Markdown file upload
- 🏷️ Automatic title and tag extraction
- 📅 Publication status management
- 📈 Reading statistics analysis

### 🚀 Project Deployment System
- 🔗 GitHub project import
- ⚡ Auto-deployment (supports multiple frameworks)
- 📋 Real-time log viewing
- 🎲 Automatic port allocation (8100-9000)

**Supported Deployment Frameworks:**
- Vue/React/Next.js project builds
- FastAPI/Flask/Django project deployment
- Static website hosting
- Docker container deployment

---

## ⚙️ Celery Task Queue

### 🐳 Docker Way (Recommended)
```bash
# Start Celery Worker (handles deployment tasks)
docker-compose up -d celery

# View Celery logs
docker-compose logs -f celery

# Start Celery Beat (scheduled tasks)
docker-compose up -d celery-beat
```

### 💻 Local Development Way
```bash
cd backend

# Start Celery Worker
celery -A app.tasks.celery_app:celery_app worker --loglevel=info --pool=solo

# Start Celery Beat (scheduled tasks)
celery -A app.tasks.celery_app:celery_app beat --loglevel=info

# Monitor task status (Flower)
celery -A app.tasks.celery_app:celery_app flower
```

### 🔧 Common Celery Commands
```bash
# View active tasks
celery -A app.tasks.celery_app:celery_app inspect active

# View registered tasks
celery -A app.tasks.celery_app:celery_app inspect registered

# Purge task queue
celery -A app.tasks.celery_app:celery_app purge
```

---

## 💻 Development Guidelines

### 📏 Code Standards
- 📝 Use [Conventional Commits](https://conventionalcommits.org/) specification
- 🐍 Backend: ruff formatting + mypy type checking
- ⚡ Frontend: ESLint + Prettier
- ✅ All PRs must pass CI checks

### 🧪 Testing
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test
```

### 🗄️ Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

---

## 🚢 Deployment

### 🐳 Docker Deployment
```bash
docker compose up -d
```

### 🏭 Production Environment Configuration
- 🌐 Use Nginx reverse proxy
- 🔐 Configure SSL certificates
- 🛡️ Set firewall rules
- 💾 Regular database backups

---

## 🔧 Troubleshooting

For common issues and solutions, please refer to this file or submit an issue.

---

## 🤝 Contributing

Welcome contributions! Please follow these steps:

1. 🍴 Fork this project
2. 🌿 Create feature branch (`git checkout -b feat/new-feature`)
3. ✨ Commit changes (`git commit -m 'feat: add new feature'`)
4. 📤 Push branch (`git push origin feat/new-feature`)
5. 🔄 Create Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Contact

- **Author**: teng00123
- **GitHub**: [@teng00123](https://github.com/teng00123)
- **Email**: teng00123@github.com

---

<div align="center">

⭐ If this project helps you, please give it a star!

</div>