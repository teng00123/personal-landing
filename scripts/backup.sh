#!/bin/bash
# scripts/backup.sh — 自动化备份脚本（数据库 + uploads）
# 用法: ./scripts/backup.sh [daily|weekly|manual]
# 配套 crontab:
#   0 2 * * * /opt/personal-landing/scripts/backup.sh daily
#   0 3 * * 0 /opt/personal-landing/scripts/backup.sh weekly

set -euo pipefail

BACKUP_TYPE="${1:-daily}"
APP_DIR="/opt/personal-landing"
BACKUP_DIR="${APP_DIR}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAILY=7    # 保留最近 7 天
RETENTION_WEEKLY=4   # 保留最近 4 周

# ── 颜色输出 ──────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

mkdir -p "${BACKUP_DIR}/${BACKUP_TYPE}"
DEST="${BACKUP_DIR}/${BACKUP_TYPE}/${TIMESTAMP}"
mkdir -p "$DEST"

log "Starting $BACKUP_TYPE backup → $DEST"

# ── 1. 数据库备份 ─────────────────────────────────────────
log "Backing up MySQL..."
DB_CONTAINER=$(docker ps --filter "name=personal-landing_db" --format "{{.Names}}" | head -1 || true)
if [ -n "$DB_CONTAINER" ]; then
  DB_PASS=$(grep DB_PASSWORD "${APP_DIR}/.env" | cut -d= -f2 | tr -d ' ')
  DB_USER=$(grep DB_USER "${APP_DIR}/.env" | cut -d= -f2 | tr -d ' ')
  DB_NAME=$(grep DB_NAME "${APP_DIR}/.env" | cut -d= -f2 | tr -d ' ')

  docker exec "$DB_CONTAINER" \
    mysqldump -u"$DB_USER" -p"$DB_PASS" --single-transaction --quick "$DB_NAME" \
    | gzip > "${DEST}/database.sql.gz"
  log "DB backup: $(du -sh "${DEST}/database.sql.gz" | cut -f1)"
else
  warn "DB container not found, skipping DB backup"
fi

# ── 2. 上传文件备份 ───────────────────────────────────────
log "Backing up uploads..."
if [ -d "${APP_DIR}/uploads" ]; then
  tar -czf "${DEST}/uploads.tar.gz" -C "${APP_DIR}" uploads/
  log "Uploads backup: $(du -sh "${DEST}/uploads.tar.gz" | cut -f1)"
else
  warn "uploads directory not found"
fi

# ── 3. 配置文件备份 ───────────────────────────────────────
log "Backing up configs..."
tar -czf "${DEST}/configs.tar.gz" \
  -C "${APP_DIR}" \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  .env \
  docker-compose.yml \
  docker-compose.prod.yml \
  monitoring/prometheus/prometheus.yml \
  monitoring/alertmanager/alertmanager.yml \
  2>/dev/null || warn "Some config files missing (non-fatal)"

# ── 4. 生成校验文件 ───────────────────────────────────────
log "Generating checksums..."
cd "$DEST" && sha256sum * > SHA256SUMS 2>/dev/null || true

# ── 5. 备份清理 ───────────────────────────────────────────
log "Pruning old backups..."
if [ "$BACKUP_TYPE" = "daily" ]; then
  find "${BACKUP_DIR}/daily" -maxdepth 1 -type d -mtime +${RETENTION_DAILY} -exec rm -rf {} + 2>/dev/null || true
elif [ "$BACKUP_TYPE" = "weekly" ]; then
  find "${BACKUP_DIR}/weekly" -maxdepth 1 -type d -mtime +$((RETENTION_WEEKLY * 7)) -exec rm -rf {} + 2>/dev/null || true
fi

# ── 6. 备份统计 ───────────────────────────────────────────
TOTAL_SIZE=$(du -sh "$DEST" | cut -f1)
log "✅ Backup complete: type=$BACKUP_TYPE size=$TOTAL_SIZE path=$DEST"

# ── 7. 可选：上传到 S3 ────────────────────────────────────
if command -v aws &>/dev/null && [ -n "${S3_BACKUP_BUCKET:-}" ]; then
  log "Uploading to S3: s3://${S3_BACKUP_BUCKET}/backups/${BACKUP_TYPE}/${TIMESTAMP}/"
  aws s3 cp "$DEST" "s3://${S3_BACKUP_BUCKET}/backups/${BACKUP_TYPE}/${TIMESTAMP}/" \
    --recursive --quiet
  log "✅ S3 upload complete"
fi
