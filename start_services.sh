#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

if pgrep -af 'python3 .*bot.py|python .*bot.py' >/dev/null; then
  echo "bot.py is already running. Stop existing bot process first to avoid Telegram Conflict errors."
  exit 1
fi

cleanup() {
  echo "Stopping services..."
  [[ -n "${APP_PID:-}" ]] && kill "$APP_PID" 2>/dev/null || true
  [[ -n "${BOT_PID:-}" ]] && kill "$BOT_PID" 2>/dev/null || true
  [[ -n "${SCRAPER_PID:-}" ]] && kill "$SCRAPER_PID" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

echo "Starting Flask app (app.py)..."
python3 -u app.py &
APP_PID=$!

echo "Starting Telegram bot (bot.py)..."
python3 -u bot.py &
BOT_PID=$!

echo "Starting Notice Scraper (scraper.py)..."
python3 -u scraper.py &
SCRAPER_PID=$!

echo "Services started. Press Ctrl+C to stop all."

wait -n "$APP_PID" "$BOT_PID" "$SCRAPER_PID"
echo "One service exited; shutting down the others."