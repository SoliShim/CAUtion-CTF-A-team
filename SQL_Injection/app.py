import os
import sqlite3
from flask import Flask, request, render_template

app = Flask(__name__)

# 🎯 플래그 양식 (금지된 함수 이름들이 조롱하듯 들어있습니다)
REAL_FLAG = 'FLAG{n0_substr_n0_glob_n0_like_n0_instr_m4st3r}'

def init_db():
    conn = sqlite3.connect('sqli.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS user_table (uid TEXT, upw TEXT)')
    
    c.execute('SELECT count(*) FROM user_table')
    if c.fetchone()[0] == 0:
        c.execute(f"INSERT INTO user_table (uid, upw) VALUES ('admin', '{REAL_FLAG}')")
        c.execute("INSERT INTO user_table (uid, upw) VALUES ('guest', 'guest')")
        conn.commit()
    conn.close()

init_db()

# 🔥 악마의 웹 방화벽 (WAF)
def check_waf(input_str):
    # 💡 중요: 플래그 자체에 'substr', 'glob' 같은 금지어가 포함되어 있으므로, 
    # 정답을 정확히 입력한 경우에는 WAF를 예외적으로 통과시켜줍니다.
    if input_str == REAL_FLAG:
        return True, "Pass"

    if ' ' in input_str:
        return False, "공백(Space)은 사용할 수 없습니다. (우회 기법을 떠올려보세요!)"

    if '=' in input_str:
        return False, "'=' 기호가 차단되었습니다! 이제 참/거짓을 어떻게 판별할 건가요? 짱구를 굴려보세요. 🧠"

    forbidden_rules = {
        'substr': "'substr'로 자르려고요? 아쉽지만 가위는 압수입니다. ✂️",
        'glob': "오, 'glob'을 아시네요? 하지만 여기선 안 통합니다. 🚫",
        'like': "'like'로 패턴 찾기? 제 취향은 아니네요. 👎",
        'instr': "'instr'로 위치 찾기? 안타깝게도 내비게이션이 고장 났습니다. 🧭",
        'replace': "'replace' 꼼수 금지! 문자열을 훼손하지 마세요. 🛑",
        'mid': "'mid' 함수로 중간을 빼먹을 순 없습니다.",
        'left': "왼쪽('left')으로 가는 길은 막혔습니다.",
        'right': "오른쪽('right') 길도 막혔습니다. 오직 부등호만 믿으세요!",
        'char': "'char' 함수로 문자를 우회 생성하는 것도 금지되어 있습니다."
    }

    for word, custom_msg in forbidden_rules.items():
        if word in input_str.lower():
            return False, custom_msg
            
    return True, "Pass"

# 🚪 1단계 관문: 메인 페이지 (로그인 폼)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')
    
    if request.method == 'POST':
        userid = request.form.get('userid', '')
        userpassword = request.form.get('userpassword', '')

        # WAF 검사
        id_pass, id_msg = check_waf(userid)
        pw_pass, pw_msg = check_waf(userpassword)

        if not id_pass or not pw_pass:
            error_message = id_msg if not id_pass else pw_msg
            return f"""
            <body style='background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;'>
                <div style='text-align:center; padding:40px; background:white; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.08); border-top: 5px solid #e74c3c;'>
                    <h1 style='color:#e74c3c; margin-top:0;'>🛡️ WAF Detected!</h1>
                    <p style='color:#333; font-size:18px; font-weight:bold;'>{error_message}</p>
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

            # 💡 로그인이 뚫렸을 때 (우회든, 찐 비번이든 무조건 대시보드 출력)
            if result:
                return f"""
                <body style='background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif; margin:0;'>
                    <div style='text-align:center; padding:40px; background:white; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.08); border-top: 5px solid #3498db; width: 350px;'>
                        <h1 style='color:#3498db; margin-top:0;'>🔓 로그인 성공!</h1>
                        <p style='color:#7f8c8d; font-size:15px; margin-bottom: 20px;'>
                            관리자 권한을 획득하셨습니다!<br>
                            하지만 진정한 클리어를 위해서는 전체 비밀번호를 알아내야 합니다.<br>
                            <strong>추출한 플래그를 아래에 인증하세요.</strong>
                        </p>
                        
                        <form method="POST" action="/flag">
                            <input type="text" name="flag" placeholder="CAUtion{{...}}" required autocomplete="off" style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #dfe6e9; border-radius:6px; box-sizing:border-box; font-size:15px;">
                            <button type="submit" style="width:100%; padding:12px; background:#3498db; color:white; border:none; border-radius:6px; font-size:16px; font-weight:bold; cursor:pointer; transition:0.3s;">플래그 제출 🚩</button>
                        </form>
                        
                        <div style="margin-top: 20px;">
                            <a href="/" style="color:#95a5a6; text-decoration:none; font-size:13px;">로그아웃 (처음으로)</a>
                        </div>
                    </div>
                </body>
                """
            else:
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
            return """
            <body style='background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;'>
                <div style='text-align:center; padding:40px; background:white; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.08); border-top: 5px solid #f39c12;'>
                    <h1 style='color:#f39c12; margin-top:0;'>❌ Login Failed</h1>
                    <p style='color:#7f8c8d; font-size:16px;'>An error occurred. Invalid SQL syntax.</p>
                    <button onclick='history.back()' style='margin-top:20px; padding:10px 20px; border:none; border-radius:6px; background:#f39c12; color:white; cursor:pointer;'>Try Again</button>
                </div>
            </body>
            """

# 🚩 2단계 관문: 플래그 인증 전용 라우터 (대시보드에서 제출했을 때)
@app.route('/flag', methods=['POST'])
def submit_flag():
    submitted_flag = request.form.get('flag', '')
    
    if submitted_flag == REAL_FLAG:
        return """
        <body style='background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;'>
            <div style='text-align:center; padding:40px; background:white; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.08); border-top: 5px solid #9b59b6;'>
                <h1 style='color:#9b59b6; margin-top:0;'>🏆 정답입니다!</h1>
                <p style='color:#333; font-size:18px; font-weight:bold;'>축하합니다! 완벽하게 플래그를 인증했습니다.</p>
                <button onclick="location.href='/'" style='margin-top:20px; padding:10px 20px; border:none; border-radius:6px; background:#9b59b6; color:white; cursor:pointer;'>처음으로 돌아가기</button>
            </div>
        </body>
        """
    else:
        return """
        <body style='background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;'>
            <div style='text-align:center; padding:40px; background:white; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.08); border-top: 5px solid #e74c3c;'>
                <h1 style='color:#e74c3c; margin-top:0;'>❌ 오답입니다</h1>
                <p style='color:#7f8c8d; font-size:16px;'>플래그가 일치하지 않습니다. 스크립트를 다시 확인해 보세요.</p>
                <button onclick='history.back()' style='margin-top:20px; padding:10px 20px; border:none; border-radius:6px; background:#e74c3c; color:white; cursor:pointer;'>다시 시도</button>
            </div>
        </body>
        """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
