from flask import Flask, request, render_template, make_response, redirect, url_for
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
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
        "coin": 4_294_967_295,
    },
    "bdmin": {
        "password": "bdmin123",
        "coin": 65_535,
    },
    "cdmin": {
        "password": "cdmin123",
        "coin": 32_767,
    },
    "ddmin": {
        "password": "ddmin123",
        "coin": 255,
    },
    "edmin": {
        "password": "edmin123",
        "coin": 127,
    },
    "guest": {
        "password": "guest",
        "coin": 0,
    },
}

session_storage = {}
token_storage = {}
problem_storage = {}


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
    service = Service(executable_path="/chromedriver")
    options = webdriver.ChromeOptions()
    try:
        for _ in [
            "headless",
            "window-size=1920x1080",
            "disable-gpu",
            "no-sandbox",
            "disable-dev-shm-usage",
        ]:
            options.add_argument(_)
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(3)
        driver.get("http://127.0.0.1:8000/login")
        driver.add_cookie(cookie)
        driver.find_element(by=By.NAME, value="username").send_keys("admin")
        driver.find_element(by=By.NAME, value="password").send_keys(users["admin"])
        driver.find_element(by=By.NAME, value="submit").click()
        driver.get(url)
    except Exception as e:
        driver.quit()
        # return str(e)
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
    coin = users[username]["coin"] if username and username in users else None
    return {"current_user": username, "current_coin": coin}


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
        return render_template("flag.html")
    elif request.method == "POST":
        param = request.form.get("param", "")
        if not check_csrf(param):
            return '<script>alert("wrong??");history.go(-1);</script>'

        return '<script>alert("good");history.go(-1);</script>'

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
        return render_template("index.html", text="please login")

    if request.method == "GET":
        return render_template("shop.html", price=FLAG_PRICE)

    if users[username]["coin"] < FLAG_PRICE:
        return render_template(
            "shop.html",
            price=FLAG_PRICE,
            text="코인이 부족합니다.",
        )

    users[username]["coin"] -= FLAG_PRICE

    return render_template("shop.html", price=FLAG_PRICE, flag=FLAG)


@app.route("/earn", methods=["GET", "POST"])
def earn():
    username = login_required()

    if username is None:
        return render_template("index.html", text="please login")

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
            users[username]["coin"] += 1
            message = ("success", "정답입니다! +1 코인")
        else:
            message = ("error", f"오답입니다. 정답은 {current['answer']} 였습니다.")

        problem_storage[session_id] = generate_problem()
    else:
        if session_id not in problem_storage:
            problem_storage[session_id] = generate_problem()

    problem = problem_storage[session_id]
    return render_template("earn.html", problem=problem, message=message)


@app.route("/rank")
def rank():
    ranking = sorted(
        users.items(),
        key=lambda item: item[1]["coin"],
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
                "coin": data["coin"],
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
        return render_template('index.html', text='please login')
    if request.method == 'GET':
        return render_template("transfer.html", csrf_token=csrf_token)
    elif request.method == 'POST':
        form_token = request.form.get("csrf_token", "")
        to = request.form.get("to", "")
        amount_raw = request.form.get("amount", "0")

        if form_token != csrf_token:
            return "invalid csrf token"
        
        if to not in users:
            return "invalid user"
        
        try:
            amount = int(amount_raw)
        except ValueError:
            return "invalid amount"
        
        if amount <= 0:
            return "invalid amount"

        if users[username]["coin"] < amount:
            return "not enough coin"

        users[username]["coin"] -= amount
        users[to]["coin"] += amount

        return "transfer success"
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)