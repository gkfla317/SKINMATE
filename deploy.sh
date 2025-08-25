#!/bin/bash

# Google Cloud Run 배포 스크립트

# 환경 변수 설정
PROJECT_ID="your-project-id"  # 실제 프로젝트 ID로 변경
SERVICE_NAME="skinmate"
REGION="asia-northeast1"
BUCKET_NAME="skinmate-uploads-${PROJECT_ID}"

echo "🚀 SKINMATE Google Cloud Run 배포 시작..."

# 1. 프로젝트 설정
echo "📋 프로젝트 설정 중..."
gcloud config set project $PROJECT_ID

# 2. 필요한 API 활성화
echo "🔧 API 활성화 중..."
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com

# 3. Cloud Storage 버킷 생성
echo "📦 Cloud Storage 버킷 생성 중..."
gcloud storage buckets create gs://$BUCKET_NAME \
    --location=$REGION \
    --uniform-bucket-level-access || echo "버킷이 이미 존재합니다."

# 4. 버킷 권한 설정
echo "🔐 버킷 권한 설정 중..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member="allUsers" \
    --role="storage.objectViewer"

# 5. Cloud Run 배포
echo "🚀 Cloud Run 배포 중..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars BUCKET_NAME=$BUCKET_NAME \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10

# 6. 배포 완료 확인
echo "✅ 배포 완료!"
echo "🌐 서비스 URL:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"

echo ""
echo "📝 다음 단계:"
echo "1. 서비스 URL로 접속하여 테스트"
echo "2. 데이터베이스 초기화 (필요시)"
echo "3. 크롤링 데이터 수집 (필요시)"
