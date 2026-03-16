"""
数据脱敏与安全工具 — Iteration 6
"""
from __future__ import annotations

import hashlib
import html
import re
from typing import Any


# ── 脱敏函数 ─────────────────────────────────────────────

def mask_email(email: str) -> str:
    """user@example.com → us**@example.com"""
    if not email or "@" not in email:
        return "****"
    local, domain = email.rsplit("@", 1)
    visible = max(2, len(local) // 3)
    return local[:visible] + "*" * (len(local) - visible) + "@" + domain


def mask_phone(phone: str) -> str:
    """13812345678 → 138****5678"""
    phone = re.sub(r"\D", "", phone)
    if len(phone) < 7:
        return "****"
    return phone[:3] + "*" * (len(phone) - 7) + phone[-4:]


def mask_ip(ip: str) -> str:
    """192.168.1.100 → 192.168.*.*"""
    parts = ip.split(".")
    if len(parts) == 4:
        return ".".join(parts[:2]) + ".*.*"
    return "****"


def mask_field(value: Any, field_type: str = "default") -> str:
    """通用脱敏"""
    if value is None:
        return ""
    s = str(value)
    if field_type == "email":
        return mask_email(s)
    if field_type == "phone":
        return mask_phone(s)
    if field_type == "ip":
        return mask_ip(s)
    # 默认：保留首尾各 1 个字符
    if len(s) <= 2:
        return "*" * len(s)
    return s[0] + "*" * (len(s) - 2) + s[-1]


# ── XSS 防护 ──────────────────────────────────────────────

# 允许的 HTML 标签（富文本展示用）
ALLOWED_TAGS = {
    "p", "br", "strong", "em", "u", "s", "del",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "blockquote", "pre", "code",
    "a", "img", "table", "thead", "tbody", "tr", "th", "td",
    "hr", "figure", "figcaption",
}

ALLOWED_ATTRS = {
    "a":   ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "*":   ["class"],
}

_DANGEROUS_ATTRS = re.compile(
    r"""(on\w+|javascript:|data:text/html|vbscript:)""",
    re.IGNORECASE,
)


def sanitize_html(raw: str) -> str:
    """
    简单 HTML 净化：移除危险属性和标签
    生产环境建议使用 bleach 或 nh3 库
    """
    if not raw:
        return ""
    # 移除 script / style 整块
    raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    # 移除 on* 属性
    raw = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', "", raw, flags=re.IGNORECASE)
    # 移除 javascript: href
    raw = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', 'href="#"', raw, flags=re.IGNORECASE)
    return raw


def escape_for_sql_like(s: str) -> str:
    """转义 LIKE 通配符"""
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# ── 密码强度验证 ──────────────────────────────────────────

def check_password_strength(password: str) -> tuple[bool, str]:
    """
    返回 (ok, message)
    要求：至少 8 位，含大写、小写、数字、特殊字符
    """
    if len(password) < 8:
        return False, "密码至少需要 8 个字符"
    if not re.search(r"[A-Z]", password):
        return False, "密码需要包含至少一个大写字母"
    if not re.search(r"[a-z]", password):
        return False, "密码需要包含至少一个小写字母"
    if not re.search(r"\d", password):
        return False, "密码需要包含至少一个数字"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "密码需要包含至少一个特殊字符"
    return True, "密码强度符合要求"


def hash_sensitive(value: str) -> str:
    """对敏感值做单向哈希（用于日志记录）"""
    return hashlib.sha256(value.encode()).hexdigest()[:16]
