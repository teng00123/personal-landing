"""
文章 CRUD Happy Path 测试
覆盖：
  - POST /api/v1/articles        — 管理员新建文章（草稿 & 已发布）
  - GET  /api/v1/articles        — 公开列表只返回已发布
  - GET  /api/v1/articles/{id}   — 管理员获取详情（含草稿）
  - GET  /api/v1/articles/slug/{slug} — 公开通过 slug 获取已发布文章
  - PUT  /api/v1/articles/{id}   — 更新文章（发布草稿）
  - DELETE /api/v1/articles/{id} — 删除文章
  - GET  /api/v1/articles/admin  — 管理员列表（含草稿）
  - 403  — 非管理员无法新建/删除
"""
import pytest


# ── 工具函数 ────────────────────────────────────────────────

def create_article(client, auth_headers, **overrides):
    payload = {
        "title": "测试文章标题",
        "content": "## Hello\n这是测试内容。",
        "is_published": False,
        **overrides,
    }
    resp = client.post("/api/v1/articles", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── 新建 ────────────────────────────────────────────────────

class TestCreateArticle:
    def test_create_draft(self, client, admin_user, auth_headers):
        """管理员新建草稿，应返回 201，is_published=False，slug 自动生成。"""
        art = create_article(client, auth_headers)
        assert art["id"] > 0
        assert art["is_published"] is False
        assert art["slug"]  # 非空
        assert art["author_id"] == admin_user.id

    def test_create_published(self, client, admin_user, auth_headers):
        """新建时直接发布，published_at 不为 None。"""
        art = create_article(client, auth_headers, is_published=True, title="已发布文章")
        assert art["is_published"] is True
        assert art["published_at"] is not None

    def test_create_with_custom_slug(self, client, admin_user, auth_headers):
        """指定 slug 时应使用自定义 slug。"""
        art = create_article(client, auth_headers, slug="my-custom-slug")
        assert art["slug"] == "my-custom-slug"

    def test_create_duplicate_slug_returns_409(self, client, admin_user, auth_headers):
        """重复 slug 应返回 409。"""
        create_article(client, auth_headers, slug="dup-slug")
        resp = client.post(
            "/api/v1/articles",
            json={"title": "另一篇", "content": "内容", "slug": "dup-slug"},
            headers=auth_headers,
        )
        assert resp.status_code == 409

    def test_create_requires_auth(self, client):
        """未认证新建文章应返回 401。"""
        resp = client.post(
            "/api/v1/articles",
            json={"title": "无权限", "content": "内容"},
        )
        assert resp.status_code == 401


# ── 公开列表 ────────────────────────────────────────────────

class TestPublicList:
    def test_public_list_only_published(self, client, admin_user, auth_headers):
        """公开列表只返回已发布文章。"""
        create_article(client, auth_headers, title="草稿", is_published=False)
        create_article(client, auth_headers, title="已发布", is_published=True)

        resp = client.get("/api/v1/articles")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "已发布"

    def test_public_list_empty(self, client):
        """无文章时返回空列表。"""
        resp = client.get("/api/v1/articles")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_public_list_pagination(self, client, admin_user, auth_headers):
        """分页参数正常工作。"""
        for i in range(5):
            create_article(client, auth_headers, title=f"文章{i}", is_published=True)

        resp = client.get("/api/v1/articles?page=1&page_size=3")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3


# ── 公开 Slug 详情 ──────────────────────────────────────────

class TestPublicSlug:
    def test_get_by_slug_published(self, client, admin_user, auth_headers):
        """通过 slug 获取已发布文章。"""
        art = create_article(client, auth_headers, is_published=True, title="Slug测试")
        slug = art["slug"]

        resp = client.get(f"/api/v1/articles/slug/{slug}")
        assert resp.status_code == 200
        assert resp.json()["slug"] == slug

    def test_get_by_slug_draft_returns_404(self, client, admin_user, auth_headers):
        """通过 slug 获取草稿应返回 404。"""
        art = create_article(client, auth_headers, is_published=False, title="草稿Slug")
        resp = client.get(f"/api/v1/articles/slug/{art['slug']}")
        assert resp.status_code == 404

    def test_get_by_slug_not_found(self, client):
        """不存在的 slug 返回 404。"""
        resp = client.get("/api/v1/articles/slug/nonexistent-slug")
        assert resp.status_code == 404


# ── 管理员详情 ──────────────────────────────────────────────

class TestAdminDetail:
    def test_get_article_by_id(self, client, admin_user, auth_headers):
        """管理员可通过 ID 获取任意文章（含草稿）。"""
        art = create_article(client, auth_headers, is_published=False)
        resp = client.get(f"/api/v1/articles/{art['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == art["id"]

    def test_get_article_not_found(self, client, admin_user, auth_headers):
        """不存在的 ID 返回 404。"""
        resp = client.get("/api/v1/articles/99999", headers=auth_headers)
        assert resp.status_code == 404


# ── 更新 ────────────────────────────────────────────────────

class TestUpdateArticle:
    def test_update_title(self, client, admin_user, auth_headers):
        """更新文章标题。"""
        art = create_article(client, auth_headers)
        resp = client.put(
            f"/api/v1/articles/{art['id']}",
            json={"title": "更新后的标题"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "更新后的标题"

    def test_publish_draft(self, client, admin_user, auth_headers):
        """将草稿更新为已发布，published_at 应被设置。"""
        art = create_article(client, auth_headers, is_published=False)
        assert art["published_at"] is None

        resp = client.put(
            f"/api/v1/articles/{art['id']}",
            json={"is_published": True},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_published"] is True
        assert data["published_at"] is not None

    def test_unpublish_article(self, client, admin_user, auth_headers):
        """将已发布文章改为草稿，published_at 应被清空。"""
        art = create_article(client, auth_headers, is_published=True)
        resp = client.put(
            f"/api/v1/articles/{art['id']}",
            json={"is_published": False},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_published"] is False
        assert resp.json()["published_at"] is None

    def test_update_nonexistent_returns_404(self, client, admin_user, auth_headers):
        resp = client.put(
            "/api/v1/articles/99999",
            json={"title": "x"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


# ── 删除 ────────────────────────────────────────────────────

class TestDeleteArticle:
    def test_delete_article(self, client, admin_user, auth_headers):
        """删除文章后应返回 204，再次查询返回 404。"""
        art = create_article(client, auth_headers)
        resp = client.delete(f"/api/v1/articles/{art['id']}", headers=auth_headers)
        assert resp.status_code == 204

        # 再查应 404
        resp2 = client.get(f"/api/v1/articles/{art['id']}", headers=auth_headers)
        assert resp2.status_code == 404

    def test_delete_nonexistent_returns_404(self, client, admin_user, auth_headers):
        resp = client.delete("/api/v1/articles/99999", headers=auth_headers)
        assert resp.status_code == 404


# ── 管理员列表 ──────────────────────────────────────────────

class TestAdminList:
    def test_admin_list_includes_drafts(self, client, admin_user, auth_headers):
        """管理员列表同时包含草稿和已发布。"""
        create_article(client, auth_headers, title="草稿A", is_published=False)
        create_article(client, auth_headers, title="已发布B", is_published=True)

        resp = client.get("/api/v1/articles/admin", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    def test_admin_list_requires_auth(self, client):
        resp = client.get("/api/v1/articles/admin")
        assert resp.status_code == 401
