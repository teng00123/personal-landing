#!/bin/bash
# scripts/healthcheck_watchdog.sh — 故障自愈看门狗
# 定时检测应用健康状态，异常时自动重启并告警
# crontab: */5 * * * * /opt/personal-landing/scripts/healthcheck_watchdog.sh

set -euo pipefail

APP_DIR="/opt/personal-landing"
LOG_FILE="${APP_DIR}/logs/watchdog.log"
STATE_FILE="/tmp/pl_watchdog_state"
HEALTH_URL="${HEALTH_URL:-http://localhost:8000/health}"
MAX_FAILURES=3      # 连续失败 3 次才重启
NOTIFY_WEBHOOK="${WECOM_WEBHOOK:-}"

mkdir -p "${APP_DIR}/logs"

ts() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "[$(ts)] $*" | tee -a "$LOG_FILE"; }

# ── 读取连续失败计数 ──────────────────────────────────────
FAILURES=$(cat "$STATE_FILE" 2>/dev/null || echo "0")

# ── 健康检查 ──────────────────────────────────────────────
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$HEALTH_URL" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
  # 健康：重置计数
  if [ "$FAILURES" -gt 0 ]; then
    log "✅ Service recovered (was ${FAILURES} failures)"
    _notify "✅ personal-landing 已恢复正常"
  fi
  echo "0" > "$STATE_FILE"
  exit 0
fi

# ── 不健康 ────────────────────────────────────────────────
FAILURES=$((FAILURES + 1))
echo "$FAILURES" > "$STATE_FILE"
log "⚠️ Health check failed (HTTP $HTTP_CODE) — failure #${FAILURES}"

if [ "$FAILURES" -lt "$MAX_FAILURES" ]; then
  log "Waiting for more failures before restart (${FAILURES}/${MAX_FAILURES})"
  exit 0
fi

# ── 达到阈值，执行重启 ────────────────────────────────────
log "🔄 Restarting application (${FAILURES} consecutive failures)..."

cd "$APP_DIR"
docker compose restart backend celery 2>&1 | tee -a "$LOG_FILE" || true

# 等待重启
sleep 20

# 重启后再检查
NEW_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$HEALTH_URL" || echo "000")
if [ "$NEW_CODE" = "200" ]; then
  log "✅ Restart successful — service is healthy"
  echo "0" > "$STATE_FILE"
  _notify "🔄 personal-landing 自动重启成功"
else
  log "❌ Restart failed — service still unhealthy (HTTP $NEW_CODE)"
  _notify "❌ personal-landing 重启失败！需要人工介入 (HTTP $NEW_CODE)"
fi

# ── 企业微信通知函数 ──────────────────────────────────────
_notify() {
  local msg="$1"
  if [ -n "$NOTIFY_WEBHOOK" ]; then
    curl -s -X POST "$NOTIFY_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{\"msgtype\":\"text\",\"text\":{\"content\":\"[personal-landing watchdog] ${msg}\"}}" \
      > /dev/null 2>&1 || true
  fi
}
