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
    
    userid = request.form.get('userid', '')
    userpassword = request.form.get('userpassword', '')

    # 입력값 필터링 검사
    if not check_waf(userid) or not check_waf(userpassword):
        return "No Hack! (WAF Detected)", 403

    try:
        conn = sqlite3.connect('sqli.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 취약점이 터지는 쿼리문
        query = f"SELECT * FROM user_table WHERE uid='{userid}' and upw='{userpassword}'"
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()

        # 로그인 결과 반환
        if result:
            return f"hello {result['uid']}"
        else:
            return "Login Failed..."
            
    except Exception as e:
        return "Login Failed..."

if __name__ == '__main__':
    # 주어진 Dockerfile의 EXPOSE 80에 맞춰 포트 변경
    app.run(host='0.0.0.0', port=5000)