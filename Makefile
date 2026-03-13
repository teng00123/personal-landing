# Makefile — personal-landing 常用命令
.PHONY: up down restart init init-seed reset-db migrate logs shell-backend shell-db help

## 启动所有服务（后台）
up:
	docker compose up -d

## 停止并移除容器（保留数据卷）
down:
	docker compose down

## 重启所有服务
restart:
	docker compose restart

## 初始化数据库（建表 + admin，不写示例数据）
init:
	docker compose exec backend python -m app.init_db

## 初始化 + 写入示例文章和项目
init-seed:
	docker compose exec backend python -m app.init_db --seed

## ⚠️  危险：删除所有表后重建（会丢失数据）
reset-db:
	docker compose exec backend python -m app.init_db --reset --seed

## 执行 Alembic 迁移（升级到 head）
migrate:
	docker compose exec backend alembic upgrade head

## 生成新的 Alembic 迁移（msg="your message"）
migration:
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

## 查看服务日志
logs:
	docker compose logs -f --tail=100

## 查看 backend 日志
logs-backend:
	docker compose logs -f --tail=100 backend

## 查看 celery worker 日志
logs-celery:
	docker compose logs -f --tail=100 celery

## 进入 backend 容器 shell
shell-backend:
	docker compose exec backend bash

## 进入 MySQL 交互式命令行
shell-db:
	docker compose exec mysql mysql -uapp -papppass personal_homepage

## 本地开发：仅启动 MySQL + Redis（前后端本地跑）
dev-deps:
	docker compose up -d mysql redis

## 查看所有容器状态
status:
	docker compose ps

help:
	@echo ""
	@echo "  personal-landing Makefile 命令："
	@echo ""
	@echo "  make up           启动所有服务"
	@echo "  make down         停止服务"
	@echo "  make init         建表 + admin"
	@echo "  make init-seed    建表 + admin + 示例数据"
	@echo "  make reset-db     ⚠️  删表重建 + 示例数据"
	@echo "  make migrate      执行 Alembic 迁移"
	@echo "  make logs         查看全部日志"
	@echo "  make shell-backend  进入后端容器"
	@echo "  make shell-db     进入 MySQL"
	@echo ""
