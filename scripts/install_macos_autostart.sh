#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$HOME/.caution-ctf-a-team"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$PLIST_DIR/com.caution.ctf.tunnels.plist"
LOG_DIR="$RUNTIME_DIR/logs"

mkdir -p "$PLIST_DIR" "$LOG_DIR"

rm -rf "$RUNTIME_DIR.new"
mkdir -p "$RUNTIME_DIR.new"

copy_item() {
  local item="$1"
  if [ -e "$ROOT_DIR/$item" ]; then
    ditto --noextattr --norsrc "$ROOT_DIR/$item" "$RUNTIME_DIR.new/$item"
  fi
}

copy_item docker-compose.ctf.yml
copy_item .env.ctf.example
copy_item .env.ctf
copy_item ctf_autostart_guide.html
copy_item Command_Injection
copy_item SQL_Injection
copy_item CSRF
copy_item XSS
copy_item File_Upload
copy_item scripts

mv "$RUNTIME_DIR" "$RUNTIME_DIR.old" 2>/dev/null || true
mv "$RUNTIME_DIR.new" "$RUNTIME_DIR"
rm -rf "$RUNTIME_DIR.old"
mkdir -p "$LOG_DIR"
chmod +x "$RUNTIME_DIR"/scripts/*.sh
xattr -cr "$RUNTIME_DIR" 2>/dev/null || true

cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.caution.ctf.tunnels</string>
  <key>ProgramArguments</key>
  <array>
    <string>$RUNTIME_DIR/scripts/autostart_ctf_tunnels.sh</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$RUNTIME_DIR</string>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>600</integer>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/autostart.out.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/autostart.err.log</string>
</dict>
</plist>
PLIST

chmod 644 "$PLIST_PATH"

launchctl bootout "gui/$(id -u)" "$PLIST_PATH" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl kickstart -k "gui/$(id -u)/com.caution.ctf.tunnels"

echo "Installed LaunchAgent: $PLIST_PATH"
echo "Runtime directory: $RUNTIME_DIR"
echo "Current links will be written to: $RUNTIME_DIR/ctf_tunnel_links.html"
