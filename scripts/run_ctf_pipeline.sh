#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT_DIR/scripts/start_free_tunnels.sh"
echo
"$ROOT_DIR/scripts/check_server_status.sh"
echo
"$ROOT_DIR/scripts/update_ctfd_challenge_links.sh" "$@"
