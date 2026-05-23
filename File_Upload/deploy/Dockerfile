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

# 업로드 디렉토리 생성
RUN mkdir -p uploads

# 플래그 권한 설정
RUN chmod 644 flag.txt

# 6. Flask가 사용할 포트 번호
EXPOSE 80

# 7. 서버 실행 명령어
CMD ["python", "app.py"]