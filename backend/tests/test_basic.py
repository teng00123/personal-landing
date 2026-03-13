import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.core.config import Settings
from backend.app.core.security import hash_password, verify_password
from backend.app.db.session import Base, get_db
from backend.app.main import app
from backend.app.models.user import User

# 内存 SQLite 数据库用于测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """创建测试数据库表"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_health_endpoint():
    """测试健康检查端点"""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "1.0.0"}


def test_create_user(test_db: Session):
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
    test_db.refresh(user)
    
    # 验证用户已创建
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == hashed_pw


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