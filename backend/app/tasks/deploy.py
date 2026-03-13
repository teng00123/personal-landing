"""
deploy.py — 占位文件，迭代三实现 Celery 自动部署任务
"""
from app.tasks.celery_app import celery_app


@celery_app.task(name="deploy_project")
def deploy_project(project_id: int):
    """迭代三实现：git clone → 检测框架 → 安装依赖 → 启动进程"""
    raise NotImplementedError("deploy_project will be implemented in iteration 3")


@celery_app.task(name="stop_project")
def stop_project(project_id: int):
    """迭代三实现"""
    raise NotImplementedError("stop_project will be implemented in iteration 3")
