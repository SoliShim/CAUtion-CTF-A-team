#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECK_SCRIPT="$ROOT_DIR/scripts/check_server_status.sh"
INTERVAL_SECONDS=60
USE_CAFFEINATE=1

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/monitor_server_status.sh [seconds]
  ./scripts/monitor_server_status.sh --interval 60
  ./scripts/monitor_server_status.sh --no-caffeinate

Options:
  -i, --interval SECONDS   Server check interval in seconds. Default: 60 seconds.
  --no-caffeinate          Do not prevent macOS sleep.
  -h, --help               Show this help.

This script keeps checking the CTF servers until you press Ctrl+C.
On macOS it uses caffeinate without the display option, so the screen may turn
off but the Mac should stay awake while the monitor is running.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -i|--interval)
      if [ "$#" -lt 2 ]; then
        echo "Missing value for $1" >&2
        exit 2
      fi
      INTERVAL_SECONDS="$2"
      shift 2
      ;;
    --no-caffeinate)
      USE_CAFFEINATE=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *[!0-9]*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      INTERVAL_SECONDS="$1"
      shift
      ;;
  esac
done

if ! [[ "$INTERVAL_SECONDS" =~ ^[0-9]+$ ]] || [ "$INTERVAL_SECONDS" -lt 10 ]; then
  echo "Interval must be a number of seconds, at least 10." >&2
  exit 2
fi

clear_screen() {
  if [ -t 1 ]; then
    printf '\033[H\033[2J'
  fi
}

format_duration() {
  local total="$1"
  local minutes=$((total / 60))
  local seconds=$((total % 60))
  printf '%02d:%02d' "$minutes" "$seconds"
}

cleanup() {
  if [ -n "${CAFFEINATE_PID:-}" ]; then
    kill "$CAFFEINATE_PID" >/dev/null 2>&1 || true
  fi
  if [ -t 1 ]; then
    printf '\n'
  fi
}

trap cleanup EXIT INT TERM

CAFFEINATE_STATUS="not used"
if [ "$USE_CAFFEINATE" -eq 1 ]; then
  if command -v caffeinate >/dev/null 2>&1; then
    caffeinate -s -i -m -w "$$" >/dev/null 2>&1 &
    CAFFEINATE_PID="$!"
    CAFFEINATE_STATUS="active; display sleep is allowed"
  else
    CAFFEINATE_STATUS="unavailable on this system"
  fi
fi

last_result="not checked yet"
last_checked="not checked yet"
last_output=""
monitor_started="$(date '+%Y-%m-%d %H:%M:%S %Z')"
spinner='-\|/'

while true; do
  clear_screen
  echo "CAUtion CTF live server monitor"
  echo "Started at: $monitor_started"
  echo "Check interval: ${INTERVAL_SECONDS}s"
  echo "Sleep prevention: $CAFFEINATE_STATUS"
  echo "Press Ctrl+C to stop."
  echo
  echo "Checking servers now..."
  echo

  set +e
  last_output="$("$CHECK_SCRIPT" 2>&1)"
  check_exit=$?
  set -e

  last_checked="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  if [ "$check_exit" -eq 0 ]; then
    last_result="OK"
  else
    last_result="CHECK NEEDED"
  fi

  clear_screen
  echo "CAUtion CTF live server monitor"
  echo "Last check: $last_checked"
  echo "Last result: $last_result"
  echo "Check interval: ${INTERVAL_SECONDS}s"
  echo "Sleep prevention: $CAFFEINATE_STATUS"
  echo "Press Ctrl+C to stop."
  echo
  echo "$last_output"
  echo

  for ((remaining=INTERVAL_SECONDS; remaining>0; remaining--)); do
    frame_index=$((remaining % 4))
    frame="${spinner:$frame_index:1}"
    printf '\r\033[K[%s] servers running monitor... next check in %s' \
      "$frame" "$(format_duration "$remaining")"
    sleep 1
  done
  printf '\r\033[K'
done
