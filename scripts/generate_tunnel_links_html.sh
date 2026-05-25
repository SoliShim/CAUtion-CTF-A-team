#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.ctf.yml"
ENV_FILE="$ROOT_DIR/.env.ctf"
OUTPUT_FILE="${1:-$ROOT_DIR/ctf_tunnel_links.html}"

get_tunnel_url() {
  local service="$1"
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --no-color "$service" 2>/dev/null \
    | sed -nE 's/.*(https:\/\/[-a-zA-Z0-9.]+\.trycloudflare\.com).*/\1/p' \
    | tail -n 1
}

COMMAND_URL="$(get_tunnel_url tunnel-command-injection)"
SQL_URL="$(get_tunnel_url tunnel-sql-injection)"
CSRF_URL="$(get_tunnel_url tunnel-csrf)"
XSS_URL="$(get_tunnel_url tunnel-xss)"
UPLOAD_URL="$(get_tunnel_url tunnel-file-upload)"
UPDATED_AT="$(date '+%Y-%m-%d %H:%M:%S %Z')"

link_or_waiting() {
  local url="$1"
  if [ -n "$url" ]; then
    printf '<a href="%s" target="_blank" rel="noreferrer">%s</a>' "$url" "$url"
  else
    printf '<span class="muted">아직 준비 중입니다. 잠시 후 새로고침하세요.</span>'
  fi
}

cat > "$OUTPUT_FILE" <<HTML
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CAUtion CTF 공개 링크</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --text: #17191c;
      --muted: #69707a;
      --line: #d9dde3;
      --accent: #0b6bcb;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #111315;
        --panel: #191c20;
        --text: #f2f4f7;
        --muted: #a3aab5;
        --line: #30353d;
        --accent: #7ab7ff;
      }
    }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
    }
    main {
      width: min(920px, calc(100% - 32px));
      margin: 40px auto;
    }
    h1 {
      margin: 0 0 8px;
      font-size: 30px;
      letter-spacing: 0;
    }
    .meta {
      color: var(--muted);
      margin-bottom: 24px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
    }
    th, td {
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }
    th {
      font-size: 13px;
      color: var(--muted);
      font-weight: 600;
    }
    tr:last-child td {
      border-bottom: 0;
    }
    a {
      color: var(--accent);
      overflow-wrap: anywhere;
    }
    .muted {
      color: var(--muted);
    }
    .note {
      margin-top: 20px;
      padding: 16px;
      border: 1px solid var(--line);
      background: var(--panel);
    }
    code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }
  </style>
</head>
<body>
  <main>
    <h1>CAUtion CTF 공개 링크</h1>
    <div class="meta">마지막 갱신: $UPDATED_AT</div>
    <table>
      <thead>
        <tr>
          <th>문제</th>
          <th>참가자에게 전달할 링크</th>
          <th>맥미니 내부 확인 주소</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Command Injection</td>
          <td>$(link_or_waiting "$COMMAND_URL")</td>
          <td><code>http://127.0.0.1:8001</code></td>
        </tr>
        <tr>
          <td>SQL Injection</td>
          <td>$(link_or_waiting "$SQL_URL")</td>
          <td><code>http://127.0.0.1:8002</code></td>
        </tr>
        <tr>
          <td>CSRF</td>
          <td>$(link_or_waiting "$CSRF_URL")</td>
          <td><code>http://127.0.0.1:8003</code></td>
        </tr>
        <tr>
          <td>XSS</td>
          <td>$(link_or_waiting "$XSS_URL")</td>
          <td><code>http://127.0.0.1:8004</code></td>
        </tr>
        <tr>
          <td>File Upload</td>
          <td>$(link_or_waiting "$UPLOAD_URL")</td>
          <td><code>http://127.0.0.1:8005</code></td>
        </tr>
      </tbody>
    </table>
    <div class="note">
      <strong>주의:</strong> <code>trycloudflare.com</code> 임시 터널 링크는 무료이지만, 터널 컨테이너를 새로 만들면 주소가 바뀔 수 있습니다.
      재부팅 후 이 파일을 열어 최신 링크를 확인하세요.
    </div>
  </main>
</body>
</html>
HTML

echo "$OUTPUT_FILE"
