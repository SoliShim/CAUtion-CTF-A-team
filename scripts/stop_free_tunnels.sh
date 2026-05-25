#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINKS_HTML="$ROOT_DIR/ctf_tunnel_links.html"

docker compose --env-file "$ROOT_DIR/.env.ctf" -f "$ROOT_DIR/docker-compose.ctf.yml" down

cat > "$LINKS_HTML" <<HTML
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CAUtion CTF 공개 링크</title>
  <style>
    body { margin: 40px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.6; }
    main { max-width: 760px; }
    code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  </style>
</head>
<body>
  <main>
    <h1>CAUtion CTF 공개 링크</h1>
    <p>마지막 갱신: $(date '+%Y-%m-%d %H:%M:%S %Z')</p>
    <p>현재 CTF 서버와 Cloudflare 터널이 종료된 상태입니다.</p>
    <p>다시 열려면 프로젝트 폴더에서 아래 명령어를 실행하세요.</p>
    <pre><code>./scripts/start_free_tunnels.sh</code></pre>
  </main>
</body>
</html>
HTML

echo "Stopped CTF servers and tunnels."
echo "Updated link HTML: $LINKS_HTML"
