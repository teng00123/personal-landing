"""
wait_for_db.py — 等待 MySQL 就绪
Docker 启动时 MySQL 需要几秒钟，此脚本轮询直到连接成功。
用法：python -m app.wait_for_db
"""
import sys
import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError


def wait(max_retries: int = 30, interval: float = 2.0):
    from app.db.session import engine
    print(f"⏳ 等待数据库就绪（最多 {max_retries * interval:.0f}s）...")
    for i in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("  ✓ 数据库已就绪")
            return
        except OperationalError as e:
            print(f"  [{i}/{max_retries}] 未就绪，{interval}s 后重试... ({e.args[0]})")
            time.sleep(interval)
    print("❌ 数据库连接超时，退出", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    wait()
