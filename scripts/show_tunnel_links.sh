#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.ctf.yml"
ENV_FILE="$ROOT_DIR/.env.ctf"

print_tunnel_url() {
  local service="$1"
  local label="$2"
  local url
  url="$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --no-color "$service" 2>/dev/null \
    | sed -nE 's/.*(https:\/\/[-a-zA-Z0-9.]+\.trycloudflare\.com).*/\1/p' \
    | tail -n 1)"

  if [ -n "$url" ]; then
    printf '  %-18s %s\n' "$label:" "$url"
  else
    printf '  %-18s %s\n' "$label:" "not ready"
  fi
}

echo "Current Cloudflare tunnel links:"
print_tunnel_url tunnel-command-injection "Command Injection"
print_tunnel_url tunnel-sql-injection "SQL Injection"
print_tunnel_url tunnel-csrf "CSRF"
print_tunnel_url tunnel-xss "XSS"
print_tunnel_url tunnel-file-upload "File Upload"
