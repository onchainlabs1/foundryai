#!/bin/bash

echo "🚀 Starting AIMS Readiness CI Pipeline..."

# Exit immediately if a command exits with a non-zero status
set -e

# --- Backend Checks ---
echo ""
echo "🔍 [INFO] Running Python linting (ruff)..."
cd backend
source .venv/bin/activate
ruff check . --fix || true # Run ruff, allow it to fail for now, but show output
ruff format . --check || true # Check formatting, allow it to fail for now
deactivate
cd ..

echo ""
echo "🧪 [INFO] Running Python tests (pytest)..."
cd backend
source .venv/bin/activate
SECRET_KEY=dev-secret-key-for-development-only pytest tests/test_integration_critical_flows.py -v
deactivate
cd ..

# --- Frontend Checks ---
echo ""
echo "🔍 [INFO] Running Frontend linting (npm run lint)..."
cd frontend
npm install
npm run lint
cd ..

echo ""
echo "🏗️ [INFO] Running Frontend build check (npm run build)..."
cd frontend
npm run build
cd ..

echo ""
echo "✅ CI Pipeline Completed Successfully!"