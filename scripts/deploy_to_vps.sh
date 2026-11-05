#!/usr/bin/env bash
# ============================================================================
# Vidhi Law Firm Management System - Linux VPS Deployment Script
# Connects to existing 'erp-db-1' (service 'db' on network 'erp_default')
# Usage: ./scripts/deploy_to_vps.sh
# ============================================================================

set -euo pipefail

echo "============================================================"
echo " ⚖️  Vidhi Law Firm CMS - Production Deployment (Port 8999)"
echo "============================================================"

# 1. Always refresh .env.production from .env.production.example if needed
cp .env.production.example .env.production
RANDOM_SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | xxd -p -c 64)
sed -i "s/vidhi-law-firm-nepal-prod-secret-jwt-key-2083/${RANDOM_SECRET}/g" .env.production

set -a
source .env.production
set +a

# 2. Ensure 'lawfirm_db' exists inside the running erp-db-1 MySQL container
if docker ps --format '{{.Names}}' | grep -q '^erp-db-1$'; then
    echo "[*] Creating database '${MYSQL_DATABASE}' inside container 'erp-db-1'..."
    docker exec erp-db-1 mysql -uroot -ppassword \
        -e "CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "[+] Database '${MYSQL_DATABASE}' verified in erp-db-1."
fi

# 3. Build and start the production container on network 'erp_default'
echo "[*] Building and starting Vidhi Law Firm container on port ${APP_PORT:-8999}..."
docker compose -f docker-compose.prod.yml up -d --build

# 4. Wait for health check
echo "[*] Waiting for application health check on port ${APP_PORT:-8999}..."
sleep 6
curl -fsS "http://127.0.0.1:${APP_PORT:-8999}/api/health" && echo ""

SERVER_IP=$(hostname -I | awk '{print $1}')
echo "============================================================"
echo " ✅ Deployment Complete!"
echo " 🌐 Application URL : http://${SERVER_IP}:${APP_PORT:-8999}"
echo " 📘 Swagger API Docs: http://${SERVER_IP}:${APP_PORT:-8999}/docs"
echo "============================================================"
