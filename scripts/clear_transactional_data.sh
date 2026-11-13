#!/usr/bin/env bash
set -e

echo "=================================================================="
echo "🧹 Clearing Transactional Data & Syncing MDM (Adalat, Mudda, etc.)"
echo "=================================================================="

ARGS="${@:---clean-demo-users}"

if ! docker ps --format '{{.Names}}' | grep -q "^vidhi_lawfirm_app$" || ! docker exec vidhi_lawfirm_app test -f /app/app/routers/tenants_router.py; then
  echo "[*] Updating 'vidhi_lawfirm_app' container with latest Multi-Tenant & MDM code..."
  ./scripts/deploy_to_vps.sh
fi

echo "[*] Executing transactional cleanup inside 'vidhi_lawfirm_app' container..."
docker cp scripts/clear_transactional_data.py vidhi_lawfirm_app:/app/clear_transactional_data.py
docker exec -i vidhi_lawfirm_app python /app/clear_transactional_data.py $ARGS
