"""
RBAC 权限模型 — Iteration 6
细粒度角色/权限控制
角色: super_admin > admin > editor > viewer
"""
from __future__ import annotations

from enum import Enum
from typing import Set

from fastapi import Depends, HTTPException

from app.api.auth import get_current_user
from app.models.user import User


class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN       = "admin"
    EDITOR      = "editor"
    VIEWER      = "viewer"


class Permission(str, Enum):
    # 文章
    ARTICLE_READ    = "article:read"
    ARTICLE_CREATE  = "article:create"
    ARTICLE_UPDATE  = "article:update"
    ARTICLE_DELETE  = "article:delete"
    ARTICLE_PUBLISH = "article:publish"
    # 项目
    PROJECT_READ    = "project:read"
    PROJECT_CREATE  = "project:create"
    PROJECT_UPDATE  = "project:update"
    PROJECT_DELETE  = "project:delete"
    PROJECT_DEPLOY  = "project:deploy"
    # 用户管理
    USER_READ       = "user:read"
    USER_CREATE     = "user:create"
    USER_UPDATE     = "user:update"
    USER_DELETE     = "user:delete"
    # 系统
    SYSTEM_CONFIG   = "system:config"
    SYSTEM_AUDIT    = "system:audit"
    SYSTEM_SECURITY = "system:security"


# 角色 → 权限映射
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.VIEWER: {
        Permission.ARTICLE_READ,
        Permission.PROJECT_READ,
    },
    Role.EDITOR: {
        Permission.ARTICLE_READ,
        Permission.ARTICLE_CREATE,
        Permission.ARTICLE_UPDATE,
        Permission.PROJECT_READ,
    },
    Role.ADMIN: {
        Permission.ARTICLE_READ,
        Permission.ARTICLE_CREATE,
        Permission.ARTICLE_UPDATE,
        Permission.ARTICLE_DELETE,
        Permission.ARTICLE_PUBLISH,
        Permission.PROJECT_READ,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        Permission.PROJECT_DEPLOY,
        Permission.USER_READ,
        Permission.SYSTEM_AUDIT,
    },
    Role.SUPER_ADMIN: set(Permission),  # 全部权限
}

# 角色继承层级（数字越大权限越高）
ROLE_LEVEL: dict[Role, int] = {
    Role.VIEWER:      1,
    Role.EDITOR:      2,
    Role.ADMIN:       3,
    Role.SUPER_ADMIN: 4,
}


def get_user_role(user: User) -> Role:
    """从 User 模型推断角色"""
    if not user.is_active:
        return Role.VIEWER
    if user.is_admin:
        return Role.ADMIN
    return Role.EDITOR


def has_permission(user: User, permission: Permission) -> bool:
    role = get_user_role(user)
    return permission in ROLE_PERMISSIONS.get(role, set())


def require_permission(permission: Permission):
    """FastAPI 依赖：要求指定权限"""
    def dep(user: User = Depends(get_current_user)) -> User:
        if not has_permission(user, permission):
            raise HTTPException(
                403,
                f"权限不足：需要 {permission.value}",
            )
        return user
    return dep


def require_role(min_role: Role):
    """FastAPI 依赖：要求最低角色级别"""
    def dep(user: User = Depends(get_current_user)) -> User:
        role = get_user_role(user)
        if ROLE_LEVEL.get(role, 0) < ROLE_LEVEL.get(min_role, 0):
            raise HTTPException(
                403,
                f"需要 {min_role.value} 或更高权限",
            )
        return user
    return dep
