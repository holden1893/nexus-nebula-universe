#!/usr/bin/env bash
set -euo pipefail

# Run from repo root
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "⚡ Starting Nexus Nebula Universe (backend + frontend) ⚡"

# Backend
echo "🧠 Backend: installing deps + launching FastAPI..."
cd "$ROOT/backend"
python -m venv .venv >/dev/null 2>&1 || true
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACK_PID=$!
deactivate

# Frontend
echo "🎨 Frontend: installing deps + launching Next.js..."
cd "$ROOT/frontend"
npm install --silent
if [ ! -f .env.local ]; then
  cp .env.local.example .env.local
fi
npm run dev &
FRONT_PID=$!

echo ""
echo "✅ Running:"
echo "  - Backend  : http://localhost:8000/health"
echo "  - Frontend : http://localhost:3000/marketplace"
echo ""
echo "Press Ctrl+C to stop."

trap 'kill $BACK_PID $FRONT_PID 2>/dev/null || true' INT TERM
wait
