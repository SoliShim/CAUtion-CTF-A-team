from flask import Flask, request, render_template, make_response, redirect, url_for
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from hashlib import md5
import urllib
import os
import random

import secrets


app = Flask(__name__)
app.secret_key = os.urandom(32)

PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"
FLAG_PRICE = 2_147_483_647

try:
    FLAG = open("./flag.txt", "r").read()
except:
    FLAG = "[**FLAG**]"

users = {
    "admin": {
        "password": secrets.token_hex(16),
        "money": 4_294_967_295,
    },
    "bdmin": {
        "password": "bdmin123",
        "money": 65_535,
    },
    "cdmin": {
        "password": "cdmin123",
        "money": 32_767,
    },
    "ddmin": {
        "password": "ddmin123",
        "money": 255,
    },
    "edmin": {
        "password": "edmin123",
        "money": 127,
    },
    "guest": {
        "password": "guest",
        "money": 0,
    },
}

session_storage = {}
token_storage = {}
problem_storage = {}
purchased_users = set()
flag_in_flight = set()


def generate_problem():
    a = random.randint(1, 50)
    b = random.randint(1, 50)
    op = random.choice(["+", "-", "*"])
    if op == "+":
        answer = a + b
    elif op == "-":
        answer = a - b
    else:
        answer = a * b
    return {"a": a, "b": b, "op": op, "answer": answer}

def read_url(url, cookie={"name": "name", "value": "value"}):
    cookie.update({"domain": "127.0.0.1"})
    service = Service(executable_path="/usr/bin/chromedriver")
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium"
    options.page_load_strategy = "eager"
    try:
        for _ in [
            "headless=new",
            "window-size=1280x720",
            "disable-gpu",
            "no-sandbox",
            "disable-dev-shm-usage",
            "disable-extensions",
            "disable-images",
            "blink-settings=imagesEnabled=false",
        ]:
            options.add_argument(_)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(10)

        session_id = create_session("admin", "127.0.0.1")
        driver.get("http://127.0.0.1:8000/")
        driver.add_cookie(cookie)
        driver.add_cookie({"name": "sessionid", "value": session_id, "domain": "127.0.0.1"})

        driver.get(url)
        current_url = driver.current_url
        try:
            WebDriverWait(driver, 5).until(lambda d: d.current_url != current_url)
        except TimeoutException:
            pass
    except Exception as e:
        try:
            driver.quit()
        except Exception:
            pass
        print(f"[read_url] Exception: {type(e).__name__}: {e}", flush=True)
        return False
    driver.quit()
    return True

def check_csrf(param, cookie={"name": "name", "value": "value"}):
    url = f"http://127.0.0.1:8000/vuln?param={urllib.parse.quote(param)}"
    return read_url(url, cookie)

def create_session(username, remote_addr):
    session_id = os.urandom(8).hex()
    session_storage[session_id] = username
    token_storage[session_id] = md5((username + remote_addr).encode()).hexdigest()
    return session_id

def get_username():
    session_id = request.cookies.get("sessionid")

    if session_id is None:
        return None

    return session_storage.get(session_id)

def get_csrf_token():
    session_id = request.cookies.get("sessionid")

    if session_id is None:
        return None

    return token_storage.get(session_id)

def login_required():
    username = get_username()

    if username is None:
        return None

    return username


@app.context_processor
def inject_user():
    username = get_username()
    money = users[username]["money"] if username and username in users else None
    return {"current_user": username, "current_money": money}


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/logout")
def logout():
    session_id = request.cookies.get("sessionid")
    if session_id:
        session_storage.pop(session_id, None)
        token_storage.pop(session_id, None)
        problem_storage.pop(session_id, None)
    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("sessionid", "", expires=0)
    return resp

@app.route("/vuln")
def vuln():
    param = request.args.get("param", "").lower()
    return param

@app.route("/flag", methods=["GET", "POST"])
def flag():
    if request.method == "GET":
        return render_template("flag.html", base_url=BASE_URL)
    elif request.method == "POST":
        session_id = request.cookies.get("sessionid") or request.remote_addr
        if session_id in flag_in_flight:
            return render_template("flag.html", base_url=BASE_URL, message=("error", "이전 요청을 처리 중입니다. 잠시 후 다시 시도해주세요."))
        flag_in_flight.add(session_id)
        try:
            param = request.form.get("param", "")
            try:
                result = check_csrf(param)
            except Exception:
                result = False
            if not result:
                return render_template("flag.html", base_url=BASE_URL, message=("error", "잘못된 payload입니다."))
            return render_template("flag.html", base_url=BASE_URL, message=("success", "payload가 전송되었습니다."))
        finally:
            flag_in_flight.discard(session_id)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username not in users:
            return '<script>alert("user not found");history.go(-1);</script>'

        if users[username]["password"] == password:
            resp = make_response(redirect(url_for("index")))
            session_id = create_session(username, request.remote_addr)
            resp.set_cookie("sessionid", session_id)
            return resp

        return '<script>alert("wrong password");history.go(-1);</script>'

@app.route("/shop", methods=["GET", "POST"])
def shop():
    username = login_required()

    if username is None:
        return render_template("shop.html", price=FLAG_PRICE, text="please login")

    already_purchased = username in purchased_users

    if request.method == "GET":
        return render_template(
            "shop.html",
            price=FLAG_PRICE,
            flag=FLAG if already_purchased else None,
            purchased=already_purchased,
        )

    if already_purchased:
        return render_template(
            "shop.html",
            price=FLAG_PRICE,
            flag=FLAG,
            purchased=True,
        )

    if users[username]["money"] < FLAG_PRICE:
        return render_template(
            "shop.html",
            price=FLAG_PRICE,
            text="잔액이 부족합니다.",
        )

    users[username]["money"] -= FLAG_PRICE
    purchased_users.add(username)

    return render_template(
        "shop.html",
        price=FLAG_PRICE,
        flag=FLAG,
        purchased=True,
    )


@app.route("/game", methods=["GET", "POST"])
def game():
    username = login_required()

    if username is None:
        return render_template("game.html", text="please login")

    session_id = request.cookies.get("sessionid")
    message = None

    if request.method == "POST":
        try:
            user_answer = int(request.form.get("answer", ""))
        except ValueError:
            user_answer = None

        current = problem_storage.get(session_id)
        if current is None:
            current = generate_problem()

        if user_answer == current["answer"]:
            users[username]["money"] += 1
            message = ("success", "정답입니다! +1원")
        else:
            message = ("error", f"오답입니다. 정답은 {current['answer']} 였습니다.")

        problem_storage[session_id] = generate_problem()
    else:
        if session_id not in problem_storage:
            problem_storage[session_id] = generate_problem()

    problem = problem_storage[session_id]
    return render_template("game.html", problem=problem, message=message)


@app.route("/rank")
def rank():
    ranking = sorted(
        users.items(),
        key=lambda item: item[1]["money"],
        reverse=True
    )

    ranking_data = []
    for i, item in enumerate(ranking, start=1):
        username = item[0]
        data = item[1]
        ranking_data.append(
            {
                "rank": i,
                "username": username,
                "money": data["money"],
            }
        )
    return render_template("rank.html", ranking=ranking_data)
    
@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    session_id = request.cookies.get('sessionid', None)
    try:
        username = session_storage[session_id]
        csrf_token = token_storage[session_id]
    except KeyError:
        return render_template('transfer.html', text='please login')
    if request.method == 'GET':
        return render_template("transfer.html", csrf_token=csrf_token)
    elif request.method == 'POST':
        form_token = request.form.get("csrf_token", "")
        to = request.form.get("to", "")
        amount_raw = request.form.get("amount", "0")

        def err(msg):
            return render_template("transfer.html", csrf_token=csrf_token, text=msg)

        if form_token != csrf_token:
            return err("유효하지 않은 요청입니다.")

        if to not in users:
            return err("존재하지 않는 사용자입니다.")

        try:
            amount = int(amount_raw)
        except ValueError:
            return err("금액이 올바르지 않습니다.")

        if amount <= 0:
            return err("금액은 1 이상이어야 합니다.")

        if users[username]["money"] < amount:
            return err("잔액이 부족합니다.")

        users[username]["money"] -= amount
        users[to]["money"] += amount

        return render_template("transfer.html", csrf_token=csrf_token, text_success="송금이 완료되었습니다.")
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)