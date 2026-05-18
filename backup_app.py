from flask import Flask, render_template, request, redirect, abort, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "dev-secret-key"


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

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

