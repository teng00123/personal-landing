from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_SECRET_KEY: str = "change-me"
    DEBUG: bool = True
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    # AI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-3.5-turbo"
    OLLAMA_URL: str = ""

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # DB
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "app"
    DB_PASSWORD: str = "apppass"
    DB_NAME: str = "personal_homepage"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # GitHub
    GITHUB_TOKEN: str = ""

    # Deploy
    DEPLOY_BASE_DIR: str = "./deploy_workspace"
    DEPLOY_BASE_PORT: int = 8100
    DEPLOY_BASE_URL: str = "http://localhost"

    # Admin seed
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "12345678"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
