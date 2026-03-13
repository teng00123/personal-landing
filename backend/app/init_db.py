"""
初始化数据库表 & 默认管理员账号
用法：
    python -m app.init_db
"""
import json
import sys

from app.db.session import engine, Base
from app.models import User, Article, Project  # noqa — 触发模型注册
from app.core.security import hash_password
from app.core.config import settings
from sqlalchemy.orm import Session


SAMPLE_RESUME = json.dumps({
    "experience": [
        {
            "company": "示例科技有限公司",
            "title": "高级后端工程师",
            "start": "2022-01",
            "end": "",
            "description": "负责核心交易系统架构设计与性能优化，QPS 提升 300%。",
            "skills": "Python,FastAPI,MySQL,Redis,Kafka"
        },
        {
            "company": "前公司",
            "title": "后端工程师",
            "start": "2020-06",
            "end": "2021-12",
            "description": "参与微服务拆分，维护 CI/CD 流水线。",
            "skills": "Go,Docker,Kubernetes"
        }
    ],
    "education": [
        {
            "school": "某某大学",
            "degree": "本科",
            "major": "计算机科学与技术",
            "start": "2016-09",
            "end": "2020-06"
        }
    ],
    "skills": [
        {
            "category": "后端",
            "items": [
                {"name": "Python / FastAPI", "level": 95},
                {"name": "Go", "level": 75},
                {"name": "MySQL / Redis", "level": 90}
            ]
        },
        {
            "category": "前端",
            "items": [
                {"name": "Vue 3", "level": 80},
                {"name": "TypeScript", "level": 70}
            ]
        },
        {
            "category": "运维",
            "items": [
                {"name": "Docker / K8s", "level": 82},
                {"name": "Linux", "level": 88}
            ]
        }
    ],
    "certifications": []
}, ensure_ascii=False)


def init():
    print("▶ 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("  ✓ 表创建完成")

    with Session(engine) as db:
        existing = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        if existing:
            print(f"  ℹ  管理员 '{settings.ADMIN_USERNAME}' 已存在，跳过创建")
            return

        admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_admin=True,
            full_name="Your Name",
            title="Senior Full Stack Engineer",
            bio="热爱技术，专注于构建高性能、高可用的软件系统。\n喜欢开源，持续学习。",
            location="深圳，中国",
            resume_data=SAMPLE_RESUME,
        )
        db.add(admin)
        db.commit()
        print(f"  ✓ 管理员已创建：{settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}")

    print("✅ 初始化完成！")


if __name__ == "__main__":
    init()
