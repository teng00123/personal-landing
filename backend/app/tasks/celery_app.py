"""
Celery App 配置
迭代一：只注册 app，不含实际任务（迭代三补充）
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "personal_landing",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.deploy"],  # 迭代三添加
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)
