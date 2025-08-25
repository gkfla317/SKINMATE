# Google Cloud Run용 Dockerfile
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Google Cloud Storage 클라이언트 설치
RUN pip install google-cloud-storage

# 프로덕션 WSGI 서버 설치
RUN pip install gunicorn

# 애플리케이션 파일 복사
COPY . .

# 포트 설정
EXPOSE 8080

# 환경 변수 설정
ENV PORT=8080
ENV FLASK_ENV=production

# 애플리케이션 실행
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
