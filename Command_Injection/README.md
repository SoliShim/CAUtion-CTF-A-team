# Command Injection Challenge

Sungmin Shim의 command injection 문제입니다.

## 실행 방법

```bash
docker build -t command-injection-challenge .
docker run --rm -p 8081:80 -e FLAG='DH{real_flag_here}' command-injection-challenge
```

브라우저에서 `http://127.0.0.1:8081`로 접속하면 됩니다.

## 문제 의도

서버 내부 report 파일을 확인하는 기능이 사용자의 입력값을 shell 명령어에 직접 붙여 실행합니다.

공백, `..`, `cat`은 막혀 있지만 shell metacharacter, redirection, 환경 변수 확장을 제대로 막지 못해 command injection이 가능합니다.

명령 실행 결과는 주입 입력에서 바로 보여주지 않으므로, 플래그를 `reports/result.txt`에 저장한 뒤 `result.txt`를 다시 조회해야 합니다.

실제 플래그는 코드에 직접 저장하지 않고 Docker 실행 시 `FLAG` 환경변수로 주입합니다. 환경변수를 주지 않으면 로컬 테스트용 가짜 플래그가 사용됩니다.
