"""
结构化日志配置 — Iteration 4
输出 JSON 格式日志，便于 ELK/Loki 采集
"""
import json
import logging
import sys
import traceback
from datetime import datetime, UTC
from typing import Any


class JSONFormatter(logging.Formatter):
    """将日志输出为单行 JSON，方便 Logstash/Filebeat 采集"""

    LEVEL_MAP = {
        logging.DEBUG:    "debug",
        logging.INFO:     "info",
        logging.WARNING:  "warn",
        logging.ERROR:    "error",
        logging.CRITICAL: "critical",
    }

    def format(self, record: logging.LogRecord) -> str:
        log: dict[str, Any] = {
            "ts":      datetime.now(UTC).isoformat(),
            "level":   self.LEVEL_MAP.get(record.levelno, "info"),
            "logger":  record.name,
            "message": record.getMessage(),
            "module":  record.module,
            "lineno":  record.lineno,
        }

        # 附加额外字段（如 request_id, user_id）
        for key in ("request_id", "user_id", "method", "path", "status_code", "duration_ms"):
            if hasattr(record, key):
                log[key] = getattr(record, key)

        # 异常堆栈
        if record.exc_info:
            log["exception"] = traceback.format_exception(*record.exc_info)

        return json.dumps(log, ensure_ascii=False)


def setup_logging(level: str = "INFO", json_logs: bool = True) -> None:
    """
    初始化日志配置
    - 生产: json_logs=True，输出 JSON
    - 开发: json_logs=False，输出可读格式
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 清除旧 handler
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if json_logs:
        handler.setFormatter(JSONFormatter())
    else:
        fmt = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
        handler.setFormatter(logging.Formatter(fmt))

    root.addHandler(handler)

    # 降低三方库噪音
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "celery"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
