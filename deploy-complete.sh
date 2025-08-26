#!/bin/bash

# 환경 변수 설정
export PROJECT_ID=$(gcloud config get-value project)
export REGION=asia-northeast3
export BUCKET_NAME=skinmate-uploads-$PROJECT_ID
export IMAGE_NAME=asia-northeast3-docker.pkg.dev/$PROJECT_ID/skinmate-repo/skinmate:latest

echo "=== SKINMATE AI 분석 오류 수정 - 재배포 시작 ==="
echo "프로젝트 ID: $PROJECT_ID"
echo "리전: $REGION"
echo "이미지 이름: $IMAGE_NAME"

# 1. Docker 이미지 재빌드 및 푸시
echo "1. Docker 이미지 재빌드 및 푸시 중..."
gcloud builds submit --tag $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "✅ Docker 이미지 빌드 성공"
else
    echo "❌ Docker 이미지 빌드 실패"
    exit 1
fi

# 2. Cloud Run 서비스 업데이트
echo "2. Cloud Run 서비스 업데이트 중..."
gcloud run deploy skinmate \
    --image $IMAGE_NAME \
    --region $REGION \
    --allow-unauthenticated \
    --memory 4Gi \
    --timeout 600 \
    --max-instances 5 \
    --set-env-vars BUCKET_NAME=$BUCKET_NAME

if [ $? -eq 0 ]; then
    echo "✅ Cloud Run 배포 성공"
    echo "서비스 URL: https://skinmate-527625461845.asia-northeast3.run.app/"
else
    echo "❌ Cloud Run 배포 실패"
    exit 1
fi

echo "=== 배포 완료 ==="
echo "이제 AI 분석 기능이 정상 작동할 것입니다."
echo "테스트 URL: https://skinmate-527625461845.asia-northeast3.run.app/analysis"

