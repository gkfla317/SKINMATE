### **Google Cloud 기반 프로젝트 배포 및 관리 전략**

**목표:** 현재 로컬에서 실행되는 웹사이트와 백엔드 파이프라인을 Google Cloud의 관리형 서비스로 전환하여 안정성, 확장성, 유지보수 용이성을 확보합니다.

**핵심 Google Cloud 서비스:**

*   **Cloud Run:** 웹 애플리케이션 및 주기적인 백엔드 작업(크롤러) 실행
*   **Cloud SQL:** 관리형 관계형 데이터베이스 (SQLite 대체)
*   **Cloud Storage:** 이미지 및 머신러닝 모델 파일 저장
*   **Cloud Scheduler:** 주기적인 크롤링 작업 트리거
*   **Cloud Logging & Monitoring:** 애플리케이션 로그 및 성능 모니터링

---

**단계별 실행 가이드:**

#### **1단계: 핵심 웹 애플리케이션 및 크롤러 배포 (Cloud Run)**

고객님의 프로젝트는 이미 `Dockerfile`과 `deploy.yml` (GitHub Actions)을 가지고 있어 Cloud Run 배포 준비가 잘 되어 있습니다.

1.  **`Dockerfile` 확인:** `Dockerfile`이 `app.py` (또는 웹 서비스를 시작하는 실제 파일)를 실행하도록 `CMD` 또는 `ENTRYPOINT`가 올바르게 설정되어 있는지 다시 한번 확인합니다. `main.py`는 주기적인 작업으로 분리할 예정이므로, `Dockerfile`은 웹 서비스에 집중하는 것이 좋습니다.
    *   **진행 상황:** `Dockerfile` 검토 완료. `app.py`를 웹 서비스 진입점으로 사용하는 것이 확인되었습니다.
2.  **GitHub Actions (deploy.yml) 활용:**
    *   `deploy.yml`은 이미 Cloud Run 배포를 자동화하고 있습니다. `main` 브랜치에 코드를 푸시하면 자동으로 이미지를 빌드하고 Cloud Run에 배포됩니다.
    *   **주의:** 현재 `deploy.yml`은 `BUCKET_NAME` 환경 변수를 설정하고 있습니다. 이는 Cloud Storage와의 연동을 의미합니다.
    *   **다음 작업:** 프로젝트의 모든 변경사항을 GitHub 저장소의 `main` 브랜치에 커밋하고 푸시하여 Cloud Run 배포를 시작하십시오.
    *   **진행 상황:** 1단계 설명 완료. 고객님의 푸시를 기다리고 있습니다.

#### **2단계: 데이터베이스 마이그레이션 (SQLite → Cloud SQL)**

현재 `database.py`는 로컬 SQLite를 사용하고 있습니다. Cloud Run은 서버리스 환경이므로 인스턴스가 재시작되거나 스케일 아웃될 때 로컬 파일 시스템의 데이터는 유실됩니다. 따라서 관리형 데이터베이스로 전환해야 합니다.

1.  **Cloud SQL 인스턴스 생성:**
    *   Google Cloud Console에서 **Cloud SQL** 서비스로 이동하여 새 인스턴스를 생성합니다. (예: PostgreSQL 또는 MySQL)
    *   데이터베이스 이름, 사용자, 비밀번호를 설정합니다.
    *   **진행 상황:** `skinmate-db-instance` 인스턴스 생성 완료 확인.
2.  **`database.py` 수정:**
    *   `database.py` 파일을 수정하여 SQLite 대신 Cloud SQL에 연결하도록 변경합니다.
    *   **예시 (PostgreSQL로 변경 시):**
        *   `sqlite3` 대신 `psycopg2` (또는 `SQLAlchemy`와 같은 ORM) 라이브러리를 사용하도록 변경합니다.
        *   `get_connection` 메서드에서 Cloud SQL 연결 문자열을 사용하도록 수정합니다. 연결 정보(호스트, 포트, 사용자, 비밀번호, DB 이름)는 환경 변수로 관리하는 것이 좋습니다.
        *   `init_database`의 `CREATE TABLE` 문을 Cloud SQL의 SQL 문법에 맞게 조정합니다.
    *   **진행 상황:** `database.py` 수정 방법에 대한 상세 설명 완료. (제가 직접 코드 수정 완료)
3.  **데이터 마이그레이션 (선택 사항):** 기존 SQLite 데이터가 있다면, `sqlite3`에서 데이터를 덤프하여 Cloud SQL로 임포트하는 과정을 거쳐야 합니다.
4.  **Cloud Run 환경 변수 설정:** `deploy.yml` 또는 Cloud Run 서비스 설정에서 Cloud SQL 연결에 필요한 환경 변수(예: `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`)를 추가합니다.
    *   **진행 상황:** Cloud Run 환경 변수 설정 방법에 대한 상세 설명 완료. `deploy.yml` 리전 변경(`asia-northeast1` -> `asia-northeast3`) 완료.
    *   **다음 작업:** Cloud Console에서 `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` 환경 변수를 설정하십시오.

#### **3단계: 주기적인 크롤링 작업 스케줄링 (Cloud Scheduler)**

`main.py`는 주기적으로 실행되어야 하는 크롤링 파이프라인을 오케스트레이션합니다. 이를 위해 Cloud Scheduler를 사용합니다.

1.  **Cloud Run 서비스 분리 (권장):** 웹 애플리케이션과 크롤링 작업이 동일한 컨테이너에 있다면, 크롤링 작업을 위한 별도의 Cloud Run 서비스를 만드는 것을 고려할 수 있습니다.
    *   **옵션 A (동일 서비스 내):** 웹 서비스가 특정 HTTP 엔드포인트(예: `/run-crawl`)를 노출하고, 이 엔드포인트가 호출되면 크롤링이 시작되도록 `app.py`를 수정합니다.
    *   **옵션 B (별도 서비스 - 선택됨):** `main.py`만 실행하는 경량의 Docker 이미지를 만들고, 이를 위한 별도의 Cloud Run 서비스를 배포합니다. 이 서비스는 HTTP 요청을 받으면 `main.py`를 실행하도록 설정합니다.
    *   **진행 상황:** 옵션 B 선택 완료. `Dockerfile.crawler` 파일 생성 완료. `.github/workflows/deploy-crawler.yml` 파일 생성 완료.
2.  **Cloud Scheduler 작업 생성:**
    *   Google Cloud Console에서 **Cloud Scheduler** 서비스로 이동하여 새 작업을 생성합니다.
    *   **빈도:** 크롤링을 실행할 주기(예: 매일 자정)를 Cron 형식으로 설정합니다.
    *   **대상:** Cloud Run 서비스를 선택하고, 해당 서비스의 URL과 HTTP 메서드(GET/POST)를 지정합니다. (옵션 A의 경우 `/run-crawl` 엔드포인트 URL, 옵션 B의 경우 해당 서비스의 기본 URL)
    *   **인증:** Cloud Run 서비스가 비공개인 경우, Cloud Scheduler가 Cloud Run을 호출할 수 있도록 서비스 계정 기반의 인증을 설정합니다.

#### **4단계: 머신러닝 모델 및 이미지 저장 (Cloud Storage)**

`image_embedding.py`가 이미지를 처리하고, `.pkl` 모델 파일들이 사용됩니다. 이 파일들을 Cloud Storage에 저장하여 관리합니다.

1.  **Cloud Storage 버킷 활용:**
    *   `deploy.yml`에서 이미 `BUCKET_NAME` 환경 변수를 설정하고 있습니다. 이 버킷을 이미지 저장 및 모델 파일 저장에 활용합니다.
    *   `image_embedding.py`가 이미지를 처리할 때, 로컬 파일 시스템 대신 Cloud Storage에서 이미지를 읽고 쓸 수 있도록 코드를 수정합니다. (예: `google-cloud-storage` 클라이언트 라이브러리 사용)
    *   `app.py` (또는 모델을 로드하는 스크립트)에서 `my_scaler.pkl`, `my_selector.pkl`, `my_xgboost_model.pkl` 파일을 로컬 경로 대신 Cloud Storage에서 로드하도록 수정합니다.
2.  **IAM 권한 설정:** Cloud Run 서비스 계정이 Cloud Storage 버킷에 대한 읽기/쓰기 권한을 가지고 있는지 확인합니다. (예: "Storage Object Viewer" 또는 "Storage Object Admin" 역할)

#### **5단계: 로깅 및 모니터링 (Cloud Logging & Monitoring)**

Google Cloud의 관리형 서비스는 기본적으로 통합된 로깅 및 모니터링 기능을 제공합니다.

1.  **Cloud Logging:** Cloud Run에서 발생하는 모든 로그(표준 출력/오류)는 자동으로 Cloud Logging으로 전송됩니다. 콘솔에서 쉽게 로그를 확인하고 필터링할 수 있습니다.
2.  **Cloud Monitoring:** Cloud Run 서비스의 성능 지표(CPU 사용량, 메모리 사용량, 요청 수 등)를 자동으로 수집합니다. 대시보드를 설정하고 알림 정책을 구성하여 서비스 상태를 모니터링할 수。

---

**고객님께서 수행하실 다음 작업 (요약):**

1.  **GitHub Secrets 추가:**
    *   GitHub 저장소의 **Settings** -> **Secrets and variables** -> **Actions**로 이동합니다.
    *   다음 Secret들을 **정확한 이름으로** 추가합니다.
        *   `DB_HOST`: `34.47.89.66`
        *   `DB_NAME`: `skinmate_db`
        *   `DB_USER`: `postgres`
        *   `DB_PASSWORD`: `skinmate@@`
        *   `DB_PORT`: `5432`
2.  **Cloud Run 환경 변수 설정:**
    *   Cloud Console에서 `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` 환경 변수를 설정합니다.
3.  **코드 푸시:**
    *   `requirements.txt`, `database.py`, `deploy.yml`, `Dockerfile.crawler`, `.github/workflows/deploy-crawler.yml` 파일의 변경사항을 GitHub 저장소의 `main` 브랜치에 커밋하고 푸시합니다.
