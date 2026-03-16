# Personal Landing — 迭代路线图

> **当前版本**: v0.8.x | **最后更新**: 2026-03-16
> **GitHub**: https://github.com/teng00123/personal-landing

---

## 🎯 总体愿景

将 Personal Landing 打造成**企业级个人品牌展示平台**，具备现代化架构、卓越用户体验和完善的运维体系。

---

## 📈 迭代状态总览

| 迭代 | 代号 | 主题 | 版本 | 状态 |
|------|------|------|------|------|
| Iter 1 | Foundation | 基础架构 | v0.1.0 | ✅ 已完成 |
| Iter 2 | Content | 内容管理 | v0.2.0 | ✅ 已完成 |
| Iter 3 | Deploy | 项目部署 | v0.3.0 | ✅ 已完成 |
| Iter 4 | Performance | 性能优化与监控 | v0.4.0 | ✅ 已完成 |
| Iter 5 | UX-Enhance | 用户体验增强 | v0.5.0 | ✅ 已完成 |
| Iter 6 | Security | 安全加固 | v0.6.0 | ✅ 已完成 |
| Iter 7 | DevOps | 部署运维自动化 | v0.7.0 | ✅ 已完成 |
| Iter 8 | Advanced | 高级功能扩展 | v0.8.x | 🚧 进行中 |
| Iter 9 | Mobile | 移动端适配 | v0.9.0 | 📋 计划中 |
| Iter 10 | Open | 开放平台 | v1.0.0 | 📋 计划中 |

---

## ✅ Iteration 1 — Foundation（基础架构）

**目标**: 搭建可运行的全栈脚手架

- [x] FastAPI 后端脚手架（路由/中间件/异常处理）
- [x] Vue 3 + Vite 前端脚手架
- [x] MySQL + SQLAlchemy ORM + Alembic 迁移
- [x] JWT 身份认证（bcrypt + SHA-256）
- [x] Docker Compose 开发环境
- [x] 简历/个人信息展示 API
- [x] GitHub 项目列表展示

---

## ✅ Iteration 2 — Content Management（内容管理）

**目标**: 完整的 Markdown 文章管理系统

- [x] Markdown 文件上传与解析
- [x] 自动提取标题、标签、摘要
- [x] 文章发布/草稿状态管理
- [x] 文章阅读量统计
- [x] 文件附件上传管理
- [x] 管理员后台 API

---

## ✅ Iteration 3 — Project Deployment（项目部署）

**目标**: GitHub 项目一键自动部署

- [x] GitHub 项目导入（API 拉取仓库信息）
- [x] 多框架自动检测（Vue/React/Next.js/FastAPI/Flask/Django）
- [x] Celery 异步部署任务
- [x] WebSocket 实时日志推送
- [x] 端口自动分配（8100-9000）
- [x] Docker 容器部署支持

---

## ✅ Iteration 4 — Performance & Monitoring（性能优化与监控）

**目标**: 系统性能提升 + 完整可观测性

- [x] 前端 Vite 代码分割（vendor chunks）
- [x] PWA / Service Worker（StaleWhileRevalidate + CacheFirst）
- [x] Terser 生产压缩，移除 console
- [x] 后端 Redis 异步缓存（`CacheManager` + `@cache()` 装饰器）
- [x] Prometheus 指标采集中间件 + `/metrics` 端点
- [x] 结构化 JSON 日志（生产）/ 可读格式（开发）
- [x] 数据库连接池调优（pool_size 20, max_overflow 30）
- [x] Prometheus + Grafana + Alertmanager 监控栈
- [x] 7 条告警规则（CPU/内存/磁盘/Redis/API 错误率/响应时间）
- [x] Grafana 8 面板概览仪表盘

---

## ✅ Iteration 5 — UX Enhancement（用户体验增强）

**目标**: 现代化用户体验，深度交互优化

- [x] 主题系统（Dark / Light / Auto，跟随系统偏好，localStorage 持久化）
- [x] 全文搜索（⌘K 唤起，防抖，关键词高亮，热词推荐）
- [x] WebSocket 实时通知（部署/系统事件，自动重连指数退避）
- [x] 社交功能（点赞 IP 去重，嵌套评论，XSS 过滤）
- [x] 页面路由切换动画（opacity + translateY）
- [x] 移动端工具栏（搜索 + 主题 + 语言切换）
- [x] 国际化扩展（搜索/主题/评论/点赞 i18n key）

---

## ✅ Iteration 6 — Security Hardening（安全加固）

**目标**: 企业级安全防护体系

- [x] TOTP 双因子认证（MFA），QR 码扫描注册
- [x] RBAC 角色权限控制（Role/Permission 枚举，依赖注入）
- [x] Redis 滑动窗口限流中间件
- [x] IP 封禁管理器
- [x] 审计日志（AuditLog ORM，同步/异步写入）
- [x] 安全工具集（email/phone/IP 脱敏，HTML 净化，密码强度检测）
- [x] Token 刷新、登出、改密 API
- [x] CI 安全扫描（Bandit / Trivy / OWASP ZAP / safety）

---

## ✅ Iteration 7 — DevOps Automation（运维自动化）

**目标**: 全套 DevOps 自动化，生产级运维能力

- [x] GitHub Actions 多环境 CI/CD 流水线
- [x] 蓝绿部署（健康检查 + Nginx 热切换 + 自动回滚）
- [x] Terraform IaC（AWS EC2 + EIP + SG，staging/production 独立 workspace）
- [x] Ansible Playbook（common/docker/nginx/app/monitoring 角色）
- [x] Kubernetes（Deployment + HPA + Ingress + cert-manager）
- [x] 多环境 Docker Compose（dev/staging/prod）
- [x] Nginx 生产配置（SSL/HTTP2/HSTS/CSP，双限流区）
- [x] 自动备份脚本（MySQL + uploads，daily/weekly 保留策略，S3 可选）
- [x] 健康检查守护进程（3 次失败自动重启 + WeCom 告警）

---

## 🚧 Iteration 8 — Advanced Features（高级功能扩展）

**目标**: AI 驱动的高级交互功能

- [x] AI 对话助手（上下文感知，后端 `/api/v1/ai/*`）
- [x] Monaco Editor 在线代码编辑器
- [x] 代码运行沙箱（多语言执行，`/api/v1/sandbox/*`）
- [x] 社区功能（`/api/v1/community/*`）
- [ ] AI 代码补全集成
- [ ] 代码分享与 Fork 功能
- [ ] 用户活动流/时间线

---

## 📋 Iteration 9 — Mobile（移动端适配）

**目标**: 原生移动端体验

- [ ] 响应式布局全面优化（320px-1920px）
- [ ] 触摸手势支持（滑动翻页、下拉刷新）
- [ ] PWA 离线功能增强
- [ ] 移动端导航重设计
- [ ] 图片懒加载与 WebP 自动转换
- [ ] 移动端性能优化（首屏 < 2s）

---

## 📋 Iteration 10 — Open Platform（开放平台）

**目标**: 生态开放，支持第三方接入

- [ ] OpenAPI 3.0 完整规范文档
- [ ] Webhook 事件系统
- [ ] OAuth2 第三方登录（GitHub / Google）
- [ ] 开放 API 密钥管理
- [ ] 插件/主题市场
- [ ] 多用户支持（SaaS 模式）

---

## 🔗 相关文档

- [CHANGELOG.md](CHANGELOG.md) — 详细变更历史
- [ITERATION_PLAN.md](ITERATION_PLAN.md) — 各迭代任务清单
- [后端 API 文档](http://localhost:8000/docs) — Swagger UI（本地运行后访问）
