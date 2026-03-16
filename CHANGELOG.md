# Changelog

All notable changes to **personal-landing** are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/).

---

## [Unreleased] — 2026-03-16

### ✨ Features

- **iter4**: Performance optimization & monitoring system ([45dcc5c])
  - Frontend: code splitting by vendor chunks, PWA/Service Worker, Terser minification
  - Backend: async Redis `CacheManager`, `@cache()` decorator, Prometheus metrics middleware
  - Structured JSON logging (`logging_config.py`)
  - Database connection pool tuned (pool_size 10→20, max_overflow 20→30)
  - Articles API: public routes now Redis-cached (list 2min / detail 5min), writes auto-invalidate
- **iter4**: Complete Iteration 4 — Performance Optimization & Monitoring ([6057b0f])
  - Prometheus + Grafana + Alertmanager + node_exporter + redis_exporter (`docker-compose.monitoring.yml`)
  - 7 alert rules: HighErrorRate, SlowAPIResponse, HighCPUUsage, HighMemoryUsage, HighDiskUsage, RedisHighMemory, RedisTooManyConnections
  - Grafana auto-provisioned 8-panel overview dashboard
  - `RETROSPECTIVE_FRAMEWORK.md` + `iteration-4-performance/IMPLEMENTATION.md`
- **roadmap**: Add comprehensive iteration roadmap and planning documents ([23f8c86])
  - `ROADMAP.md`: full 5-iteration product roadmap
  - `ITERATION_PLAN.md`: detailed task checklists per iteration
- **i18n**: Add comprehensive internationalization support ([bb50e7c])
  - Frontend: `vue-i18n@9`, `LanguageSwitcher.vue`, locales `zh-CN.json` / `en-US.json`
  - Backend: custom `I18n` class with JSON locale files, wired into error handlers
- **license**: Add MIT LICENSE file ([b418dd0])
- **readme**: Beautify bilingual README files with modern design ([14335fa])
  - Emojis, badges, feature tables, structured layout for both `README.md` and `README_EN.md`
- **readme**: Add cross-links between Chinese and English READMEs ([633dca2])
- **readme**: Add English `README_EN.md` for international users ([f09ed21])

---

## [v0.3.0] — 2026-03-13

### ✨ Features

- **iter3**: Celery auto-deploy — GitHub projects with real-time logs ([43c0a39])
- **docs**: Add Celery documentation ([40719ed])
- **tests**: Add basic tests and comprehensive documentation ([3d3c95b])
- **polish**: Project polish — security, UX, responsiveness ([c500f9b])
- **db**: Robust DB init — auto-create DB, seed data, wait_for_db, Makefile ([3986eb7])

### 🐛 Bug Fixes

- **iter3**: Fix import issue #12 ([92abd72])
- **ci**: Resolve bcrypt compatibility & password length issues ([31887af])
- **ci**: Set `PYTHONPATH=.` and suppress SQLAlchemy mypy false positives ([76a7a98])
- **ci**: Resolve all ruff lint errors ([453f3f4])
- **bcrypt**: Pre-hash password with SHA-256 to bypass 72-byte limit ([d04997b])
- **tests**: Resolve review comments in test file ([fb836e9])

### 👷 CI/CD

- Add GitHub Actions workflows ([8d2dcce])
- Fix duplicate workflow triggers on feature branches ([424e730])

---

## [v0.2.0] — 2026-03-13

### ✨ Features

- **iter2**: Article system — MD upload, editor, cover image ([ce50ce1])

---

## [v0.1.0] — 2026-03-13

### ✨ Features

- **iter1**: Full-stack personal homepage skeleton ([bec262f])

---

<!-- Commit short refs -->
[45dcc5c]: https://github.com/teng00123/personal-landing/commit/45dcc5c
[6057b0f]: https://github.com/teng00123/personal-landing/commit/6057b0f
[23f8c86]: https://github.com/teng00123/personal-landing/commit/23f8c86
[bb50e7c]: https://github.com/teng00123/personal-landing/commit/bb50e7c
[b418dd0]: https://github.com/teng00123/personal-landing/commit/b418dd0
[14335fa]: https://github.com/teng00123/personal-landing/commit/14335fa
[633dca2]: https://github.com/teng00123/personal-landing/commit/633dca2
[f09ed21]: https://github.com/teng00123/personal-landing/commit/f09ed21
[43c0a39]: https://github.com/teng00123/personal-landing/commit/43c0a39
[40719ed]: https://github.com/teng00123/personal-landing/commit/40719ed
[3d3c95b]: https://github.com/teng00123/personal-landing/commit/3d3c95b
[c500f9b]: https://github.com/teng00123/personal-landing/commit/c500f9b
[3986eb7]: https://github.com/teng00123/personal-landing/commit/3986eb7
[92abd72]: https://github.com/teng00123/personal-landing/commit/92abd72
[31887af]: https://github.com/teng00123/personal-landing/commit/31887af
[76a7a98]: https://github.com/teng00123/personal-landing/commit/76a7a98
[453f3f4]: https://github.com/teng00123/personal-landing/commit/453f3f4
[d04997b]: https://github.com/teng00123/personal-landing/commit/d04997b
[fb836e9]: https://github.com/teng00123/personal-landing/commit/fb836e9
[8d2dcce]: https://github.com/teng00123/personal-landing/commit/8d2dcce
[424e730]: https://github.com/teng00123/personal-landing/commit/424e730
[ce50ce1]: https://github.com/teng00123/personal-landing/commit/ce50ce1
[bec262f]: https://github.com/teng00123/personal-landing/commit/bec262f
