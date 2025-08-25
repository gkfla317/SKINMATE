# SKINMATE Google Cloud 수동 배포 가이드

## 1단계: Google Cloud 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성: `skinmate-project`
3. 프로젝트 ID 확인 (예: `skinmate-project-123456`)

## 2단계: Google Cloud SDK 설치

### Windows에서 설치:
1. [Google Cloud SDK 다운로드](https://cloud.google.com/sdk/docs/install)
2. 설치 파일 실행
3. PowerShell 재시작

### 설치 확인:
```bash
gcloud --version
```

## 3단계: 인증 및 프로젝트 설정

```bash
# 로그인
gcloud auth login

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# API 활성화
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
```

## 4단계: Cloud Storage 버킷 생성

```bash
# 버킷 생성
gcloud storage buckets create gs://skinmate-uploads-YOUR_PROJECT_ID \
    --location=asia-northeast1 \
    --uniform-bucket-level-access

# 권한 설정
gcloud storage buckets add-iam-policy-binding gs://skinmate-uploads-YOUR_PROJECT_ID \
    --member="allUsers" \
    --role="storage.objectViewer"
```

## 5단계: Cloud Run 배포

```bash
# 배포 실행
gcloud run deploy skinmate \
    --source . \
    --platform managed \
    --region asia-northeast1 \
    --allow-unauthenticated \
    --set-env-vars BUCKET_NAME=skinmate-uploads-YOUR_PROJECT_ID \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10
```

## 6단계: 배포 확인

```bash
# 서비스 URL 확인
gcloud run services describe skinmate --region=asia-northeast1 --format="value(status.url)"

# 로그 확인
gcloud run services logs tail skinmate --region=asia-northeast1
```

## 7단계: 데이터베이스 초기화 (선택사항)

```bash
# 데이터베이스 초기화
gcloud run jobs create init-db \
    --image gcr.io/YOUR_PROJECT_ID/skinmate \
    --command="flask" \
    --args="init-db" \
    --region asia-northeast1
```

## 주의사항

- `YOUR_PROJECT_ID`를 실제 프로젝트 ID로 변경
- 비용이 발생할 수 있음 (사용량 기반)
- 메모리 사용량 모니터링 필요
