import os
import re
import subprocess

from flask import Flask, render_template, request


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")
FLAG_PATH = os.path.join(BASE_DIR, "flag.txt")
FLAG = os.environ.get("FLAG", "DH{fake_flag_for_local_test}")
SAFE_FILENAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


def init_challenge_files():
    os.makedirs(REPORT_DIR, exist_ok=True)

    sample_files = {
        "notice.txt": "Only report files can be inspected from this page.\n",
        "health.log": "web=ok db=ok cache=ok\n",
        "backup.log": "daily backup completed\n",
        "result.txt": "No saved command output yet.\n",
    }

    for filename, content in sample_files.items():
        path = os.path.join(REPORT_DIR, filename)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)

    if not os.path.exists(FLAG_PATH):
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

    if request.method == "POST":
        filename = request.form.get("filename", "")
        passed, message = check_waf(filename)

        if not passed:
            error = message
        else:
            command = f"head -n 20 {REPORT_DIR}/{filename}"

            try:
                completed = subprocess.run(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=3,
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
