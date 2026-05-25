#!/usr/bin/env python3
import argparse
import getpass
import html
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT_DIR / "docker-compose.ctf.yml"
ENV_FILE = ROOT_DIR / ".env.ctf"
LINKS_HTML = ROOT_DIR / "ctf_tunnel_links.html"

CHALLENGES = [
    {
        "label": "Command Injection",
        "service": "tunnel-command-injection",
        "aliases": ["command injection", "command_injection", "command", "cmd"],
        "message_name": "Command Injection",
    },
    {
        "label": "SQL Injection",
        "service": "tunnel-sql-injection",
        "aliases": ["sql injection", "sql_injection", "sqli", "sql"],
        "message_name": "SQL Injection",
    },
    {
        "label": "CSRF",
        "service": "tunnel-csrf",
        "aliases": ["csrf"],
        "message_name": "CSRF",
    },
    {
        "label": "XSS",
        "service": "tunnel-xss",
        "aliases": ["xss"],
        "message_name": "XSS",
    },
    {
        "label": "File Upload",
        "service": "tunnel-file-upload",
        "aliases": ["file upload", "file_upload", "upload"],
        "message_name": "File Upload",
    },
]

PATCH_KEYS = [
    "name",
    "category",
    "value",
    "type",
    "state",
    "max_attempts",
    "next_id",
    "requirements",
    "connection_info",
    "initial",
    "minimum",
    "decay",
    "function",
    "description",
]


class CTFdClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.csrf_nonce = None
        self.cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookies)
        )

    def request(self, method, path, data=None, headers=None):
        url = self.base_url + path
        body = None
        final_headers = {
            "User-Agent": "caution-ctf-link-updater/1.0",
            "Accept": "application/json",
        }
        if headers:
            final_headers.update(headers)
        if self.token:
            final_headers["Authorization"] = f"Token {self.token}"
        if self.csrf_nonce and method not in {"GET", "HEAD"}:
            final_headers["CSRF-Token"] = self.csrf_nonce

        if data is not None:
            if isinstance(data, bytes):
                body = data
            else:
                body = json.dumps(data).encode("utf-8")
                final_headers["Content-Type"] = "application/json"

        req = urllib.request.Request(
            url, data=body, headers=final_headers, method=method
        )
        try:
            with self.opener.open(req, timeout=20) as resp:
                raw = resp.read()
                content_type = resp.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return json.loads(raw.decode("utf-8"))
                return raw.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"{method} {path} failed with HTTP {exc.code}: {shorten(detail)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"{method} {path} failed: {exc.reason}") from exc

    def get_text(self, path):
        url = self.base_url + path
        headers = {"User-Agent": "caution-ctf-link-updater/1.0"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        req = urllib.request.Request(url, headers=headers, method="GET")
        with self.opener.open(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="replace")

    def login(self, username, password):
        page = self.get_text("/login")
        nonce = extract_nonce(page)
        if not nonce:
            raise RuntimeError("Could not find CTFd login nonce on /login")
        self.csrf_nonce = nonce

        form = urllib.parse.urlencode(
            {
                "name": username,
                "password": password,
                "nonce": nonce,
                "_submit": "Submit",
            }
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": self.base_url + "/login",
            "User-Agent": "caution-ctf-link-updater/1.0",
        }
        req = urllib.request.Request(
            self.base_url + "/login", data=form, headers=headers, method="POST"
        )
        with self.opener.open(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")

        admin_page = self.get_text("/admin/challenges")
        self.csrf_nonce = extract_nonce(admin_page) or self.csrf_nonce
        if "admin/challenges" not in admin_page and "Challenges" not in admin_page:
            if "incorrect" in body.lower() or "invalid" in body.lower():
                raise RuntimeError("CTFd login failed")

    def list_challenges(self):
        data = self.request("GET", "/api/v1/challenges?view=admin")
        if not isinstance(data, dict) or not data.get("success"):
            raise RuntimeError(f"Could not list challenges: {data}")
        return data.get("data", [])

    def get_challenge(self, challenge_id):
        data = self.request("GET", f"/api/v1/challenges/{challenge_id}")
        if not isinstance(data, dict) or not data.get("success"):
            raise RuntimeError(f"Could not read challenge {challenge_id}: {data}")
        return data.get("data", {})

    def patch_challenge(self, challenge_id, payload):
        data = self.request("PATCH", f"/api/v1/challenges/{challenge_id}", payload)
        if not isinstance(data, dict) or not data.get("success"):
            raise RuntimeError(f"Could not update challenge {challenge_id}: {data}")
        return data.get("data", {})


def shorten(text, limit=500):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def extract_nonce(page):
    patterns = [
        r'name=["\']nonce["\']\s+value=["\']([^"\']+)["\']',
        r'value=["\']([^"\']+)["\']\s+name=["\']nonce["\']',
        r'csrfNonce["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        r'nonce["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, page)
        if match:
            return html.unescape(match.group(1))
    return None


def compose_cmd():
    cmd = ["docker", "compose"]
    if ENV_FILE.exists():
        cmd += ["--env-file", str(ENV_FILE)]
    cmd += ["-f", str(COMPOSE_FILE)]
    return cmd


def tunnel_url_from_logs(service):
    cmd = compose_cmd() + ["logs", "--no-color", service]
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT_DIR,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except FileNotFoundError:
        return None

    matches = re.findall(r"https://[-a-zA-Z0-9.]+\.trycloudflare\.com", result.stdout)
    return matches[-1] if matches else None


def tunnel_urls_from_html():
    if not LINKS_HTML.exists():
        return []
    text = LINKS_HTML.read_text(encoding="utf-8", errors="replace")
    return re.findall(r"https://[-a-zA-Z0-9.]+\.trycloudflare\.com", text)


def collect_tunnel_urls():
    urls = {}
    html_urls = tunnel_urls_from_html()
    html_index = 0
    for challenge in CHALLENGES:
        url = tunnel_url_from_logs(challenge["service"])
        if not url and html_index < len(html_urls):
            url = html_urls[html_index]
            html_index += 1
        urls[challenge["label"]] = url
    return urls


def normalize(text):
    return re.sub(r"[^a-z0-9가-힣]+", " ", (text or "").lower()).strip()


def is_b_group(challenge):
    combined = normalize(
        " ".join(
            str(challenge.get(key, ""))
            for key in ["name", "category", "description", "tags"]
        )
    )
    return "b조" in combined or "b 조" in combined or " b " in f" {combined} "


def match_problem(challenge, problem):
    fields = " ".join(
        str(challenge.get(key, "")) for key in ["name", "category", "description"]
    )
    normalized = normalize(fields).replace("_", " ")
    return any(alias in normalized for alias in problem["aliases"])


def find_targets(challenges):
    targets = {}
    unmatched = []

    for problem in CHALLENGES:
        candidates = [
            challenge
            for challenge in challenges
            if is_b_group(challenge) and match_problem(challenge, problem)
        ]
        if len(candidates) == 1:
            targets[problem["label"]] = candidates[0]
        else:
            unmatched.append((problem, candidates))

    return targets, unmatched


def challenge_display(challenge):
    return (
        f"id={challenge.get('id')} name={challenge.get('name')!r} "
        f"category={challenge.get('category')!r}"
    )


def build_description(problem, url):
    return (
        f"B조 {problem['message_name']} 문제입니다.\n"
        "아래 링크로 접속해주세요.\n"
        f"{url}"
    )


def build_patch_payload(current, description):
    payload = {key: current[key] for key in PATCH_KEYS if key in current}
    payload["description"] = description
    return payload


def env_or_arg(value, env_name):
    return value if value is not None else os.environ.get(env_name)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Update B group CTFd challenge messages with current tunnel URLs."
    )
    parser.add_argument("--url", default=None, help="CTFd base URL")
    parser.add_argument("--username", default=None, help="CTFd admin username")
    parser.add_argument("--password", default=None, help="CTFd admin password")
    parser.add_argument("--token", default=None, help="CTFd access token")
    parser.add_argument("--dry-run", action="store_true", help="Print updates only")
    return parser.parse_args()


def main():
    args = parse_args()
    base_url = env_or_arg(args.url, "CTFD_URL") or "http://158.179.192.158:8000"
    username = env_or_arg(args.username, "CTFD_USERNAME") or "admin"
    password = env_or_arg(args.password, "CTFD_PASSWORD")
    token = env_or_arg(args.token, "CTFD_TOKEN")

    tunnel_urls = collect_tunnel_urls()
    missing_urls = [label for label, url in tunnel_urls.items() if not url]
    if missing_urls:
        print("Missing tunnel URL(s): " + ", ".join(missing_urls), file=sys.stderr)
        print("Run ./scripts/start_free_tunnels.sh first.", file=sys.stderr)
        return 1

    client = CTFdClient(base_url, token=token)
    if not token:
        if not password:
            password = getpass.getpass(f"CTFd password for {username}: ")
        client.login(username, password)

    challenges = client.list_challenges()
    targets, unmatched = find_targets(challenges)
    if unmatched:
        print("Could not uniquely match every B group challenge.", file=sys.stderr)
        for problem, candidates in unmatched:
            print(f"- {problem['label']}: {len(candidates)} candidate(s)", file=sys.stderr)
            for candidate in candidates[:5]:
                print(f"  {challenge_display(candidate)}", file=sys.stderr)
        print("\nVisible challenge candidates:", file=sys.stderr)
        for challenge in challenges:
            if is_b_group(challenge):
                print(f"  {challenge_display(challenge)}", file=sys.stderr)
        return 1

    for problem in CHALLENGES:
        label = problem["label"]
        target = targets[label]
        description = build_description(problem, tunnel_urls[label])
        print(f"{label}: {challenge_display(target)}")
        print(description)
        if args.dry_run:
            print("dry-run: not updated")
            continue

        current = client.get_challenge(target["id"])
        payload = build_patch_payload(current, description)
        client.patch_challenge(target["id"], payload)
        print("updated")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
