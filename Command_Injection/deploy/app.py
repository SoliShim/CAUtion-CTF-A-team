import os
import pwd
import re
import secrets
import subprocess

from flask import Flask, render_template, request, session


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_ROOT = os.path.join(BASE_DIR, "reports")
FLAG_PATH = os.path.join(BASE_DIR, "flag.txt")
SAFE_FILENAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
CLIENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,64}$")
COMMAND_USER = os.environ.get("COMMAND_USER", "command")
SAMPLE_FILES = {
    "notice.txt": "Only report files can be inspected from this page.\n",
    "health.log": "web=ok db=ok cache=ok\n",
    "backup.log": "daily backup completed\n",
    "result.txt": "No saved command output yet.\n",
}


def load_flag():
    env_flag = os.environ.get("FLAG")
    if env_flag:
        return env_flag

    if os.path.exists(FLAG_PATH):
        with open(FLAG_PATH, "r", encoding="utf-8") as file:
            return file.read().strip()

    return "FLAG{fake_flag_for_local_test}"


FLAG = load_flag()


def ensure_report_files(report_dir):
    os.makedirs(report_dir, exist_ok=True)

    for filename, content in SAMPLE_FILES.items():
        path = os.path.join(report_dir, filename)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)

    try:
        user_info = pwd.getpwnam(COMMAND_USER)
        os.chown(os.path.dirname(report_dir), user_info.pw_uid, user_info.pw_gid)
        os.chown(report_dir, user_info.pw_uid, user_info.pw_gid)
        for filename in SAMPLE_FILES:
            os.chown(os.path.join(report_dir, filename), user_info.pw_uid, user_info.pw_gid)
    except (KeyError, PermissionError, OSError):
        pass


def get_client_report_dir():
    client_id = session.get("client_id")

    if not client_id or not CLIENT_ID_PATTERN.fullmatch(client_id):
        client_id = secrets.token_urlsafe(18)
        session["client_id"] = client_id

    report_dir = os.path.join(REPORT_ROOT, client_id, "reports")
    ensure_report_files(report_dir)
    return report_dir


def init_challenge_files():
    os.makedirs(REPORT_ROOT, exist_ok=True)

    if os.environ.get("FLAG") or not os.path.exists(FLAG_PATH):
        with open(FLAG_PATH, "w", encoding="utf-8") as file:
            file.write(FLAG + "\n")


def check_waf(filename):
    if not filename:
        return False, "파일 이름을 입력해야 합니다."

    if " " in filename:
        return False, "공백(Space)은 사용할 수 없습니다."

    if ".." in filename:
        return False, "상위 디렉토리 이동(..)은 사용할 수 없습니다."

    if "cat" in filename.lower():
        return False, "'cat' 명령어는 사용할 수 없습니다."

    return True, "Pass"


def is_safe_report_name(filename):
    return bool(SAFE_FILENAME_PATTERN.fullmatch(filename))


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    status = None
    filename = "notice.txt"
    report_dir = get_client_report_dir()

    if request.method == "POST":
        filename = request.form.get("filename", "")
        passed, message = check_waf(filename)

        if not passed:
            error = message
        else:
            command = f"head -n 20 {report_dir}/{filename}"

            try:
                completed = subprocess.run(
                    command,
                    shell=True,
                    cwd=os.path.dirname(report_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=3,
                    user=COMMAND_USER,
                )

                if is_safe_report_name(filename):
                    result = completed.stdout or "No output."
                else:
                    status = "Report inspection completed."
            except subprocess.TimeoutExpired:
                error = "명령 실행 시간이 초과되었습니다."

    return render_template(
        "index.html",
        error=error,
        filename=filename,
        result=result,
        status=status,
    )


if __name__ == "__main__":
    init_challenge_files()
    app.run(host="0.0.0.0", port=80)
