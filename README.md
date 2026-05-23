# CAUtion CTF A Team

CAUtion CTF A팀에서 제작한 웹 보안 CTF 문제 모음입니다. 각 문제 디렉토리는 서버 구축용 `deploy/`와 CTFd 첨부용 `CTFd_*.zip`으로 구분되어 있습니다.

플래그 형식은 `FLAG{...}`로 통일합니다.

## 문제 목록

| 디렉토리 | 주제 | 설명 | 기본 포트 |
| --- | --- | --- | --- |
| `SQL_Injection/` | SQL Injection | 로그인 기능의 SQL 쿼리 취약점을 이용해 관리자 계정 인증을 우회하거나 비밀번호를 추론하는 문제 | `80` |
| `CSRF/` | Cross-Site Request Forgery | 관리자 봇이 방문하는 페이지를 이용해 송금 요청을 유도하고 플래그 구매 조건을 만족시키는 문제 | `8000` |
| `Command_Injection/` | Command Injection | 보고서 파일 조회 기능의 쉘 명령 실행 흐름을 분석해 명령 주입을 수행하는 문제 | `80` |
| `File_Upload/` | File Upload | 이미지 업로드 처리와 세션 데이터 반영 로직을 이용해 관리자 권한 및 파일 읽기를 노리는 문제 | `80` |
| `XSS/` | Cross-Site Scripting | 티켓/신고 기능과 관리자 봇을 이용해 민감 정보를 획득하는 XSS 문제 | `80` |

## 실행 방법

각 문제는 해당 디렉토리의 `deploy/`로 이동한 뒤 Docker 이미지를 빌드하고 실행합니다.

```bash
cd SQL_Injection/deploy
docker build -t caution-sqli .
docker run --rm -p 8080:80 caution-sqli
```

실행 후 브라우저에서 `http://127.0.0.1:8080`으로 접속합니다. 다른 문제가 이미 같은 포트를 사용 중이면 호스트 포트만 바꾸면 됩니다.

```bash
docker run --rm -p 8081:80 caution-sqli
```

CSRF 문제는 애플리케이션 내부 포트가 `8000`입니다.

```bash
cd CSRF/deploy
docker build -t caution-csrf .
docker run --rm -p 8000:8000 caution-csrf
```

Command Injection 문제는 실제 플래그를 환경 변수로 주입할 수 있습니다.

```bash
cd Command_Injection/deploy
docker build -t caution-command-injection .
docker run --rm -p 8081:80 -e FLAG='FLAG{real_flag_here}' caution-command-injection
```

## 로컬 실행

Docker 없이 실행하려면 각 문제의 `deploy/` 디렉토리에서 Python 의존성을 설치한 뒤 `app.py`를 실행합니다.

```bash
pip install -r requirements.txt
python app.py
```

Selenium 기반 관리자 봇이 포함된 `CSRF/`, `XSS/` 문제는 Chromium과 ChromeDriver가 필요하므로 Docker 실행을 권장합니다.

## 디렉토리 구조

```text
.
├── SQL_Injection/
│   ├── deploy/
│   └── CTFd_SQL_Injection.zip
├── CSRF/
│   ├── deploy/
│   └── CTFd_CSRF.zip
├── Command_Injection/
│   ├── deploy/
│   └── CTFd_Command_Injection.zip
├── File_Upload/
│   ├── deploy/
│   └── CTFd_File_Upload.zip
├── XSS/
│   ├── deploy/
│   └── CTFd_XSS.zip
└── README.md
```

각 문제의 `deploy/`에는 일반적으로 다음 파일이 포함되어 있습니다.

```text
app.py
Dockerfile
requirements.txt
templates/
static/
```

## 운영 참고

- 서버에 업로드할 파일은 각 문제의 `deploy/`를 사용하세요.
- CTFd에 첨부할 참가자 배포용 파일은 각 문제의 `CTFd_*.zip`을 사용하세요.
- 참가자용 zip에는 실제 플래그가 아닌 더미 값 또는 플레이스홀더만 포함되어 있습니다.
- 문제별 `README.md` 또는 `WRITEUP.md`가 있는 경우 `deploy/` 안에서 세부 설명을 확인하세요.
- 로컬 테스트용 플래그와 운영용 플래그는 분리해서 관리하는 것을 권장합니다.
- 여러 문제를 동시에 실행할 때는 호스트 포트 충돌에 주의하세요.
