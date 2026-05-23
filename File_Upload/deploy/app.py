from flask import Flask, render_template, request, redirect, session
from pathlib import Path
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.secret_key = "super-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def allowed_extension(filename):
    path = Path(filename)

    if len(path.suffixes) != 1:
        return False

    return path.suffix.lower() in ALLOWED_EXTENSIONS


def valid_magic_bytes(file_storage):
    file_storage.stream.seek(0)
    header = file_storage.stream.read(8)
    file_storage.stream.seek(0)

    png_magic = b"\x89PNG\r\n\x1a\n"
    jpg_magic = b"\xff\xd8\xff"

    return header.startswith(png_magic) or header.startswith(jpg_magic)


def extract_json_from_file(path):
    with open(path, "r", encoding="latin-1") as f:
        raw = f.read()

    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1 or start >= end:
        return None

    return json.loads(raw[start:end + 1])


def status_page(title, message, variant="info", action_href="/", action_label="Back"):
    return render_template(
        "status.html",
        title=title,
        message=message,
        variant=variant,
        action_href=action_href,
        action_label=action_label,
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session["is_admin"] = False
    return redirect("/upload")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")

        if not file:
            return status_page(
                "파일이 선택되지 않았습니다",
                "업로드할 파일을 선택한 뒤 다시 시도하세요.",
                "warning",
                "/upload",
                "다시 업로드하기",
            )

        filename = secure_filename(file.filename)

        if not filename:
            return status_page(
                "파일 이름이 올바르지 않습니다",
                "처리할 수 없는 파일 이름입니다. 다른 이름으로 다시 시도하세요.",
                "warning",
                "/upload",
                "다시 업로드하기",
            )

        if not allowed_extension(filename):
            return status_page(
                "허용되지 않는 확장자입니다",
                "업로드 정책에 맞지 않는 파일입니다.",
                "danger",
                "/upload",
                "업로드로 돌아가기",
            )

        if not valid_magic_bytes(file):
            return status_page(
                "파일 검증에 실패했습니다",
                "업로드 정책에 맞지 않는 파일입니다.",
                "danger",
                "/upload",
                "업로드로 돌아가기",
            )

        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        try:
            data = extract_json_from_file(save_path)

            if isinstance(data, dict):
                session.update(data)

        except Exception:
            pass

        return status_page(
            "업로드 완료",
            "파일이 검사 과정을 통과하고 서버에 저장되었습니다.",
            "success",
            "/admin",
            "관리자 페이지 확인",
        )

    return render_template("upload.html")


@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return status_page(
            "관리자 전용 페이지입니다",
            "이 페이지는 관리자 권한이 있는 사용자만 접근할 수 있습니다.",
            "danger",
            "/upload",
            "업로드로 돌아가기",
        )

    filename = request.args.get("file")

    if not filename:
        return render_template("admin.html")

    target = os.path.join(BASE_DIR, filename)

    try:
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()

        return render_template("result.html", filename=filename, content=content)

    except Exception as e:
        return status_page(
            "파일을 읽을 수 없습니다",
            str(e),
            "warning",
            "/admin",
            "다시 검색하기",
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
