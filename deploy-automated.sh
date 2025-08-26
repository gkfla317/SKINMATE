#!/bin/bash

# SKINMATE 구글 클라우드 자동 배포 스크립트
# 사용법: ./deploy-automated.sh

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 SKINMATE 구글 클라우드 배포 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 프로젝트 ID 확인
log_info "프로젝트 ID 확인 중..."
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    log_error "프로젝트 ID가 설정되지 않았습니다."
    log_info "다음 명령어로 프로젝트를 설정하세요:"
    log_info "gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi
log_success "프로젝트 ID: $PROJECT_ID"

# 2. 환경 변수 설정
log_info "환경 변수 설정 중..."
export REGION=asia-northeast3
export BUCKET_NAME=skinmate-uploads-$PROJECT_ID
export REPOSITORY=skinmate-repo
export SERVICE_NAME=skinmate

log_success "리전: $REGION"
log_success "버킷 이름: $BUCKET_NAME"
log_success "저장소 이름: $REPOSITORY"

# 3. 필요한 API 활성화
log_info "필요한 API 활성화 중..."
apis=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "storage.googleapis.com"
)

for api in "${apis[@]}"; do
    log_info "API 활성화: $api"
    gcloud services enable $api --quiet
done
log_success "모든 API가 활성화되었습니다."

# 4. Cloud Storage 버킷 생성
log_info "Cloud Storage 버킷 생성 중..."
if gsutil ls -b gs://$BUCKET_NAME >/dev/null 2>&1; then
    log_warning "버킷 $BUCKET_NAME이 이미 존재합니다."
else
    gsutil mb -l $REGION gs://$BUCKET_NAME
    log_success "버킷 $BUCKET_NAME이 생성되었습니다."
fi

# 버킷 권한 설정
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
log_success "버킷 권한이 설정되었습니다."

# 5. Artifact Registry 저장소 생성
log_info "Artifact Registry 저장소 생성 중..."
if gcloud artifacts repositories describe $REPOSITORY --location=$REGION >/dev/null 2>&1; then
    log_warning "저장소 $REPOSITORY가 이미 존재합니다."
else
    gcloud artifacts repositories create $REPOSITORY \
        --repository-format=docker \
        --location=$REGION \
        --description="SKINMATE Docker images" \
        --quiet
    log_success "저장소 $REPOSITORY가 생성되었습니다."
fi

# 6. Docker 인증 설정
log_info "Docker 인증 설정 중..."
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet
log_success "Docker 인증이 설정되었습니다."

# 7. 이미지 태그 설정
IMAGE_NAME=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME:latest
log_info "이미지 태그: $IMAGE_NAME"

# 8. Docker 이미지 빌드 및 푸시
log_info "Docker 이미지 빌드 및 푸시 중..."
log_info "이 과정은 몇 분 정도 소요될 수 있습니다..."

if gcloud builds submit --tag $IMAGE_NAME . --quiet; then
    log_success "Docker 이미지가 성공적으로 빌드되고 푸시되었습니다."
else
    log_error "Docker 이미지 빌드에 실패했습니다."
    log_info "빌드 로그를 확인하세요: gcloud builds log [BUILD_ID]"
    exit 1
fi

# 9. Cloud Run 서비스 배포
log_info "Cloud Run 서비스 배포 중..."
if gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --timeout 300 \
    --max-instances 5 \
    --set-env-vars BUCKET_NAME=$BUCKET_NAME \
    --quiet; then
    log_success "Cloud Run 서비스가 성공적으로 배포되었습니다."
else
    log_error "Cloud Run 서비스 배포에 실패했습니다."
    exit 1
fi

# 10. 서비스 URL 확인
log_info "서비스 URL 확인 중..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
log_success "서비스 URL: $SERVICE_URL"

# 11. 배포 완료 메시지
echo ""
echo "🎉 배포가 완료되었습니다!"
echo ""
echo "📋 배포 정보:"
echo "   프로젝트 ID: $PROJECT_ID"
echo "   리전: $REGION"
echo "   서비스 이름: $SERVICE_NAME"
echo "   서비스 URL: $SERVICE_URL"
echo "   Cloud Storage 버킷: gs://$BUCKET_NAME"
echo "   Artifact Registry: $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY"
echo ""
echo "🔗 다음 명령어로 서비스 상태를 확인할 수 있습니다:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION"
echo ""
echo "📊 다음 명령어로 서비스 로그를 확인할 수 있습니다:"
echo "   gcloud logs read --service=$SERVICE_NAME --limit=50"
echo ""
echo "🌐 브라우저에서 다음 URL로 접속하세요:"
echo "   $SERVICE_URL"
echo ""

# 12. 선택적 데이터베이스 설정 안내
echo "💡 데이터베이스 설정 (선택사항):"
echo "   PostgreSQL을 사용하려면 다음 명령어를 실행하세요:"
echo "   gcloud sql instances create skinmate-db --database-version=POSTGRES_14 --tier=db-f1-micro --region=$REGION"
echo ""

log_success "배포 스크립트가 완료되었습니다!"

