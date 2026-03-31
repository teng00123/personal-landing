"""
认证 API Happy Path 测试
覆盖：
  - POST /api/v1/auth/login  — 正确凭据 → 返回 token
  - POST /api/v1/auth/login  — 错误密码 → 401
  - POST /api/v1/auth/login  — 不存在用户 → 401
  - GET  /api/v1/auth/me     — 携带 token → 返回当前用户
  - GET  /api/v1/auth/me     — 无 token → 401
"""

import pytest


class TestLogin:
    def test_login_success(self, client, admin_user):
        """正确凭据登录，应返回 access_token 和用户信息。"""
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Test1234!"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "access_token" in data
        assert data["access_token"]  # 非空
        assert data["user"]["username"] == "admin"
        assert data["user"]["is_admin"] is True

    def test_login_wrong_password(self, client, admin_user):
        """错误密码应返回 401。"""
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "WrongPass"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        """不存在的用户应返回 401。"""
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "ghost", "password": "anything"},
        )
        assert resp.status_code == 401


class TestMe:
    def test_me_with_valid_token(self, client, admin_user, auth_headers):
        """携带有效 token 请求 /me，应返回当前用户信息。"""
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@test.com"
        assert data["is_admin"] is True

    def test_me_without_token(self, client):
        """无 token 请求 /me，应返回 401。"""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_with_invalid_token(self, client):
        """无效 token 请求 /me，应返回 401。"""
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer this.is.not.a.valid.token"},
        )
        assert resp.status_code == 401
