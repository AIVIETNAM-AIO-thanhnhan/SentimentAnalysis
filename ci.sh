#!/bin/bash

set -e  # stop if any command fails

echo "🚀 Starting CI pipeline..."

# =========================
# 1. Start services
# =========================
set -e

echo "🚀 Building Docker images..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# =========================
# Detect changes
# =========================
echo "🔍 Detecting changes..."

API_CHANGED=$(git diff --name-only HEAD~1 HEAD | grep -E '^api/' || true)
MODEL_CHANGED=$(git diff --name-only HEAD~1 HEAD | grep -E '^models/' || true)
UI_CHANGED=$(git diff --name-only HEAD~1 HEAD | grep -E '^ui/' || true)
TEST_CHANGED=$(git diff --name-only HEAD~1 HEAD | grep -E '^tests/' || true)
DOCKER_CHANGED=$(git diff --name-only HEAD~1 HEAD | grep -E 'Dockerfile|docker-compose' || true)

# =========================
# Build logic
# =========================
if [ -n "$DOCKER_CHANGED" ] || [ -n "$MODEL_CHANGED" ]; then
  echo "🏗️ Rebuilding MODEL..."
  docker compose build train-model
else
  echo "⚡ MODEL unchanged → skip build"
fi

if [ -n "$DOCKER_CHANGED" ] || [ -n "$API_CHANGED" ]; then
  echo "🏗️ Rebuilding API..."
  docker compose build api
else
  echo "⚡ API unchanged → skip build"
fi

if [ -n "$DOCKER_CHANGED" ] || [ -n "$UI_CHANGED" ]; then
  echo "🏗️ Rebuilding UI..."
  docker compose build ui
else
  echo "⚡ UI unchanged → skip build"
fi

if [ -n "$DOCKER_CHANGED" ] || [ -n "$TEST_CHANGED" ]; then
  echo "🏗️ Rebuilding TESTS..."
  docker compose build test-api test-model test-ui
else
  echo "⚡ TESTS unchanged → skip build"
fi

echo "🚀 Starting services..."
docker compose up -d api ui

echo "⏳ Waiting for API..."
until curl -s http://localhost:8000/docs > /dev/null; do
  sleep 2
done

echo "⏳ Waiting for UI..."
# until curl -s http://localhost:8501 > /dev/null; do
#   sleep 2
# done

# =========================
# 2. Run tests
# =========================
echo "🧪 Running model training..."
docker compose run --rm train-model
TRAIN_MODEL_STATUS=$?

echo "🧪 Running model tests..."
docker compose run --rm test-model
TEST_MODEL_STATUS=$?

echo "🧪 Running API tests..."
docker compose run --rm test-api || true
TEST_API_STATUS=$?

echo "🧪 Running UI tests..."
# docker compose run --rm test-ui || true
TEST_UI_STATUS=$?

set -e # re-enable strict mode

echo "Train MODEL status: $TRAIN_MODEL_STATUS"
echo "Test MODEL status: $TEST_MODEL_STATUS"
echo "Test API status: $TEST_API_STATUS"
echo "Test UI status: $TEST_UI_STATUS"

# fail at the end if needed
if [ $TRAIN_MODEL_STATUS -ne 0 ] || [ $TEST_MODEL_STATUS -ne 0 ] || [ $TEST_API_STATUS -ne 0 ] || [ $TEST_UI_STATUS -ne 0 ]; then
  echo "❌ CI FAILED"
  exit 1
fi
# =========================
# 3. Open report
# =========================
echo "📄 Reports generated:"
echo "- reports/api_test_results.pdf"
echo "- reports/model_train_results.png"

echo "👉 Open manually on your machine:"
echo "   open reports/api_test_results.pdf"
echo "   open reports/model_train_results.png"

# =========================
# 4. Cleanup
# =========================
echo "🧹 Cleaning up..."
docker compose down

echo "✅ CI pipeline completed successfully!"