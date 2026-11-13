#!/usr/bin/env bash
set -e

echo "=================================================================="
echo "🧹 Clearing Transactional Data & Syncing MDM (Adalat, Mudda, etc.)"
echo "=================================================================="

if docker ps --format '{{.Names}}' | grep -q "vidhi-lawfirm-app"; then
  docker exec -i vidhi-lawfirm-app python scripts/clear_transactional_data.py --clean-demo-users
else
  python3 scripts/clear_transactional_data.py --clean-demo-users
fi
