# SKINMATE 구글 클라우드 배포 가이드 (단계별)

## 사전 준비사항
1. 구글 클라우드 계정 필요
2. 구글 클라우드 프로젝트 생성 필요
3. 결제 계정 연결 필요

## 1단계: 구글 클라우드 프로젝트 설정

### 1-1. 프로젝트 생성 (웹 콘솔에서)
1. https://console.cloud.google.com 접속
2. 상단 프로젝트 선택 → "새 프로젝트"
3. 프로젝트 이름: `skinmate-project` (또는 원하는 이름)
4. "만들기" 클릭

### 1-2. 결제 계정 연결
1. 왼쪽 메뉴 → "결제"
2. "결제 계정 연결" 클릭
3. 기존 계정 선택 또는 새 계정 생성

## 2단계: 구글 클라우드 셸 접속

### 2-1. Cloud Shell 열기
1. 구글 클라우드 콘솔 상단 → "Cloud Shell" 아이콘 클릭
2. 터미널이 열릴 때까지 대기 (약 1-2분)

### 2-2. 프로젝트 확인
```bash
# 현재 프로젝트 확인
gcloud config get-value project

# 프로젝트가 다르다면 설정
gcloud config set project [YOUR_PROJECT_ID]
```

## 3단계: 필요한 API 활성화

```bash
# Cloud Run API 활성화
gcloud services enable run.googleapis.com

# Cloud Build API 활성화
gcloud services enable cloudbuild.googleapis.com

# Artifact Registry API 활성화
gcloud services enable artifactregistry.googleapis.com

# Cloud Storage API 활성화
gcloud services enable storage.googleapis.com
```

## 4단계: GitHub 저장소 클론

```bash
# 홈 디렉토리로 이동
cd ~

# GitHub 저장소 클론 (Personal Access Token 사용)
git clone https://github.com/jera0520/SKINMATE.git

# 프로젝트 디렉토리로 이동
cd SKINMATE

# 파일 목록 확인
ls -la
```

## 5단계: 환경 변수 설정

```bash
# 프로젝트 ID 설정
export PROJECT_ID=$(gcloud config get-value project)

# 리전 설정 (한국 리전 권장)
export REGION=asia-northeast3

# Cloud Storage 버킷 이름 설정
export BUCKET_NAME=skinmate-uploads-$PROJECT_ID

# Artifact Registry 저장소 이름
export REPOSITORY=skinmate-repo
```

## 6단계: Cloud Storage 버킷 생성

```bash
# 버킷 생성
gsutil mb -l $REGION gs://$BUCKET_NAME

# 버킷을 공개로 설정 (이미지 접근용)
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
```

## 7단계: Artifact Registry 저장소 생성

```bash
# Docker 저장소 생성
gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --description="SKINMATE Docker images"
```

## 8단계: Docker 이미지 빌드 및 푸시

```bash
# Docker 인증 설정
gcloud auth configure-docker $REGION-docker.pkg.dev

# 이미지 태그 설정
export IMAGE_NAME=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/skinmate:latest

# 이미지 빌드 및 푸시
gcloud builds submit --tag $IMAGE_NAME .
```

## 9단계: Cloud Run 서비스 배포

```bash
# Cloud Run 서비스 배포
gcloud run deploy skinmate \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --timeout 300 \
    --max-instances 5 \
    --set-env-vars BUCKET_NAME=$BUCKET_NAME
```

## 10단계: 데이터베이스 설정 (선택사항)

### 10-1. Cloud SQL 인스턴스 생성 (PostgreSQL)
```bash
# PostgreSQL 인스턴스 생성
gcloud sql instances create skinmate-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --backup-start-time=02:00 \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=03

# 데이터베이스 생성
gcloud sql databases create skinmate --instance=skinmate-db

# 사용자 생성
gcloud sql users create skinmate-user \
    --instance=skinmate-db \
    --password=your-secure-password

# 공개 IP 활성화
gcloud sql instances patch skinmate-db \
    --authorized-networks=0.0.0.0/0
```

### 10-2. 환경 변수 설정 (Cloud SQL 사용 시)
```bash
# Cloud Run 서비스 업데이트 (환경 변수 추가)
gcloud run services update skinmate \
    --region $REGION \
    --set-env-vars \
    DB_USER=skinmate-user,\
    DB_PASS=your-secure-password,\
    DB_NAME=skinmate,\
    DB_HOST=[INSTANCE_IP]
```

## 11단계: 배포 확인

```bash
# 서비스 URL 확인
gcloud run services describe skinmate --region=$REGION --format="value(status.url)"

# 서비스 로그 확인
gcloud logs read --service=skinmate --limit=50
```

## 12단계: 도메인 설정 (선택사항)

```bash
# 커스텀 도메인 매핑
gcloud run domain-mappings create \
    --service skinmate \
    --domain your-domain.com \
    --region $REGION
```

## 문제 해결

### 빌드 실패 시
```bash
# 빌드 로그 확인
gcloud builds log [BUILD_ID]

# 로컬에서 테스트
docker build -t skinmate .
docker run -p 8080:8080 skinmate
```

### 서비스 오류 시
```bash
# 서비스 로그 확인
gcloud logs read --service=skinmate --limit=100

# 서비스 상태 확인
gcloud run services describe skinmate --region=$REGION
```

## 비용 최적화

1. **Cloud Run**: 요청이 있을 때만 실행 (무료 티어: 월 200만 요청)
2. **Cloud Storage**: 사용한 만큼만 과금
3. **Cloud SQL**: f1-micro 인스턴스 사용 (월 약 $7)
4. **Artifact Registry**: 저장소당 월 $0.026/GB

## 보안 고려사항

1. 환경 변수에 민감한 정보 저장
2. IAM 권한 최소화
3. 네트워크 보안 규칙 설정
4. 정기적인 보안 업데이트

