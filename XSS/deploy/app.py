from flask import Flask, render_template, request, redirect, abort, session, jsonify, make_response
import os
import sqlite3
from datetime import datetime
import secrets
import re
from bot import visit_ticket

app = Flask(__name__)
app.secret_key = "dev-secret-key"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_PATH = os.path.join(BASE_DIR, "flag.txt")


def load_flag():
    env_flag = os.environ.get("FLAG")
    if env_flag:
        return env_flag

    if os.path.exists(FLAG_PATH):
        with open(FLAG_PATH, "r", encoding="utf-8") as file:
            return file.read().strip()

    return "FLAG{dummy_xss_flag_for_local_test}"


FLAG = load_flag()
COLLECTED_BY_CLIENT = {}
XSS_CLIENT_COOKIE = "xss_client_id"
CLIENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,64}$")


def get_xss_client_id():
    client_id = request.cookies.get(XSS_CLIENT_COOKIE)
    if client_id and CLIENT_ID_PATTERN.fullmatch(client_id):
        return client_id

    return secrets.token_urlsafe(18)


def set_xss_client_cookie(resp, client_id):
    resp.set_cookie(
        XSS_CLIENT_COOKIE,
        client_id,
        max_age=60 * 60 * 6,
        httponly=True,
        samesite="Lax",
    )
    return resp

def get_db():
    conn = sqlite3.connect("ctf.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            owner_client_id TEXT
        )
    """)
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(tickets)").fetchall()}
    if "owner_client_id" not in columns:
        conn.execute("ALTER TABLE tickets ADD COLUMN owner_client_id TEXT")
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/request", methods=["GET", "POST"])
def create_request():
    client_id = get_xss_client_id()

    if request.method == "POST":
        title = request.form.get("title", "")
        content = request.form.get("content", "")

        conn = get_db()
        cur = conn.execute(
            "INSERT INTO tickets (title, content, created_at, owner_client_id) VALUES (?, ?, ?, ?)",
            (title, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), client_id)
        )
        conn.commit()

        ticket_id = cur.lastrowid
        conn.close()

        resp = make_response(redirect(f"/ticket/{ticket_id}"))
        return set_xss_client_cookie(resp, client_id)

    resp = make_response(render_template("request.html"))
    return set_xss_client_cookie(resp, client_id)
@app.route("/ticket/<int:ticket_id>")
def ticket(ticket_id):
    conn = get_db()
    ticket_data = conn.execute(
        "SELECT * FROM tickets WHERE id = ?",
        (ticket_id,)
    ).fetchone()
    conn.close()

    if ticket_data is None:
        abort(404)

    return render_template("ticket.html", ticket=ticket_data)

@app.route("/admin/login")
def admin_login():
    if request.remote_addr not in ("127.0.0.1", "::1"):
        abort(403)

    session["admin"] = True
    return "admin login success"

@app.route("/admin/ticket/<int:ticket_id>")
def admin_ticket(ticket_id):
    if not session.get("admin"):
        abort(403)

    conn = get_db()
    ticket = conn.execute(
        "SELECT * FROM tickets WHERE id = ?",
        (ticket_id,)
    ).fetchone()
    conn.close()

    if ticket is None:
        abort(404)

    return render_template("admin_ticket.html", ticket=ticket)

@app.route("/admin/audit")
def admin_audit():
    if not session.get("admin"):
        abort(403)

    csrf_token = secrets.token_hex(16)
    session["csrf_token"] = csrf_token

    return render_template("audit.html", csrf_token=csrf_token)

@app.route("/api/unmask")
def api_unmask():
    if not session.get("admin"):
        abort(403)

    target_id = request.args.get("target_id")
    csrf_token = request.args.get("csrf_token")

    if csrf_token != session.get("csrf_token"):
        abort(403)

    if target_id != "1004":
        abort(404)

    return jsonify({
        "target_id": "1004",
        "name": "김민수",
        "phone": "010-1234-1234",
        "email": "kimminsu@example.com",
        "sensitive_note": FLAG
    })

@app.route("/report", methods=["GET", "POST"])
def report():
    client_id = get_xss_client_id()

    if request.method == "POST":

        ticket_id = request.form.get("ticket_id", "")

        if not ticket_id.isdigit():
            return "invalid ticket id", 400

        conn = get_db()
        ticket = conn.execute(
            "SELECT owner_client_id FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()
        conn.close()

        if ticket is None:
            return "ticket not found", 404

        if ticket["owner_client_id"] != client_id:
            return "ticket does not belong to this browser session", 403

        visit_ticket(ticket_id, client_id)

        resp = make_response("admin bot visited your ticket. collected reports are temporarily stored internally")
        return set_xss_client_cookie(resp, client_id)

    resp = make_response(render_template("report.html"))
    return set_xss_client_cookie(resp, client_id)


@app.route("/collect")
def collect():
    data = request.args.get("data", "")
    client_id = request.cookies.get(XSS_CLIENT_COOKIE)
    if client_id and CLIENT_ID_PATTERN.fullmatch(client_id):
        COLLECTED_BY_CLIENT.setdefault(client_id, []).append(data)
    print("[COLLECT]", data)
    return "Saved to internal audit _log"

@app.route("/collect_log")
def collect_logs():
    client_id = get_xss_client_id()
    logs = COLLECTED_BY_CLIENT.get(client_id, [])
    resp = make_response("<br><hr>".join(logs))
    return set_xss_client_cookie(resp, client_id)

@app.route("/flag", methods=["GET", "POST"])
def flag_submit():
    message = ""

    if request.method == "POST":
        submitted_flag = request.form.get("flag", "")

        if submitted_flag == FLAG:
            message = "Correct!"
        else:
            message = "Wrong flag."

    return render_template("flag.html", message=message)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=80)
