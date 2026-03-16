# Personal Landing - Full Stack Personal Portfolio Application

## Project Overview

This is a full-stack personal homepage/portfolio application featuring:
- **Backend**: Python + FastAPI + SQLAlchemy + MySQL + Redis + Celery
- **Frontend**: Vue 3 + Vite + Element Plus
- **Features**: Resume display, Markdown article management, GitHub project auto-deployment

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- MySQL 8.0+
- Redis 7+
- Docker & Docker Compose

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/teng00123/personal-landing.git
   cd personal-landing
   ```

2. **Backend setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env file to configure database and other settings
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   ```

4. **Start services**
   ```bash
   # Using Docker Compose (recommended)
   docker compose up -d
   
   # Or manual startup
   # Backend: uvicorn app.main:app --reload
   # Frontend: npm run dev
   # Database: Ensure MySQL and Redis are running
   ```

## API Documentation

After startup, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Features

### User Authentication
- JWT Token authentication
- Admin permission control
- Password encryption storage (bcrypt + SHA-256 pre-hash)

### Article Management
- Markdown file upload
- Automatic title and tag extraction
- Publication status management
- Reading statistics

### Project Management
- GitHub project import
- Auto-deployment (supports multiple frameworks)
- Real-time log viewing
- Automatic port allocation

## Celery Task Queue Setup

### Docker Method (Recommended)
```bash
# Start Celery Worker (handles deployment tasks)
docker-compose up -d celery

# View Celery logs
docker-compose logs -f celery

# Start Celery Beat (scheduled tasks, if needed)
docker-compose up -d celery-beat
```

### Local Development Method
```bash
# Enter backend directory
cd backend

# Start Celery Worker
celery -A app.tasks.celery_app:celery_app worker --loglevel=info --pool=solo

# Start Celery Beat (scheduled tasks)
celery -A app.tasks.celery_app:celery_app beat --loglevel=info

# Monitor task status (Flower)
celery -A app.tasks.celery_app:celery_app flower
```

### Celery Task Types
- **Project Deployment**: Automatically clone and deploy GitHub projects
- **Supported Frameworks**: Vue/React/Next.js/Node/FastAPI/Flask/Django/Static/Docker
- **Port Allocation**: Automatically scans 8100-9000 port range
- **Log Viewing**: Real-time deployment logs via API `/projects/{id}/logs`

### Common Celery Commands
```bash
# View active tasks
celery -A app.tasks.celery_app:celery_app inspect active

# View registered tasks
celery -A app.tasks.celery_app:celery_app inspect registered

# Purge task queue
celery -A app.tasks.celery_app:celery_app purge
```

## Local Development
### Deployment Features
- Vue/React/Next.js project builds
- FastAPI/Flask/Django project deployment
- Static website hosting
- Docker container deployment

## Development Guidelines

### Code Standards
- Use Conventional Commits specification
- Backend: ruff formatting + mypy type checking
- Frontend: ESLint + Prettier
- All PRs must pass CI checks

### Testing
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Deployment

### Docker Deployment
```bash
docker compose up -d
```

### Production Environment
- Use Nginx reverse proxy
- Configure SSL certificates
- Set firewall rules
- Regular database backups

## Troubleshooting

For common issues and solutions, please refer to README.md

## Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feat/new-feature`)
3. Commit your changes (`git commit -m 'feat: add new feature'`)
4. Push to the branch (`git push origin feat/new-feature`)
5. Create a Pull Request

## License

MIT License

## Contact

- Author: teng00123
- GitHub: https://github.com/teng00123
- Email: teng00123@github.com