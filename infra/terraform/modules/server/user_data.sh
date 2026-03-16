#!/bin/bash
# infra/terraform/modules/server/user_data.sh
# 服务器初始化脚本（Ubuntu 22.04）

set -euo pipefail
ENV="${env}"

echo "▶ Bootstrapping personal-landing ($ENV) server..."

# ── 系统更新 ──────────────────────────────────────────────
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
  curl wget git vim htop \
  docker.io docker-compose-plugin \
  nginx certbot python3-certbot-nginx \
  fail2ban ufw

# ── Docker 配置 ───────────────────────────────────────────
systemctl enable --now docker
usermod -aG docker ubuntu

# ── UFW 防火墙 ────────────────────────────────────────────
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    comment "SSH"
ufw allow 80/tcp    comment "HTTP"
ufw allow 443/tcp   comment "HTTPS"
ufw --force enable

# ── fail2ban 防暴力破解 ───────────────────────────────────
cat > /etc/fail2ban/jail.local << 'FAIL2BAN'
[sshd]
enabled  = true
maxretry = 5
findtime = 300
bantime  = 3600
FAIL2BAN
systemctl enable --now fail2ban

# ── 应用目录 ──────────────────────────────────────────────
mkdir -p /opt/personal-landing
cd /opt/personal-landing

# ── 克隆代码 ──────────────────────────────────────────────
git clone https://github.com/teng00123/personal-landing.git . || git pull

# ── 环境标识 ──────────────────────────────────────────────
echo "$ENV" > /opt/personal-landing/.deploy-env

echo "✅ Bootstrap complete for env=$ENV"
