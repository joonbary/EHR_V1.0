# 🏗️ EHR Project 전체 구조 문서

## 📋 프로젝트 개요
- **프로젝트명**: EHR (Employee Human Resource) Evaluation System
- **통합 시스템**: Elevate Growth System + AIRISS AI Integration
- **기술 스택**: Django 5.2, React 18, PostgreSQL/SQLite, OpenAI API, WebSocket

## 🗂️ 디렉토리 구조

### 📁 루트 디렉토리
```
D:\EHR_project\
├── 📄 설정 파일들
│   ├── manage.py                    # Django 관리 스크립트
│   ├── requirements.txt              # Python 패키지 의존성
│   ├── railway.json                  # Railway 배포 설정
│   ├── Procfile                      # Heroku 배포 설정
│   ├── runtime.txt                   # Python 버전 지정
│   └── .env                          # 환경 변수 (미포함)
│
├── 📄 문서 파일들
│   ├── README.md                     # 프로젝트 소개
│   ├── CLAUDE.md                     # Claude AI 컨텍스트 문서
│   ├── INSTALLATION_GUIDE.md         # 설치 가이드
│   ├── IMPLEMENTATION_SUMMARY.md     # 구현 요약
│   └── EVALUATION_IMPLEMENTATION_GUIDE.md  # 평가 시스템 구현 가이드
│
└── 📄 실행 스크립트
    ├── run_server.bat               # 백엔드 서버 실행 (Windows)
    ├── run_frontend.bat             # 프론트엔드 실행 (Windows)
    └── setup_initial_data.py        # 초기 데이터 설정
```

### 🎯 핵심 Django 앱

#### 1️⃣ ehr_evaluation/ (Django 설정)
```
ehr_evaluation/
├── __init__.py
├── settings.py          # Django 설정
├── urls.py             # 루트 URL 설정
├── wsgi.py             # WSGI 설정
└── asgi.py             # ASGI 설정 (WebSocket)
```

#### 2️⃣ users/ (사용자 관리)
```
users/
├── models.py           # User 모델 (역할 기반 접근 제어)
├── serializers.py      # DRF 시리얼라이저
├── views.py           # 인증/인가 뷰
├── urls.py            # 사용자 관련 URL
└── admin.py           # Django Admin 설정
```

#### 3️⃣ evaluations/ (평가 시스템 - 핵심)
```
evaluations/
├── models.py           # Evaluation, Task, Score, Feedback, Goal 모델
├── views.py           # 평가 관련 뷰
├── ai_service.py      # OpenAI 통합 서비스
├── analytics.py       # 분석 기능
├── serializers.py     # API 시리얼라이저
├── templates/evaluations/
│   ├── contribution_evaluation.html  # 기여도 평가 페이지
│   ├── dashboard.html                # 평가 대시보드
│   └── my_evaluations_dashboard.html # 개인 평가 대시보드
└── urls.py            # 평가 관련 URL
```

#### 4️⃣ employees/ (직원 관리)
```
employees/
├── models.py           # Employee 모델
├── models_hr.py        # HR 관련 모델
├── models_workforce.py # 인력 관리 모델
├── views.py           # 직원 관리 뷰
├── api_views.py       # API 엔드포인트
├── services/
│   └── excel_parser.py # Excel 파일 처리
├── templates/employees/
│   ├── employee_list.html          # 직원 목록
│   └── employee_management.html    # 직원 관리 페이지
└── management/commands/
    └── load_initial_data.py        # 초기 데이터 로드
```

#### 5️⃣ notifications/ (알림 시스템)
```
notifications/
├── models.py          # Notification 모델
├── services.py        # 알림 서비스
├── serializers.py     # API 시리얼라이저
├── views.py          # 알림 뷰
└── urls.py           # 알림 URL
```

### 🤖 AI 통합 모듈

#### 1️⃣ airiss/ (AIRISS AI 통합 시스템)
```
airiss/
├── models.py          # AIRISS 데이터 모델
├── ai_chatbot.py      # AI 챗봇 기능
├── ai_models.py       # AI 모델 통합
├── services.py        # AIRISS 서비스
├── excel_parser.py    # Excel 데이터 파싱
├── templates/airiss/
│   ├── dashboard.html               # AIRISS 대시보드
│   ├── airiss_v4_portal.html       # AIRISS 포털
│   └── executive_dashboard.html    # 경영진 대시보드
└── urls.py           # AIRISS URL
```

#### 2️⃣ ai_quickwin/ (AI Quick Win 기능)
```
ai_quickwin/
├── ai_config.py       # AI 설정
├── services.py        # Quick Win 서비스
├── views.py          # Quick Win 뷰
├── management/commands/
│   └── test_ai_integration.py  # AI 통합 테스트
└── urls.py           # Quick Win URL
```

#### 3️⃣ AI 관련 앱들
```
ai_coaching/          # AI 코칭 시스템
ai_insights/          # AI 인사이트
ai_interviewer/       # AI 면접관
ai_predictions/       # AI 예측 (이직 위험 등)
ai_team_optimizer/    # AI 팀 최적화
ai_chatbot/          # AI 챗봇
```

### 🏢 조직 관리 모듈

#### 1️⃣ organization/ (조직 구조)
```
organization/
├── models.py         # Department, Position, Transfer 모델
├── views.py         # 조직 관리 뷰
├── templates/organization/
│   ├── organization_chart.html  # 조직도
│   └── department_tree_node.html # 부서 트리
└── urls.py          # 조직 관련 URL
```

#### 2️⃣ job_profiles/ (직무 프로필)
```
job_profiles/
├── models.py              # JobProfile 모델
├── matching_engine.py     # 직무 매칭 엔진
├── growth_services.py     # 성장 경로 서비스
├── leader_services.py     # 리더 추천 서비스
├── templates/job_profiles/
│   ├── job_hierarchy.html        # 직무 계층 구조
│   ├── job_tree_unified.html     # 통합 직무 트리
│   └── job_treemap.html          # 직무 트리맵
└── urls.py               # 직무 관련 URL
```

### 💰 보상 및 승진 모듈

#### 1️⃣ compensation/ (보상 관리)
```
compensation/
├── models.py         # Compensation 모델
├── views.py         # 보상 관리 뷰
├── templates/compensation/
│   └── dashboard.html  # 보상 대시보드
└── urls.py          # 보상 관련 URL
```

#### 2️⃣ promotions/ (승진 관리)
```
promotions/
├── models.py              # Promotion 모델
├── promotion_analyzer.py  # 승진 분석기
├── views.py              # 승진 관리 뷰
└── urls.py               # 승진 관련 URL
```

### 🎓 기타 모듈

#### 1️⃣ certifications/ (자격증 관리)
```
certifications/
├── models.py                      # Certification 모델
├── certification_engine.py        # 자격증 엔진
├── certification_services.py      # 자격증 서비스
└── urls.py                       # 자격증 URL
```

#### 2️⃣ trainings/ (교육 관리)
```
trainings/
├── models.py                 # Training 모델
├── training_recommender.py  # 교육 추천 시스템
├── training_services.py     # 교육 서비스
└── urls.py                  # 교육 URL
```

#### 3️⃣ recruitment/ (채용 관리)
```
recruitment/
├── models.py         # JobPosting, Application 모델
├── views.py         # 채용 관리 뷰
├── forms.py         # 채용 폼
└── urls.py          # 채용 URL
```

### ⚛️ Frontend (React)
```
frontend/
├── package.json           # Node.js 패키지 설정
├── tsconfig.json         # TypeScript 설정
├── public/
│   └── index.html        # HTML 템플릿
└── src/
    ├── App.tsx           # 메인 앱 컴포넌트
    ├── index.tsx         # 진입점
    ├── pages/
    │   └── ContributionEvaluation.tsx  # 기여도 평가 페이지
    ├── services/
    │   └── api.ts        # API 통신 서비스
    ├── components/       # 재사용 가능 컴포넌트
    └── styles/          # 스타일 파일
```

### 🎨 정적 파일
```
static/
├── css/
│   ├── brand.css                  # 브랜드 스타일
│   ├── design-system.css          # 디자인 시스템
│   └── job_tree_unified.css       # 직무 트리 스타일
├── js/
│   ├── job_tree_unified.js        # 직무 트리 스크립트
│   ├── contribution_scoring.js    # 기여도 점수 계산
│   └── employee-management.js     # 직원 관리 스크립트
└── images/
    └── ok-financial-logo.svg      # OK금융 로고
```

### 📊 템플릿 구조
```
templates/
├── base.html                      # 기본 템플릿
├── base_modern.html              # 모던 디자인 템플릿
├── dashboard.html                # 메인 대시보드
├── admin/                       # Django Admin 커스터마이징
├── ai/                          # AI 관련 템플릿
├── evaluations/                 # 평가 관련 템플릿
├── employees/                   # 직원 관련 템플릿
├── organization/                # 조직 관련 템플릿
├── hr/                         # HR 관련 템플릿
└── errors/                     # 에러 페이지
```

### 🛠️ 유틸리티 및 서비스
```
utils/
├── airiss_service.py         # AIRISS 서비스 유틸
├── evaluation_processor.py   # 평가 처리기
├── file_manager.py          # 파일 관리
├── file_upload.py           # 파일 업로드
└── security.py              # 보안 유틸리티

services/
├── compensation_service.py  # 보상 서비스
├── employee_service.py      # 직원 서비스
├── evaluation_service.py    # 평가 서비스
└── promotion_service.py     # 승진 서비스

core/
├── decorators.py           # 데코레이터
├── error_handlers.py       # 에러 핸들러
├── exceptions.py           # 커스텀 예외
├── mixins.py              # 믹스인 클래스
└── validators.py          # 유효성 검사기
```

### 🗄️ 데이터베이스 및 마이그레이션
```
├── db.sqlite3                    # SQLite 데이터베이스
├── */migrations/                 # 각 앱의 마이그레이션 파일
│   └── 0001_initial.py          # 초기 마이그레이션
```

### 📝 데이터 파일
```
├── OK_employee_*.xlsx           # 직원 데이터 Excel 파일들
├── employees_data.json          # 직원 데이터 JSON
└── sample_employees.xlsx        # 샘플 직원 데이터
```

### 🚀 배포 관련
```
├── railway.json                 # Railway 배포 설정
├── railway.toml                # Railway TOML 설정
├── Procfile                    # Heroku 배포
├── gunicorn.conf.py           # Gunicorn 설정
└── runtime.txt                # Python 런타임 버전
```

## 🔑 주요 기능별 위치

### 평가 시스템
- **메인 평가**: `/evaluations/contribution/`
- **AI 피드백**: `evaluations/ai_service.py`
- **점수 계산**: `static/js/contribution_scoring.js`

### 직원 관리
- **직원 목록**: `/employees/`
- **Excel 업로드**: `employees/services/excel_parser.py`
- **API**: `employees/api_views.py`

### AI 기능
- **AIRISS 대시보드**: `/airiss/dashboard/`
- **AI 챗봇**: `/ai_chatbot/`
- **예측 분석**: `/ai_predictions/`

### 조직 관리
- **조직도**: `/organization/chart/`
- **직무 프로필**: `/job_profiles/`
- **직무 매칭**: `job_profiles/matching_engine.py`

## 📌 중요 URL 패턴

### API 엔드포인트
- `/api/evaluations/` - 평가 CRUD
- `/api/evaluations/{id}/submit/` - 평가 제출
- `/api/evaluations/feedbacks/generate_ai/` - AI 피드백 생성
- `/api/tasks/` - 업무 관리
- `/api/notifications/` - 알림 시스템
- `/api/employees/` - 직원 관리

### 웹 페이지
- `/` - 메인 대시보드
- `/evaluations/contribution/` - 기여도 평가
- `/employees/` - 직원 관리
- `/organization/chart/` - 조직도
- `/job_profiles/` - 직무 프로필
- `/airiss/dashboard/` - AIRISS 대시보드

## 🔐 환경 변수 (.env)
- `SECRET_KEY` - Django 시크릿 키
- `OPENAI_API_KEY` - OpenAI API 키
- `DEBUG` - 디버그 모드
- `DATABASE_URL` - PostgreSQL 연결 (선택사항)
- `ALLOWED_HOSTS` - 허용된 호스트

## 🚦 개발 워크플로우

### 백엔드 시작
```bash
python manage.py migrate
python setup_initial_data.py
python manage.py runserver
```

### 프론트엔드 시작
```bash
cd frontend
npm install
npm start
```

### 테스트 계정
- **Admin**: admin / admin123
- **Evaluator**: evaluator1 / password123
- **Employee**: employee1 / password123

## 📊 데이터 모델 관계

### 핵심 관계
- User ← Employee (1:1)
- Employee → Department (N:1)
- Employee → Evaluation (1:N)
- Evaluation → Task (1:N)
- Evaluation → Score (1:N)
- Evaluation → Feedback (1:N)
- Employee → Goal (1:N)

## 🎯 프로젝트 특징
1. **통합 평가 시스템**: 기여도, 전문성, 영향력 평가
2. **AI 피드백**: OpenAI API를 통한 자동 피드백 생성
3. **실시간 알림**: WebSocket 기반 실시간 알림
4. **역할 기반 접근**: Employee, Evaluator, HR, Admin 역할
5. **대시보드**: 개인별, 부서별, 전사 대시보드
6. **Excel 통합**: 대량 데이터 업로드/다운로드
7. **직무 매칭**: AI 기반 직무 추천 시스템

## 🔧 유지보수 참고사항
- 마이그레이션 충돌 시: `python manage.py migrate --fake-initial`
- 정적 파일 수집: `python manage.py collectstatic`
- 캐시 초기화: `python manage.py clear_cache`
- 테스트 데이터 생성: `python setup_initial_data.py`

---
*마지막 업데이트: 2025년 1월*