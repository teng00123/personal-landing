# 迭代计划 · Personal Landing

> GitHub: https://github.com/teng00123/personal-landing

---

## 迭代总览

| 迭代 | 主题 | 状态 |
|------|------|------|
| **Iter 1** | 项目骨架 + 后端核心 + 可运行环境 | ✅ 完成 |
| **Iter 2** | 文章系统（上传 .md / 编辑器 / 渲染） | ✅ 完成 |
| **Iter 3** | 项目展示 + Celery 自动部署 | 🔜 计划中 |

---

## Iteration 1 — 项目骨架（已完成）

### 交付物
- Docker Compose 一键启动（MySQL 8 / Redis 7 / FastAPI / Celery / Vue 3 Dev Server）
- 后端全套 API（认证、Profile、文章 CRUD、项目 CRUD）
- Alembic 迁移框架 + `init_db.py` 一键初始化
- 前端完整路由体系 + 暗色主题 UI
- 首页简历展示（工作经历时间轴、技能进度条、教育背景）
- 文章列表 + 文章详情（Markdown 渲染，含语法高亮）
- 项目列表（展示部署状态）
- 管理后台骨架（个人资料编辑）

---

## Iteration 2 — 文章系统（已完成）

### 交付物

#### 后端新增
| 接口 | 说明 |
|------|------|
| `POST /api/v1/articles/upload-md` | 上传 `.md` 文件，自动解析标题/摘要/标签，保存为草稿 |
| `POST /api/v1/articles/{id}/cover` | 上传封面图（JPEG/PNG/WebP，≤5MB），存 `/uploads/covers/` |
| `GET  /api/v1/articles/admin` | 管理员文章列表，支持 `q`（标题搜索）、`published` 筛选 |
| `PUT  /api/v1/articles/{id}` | 更新文章，`is_published` 切换时自动写入 `published_at` |
| `DELETE /api/v1/articles/{id}` | 删除文章同时清理封面图文件 |

#### 前端新增
- **ArticleManager.vue** — 文章管理列表
  - 搜索框 + 发布状态筛选
  - 一键上传 `.md` 文件，自动跳转编辑器
  - 发布/取消发布 Switch 实时切换
  - 编辑 / 预览 / 删除操作
- **ArticleEditor.vue** — 分栏 Markdown 编辑器
  - 左栏：标题、摘要、标签、封面图上传、发布开关 + Markdown 编辑区
  - 右栏：实时预览（marked + highlight.js）
  - 工具栏：B / I / ` ` / 代码块 / H2 / H3 / 列表 / 引用 / 链接 / 图片
  - 支持 Tab 缩进、导入 `.md` 文件覆盖

### 用法
```
后台 → 文章管理 → 点击「上传.md」选择文件 → 自动解析标题/摘要 → 进入编辑器完善内容
后台 → 文章管理 → 点击「新建文章」→ 在编辑器中手写 Markdown
切换 is_published = true → 立即在前台文章列表可见
```

---

## Iteration 3 — 项目自动部署（计划）

### 计划功能
- [ ] 后台录入 GitHub URL + branch + 自定义命令
- [ ] Celery Task `deploy_project`：git clone → 框架识别 → 安装依赖 → 构建 → 启动
- [ ] 支持框架：Vue/React/Next.js/Node/FastAPI/Flask/Django/Static/Docker
- [ ] 端口自动分配（8100~9000）
- [ ] 部署日志轮询（`GET /projects/{id}/logs`）
- [ ] 状态：pending → deploying → running / failed
- [ ] 停止 / 重新部署操作
- [ ] 前端卡片：运行状态绿点 + "访问" 按钮
