#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

rebuild_one() {
  local category="$1"
  local zip_name="$2"
  local challenge_dir="$ROOT_DIR/$category"
  local deploy_dir="$challenge_dir/deploy"
  local ctfd_dir="$challenge_dir/CTFd"
  local zip_path="$challenge_dir/$zip_name"

  if [ ! -d "$deploy_dir" ]; then
    echo "Missing deploy directory: $deploy_dir" >&2
    exit 1
  fi

  rm -rf "$ctfd_dir"
  mkdir -p "$ctfd_dir"
  rsync -a --exclude ".DS_Store" "$deploy_dir"/ "$ctfd_dir"/

  find "$ctfd_dir" -name ".DS_Store" -delete
  find "$ctfd_dir" -name ".gitignore" -delete
  find "$ctfd_dir" -name "__pycache__" -type d -prune -exec rm -rf {} +
  find "$ctfd_dir" -name "*.pyc" -delete
  find "$ctfd_dir" -name "flag.txt" -delete
  find "$ctfd_dir" -name "WRITEUP.md" -delete
  find "$ctfd_dir" -name "sqli.db" -delete
  find "$ctfd_dir" -name "ctf.db" -delete
  find "$ctfd_dir" -type f \( -name "*.py" -o -name "*.html" -o -name "*.md" \) -exec perl -0pi -e 's/FLAG\{\{?\.\.\.\}?\}/FLAG_REMOVED_FOR_CTFD/g; s/FLAG\{[^}]+\}/FLAG_REMOVED_FOR_CTFD/g; s/FLAG\{[^\n]*/FLAG_REMOVED_FOR_CTFD/g; s/FLAG_REMOVED_FOR_CTFD\}/FLAG_REMOVED_FOR_CTFD/g' {} +

  if [ "$category" = "Command_Injection" ]; then
    cat > "$ctfd_dir/README.md" <<'README'
# Command Injection Challenge

서버 내부 report 파일을 확인하는 관리자 도구를 분석하는 문제입니다.

## 로컬 실행

```bash
docker build -t command-injection-challenge .
docker run --rm -p 8081:80 command-injection-challenge
```

브라우저에서 `http://127.0.0.1:8081`로 접속합니다.
README
  fi

  if [ "$category" = "CSRF" ]; then
    cat > "$ctfd_dir/README.md" <<'README'
# CSRF Challenge

가상의 은행 서비스에서 CSRF 취약점을 분석하는 문제입니다.

상점에서 플래그를 구매할 수 있으며, 이를 위해서는 매우 많은 금액이 필요합니다. 게임으로 돈을 벌 수 있지만 한 번에 얻는 금액은 제한적입니다.

## 로컬 실행

```bash
docker build -t csrf-challenge .
docker run --rm -p 8000:8000 csrf-challenge
```

브라우저에서 `http://127.0.0.1:8000`으로 접속합니다.
README
  fi

  if [ "$category" = "SQL_Injection" ]; then
    cat > "$ctfd_dir/README.md" <<'README'
# SQL Injection

로그인 기능을 분석하여 관리자 계정으로 인증하는 SQL Injection 문제입니다.

## 로컬 실행

```bash
docker build -t blind-sqli .
docker run -d -p 80:80 blind-sqli
```

브라우저에서 `http://localhost`로 접속합니다.
README
    perl -0pi -e 's/\n\s*# 💡 중요: 플래그 자체에.*?\n\s*# 정답을 정확히 입력한 경우에는.*?\n/\n/s; s/\n\s*# 💡 로그인이 뚫렸을 때.*?\n/\n/s' "$ctfd_dir/app.py"
  fi

  if [ "$category" = "CSRF" ]; then
    perl -0pi -e 's/RUN chown -R \$user:\$user \/app \\\n    && chown root:\$user \/app\/flag\.txt \\\n    && chmod 440 \/app\/flag\.txt/RUN printf "%s\\n" "FLAG_REMOVED_FOR_CTFD" > \/app\/flag.txt \\\n    \&\& chown -R \$user:\$user \/app \\\n    \&\& chown root:\$user \/app\/flag.txt \\\n    \&\& chmod 440 \/app\/flag.txt/' "$ctfd_dir/Dockerfile"
  fi

  if [ "$category" = "File_Upload" ]; then
    perl -0pi -e 's/RUN chmod 644 flag\.txt/RUN printf "%s\\n" "FLAG_REMOVED_FOR_CTFD" > flag.txt \&\& chmod 644 flag.txt/' "$ctfd_dir/Dockerfile"
  fi

  rm -f "$zip_path"
  (
    cd "$ctfd_dir"
    find . -type f | sort | zip -q "$zip_path" -@
  )

  echo "Rebuilt $zip_path from $ctfd_dir"
}

rebuild_one "Command_Injection" "CTFd_Command_Injection.zip"
rebuild_one "SQL_Injection" "CTFd_SQL_Injection.zip"
rebuild_one "CSRF" "CTFd_CSRF.zip"
rebuild_one "XSS" "CTFd_XSS.zip"
rebuild_one "File_Upload" "CTFd_File_Upload.zip"
