#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.ctf.yml"
ENV_FILE="$ROOT_DIR/.env.ctf"

COMPOSE_CMD=(docker compose)
if [ -f "$ENV_FILE" ]; then
  COMPOSE_CMD+=(--env-file "$ENV_FILE")
fi
COMPOSE_CMD+=(-f "$COMPOSE_FILE")

fail_count=0

mark_fail() {
  fail_count=$((fail_count + 1))
}

http_status() {
  local url="$1"
  local code

  if ! command -v curl >/dev/null 2>&1; then
    echo "curl not found"
    return 1
  fi

  code="$(curl -k -L --silent --output /dev/null --max-time 8 --write-out '%{http_code}' "$url" 2>/dev/null || true)"
  case "$code" in
    2*|3*)
      echo "OK ($code)"
      return 0
      ;;
    000|"")
      echo "NO RESPONSE"
      return 1
      ;;
    *)
      echo "HTTP $code"
      return 1
      ;;
  esac
}

container_status() {
  local service="$1"
  local container_id

  container_id="$("${COMPOSE_CMD[@]}" ps -q "$service" 2>/dev/null | head -n 1)"
  if [ -z "$container_id" ]; then
    echo "not running"
    return 1
  fi

  docker inspect -f '{{.State.Status}}' "$container_id" 2>/dev/null || {
    echo "unknown"
    return 1
  }
}

tunnel_url() {
  local service="$1"
  "${COMPOSE_CMD[@]}" logs --no-color "$service" 2>/dev/null \
    | sed -nE 's/.*(https:\/\/[-a-zA-Z0-9.]+\.trycloudflare\.com).*/\1/p' \
    | tail -n 1
}

print_row() {
  printf '%-19s %-14s %-18s %s\n' "$1" "$2" "$3" "$4"
}

print_docker_info_error() {
  local error_text="$1"

  echo "$error_text" \
    | sed -E 's/[[:space:]]+/ /g' \
    | sed '/^$/d' \
    | head -n 3 \
    | sed 's/^/  /'
}

echo "CAUtion CTF server status"
echo "Checked at: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker: not found"
  echo "Run Docker Desktop first, then try again."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose: not available"
  exit 1
fi

docker_info_output="$(docker info 2>&1 >/dev/null)"
docker_info_status=$?
if [ "$docker_info_status" -ne 0 ]; then
  case "$docker_info_output" in
    *"permission denied"*|*"Permission denied"*)
      echo "Docker: access denied"
      echo "Docker Desktop may be running, but this shell cannot access the Docker API."
      echo "If this is running inside Codex or another sandbox, allow Docker access or run the script in a normal terminal."
      echo "Docker error:"
      print_docker_info_error "$docker_info_output"
      ;;
    *"Cannot connect to the Docker daemon"*|*"Is the docker daemon running"*|*"docker daemon is not running"*)
      echo "Docker: not running"
      echo "Open Docker Desktop, wait until it is ready, then try again."
      echo "Docker error:"
      print_docker_info_error "$docker_info_output"
      ;;
    *)
      echo "Docker: unavailable"
      echo "Docker exists, but the status check could not talk to the Docker API."
      echo "Docker error:"
      print_docker_info_error "$docker_info_output"
      ;;
  esac
  exit 1
fi

echo "Docker: running"
if [ -f "$ENV_FILE" ]; then
  echo "Env file: $ENV_FILE"
else
  echo "Env file: not found; compose defaults will be used"
fi
echo

echo "Local challenge servers"
print_row "Problem" "Container" "Local HTTP" "URL"
print_row "-------" "---------" "----------" "---"
while IFS='|' read -r label service url; do
  container="$(container_status "$service")"
  if [ "$container" != "running" ]; then
    mark_fail
  fi

  http="$(http_status "$url")"
  if [[ "$http" != OK* ]]; then
    mark_fail
  fi

  print_row "$label" "$container" "$http" "$url"
done <<'SERVERS'
Command Injection|command-injection|http://127.0.0.1:8001
SQL Injection|sql-injection|http://127.0.0.1:8002
CSRF|csrf|http://127.0.0.1:8003
XSS|xss|http://127.0.0.1:8004
File Upload|file-upload|http://127.0.0.1:8005
SERVERS

echo
echo "Cloudflare public tunnels"
print_row "Problem" "Container" "Public HTTP" "URL"
print_row "-------" "---------" "-----------" "---"
while IFS='|' read -r label service; do
  container="$(container_status "$service")"
  if [ "$container" != "running" ]; then
    mark_fail
  fi

  url="$(tunnel_url "$service")"
  if [ -z "$url" ]; then
    mark_fail
    print_row "$label" "$container" "not ready" "no tunnel URL yet"
    continue
  fi

  http="$(http_status "$url")"
  if [[ "$http" != OK* ]]; then
    mark_fail
  fi

  print_row "$label" "$container" "$http" "$url"
done <<'TUNNELS'
Command Injection|tunnel-command-injection
SQL Injection|tunnel-sql-injection
CSRF|tunnel-csrf
XSS|tunnel-xss
File Upload|tunnel-file-upload
TUNNELS

echo
if [ "$fail_count" -eq 0 ]; then
  echo "Overall: OK - all local servers and public tunnels responded."
  exit 0
fi

echo "Overall: CHECK NEEDED - $fail_count check(s) did not pass."
echo "If the servers should be running, use: ./scripts/start_free_tunnels.sh"
exit 1
