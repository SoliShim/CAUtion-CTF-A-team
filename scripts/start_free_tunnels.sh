#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.ctf.yml"
ENV_FILE="$ROOT_DIR/.env.ctf"
LINKS_HTML="$ROOT_DIR/ctf_tunnel_links.html"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not in PATH." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose is not available." >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  cp "$ROOT_DIR/.env.ctf.example" "$ENV_FILE"
  echo "Created $ENV_FILE from the example. Edit it before the real event flags are needed."
fi

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up --build -d

echo
echo "Local challenge URLs:"
echo "  Command Injection: http://127.0.0.1:8001"
echo "  SQL Injection:     http://127.0.0.1:8002"
echo "  CSRF:              http://127.0.0.1:8003"
echo "  XSS:               http://127.0.0.1:8004"
echo "  File Upload:       http://127.0.0.1:8005"
echo
echo "Waiting for free Cloudflare tunnel URLs..."
for _ in $(seq 1 30); do
  "$ROOT_DIR/scripts/generate_tunnel_links_html.sh" "$LINKS_HTML" >/dev/null
  ready_count="$( (grep -oE 'https://[-a-zA-Z0-9.]+\.trycloudflare\.com' "$LINKS_HTML" || true) | sort -u | wc -l | tr -d ' ')"
  if [ "$ready_count" -ge 5 ]; then
    break
  fi
  sleep 2
done

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
    printf '  %-18s %s\n' "$label:" "not ready yet; run: docker compose --env-file .env.ctf -f docker-compose.ctf.yml logs -f $service"
  fi
}

echo "Share these challenge links:"
print_tunnel_url tunnel-command-injection "Command Injection"
print_tunnel_url tunnel-sql-injection "SQL Injection"
print_tunnel_url tunnel-csrf "CSRF"
print_tunnel_url tunnel-xss "XSS"
print_tunnel_url tunnel-file-upload "File Upload"
echo
echo "Updated link HTML:"
echo "  $LINKS_HTML"
echo
echo "Check server status with:"
echo "  ./scripts/check_server_status.sh"
echo
echo "Stop everything with:"
echo "  ./scripts/stop_free_tunnels.sh"
