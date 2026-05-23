# CSRF Challenge
CSRF(Cross-Site Request Forgery)에 관련된 CTF 문제입니다.

돈을 모으고 거래할 수 있는 가상의 은행 서비스가 있습니다.  
상점에서 플래그를 구매할 수 있으며, 이를 위해선 2,147,483,647 원이 필요합니다.  
수학 문제를 풀면 돈을 벌 수 있습니다. 그러나 한 문제당 1 원밖에 못 법니다.  
랭킹에는 보유 자산 순으로 사용자가 나열되어 있습니다. admin의 돈을 뺏고 싶지 않으신가요? 

/flag 엔드포인트에 페이로드를 제출하여 admin의 돈을 몰래 가져오십쇼!

플래그 형식: `FLAG{...}`

## 로컬 환경 실행 방법
아래의 도커(Docker) 명령어를 순서대로 입력하여 로컬 환경에서 문제를 실행할 수 있습니다.
```
docker build -t csrf-challenge .
docker run -d -p 8000:8000 csrf-challenge
```

## 참가자에게 제공할 파일

아래 파일/디렉터리를 참가자에게 공개합니다.

```
CSRF/
├── Dockerfile
├── app.py
├── requirements.txt
├── flag.txt          ← 진짜 플래그 대신 FLAG{dummy_flag_for_local_test} 로 교체 후 제공
├── static/
└── templates/
```

실제 플래그는 운영 서버의 `flag.txt`에만 존재합니다.

## 사용 기술
* Backend: Python 3.11, Flask
* Admin Bot: Selenium + Chromium (Headless)
* Container: Docker (python:3.11-slim 기반)
