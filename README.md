# CAUtion CTF A Team

CAUtion CTF A팀에서 제작한 웹 보안 CTF 문제 모음입니다. 각 문제 디렉토리는 서버 구축용 `deploy/`, 참가자 배포용 원본 `CTFd/`, CTFd 첨부용 `CTFd_*.zip`으로 분리되어 있습니다.

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
│   ├── CTFd/
│   └── CTFd_SQL_Injection.zip
├── CSRF/
│   ├── deploy/
│   ├── CTFd/
│   └── CTFd_CSRF.zip
├── Command_Injection/
│   ├── deploy/
│   ├── CTFd/
│   └── CTFd_Command_Injection.zip
├── File_Upload/
│   ├── deploy/
│   ├── CTFd/
│   └── CTFd_File_Upload.zip
├── XSS/
│   ├── deploy/
│   ├── CTFd/
│   └── CTFd_XSS.zip
└── README.md
```

각 문제의 `deploy/`는 서버 구축용입니다. 실제 플래그는 `deploy/flag.txt`와 `.env.ctf`에만 둡니다.

```text
app.py
Dockerfile
requirements.txt
flag.txt
templates/
static/
```

각 문제의 `CTFd/`는 참가자 배포용 원본입니다. 이 폴더에는 `flag.txt`와 `WRITEUP.md`를 넣지 않습니다. CTFd에 첨부하는 `CTFd_*.zip`은 이 `CTFd/` 폴더를 압축한 파일입니다.

CTFd 배포용 폴더와 zip을 다시 만들려면 아래 명령어를 실행합니다.

```bash
./scripts/rebuild_ctfd_packages.sh
```

## 운영 참고

- 서버에는 각 문제의 `deploy/` 내용을 업로드하고, CTFd에는 문제 폴더 루트의 `CTFd_*.zip`만 첨부하세요.
- `deploy/`에는 실제 플래그가 들어갈 수 있지만, `CTFd/`와 `CTFd_*.zip`에는 실제 플래그가 없어야 합니다.
- 문제별 `README.md` 또는 `WRITEUP.md`가 있는 경우 세부 설명을 함께 확인하세요.
- 참가자에게 배포할 때는 실제 플래그가 소스에 직접 노출되지 않도록 확인하세요.
- 로컬 테스트용 플래그와 운영용 플래그는 분리해서 관리하는 것을 권장합니다.
- 여러 문제를 동시에 실행할 때는 호스트 포트 충돌에 주의하세요.
## 무료 로컬 호스팅과 외부 공개 링크

맥미니에서 문제 서버를 직접 띄우고, 포트포워딩 없이 무료 임시 링크를 배포하려면 아래 방식을 사용합니다.

```bash
./scripts/start_free_tunnels.sh
```

이 스크립트는 5개 문제 서버를 로컬에서 실행하고, 문제별 Cloudflare 무료 임시 터널 주소를 출력합니다.

로컬 확인 주소:

- Command Injection: `http://127.0.0.1:8001`
- SQL Injection: `http://127.0.0.1:8002`
- CSRF: `http://127.0.0.1:8003`
- XSS: `http://127.0.0.1:8004`
- File Upload: `http://127.0.0.1:8005`

실제 대회 플래그는 `.env.ctf`에만 넣고 깃에 올리지 않습니다. 처음 실행하면 `.env.ctf.example`을 복사해 `.env.ctf`를 자동 생성합니다. `.env.ctf`에서 `COMMAND_FLAG`, `SQL_FLAG`, `CSRF_FLAG`, `XSS_FLAG`, `FILE_UPLOAD_FLAG`를 실제 값으로 바꾼 뒤 실행하세요.

종료:

```bash
./scripts/stop_free_tunnels.sh
```

현재 실행 중인 외부 링크만 다시 확인:

```bash
./scripts/show_tunnel_links.sh
```

서버 상태를 한 번 확인:

```bash
./scripts/check_server_status.sh
```

서버 상태를 계속 감시하면서 맥이 절전모드에 들어가지 않게 유지:

```bash
./scripts/monitor_server_status.sh
```

기본 확인 주기는 1분입니다. 매개변수는 초 단위입니다. 예를 들어 30초마다 확인하려면 아래처럼 실행합니다. 이 기능은 화면 잠자기는 막지 않으므로 화면은 꺼질 수 있지만, 모니터링이 켜져 있는 동안 서버는 계속 동작하도록 유지합니다.

```bash
./scripts/monitor_server_status.sh --interval 30
```

현재 실행 중인 외부 링크를 CTFd의 B조 문제 Message에 자동 반영:

```bash
./scripts/update_ctfd_challenge_links.sh
```

이 스크립트는 CTFd의 B조 5문제를 찾아 각 문제 Message를 아래 형식으로 바꿉니다.

```text
B조 XSS 문제입니다.
아래 링크로 접속해주세요.
https://...trycloudflare.com
```

CTFd 접속 정보는 실행할 때 입력하거나, 추적되지 않는 로컬 파일인 `.env.ctfd.local`에 넣을 수 있습니다.

```bash
cp .env.ctfd.local.example .env.ctfd.local
```

서버 실행, 상태 확인, CTFd Message 업데이트를 한 번에 실행:

```bash
./scripts/run_ctf_pipeline.sh
```

Cloudflare `trycloudflare.com` 임시 터널은 무료이며 계정 없이 쓸 수 있지만, 재시작할 때마다 URL이 바뀔 수 있습니다.
