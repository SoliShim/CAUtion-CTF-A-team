import os
import sqlite3
from flask import Flask, request, render_template

app = Flask(__name__)

# 🎯 진짜 플래그 (VIP 프리패스용)
REAL_FLAG = 'DH{n0_sp4c3_n0_substr_m4st3r}'

def init_db():
    conn = sqlite3.connect('sqli.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS user_table (uid TEXT, upw TEXT)')
    
    c.execute('SELECT count(*) FROM user_table')
    if c.fetchone()[0] == 0:
        # DB에도 REAL_FLAG 변수를 그대로 넣습니다.
        c.execute(f"INSERT INTO user_table (uid, upw) VALUES ('admin', '{REAL_FLAG}')")
        c.execute("INSERT INTO user_table (uid, upw) VALUES ('guest', 'guest')")
        conn.commit()
    conn.close()

init_db()

# 🔥 [핵심] WAF (웹 방화벽) 로직
def check_waf(input_str):
    # 1. VIP 프리패스: 완벽한 정답 플래그가 들어오면 무사 통과!
    if input_str == REAL_FLAG:
        return True

    # 2. 일반 검사: 띄어쓰기 차단
    if ' ' in input_str:
        return False
    # 3. 일반 검사: substr 차단
    if 'substr' in input_str.lower():
        return False
        
    return True

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')
    
    if request.method == 'POST':
        userid = request.form.get('userid', '')
        userpassword = request.form.get('userpassword', '')

        # WAF 검사 (실패 시 예쁜 경고 화면)
        if not check_waf(userid) or not check_waf(userpassword):
            return """
            <body style='background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;'>
                <div style='text-align:center; padding:40px; background:white; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.08); border-top: 5px solid #e74c3c;'>
                    <h1 style='color:#e74c3c; margin-top:0;'>🛡️ WAF Detected!</h1>
                    <p style='color:#7f8c8d; font-size:16px;'>No Hack! Malicious input blocked.</p>
                    <button onclick='history.back()' style='margin-top:20px; padding:10px 20px; border:none; border-radius:6px; background:#e74c3c; color:white; cursor:pointer;'>Go Back</button>
                </div>
            </body>
            """

        conn = sqlite3.connect('sqli.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            query = f"SELECT * FROM user_table WHERE uid='{userid}' and upw='{userpassword}'"
            cursor.execute(query)
            result = cursor.fetchone()
            conn.close()

            if result:
                # 로그인 성공 (예쁜 환영 화면)
                return f"""
                <body style='background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;'>
                    <div style='text-align:center; padding:40px; background:white; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.08); border-top: 5px solid #2ecc71;'>
                        <h1 style='color:#2ecc71; margin-top:0;'>🎉 Hello, {result['uid']}!</h1>
                        <p style='color:#7f8c8d; font-size:16px;'>Welcome to the secret area.</p>
                    </div>
                </body>
                """
            else:
                # 로그인 실패 (예쁜 에러 화면)
                return """
                <body style='background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;'>
                    <div style='text-align:center; padding:40px; background:white; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.08); border-top: 5px solid #f39c12;'>
                        <h1 style='color:#f39c12; margin-top:0;'>❌ Login Failed</h1>
                        <p style='color:#7f8c8d; font-size:16px;'>Invalid username or password.</p>
                        <button onclick='history.back()' style='margin-top:20px; padding:10px 20px; border:none; border-radius:6px; background:#f39c12; color:white; cursor:pointer;'>Try Again</button>
                    </div>
                </body>
                """

        except Exception as e:
            # SQL 문법 에러 (마찬가지로 실패 화면)
            return """
            <body style='background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;'>
                <div style='text-align:center; padding:40px; background:white; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.08); border-top: 5px solid #f39c12;'>
                    <h1 style='color:#f39c12; margin-top:0;'>❌ Login Failed</h1>
                    <p style='color:#7f8c8d; font-size:16px;'>An error occurred. Invalid input.</p>
                    <button onclick='history.back()' style='margin-top:20px; padding:10px 20px; border:none; border-radius:6px; background:#f39c12; color:white; cursor:pointer;'>Try Again</button>
                </div>
            </body>
            """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
