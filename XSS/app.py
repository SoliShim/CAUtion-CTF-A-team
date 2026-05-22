from flask import Flask, render_template, request, redirect, abort, session, jsonify
import sqlite3
from datetime import datetime
import secrets
from bot import visit_ticket

app = Flask(__name__)
app.secret_key = "dev-secret-key"
FLAG = "FLAG{XSSCompleted!}"
COLLECTED = []

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
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/request", methods=["GET", "POST"])
def create_request():
    if request.method == "POST":
        title = request.form.get("title", "")
        content = request.form.get("content", "")

        conn = get_db()
        cur = conn.execute(
            "INSERT INTO tickets (title, content, created_at) VALUES (?, ?, ?)",
            (title, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()

        ticket_id = cur.lastrowid
        conn.close()

        return redirect(f"/ticket/{ticket_id}")

    return render_template("request.html")
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

    if request.method == "POST":

        ticket_id = request.form.get("ticket_id", "")

        if not ticket_id.isdigit():
            return "invalid ticket id", 400

        visit_ticket(ticket_id)

        return "admin bot visited your ticket. collected reports are temporarily stored internally"

    return render_template("report.html")


@app.route("/collect")
def collect():
    data = request.args.get("data", "")
    COLLECTED.append(data)
    print("[COLLECT]", data)
    return "Saved to internal audit _log"

@app.route("/collect_log")
def collect_logs():
    return "<br><hr>".join(COLLECTED)

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
