#!/usr/bin/env bash
set -e

echo "=================================================================="
echo "🧹 Clearing Transactional Data & Syncing MDM (Adalat, Mudda, etc.)"
echo "=================================================================="

ARGS="${@:---clean-demo-users}"

if ! docker ps --format '{{.Names}}' | grep -q "^vidhi_lawfirm_app$"; then
  echo "[*] Starting 'vidhi_lawfirm_app' container..."
  ./scripts/deploy_to_vps.sh
fi

echo "[*] Syncing latest application & MDM files into 'vidhi_lawfirm_app'..."
docker cp app/. vidhi_lawfirm_app:/app/app/
docker cp scripts/clear_transactional_data.py vidhi_lawfirm_app:/app/clear_transactional_data.py

echo "[*] Running transactional cleanup & MDM sync..."
docker exec -i vidhi_lawfirm_app python /app/clear_transactional_data.py $ARGS

echo "[*] Restarting 'vidhi_lawfirm_app' workers to serve latest UI & MDM..."
docker restart vidhi_lawfirm_app
echo "✅ Done! Refresh your browser (Ctrl+F5) at port 8999."
