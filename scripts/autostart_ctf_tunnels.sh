#!/usr/bin/env bash
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.ctf.yml"
ENV_FILE="$ROOT_DIR/.env.ctf"
LOG_DIR="$ROOT_DIR/logs"
LINKS_HTML="$ROOT_DIR/ctf_tunnel_links.html"

mkdir -p "$LOG_DIR"

if [ ! -f "$ENV_FILE" ]; then
  cp "$ROOT_DIR/.env.ctf.example" "$ENV_FILE"
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker command not found"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  open -ga Docker || true
fi

for _ in $(seq 1 90); do
  if docker info >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if ! docker info >/dev/null 2>&1; then
  echo "Docker did not become ready in time"
  exit 1
fi

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up --build -d

for _ in $(seq 1 30); do
  "$ROOT_DIR/scripts/generate_tunnel_links_html.sh" "$LINKS_HTML" >/dev/null
  ready_count="$( (grep -oE 'https://[-a-zA-Z0-9.]+\.trycloudflare\.com' "$LINKS_HTML" || true) | sort -u | wc -l | tr -d ' ')"
  if [ "$ready_count" -ge 5 ]; then
    break
  fi
  sleep 2
done

echo "CAUtion CTF tunnels are running. Links: $LINKS_HTML"
