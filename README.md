# SKINMATE: AI 피부 분석 및 맞춤 스킨케어 추천 시스템

---

## 📖 프로젝트 소개

**SKINMATE**는 사용자가 업로드한 얼굴 사진을 AI로 분석하여 개인의 피부 타입을 진단하고, 그 결과를 바탕으로 개인 맞춤형 스킨케어 제품 및 아침/저녁 루틴을 추천해주는 웹 애플리케이션입니다.

단순히 인기 제품을 나열하는 것이 아니라, 사용자의 피부 상태, 주요 고민, 그리고 현재 계절까지 고려하여 과학적이고 체계적인 추천을 제공하는 것을 목표로 합니다.

---

## ✨ 주요 기능

- **AI 피부 타입 분석**: Google Cloud Vertex AI를 활용하여 업로드된 이미지로부터 피부 타입(건성, 지성, 복합성 등)을 예측합니다.
- **개인 맞춤 루틴 추천**: 피부 타입, 주요 고민(수분, 탄력, 주름), 계절(여름, 겨울, 환절기)을 종합적으로 고려한 동적 추천 엔진을 통해 아침/저녁 스킨케어 루틴을 제공합니다.
- **상세 분석 리포트**: 종합 점수, 항목별 점수(수분, 탄력, 주름)를 시각적인 차트와 아이콘으로 제공하여 사용자가 자신의 피부 상태를 쉽게 파악할 수 있도록 돕습니다.
- **사용자 인증 및 기록 관리**: 회원가입 및 로그인 기능을 통해 과거의 분석 기록을 관리하고, 시간 경과에 따른 피부 상태 변화를 추적할 수 있습니다.
- **웹 크롤러**: `main.py` 스크립트를 통해 화해(Hwahae) 웹사이트의 제품 데이터를 수집하여 추천에 사용될 데이터베이스를 구축합니다.

---

## 🛠️ 기술 스택

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **AI/ML**: Google Cloud Vertex AI
- **Image Processing**: OpenCV
- **Dependencies**: `requirements.txt` 참고

---

## ⚙️ 설치 및 실행 방법

### 1. 사전 준비

- Python 3.9 이상
- Git

### 2. 설치

```bash
# 1. 프로젝트를 로컬 환경으로 복제합니다.
git clone <repository_url>
cd test-skinmate-api

# 2. 가상 환경을 생성하고 활성화합니다.
python -m venv venv
# Windows
virtualenv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 필요한 라이브러리를 설치합니다.
pip install -r requirements.txt
```

### 3. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, 아래 내용을 자신의 환경에 맞게 채워넣습니다. 이는 Vertex AI API 인증 및 Flask 앱 설정을 위해 필수적입니다.

```env
# .env 파일 예시

# Google Cloud 설정
PROJECT_ID="your-google-cloud-project-id"
ENDPOINT_ID="your-vertex-ai-endpoint-id"
REGION="your-gcp-region"
GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your-service-account-file.json"

# Flask 설정
SECRET_KEY="your-strong-and-secret-key"
```

### 4. 데이터베이스 초기화 및 데이터 수집

애플리케이션을 실행하기 전에, 데이터베이스 테이블을 생성하고 추천에 필요한 제품 데이터를 수집해야 합니다.

```bash
# 1. Flask CLI를 사용하여 데이터베이스 스키마를 생성합니다.
flask init-db

# 2. 데이터 크롤러를 실행하여 제품 데이터를 수집합니다. (시간이 다소 소요될 수 있습니다)
python main.py
```

### 5. 애플리케이션 실행

모든 설정이 완료되면, 아래 명령어로 Flask 개발 서버를 실행합니다.

```bash
python app.py
```

서버가 실행되면 웹 브라우저에서 `http://127.0.0.1:5001` 주소로 접속하여 SKINMATE 서비스를 이용할 수 있습니다.

---

## 📂 프로젝트 구조

```
.test-skinmate-api/
├── instance/             # SQLite DB 파일 등 인스턴스 데이터
├── static/               # CSS, JavaScript, 이미지 등 정적 파일
│   ├── css/
│   └── images/
├── templates/            # HTML 템플릿 파일
├── uploads/              # 사용자가 업로드한 이미지
├── .env                  # 환경 변수 설정 파일
├── app.py                # 메인 Flask 애플리케이션
├── main.py               # 데이터 수집 파이프라인 실행 스크립트
├── crawler.py            # 화해 웹 크롤러
├── database.py           # 데이터베이스 핸들러
├── routine_rules.py      # 스킨케어 루틴 추천 규칙
├── schema.sql            # 데이터베이스 테이블 스키마
├── requirements.txt      # Python 종속성 목록
└── README.md             # 프로젝트 설명 파일
```