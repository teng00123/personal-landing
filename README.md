# Personal Landing 项目文档

**🇺🇸 English Version**: [README_EN.md](README_EN.md)

## 项目概述

这是一个全栈个人主页/作品集应用，包含：
- **后端**: Python + FastAPI + SQLAlchemy + MySQL + Redis + Celery
- **前端**: Vue 3 + Vite + Element Plus
- **功能**: 简历展示、Markdown文章管理、GitHub项目自动部署

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 20+
- MySQL 8.0+
- Redis 7+
- Docker & Docker Compose

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/teng00123/personal-landing.git
   cd personal-landing
   ```

2. **后端设置**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # 编辑 .env 文件，配置数据库等信息
   ```

3. **前端设置**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   ```

4. **启动服务**
   ```bash
   # 使用 Docker Compose (推荐)
   docker compose up -d
   
   # 或手动启动
   # 后端: uvicorn app.main:app --reload
   # 前端: npm run dev
   # 数据库: 确保 MySQL 和 Redis 运行
   ```

## API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要功能

### 用户认证
- JWT Token 认证
- 管理员权限控制
- 密码加密存储 (bcrypt + SHA-256 pre-hash)

### 文章管理
- Markdown 文件上传
- 自动提取标题和标签
- 发布状态管理
- 阅读统计

### 项目管理
- GitHub 项目导入
- 自动部署 (支持多种框架)
- 实时日志查看
- 端口自动分配

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
### 部署功能
- Vue/React/Next.js 项目构建
- FastAPI/Flask/Django 项目部署
- 静态网站托管
- Docker 容器部署

## 开发指南

### 代码规范
- 使用 Conventional Commits 提交规范
- 后端: ruff 格式化 + mypy 类型检查
- 前端: ESLint + Prettier
- 所有 PR 必须通过 CI 检查

### 测试
```bash
# 后端测试
cd backend
pytest tests/ -v

# 前端测试
cd frontend
npm run test
```

### 数据库迁移
```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head
```

## 部署

### Docker 部署
```bash
docker compose up -d
```

### 生产环境
- 使用 Nginx 反向代理
- 配置 SSL 证书
- 设置防火墙规则
- 定期备份数据库

## 故障排除

常见问题及解决方案请参考 README.md

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feat/新功能`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送分支 (`git push origin feat/新功能`)
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

- 作者: teng00123
- GitHub: https://github.com/teng00123
- 邮箱: teng00123@github.com