# CSRF Challenge
CSRF(Cross-Site Request Forgery)에 관련된 CTF 문제입니다.

코인을 모으고 거래할 수 있는 가상의 서비스가 있습니다.  
상점에서 플래그를 구매할 수 있으며, 이를 위해선 2,147,483,647 코인이 필요합니다.  
수학 문제를 풀면 돈을 벌 수 있습니다. 그러나 한 문제당 1 코인밖에 못 법니다.  
랭킹에는 보유 자산 순으로 사용자가 나열되어 있습니다. admin의 돈을 뺏고 싶지 않으신가요? 

/flag 엔드포인트에 페이로드를 제출하여 admin의 돈을 몰래 가져오십쇼!

## 로컬 환경 실행 방법
아래의 도커(Docker) 명령어를 순서대로 입력하여 로컬 환경에서 문제를 실행할 수 있습니다.
```
docker build -t csrf-challenge .
docker run -d -p 8000:8000 csrf-challenge
```
## 디렉터리 구성
```
CSRF/
├── Dockerfile          # Python 3.11 + Chromium + ChromeDriver 환경 구성
├── app.py              # Flask 애플리케이션 (CSRF 취약점 포함)
├── flag.txt            # 플래그 파일
├── requirements.txt    # Python 의존성 (flask, selenium)
├── static/             # 정적 리소스 (CSS 등)
└── templates/          # HTML 템플릿
    ├── base.html
    ├── index.html
    ├── login.html
    ├── earn.html       # 수학 문제를 풀어 코인을 얻는 페이지
    ├── shop.html       # 코인으로 Flag를 구매하는 페이지
    ├── transfer.html   # 코인 송금 페이지 (CSRF 토큰 보호)
    ├── flag.html       # admin 봇에게 URL 전달
    └── rank.html       # 사용자 코인 랭킹
```
## 사용 기술
* Backend: Python 3.11, Flask
* Admin Bot: Selenium + Chromium (Headless)
* Container: Docker (python:3.11-slim 기반)
