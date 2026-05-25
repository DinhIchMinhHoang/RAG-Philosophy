#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# deploy-vm.sh — Deploy RAG-Philosophy on a 2vCPU / 8GB VM
# Usage: bash deploy-vm.sh
# ============================================================

REPO_URL="https://github.com/DinhIchMinhHoang/RAG-Philosophy.git"
INSTALL_DIR="/opt/rag-philosophy"

echo "=== 1. Install Docker ==="
if ! command -v docker &>/dev/null; then
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER"
  echo "  Docker installed. Log out and back in for group changes, or run: newgrp docker"
fi

if ! docker compose version &>/dev/null; then
  echo "  Installing Docker Compose plugin..."
  sudo apt-get update && sudo apt-get install -y docker-compose-plugin
fi

echo "=== 2. Clone / update project ==="
if [ -d "$INSTALL_DIR" ]; then
  cd "$INSTALL_DIR"
  git pull
else
  sudo git clone "$REPO_URL" "$INSTALL_DIR"
  sudo chown -R "$USER:$USER" "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi

echo "=== 3. Create data directories ==="
mkdir -p data/{raw,processed,stores/{qdrant,doc_store}}

echo "=== 4. Create .env from template ==="
if [ ! -f .env ]; then
  cp .env.vm .env
  echo "  !! Edit .env and set your API keys: GEMINI_API_KEY, COHERE_API_KEY, SECRET_KEY"
  echo "  !! Then re-run this script or start manually."
  exit 0
fi

echo "=== 5. Pre-pull images (faster startup) ==="
docker compose -f docker-compose.vm.yml pull

echo "=== 6. Boot the stack ==="
docker compose -f docker-compose.vm.yml up -d

echo "=== 7. Health check ==="
echo "  Waiting for backend health check (up to 90s)..."
if docker compose -f docker-compose.vm.yml exec -T backend \
     sh -c "python -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:8000/docs\")' 2>/dev/null"; then
  echo "  Backend is healthy at http://localhost:8000"
fi

echo ""
echo "=== Done ==="
echo "  Frontend : http://$(curl -s http://checkip.amazonaws.com || echo 'localhost')"
echo "  Backend  : http://localhost:8000"
echo "  Docs     : http://localhost:8000/docs"
echo ""
echo "  Commands:"
echo "    Logs : docker compose -f docker-compose.vm.yml logs -f backend"
echo "    Stop : docker compose -f docker-compose.vm.yml down"
echo "    Stats: docker stats"
