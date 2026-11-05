#!/usr/bin/env bash
# ============================================================================
# Vidhi Law Firm Management System - Linux VPS Deployment Script
# Target OS: Ubuntu / Debian with Docker & Docker Compose
# Usage: chmod +x scripts/deploy_to_vps.sh && ./scripts/deploy_to_vps.sh
# ============================================================================

set -euo pipefail

echo "============================================================"
echo " ⚖️  Vidhi Law Firm CMS - Production Deployment (Linux VPS)"
echo "============================================================"

# 1. Verify Docker & Docker Compose
if ! command -v docker >/dev/null 2>&1; then
    echo "[!] Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER" || true
fi

# 2. Check .env.production
if [ ! -f ".env.production" ]; then
    echo "[!] .env.production not found. Creating from .env.production.example..."
    cp .env.production.example .env.production
    RANDOM_SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | xxd -p -c 64)
    sed -i "s/CHANGE_ME_WITH_64_CHAR_RANDOM_HEX_SECRET_KEY_FOR_PRODUCTION/${RANDOM_SECRET}/g" .env.production
    echo "[!] IMPORTANT: Please edit .env.production with your server's MYSQL_HOST, MYSQL_USER, and MYSQL_PASSWORD,"
    echo "    then re-run: ./scripts/deploy_to_vps.sh"
    exit 1
fi

# Load variables from .env.production
set -a
source .env.production
set +a

# 3. Optional: Import lawfirm_db_backup.sql if present and requested
if [ -f "lawfirm_db_backup.sql" ]; then
    echo "[*] Found lawfirm_db_backup.sql."
    read -r -p "Do you want to import lawfirm_db_backup.sql into MySQL ($MYSQL_HOST:$MYSQL_PORT)? [y/N] " REPLY
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        IMPORT_HOST="$MYSQL_HOST"
        if [ "$IMPORT_HOST" = "host.docker.internal" ]; then
            IMPORT_HOST="127.0.0.1"
        fi
        echo "[*] Importing database into $IMPORT_HOST:$MYSQL_PORT/$MYSQL_DATABASE..."
        mysql -h "$IMPORT_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" --default-character-set=utf8mb4 < lawfirm_db_backup.sql
        echo "[+] Database imported successfully."
    fi
fi

# 4. Build and start the production container
echo "[*] Building and starting Vidhi Law Firm container..."
docker compose -f docker-compose.prod.yml up -d --build

# 5. Wait for health check
echo "[*] Waiting for application health check on port ${APP_EXTERNAL_PORT:-8080}..."
sleep 5
curl -fsS "http://127.0.0.1:${APP_EXTERNAL_PORT:-8080}/api/health" && echo ""

SERVER_IP=$(hostname -I | awk '{print $1}')
echo "============================================================"
echo " ✅ Deployment Complete!"
echo " 🌐 Application URL : http://${SERVER_IP}:${APP_EXTERNAL_PORT:-8080}"
echo " 📘 Swagger API Docs: http://${SERVER_IP}:${APP_EXTERNAL_PORT:-8080}/docs"
echo "============================================================"
