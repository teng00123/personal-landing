from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.DATABASE_URL,
    # ── 连接池调优 ─────────────────────────────────────────
    poolclass=QueuePool,
    pool_size=20,  # 常驻连接数（原 10 → 20）
    max_overflow=30,  # 峰值额外连接（原 20 → 30）
    pool_pre_ping=True,  # 使用前检测连接活性
    pool_recycle=1800,  # 30 分钟回收连接，避免 MySQL gone away
    pool_timeout=10,  # 等待连接超时 10 秒
    echo=settings.DEBUG,
)


@event.listens_for(engine, "connect")
def set_mysql_session_options(dbapi_conn, connection_record):
    """每个连接建立时设置 MySQL session 参数"""
    with dbapi_conn.cursor() as cursor:
        # 排序缓冲区
        cursor.execute("SET SESSION sort_buffer_size = 4194304")  # 4 MB
        # 连接字符集
        cursor.execute("SET NAMES utf8mb4")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
