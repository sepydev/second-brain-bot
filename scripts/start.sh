#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p logs run

if redis-cli ping > /dev/null 2>&1; then
  :
else
  echo "Redis does not seem to be running (redis-cli ping failed)." >&2
  echo "Start it with: brew services start redis" >&2
  exit 1
fi

if curl -sf http://localhost:11434 > /dev/null 2>&1; then
  :
else
  echo "Ollama does not seem to be running on localhost:11434." >&2
  echo "Start it with: ollama serve" >&2
  exit 1
fi

nohup uv run second-brain-bot > logs/bot.log 2>&1 &
echo $! > run/bot.pid
echo "Bot started (pid $(cat run/bot.pid)), logging to logs/bot.log"

nohup uv run celery -A second_brain_bot.tasks.celery_app worker --loglevel=INFO --pool=solo > logs/worker.log 2>&1 &
echo $! > run/worker.pid
echo "Celery worker started (pid $(cat run/worker.pid)), logging to logs/worker.log"
