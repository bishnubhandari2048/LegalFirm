#!/usr/bin/env bash
# ============================================================================
# Vidhi Law Firm Management System - Linux VPS Deployment Script
# Target OS: Ubuntu / Debian with Docker & Docker Compose
# Usage: chmod +x scripts/deploy_to_vps.sh && ./scripts/deploy_to_vps.sh
# ============================================================================

set -euo pipefail

echo "============================================================"
echo " ⚖️  Vidhi Law Firm CMS - Production Deployment (Port 8999)"
echo "============================================================"

# 1. Verify Docker & Docker Compose
if ! command -v docker >/dev/null 2>&1; then
    echo "[!] Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER" || true
fi

# 2. Ensure .env.production exists
if [ ! -f ".env.production" ]; then
    echo "[*] Creating .env.production from .env.production.example..."
    cp .env.production.example .env.production
    RANDOM_SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | xxd -p -c 64)
    sed -i "s/vidhi-law-firm-nepal-prod-secret-jwt-key-2083/${RANDOM_SECRET}/g" .env.production
fi

# Load variables from .env.production
set -a
source .env.production
set +a

# 3. Ensure database 'lawfirm_db' exists in MySQL if mysql client is available
if command -v mysql >/dev/null 2>&1; then
    echo "[*] Verifying database '${MYSQL_DATABASE}' on ${MYSQL_HOST}:${MYSQL_PORT} as user '${MYSQL_USER}'..."
    mysql -h "${MYSQL_HOST}" -P "${MYSQL_PORT}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
        -e "CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" || \
        echo "[!] Note: Could not run CREATE DATABASE via CLI (user '${MYSQL_USER}' may need privilege or app will create tables inside '${MYSQL_DATABASE}')."
fi

# 4. Build and start the production container
echo "[*] Building and starting Vidhi Law Firm container on port ${APP_PORT:-8999}..."
docker compose -f docker-compose.prod.yml up -d --build

# 5. Wait for health check
echo "[*] Waiting for application health check on port ${APP_PORT:-8999}..."
sleep 5
curl -fsS "http://127.0.0.1:${APP_PORT:-8999}/api/health" && echo ""

SERVER_IP=$(hostname -I | awk '{print $1}')
echo "============================================================"
echo " ✅ Deployment Complete!"
echo " 🌐 Application URL : http://${SERVER_IP}:${APP_PORT:-8999}"
echo " 📘 Swagger API Docs: http://${SERVER_IP}:${APP_PORT:-8999}/docs"
echo "============================================================"
