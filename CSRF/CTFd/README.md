# CSRF Challenge

가상의 은행 서비스에서 CSRF 취약점을 분석하는 문제입니다.

상점에서 플래그를 구매할 수 있으며, 이를 위해서는 매우 많은 금액이 필요합니다. 게임으로 돈을 벌 수 있지만 한 번에 얻는 금액은 제한적입니다.

## 로컬 실행

```bash
docker build -t csrf-challenge .
docker run --rm -p 8000:8000 csrf-challenge
```

브라우저에서 `http://127.0.0.1:8000`으로 접속합니다.
