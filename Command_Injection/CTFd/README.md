# Command Injection Challenge

서버 내부 report 파일을 확인하는 관리자 도구를 분석하는 문제입니다.

## 로컬 실행

```bash
docker build -t command-injection-challenge .
docker run --rm -p 8081:80 command-injection-challenge
```

브라우저에서 `http://127.0.0.1:8081`로 접속합니다.
