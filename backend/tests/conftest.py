"""
pytest 全局 fixtures
策略：
  1. 在 app.main 被 import 之前，把 app.db.session 模块里的 engine/SessionLocal
     替换成 SQLite 版本（模块级赋值，影响所有后续 import）。
  2. lifespan 里有 `from app.db.session import engine` — 这是值拷贝，无法被 patch。
     所以额外 mock lifespan 让它成为 no-op，由 conftest 自己管理建表/清表。
  3. 测试 Session 直接通过 dependency_overrides[get_db] 注入。
"""
from __future__ import annotations

# ── Step 1: 在 import app.main 之前替换引擎（顺序敏感！） ──
import app.db.session as _sess

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

SQLITE_URL = "sqlite:///./test_db.sqlite3"

_test_engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

@event.listens_for(_test_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# 替换模块属性（影响所有在此之后从模块里 import engine 的代码）
_sess.engine = _test_engine
_sess.SessionLocal = _TestingSessionLocal

# ── Step 2: 现在才 import app —— 此时 app.db.session.engine 已是测试引擎 ──
import pytest
from contextlib import asynccontextmanager
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.db.session import Base, get_db
from app.main import app
from app.models.article import Article     # noqa: F401
from app.models.project import Project     # noqa: F401
from app.models.user import User
from app.api.community import Activity, ActivityRegistration, Follow, Message
from app.api.social import Comment
from app.utils.audit import AuditLog
from app.core.security import create_access_token
from app.utils.cache import CacheManager, get_cache


# ── NullCacheManager ──────────────────────────────────────

class NullCacheManager(CacheManager):
    """永远 miss，测试不依赖 Redis。"""
    def __init__(self): pass

    async def get(self, key): return None
    async def set(self, key, value, ttl=300): return True
    async def delete(self, key): return True
    async def clear_pattern(self, pattern): return 0
    async def exists(self, key): return False


# ── no-op lifespan —————————————————————————————————————────

@asynccontextmanager
async def _noop_lifespan(_app):
    """测试用 lifespan：跳过 MySQL 建表，由 conftest 自己管理。"""
    yield


# ── Fixtures ───────────────────────────────────────────────

@pytest.fixture(scope="function")
def db_session():
    """每个测试用独立的 SQLite 数据库（建表 → yield → 清表）。"""
    Base.metadata.create_all(bind=_test_engine)
    session = _TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient，注入测试 DB 和空缓存，lifespan 替换为 no-op。"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    async def override_get_cache():
        return NullCacheManager()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache] = override_get_cache

    # 替换 lifespan，避免 lifespan 里再做 MySQL 建表
    original_router = app.router
    with patch.object(app, "router") as mock_router:
        # 让 TestClient 能正常路由，只 mock lifespan
        mock_router.on_startup = []
        mock_router.on_shutdown = []
        mock_router.lifespan_context = _noop_lifespan

        # 恢复路由（只 no-op lifespan）
        app.router = original_router
        app.router.lifespan_context = _noop_lifespan

        with TestClient(app, raise_server_exceptions=True) as c:
            yield c

    app.dependency_overrides.clear()
    # 恢复原始 lifespan（避免影响其他 fixture）
    from app.main import lifespan as _orig_lifespan
    app.router.lifespan_context = _orig_lifespan


@pytest.fixture(scope="function")
def admin_user(db_session):
    """预先插入管理员用户（密码即明文，与 auth.login 实现一致）。"""
    user = User(
        username="admin",
        email="admin@test.com",
        hashed_password="Test1234!",
        is_admin=True,
        is_active=True,
        full_name="Admin Tester",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_token(admin_user):
    return create_access_token(admin_user.id)


@pytest.fixture(scope="function")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
