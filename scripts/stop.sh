#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

for name in bot worker; do
  pidfile="run/$name.pid"

  if [ -f "$pidfile" ]; then
    pid="$(cat "$pidfile")"

    if kill "$pid" 2>/dev/null; then
      echo "Stopped $name (pid $pid)"
    else
      echo "$name (pid $pid) was not running"
    fi

    rm -f "$pidfile"
  else
    echo "No pidfile for $name, skipping"
  fi
done
