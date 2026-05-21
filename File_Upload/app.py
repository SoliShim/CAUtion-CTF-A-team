from flask import Flask, render_template, request, redirect, session
import os
import json

app = Flask(__name__)
app.secret_key = "super-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')

        session['username'] = username
        session['is_admin'] = False

        return redirect('/')

    return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            return 'No file'

        filename = file.filename

        # 취약한 확장자 검사
        if not (filename.endswith('.png') or filename.endswith('.jpg')):
            return 'Only png/jpg allowed'

        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        # 업로드 파일 내용을 JSON으로 파싱
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 취약한 세션 merge
            session.update(data)

        except Exception:
            pass

        return 'Upload success'

    return render_template('upload.html')


@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return 'Admin only'

    filename = request.args.get('file')

    if not filename:
        return render_template('admin.html')

    target = os.path.join(BASE_DIR, filename)

    try:
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()

        return f'<pre>{content}</pre>'

    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)