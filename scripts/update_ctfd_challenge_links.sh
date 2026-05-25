#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_ENV="$ROOT_DIR/.env.ctfd.local"

if [ -f "$LOCAL_ENV" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$LOCAL_ENV"
  set +a
fi

exec python3 "$ROOT_DIR/scripts/ctfd_update_challenge_links.py" "$@"
