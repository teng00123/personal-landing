"""
项目 CRUD Happy Path 测试
覆盖：
  - POST /api/v1/projects               — 管理员新建项目
  - GET  /api/v1/projects               — 公开列表（已发布）
  - GET  /api/v1/projects/public/{id}   — 公开详情
  - GET  /api/v1/projects/{id}          — 管理员详情
  - PUT  /api/v1/projects/{id}          — 更新项目
  - DELETE /api/v1/projects/{id}        — 删除项目
  - GET  /api/v1/projects/admin         — 管理员列表（所有）
  - github_repo 解析
"""
import pytest


# ── 工具函数 ────────────────────────────────────────────────

def create_project(client, auth_headers, **overrides):
    payload = {
        "name": "测试项目",
        "description": "这是一个测试项目",
        "github_url": "https://github.com/teng00123/personal-landing",
        "is_published": True,
        **overrides,
    }
    resp = client.post("/api/v1/projects", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── 新建 ────────────────────────────────────────────────────

class TestCreateProject:
    def test_create_project(self, client, admin_user, auth_headers):
        """管理员新建项目，返回 201，自动解析 github_repo，deploy_status 初始为 pending。"""
        proj = create_project(client, auth_headers)
        assert proj["id"] > 0
        assert proj["name"] == "测试项目"
        assert proj["github_repo"] == "teng00123/personal-landing"
        assert proj["deploy_status"] == "pending"
        # owner_id 不对外暴露（响应 schema 中不包含），此处验证可访问性即可
        assert "id" in proj

    def test_create_project_without_description(self, client, admin_user, auth_headers):
        """description 可选，不传应成功。"""
        proj = create_project(client, auth_headers, description=None)
        assert proj["id"] > 0
        assert proj["description"] is None

    def test_create_unpublished_project(self, client, admin_user, auth_headers):
        """创建未发布项目。"""
        proj = create_project(client, auth_headers, is_published=False)
        assert proj["is_published"] is False

    def test_create_project_requires_auth(self, client):
        """未认证应返回 401。"""
        resp = client.post(
            "/api/v1/projects",
            json={
                "name": "未授权项目",
                "github_url": "https://github.com/test/repo",
            },
        )
        assert resp.status_code == 401

    def test_github_repo_parsed_correctly(self, client, admin_user, auth_headers):
        """各种格式的 GitHub URL 应正确解析为 owner/repo。"""
        for url, expected in [
            ("https://github.com/alice/my-repo", "alice/my-repo"),
            ("https://github.com/alice/my-repo.git", "alice/my-repo"),
            ("https://github.com/alice/my-repo/tree/main", "alice/my-repo"),
        ]:
            resp = client.post(
                "/api/v1/projects",
                json={"name": f"proj-{expected}", "github_url": url},
                headers=auth_headers,
            )
            assert resp.status_code == 201, f"Failed for URL: {url}"
            assert resp.json()["github_repo"] == expected


# ── 公开列表 ────────────────────────────────────────────────

class TestPublicProjectList:
    def test_public_list_only_published(self, client, admin_user, auth_headers):
        """公开列表只返回已发布项目。"""
        create_project(client, auth_headers, name="已发布", is_published=True)
        create_project(client, auth_headers, name="未发布", is_published=False)

        resp = client.get("/api/v1/projects")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "已发布"

    def test_public_list_empty(self, client):
        """无项目时返回空列表。"""
        resp = client.get("/api/v1/projects")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_public_list_pagination(self, client, admin_user, auth_headers):
        """分页参数正常工作。"""
        for i in range(6):
            create_project(client, auth_headers, name=f"项目{i}", is_published=True)

        resp = client.get("/api/v1/projects?page=1&page_size=4")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 6
        assert len(data["items"]) == 4


# ── 公开详情 ────────────────────────────────────────────────

class TestPublicProjectDetail:
    def test_get_public_project(self, client, admin_user, auth_headers):
        """公开获取已发布项目详情。"""
        proj = create_project(client, auth_headers, is_published=True)
        resp = client.get(f"/api/v1/projects/public/{proj['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == proj["id"]

    def test_get_unpublished_project_public_returns_404(self, client, admin_user, auth_headers):
        """公开接口不能访问未发布项目。"""
        proj = create_project(client, auth_headers, is_published=False)
        resp = client.get(f"/api/v1/projects/public/{proj['id']}")
        assert resp.status_code == 404

    def test_get_nonexistent_project_returns_404(self, client):
        resp = client.get("/api/v1/projects/public/99999")
        assert resp.status_code == 404


# ── 管理员详情 ──────────────────────────────────────────────

class TestAdminProjectDetail:
    def test_admin_get_project(self, client, admin_user, auth_headers):
        """管理员获取任意项目（含未发布）。"""
        proj = create_project(client, auth_headers, is_published=False)
        resp = client.get(f"/api/v1/projects/{proj['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == proj["id"]

    def test_admin_get_not_found(self, client, admin_user, auth_headers):
        resp = client.get("/api/v1/projects/99999", headers=auth_headers)
        assert resp.status_code == 404


# ── 更新 ────────────────────────────────────────────────────

class TestUpdateProject:
    def test_update_name(self, client, admin_user, auth_headers):
        """更新项目名称。"""
        proj = create_project(client, auth_headers)
        resp = client.put(
            f"/api/v1/projects/{proj['id']}",
            json={"name": "新项目名称"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "新项目名称"

    def test_update_publish_status(self, client, admin_user, auth_headers):
        """将未发布项目改为已发布。"""
        proj = create_project(client, auth_headers, is_published=False)
        resp = client.put(
            f"/api/v1/projects/{proj['id']}",
            json={"is_published": True},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_published"] is True

    def test_update_tags_and_tech_stack(self, client, admin_user, auth_headers):
        """更新标签和技术栈字段。"""
        proj = create_project(client, auth_headers)
        resp = client.put(
            f"/api/v1/projects/{proj['id']}",
            json={"tags": "Python,FastAPI", "tech_stack": "Vue,Redis"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tags"] == "Python,FastAPI"
        assert data["tech_stack"] == "Vue,Redis"

    def test_update_nonexistent_returns_404(self, client, admin_user, auth_headers):
        resp = client.put(
            "/api/v1/projects/99999",
            json={"name": "x"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


# ── 删除 ────────────────────────────────────────────────────

class TestDeleteProject:
    def test_delete_project(self, client, admin_user, auth_headers):
        """删除项目后返回 204，再次查询返回 404。"""
        proj = create_project(client, auth_headers)
        resp = client.delete(f"/api/v1/projects/{proj['id']}", headers=auth_headers)
        assert resp.status_code == 204

        resp2 = client.get(f"/api/v1/projects/{proj['id']}", headers=auth_headers)
        assert resp2.status_code == 404

    def test_delete_nonexistent_returns_404(self, client, admin_user, auth_headers):
        resp = client.delete("/api/v1/projects/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_requires_auth(self, client, admin_user, auth_headers):
        """未认证删除应返回 401。"""
        proj = create_project(client, auth_headers)
        resp = client.delete(f"/api/v1/projects/{proj['id']}")
        assert resp.status_code == 401


# ── 管理员列表 ──────────────────────────────────────────────

class TestAdminProjectList:
    def test_admin_list_includes_unpublished(self, client, admin_user, auth_headers):
        """管理员列表包含已发布和未发布。"""
        create_project(client, auth_headers, name="P1", is_published=True)
        create_project(client, auth_headers, name="P2", is_published=False)

        resp = client.get("/api/v1/projects/admin", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    def test_admin_list_search(self, client, admin_user, auth_headers):
        """管理员列表支持按名称搜索。"""
        create_project(client, auth_headers, name="VueProject")
        create_project(client, auth_headers, name="FastAPIProject")

        resp = client.get("/api/v1/projects/admin?q=Vue", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert "Vue" in data["items"][0]["name"]

    def test_admin_list_requires_auth(self, client):
        resp = client.get("/api/v1/projects/admin")
        assert resp.status_code == 401
