# Changelog

All notable changes to **personal-landing** are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/).

---

## [v0.8.x] — 2026-03-16 · Iteration 8: Advanced Features

### 🐛 Bug Fixes
- **fix**: remove TypeScript syntax from JS files and fix named import of `http` ([93cbe96])
  - `src/store/theme.js`: removed `export type`, `ref<T>`, parameter type annotations
  - `SearchModal.vue` / `MFASetup.vue`: `import { http }` → `import http` (default export)
- **fix**: handle CJS default export for `vite-plugin-monaco-editor` ([1722544])
  - Use `plugin.default || plugin` to handle both CJS and ESM export shapes
- **fix**: replace non-existent `@monaco-editor/vite-plugin` with `vite-plugin-monaco-editor` ([aada164])
- **fix**: remove `query_cache_type` session variable, unsupported in MySQL 8.0+ ([62e5fc8])

### ✨ Features
- **feat(iter8)**: Advanced Features — AI, Code Playground, Community & Activity System ([f6cd8b7])
  - `backend/app/api/ai.py` — AI chat assistant endpoint
  - `backend/app/api/community.py` — community features
  - `backend/app/api/sandbox.py` — code execution sandbox
  - `frontend/src/components/AIAssistant.vue` — AI chat UI
  - `frontend/src/components/CodePlayground.vue` — Monaco Editor-based code runner

---

## [v0.7.0] — 2026-03-16 · Iteration 7: DevOps Automation

### ✨ Features
- **feat(iter7)**: DevOps Automation — CI/CD, Blue-Green, IaC, K8s & Auto-Ops ([3a4ba31])

#### CI/CD Workflows
  - `.github/workflows/deploy.yml` — multi-env pipeline: PR→CI, push main→staging SSH, tag v*→blue-green prod, dispatch→rollback
  - `.github/workflows/terraform.yml` — auto plan on PR, manual apply/destroy via dispatch

#### Blue-Green Deployment
  - Detect blue/green slot → start new → 12×5s health poll → Nginx upstream swap → stop old
  - `nginx/prod.conf` — SSL+HTTP2, HSTS/CSP/XFO/XCTO headers, dual rate-limit zones, WebSocket timeout

#### Multi-Env Docker Compose
  - `docker-compose.staging.yml` — port 8080, 3-day Prometheus retention
  - `docker-compose.prod.yml` — resource limits (2CPU/2GB), restart:always, certbot volume

#### Terraform IaC
  - `infra/terraform/modules/server/` — EC2+EIP+SG module, encrypted gp3, create_before_destroy
  - `infra/terraform/environments/staging|production/` — S3+DynamoDB backend

#### Ansible
  - `infra/ansible/site.yml` — roles: common→docker→nginx→app→monitoring
  - Roles: UFW, fail2ban, Docker CE, git pull, compose up --wait

#### Kubernetes
  - `infra/k8s/base/` — RollingUpdate, HPA (CPU 70%/Mem 80%, 2-10 pods), cert-manager ingress
  - `infra/k8s/overlays/production/` — 3 replicas, higher limits

#### Auto-Ops Scripts
  - `scripts/backup.sh` — MySQL dump + uploads tar, SHA256, daily(7d)/weekly(4w), S3 optional
  - `scripts/healthcheck_watchdog.sh` — 3-strike → docker compose restart → WeCom webhook

---

## [v0.6.0] — 2026-03-16 · Iteration 6: Security Hardening

### ✨ Features
- **feat(iter6)**: Security Hardening — MFA, RBAC, rate-limiting & audit ([4e599c4])
  - `backend/app/utils/mfa.py` — TOTP (pyotp), QR code PNG as base64
  - `backend/app/utils/rbac.py` — Role/Permission enums, `require_permission` / `require_role` deps
  - `backend/app/utils/rate_limit.py` — Redis sliding-window middleware, `IPBlocklistManager`
  - `backend/app/utils/audit.py` — AuditLog ORM, sync+async write
  - `backend/app/utils/security_tools.py` — `mask_email/phone/ip`, `sanitize_html`, password strength check
  - `backend/app/api/security.py` — `/mfa/*`, `/refresh`, `/logout`, `/change-password`, `/blocklist`, `/audit-logs`
  - `frontend/src/components/MFASetup.vue` — QR scan flow, TOTP confirm
  - `.github/workflows/security.yml` — Bandit, Trivy, OWASP ZAP, safety

### 🐛 Bug Fixes
- **fix(lint)**: resolve all Ruff CI errors ([2480f2e])
  - `UP035` `UP041` `UP037` `I001` `E711` `F401` `E741`

---

## [v0.5.0] — 2026-03-16 · Iteration 5: UX Enhancement

### ✨ Features
- **feat(iter5)**: UX Enhancement — theme system, search, realtime & social ([78a0b39])

#### Theme System
  - `frontend/src/store/theme.js` — Pinia store, dark/light/auto, `prefers-color-scheme`, localStorage persist
  - `frontend/src/components/ThemeSwitcher.vue` — ☀️🌗🌙 3-button toggle
  - `global.css` — `[data-theme="light"]` CSS vars, 0.25s smooth transition, Element Plus overrides

#### Full-text Search
  - `frontend/src/components/SearchModal.vue` — ⌘K/Ctrl+K, 280ms debounce, keyword highlight, hot keywords
  - `backend/app/api/search.py` — `/search` (MySQL ilike + Redis 60s), `/suggest` (120s), `/hot` (Redis zset)

#### Real-time Notifications
  - `frontend/src/composables/useWebSocket.js` — auto-reconnect (exponential backoff max 30s), 20s ping
  - `backend/app/api/websocket.py` — `ConnectionManager` multi-channel, `notify_deploy()` / `notify_system()`

#### Social Features
  - `backend/app/api/social.py` — Redis IP-deduped likes, threaded comments (parent_id FK), XSS filter

#### Animations
  - `App.vue` — `page-fade` route transition (opacity + translateY, 0.22s)
  - `PublicLayout.vue` — navbar integrates Search + ThemeSwitcher + LanguageSwitcher

---

## [v0.4.0] — 2026-03-16 · Iteration 4: Performance & Monitoring

### ✨ Features
- **feat(iter4)**: Performance optimization & monitoring system ([45dcc5c])

#### Frontend
  - `vite.config.js` — `manualChunks` (vendor-vue/ui/i18n/marked), PWA StaleWhileRevalidate 5min, CacheFirst 7d
  - Terser minify with `drop_console: true` in prod, CSS code splitting

#### Backend
  - `backend/app/utils/cache.py` — async `CacheManager` (get/set/delete/clear_pattern), `@cache()` decorator
  - `backend/app/utils/metrics.py` — Prometheus counters/histograms/gauges, HTTP middleware, `/metrics`
  - `backend/app/utils/logging_config.py` — `JSONFormatter` for prod, readable for dev
  - `backend/app/db/session.py` — pool_size 10→20, max_overflow 20→30, pool_timeout=10s
  - `backend/app/api/articles.py` — async + Redis cached, writes invalidate cache

#### Monitoring Stack
  - `docker-compose.monitoring.yml` — Prometheus 2.47, Grafana 10.2, Alertmanager 0.26, exporters
  - 7 alert rules: HighErrorRate, SlowAPIResponse, HighCPUUsage, HighMemoryUsage, HighDiskUsage, RedisHighMemory, RedisTooManyConnections
  - Grafana 8-panel overview dashboard (RPS, error rate, P95, article views, latency, CPU, memory)

---

## [v0.3.0] — 2026-03-13 · Iteration 3: Core Features

### ✨ Features
- Project deployment system (GitHub import, multi-framework support)
- Real-time log streaming via WebSocket
- Automatic port allocation (8100-9000)
- Celery task queue for async deployment

---

## [v0.2.0] — 2026-03-13 · Iteration 2: Content Management

### ✨ Features
- Markdown article upload, edit, publish
- Auto title/tag extraction
- Article read statistics
- File upload management

---

## [v0.1.0] — 2026-03-13 · Iteration 1: Foundation

### ✨ Features
- FastAPI backend scaffold
- Vue 3 + Vite frontend scaffold
- MySQL + SQLAlchemy ORM
- JWT authentication (bcrypt + SHA-256)
- Docker Compose dev environment
- Resume/profile display API
- GitHub project listing

---

[v0.8.x]: https://github.com/teng00123/personal-landing/compare/v0.7.0...HEAD
[v0.7.0]: https://github.com/teng00123/personal-landing/compare/v0.6.0...v0.7.0
[v0.6.0]: https://github.com/teng00123/personal-landing/compare/v0.5.0...v0.6.0
[v0.5.0]: https://github.com/teng00123/personal-landing/compare/v0.4.0...v0.5.0
[v0.4.0]: https://github.com/teng00123/personal-landing/compare/v0.3.0...v0.4.0
[v0.3.0]: https://github.com/teng00123/personal-landing/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/teng00123/personal-landing/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/teng00123/personal-landing/releases/tag/v0.1.0
