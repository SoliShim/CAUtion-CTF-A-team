# SQL Injection

로그인 기능을 분석하여 관리자 계정으로 인증하는 SQL Injection 문제입니다.

## 로컬 실행

```bash
docker build -t blind-sqli .
docker run -d -p 80:80 blind-sqli
```

브라우저에서 `http://localhost`로 접속합니다.
