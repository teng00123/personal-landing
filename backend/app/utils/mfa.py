"""
MFA 工具 — Iteration 6
支持 TOTP (RFC 6238) 兼容 Google Authenticator / Authy
"""
from __future__ import annotations

import base64
import io
import os

import pyotp
import qrcode


def generate_totp_secret() -> str:
    """生成 16 字节随机 Base32 密钥"""
    return pyotp.random_base32()


def get_totp_uri(secret: str, username: str, issuer: str = "PersonalLanding") -> str:
    """返回 otpauth:// URI，可生成 QR 码"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=issuer)


def get_totp_qr_base64(secret: str, username: str) -> str:
    """返回 base64 编码的 QR 码 PNG（data URI 格式）"""
    uri = get_totp_uri(secret, username)
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """
    验证 TOTP 码
    window=1 允许前后各 1 个时间窗口（30s）的偏差
    """
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(code.strip(), valid_window=window)
