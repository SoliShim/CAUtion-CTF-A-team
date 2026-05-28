# 1. 파이썬 실행 버전 설정
FROM python:3.11-slim

# 2. 컨테이너 내부 작업 디렉토리 설정
WORKDIR /app

# 3. 라이브러리 목록 파일을 먼저 복사
COPY requirements.txt .

# 4. 필요한 파이썬 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 나머지 모든 문제 파일(app.py, templates 등) 복사
COPY . .

RUN adduser --disabled-password --gecos "" command \
    && mkdir -p reports \
    && chown -R root:root /app \
    && chown -R command:command /app/reports \
    && chmod 755 /app \
    && chmod 644 /app/flag.txt

# 6. Flask가 사용할 포트 번호 (기본 80번)
EXPOSE 80

# 7. 서버 실행 명령어
CMD ["python", "app.py"]
