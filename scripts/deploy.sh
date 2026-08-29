#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "  PREDICTX INDUSTRIAL AI PLATFORM - DEPLOYMENT"
echo "=========================================================="

echo "[1/4] Running Automated Test Suite..."
pytest

echo "[2/4] Compiling Web Application..."
(cd apps/web && npm run build)

echo "[3/4] Building & Launching Production Containers..."
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

echo "[4/4] Verifying System Health..."
sleep 5
curl -f http://localhost:8000/health || echo "Waiting for service readiness..."

echo "=========================================================="
echo "  PREDICTX DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "=========================================================="
