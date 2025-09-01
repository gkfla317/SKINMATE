# 1. 베이스 이미지 선택 (Python 3.10 사용)
FROM python:3.10-slim

# 2. 환경 변수 설정
# 파이썬이 .pyc 파일을 만들지 않도록 하고, 출력을 바로 터미널에 표시
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 설치
# requirements.txt 파일을 먼저 복사하여 설치합니다.
# 이 파일을 먼저 복사하면, 코드 변경 시 매번 라이브러리를 새로 설치하지 않아 효율적입니다.
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5. 애플리케이션 소스 코드 복사
COPY . .

# Cloud Run은 PORT 환경변수를 줌
ENV PORT=8080

# 6. 애플리케이션 실행
# Cloud Run이 외부 요청을 받을 수 있도록 8080 포트를 사용합니다.
# gunicorn을 사용해 app.py 파일 안에 있는 'app' 객체를 실행합니다.
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "app:app"]