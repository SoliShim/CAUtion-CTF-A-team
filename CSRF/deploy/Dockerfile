FROM python:3.11-slim

# 컨테이너에서 사용할 환경변수 설정
ENV user=csrf
ENV port=8000
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Selenium admin bot 실행에 필요한 Chromium 브라우저와 ChromeDriver 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# 보안을 위해 root가 아닌 일반 사용자 생성
RUN adduser --disabled-password --gecos "" $user

# 컨테이너 내부 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉터리의 소스코드를 컨테이너의 /app 디렉터리로 복사
COPY . /app

# 필요한 파이썬 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드와 플래그 파일 권한 설정
RUN chown -R $user:$user /app \
    && chown root:$user /app/flag.txt \
    && chmod 440 /app/flag.txt

# 이후 명령을 일반 사용자 권한으로 실행
USER $user

# 컨테이너에서 사용할 포트 명시
EXPOSE $port

# Flask 애플리케이션 실행
ENTRYPOINT ["python3"]
CMD ["app.py"]