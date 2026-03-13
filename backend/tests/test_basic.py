import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import Settings
from backend.app.core.security import hash_password
from backend.app.db.session import Base
from backend.app.main import app
from backend.app.models.user import User

# 测试配置
TEST_SETTINGS = Settings(
    DB_HOST="localhost",
    DB_PORT=3306,
    DB_USER="test_user",
    DB_PASSWORD="test_pass",
    DB_NAME="test_personal_homepage",
    APP_SECRET_KEY="test-secret-key",
    DEBUG=True,
    ADMIN_USERNAME="admin",
    ADMIN_EMAIL="admin@example.com",
    ADMIN_PASSWORD="12345678"
)

# 内存 SQLite 数据库用于测试
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    """创建测试数据库表"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


def test_health_endpoint():
    """测试健康检查端点"""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "1.0.0"}


def test_create_user(test_db):
    """测试用户创建"""
    hashed_pw = hash_password("test_password")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_pw,
        is_admin=False,
        full_name="Test User"
    )
    test_db.add(user)
    test_db.commit()
    
    # 验证用户已创建
    saved_user = test_db.query(User).filter(User.username == "testuser").first()
    assert saved_user is not None
    assert saved_user.email == "test@example.com"


def test_password_hashing():
    """测试密码哈希和验证"""
    plain_password = "MySecurePassword123!"
    hashed = hash_password(plain_password)
    
    # 验证哈希不是明文
    assert hashed != plain_password
    assert len(hashed) > 50  # bcrypt 哈希长度
    
    # 验证密码验证工作
    assert verify_password(plain_password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])