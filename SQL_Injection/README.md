# SQL Injection
이 문제는 **SQL Injection**에 관련된 문제입니다.

관리자 계정으로 로그인에 성공하면 되는 문제입니다.

ID는 amdmin이며 비밀번호가 이 문제의 플래그입니다.

따라서 비밀번호는 DH{..로 시작됩니다.

### 🚀 로컬 환경 실행 방법
아래의 도커(Docker) 명령어를 순서대로 입력하여 로컬 환경에서 문제를 실행할 수 있습니다.

```bash
docker build -t blind-sqli .
docker run -d -p 80:80 blind-sqli
```
