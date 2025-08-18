# EHR Evaluation System - 직원 성과 평가 시스템

## 개요
EHR Evaluation System은 Elevate Growth System의 기능을 통합한 직원 성과 및 기여도 평가 시스템입니다. AI 기반 피드백 생성, 실시간 알림, 대시보드 분석 등의 기능을 제공합니다.

## 주요 기능

### 1. 기여도 평가 시스템 (/evaluations/contribution/)
- **단계별 평가 프로세스**: 직원 선택 → 업무 평가 → 성과 점수 → AI 피드백 → 최종 검토
- **다차원 평가 기준**:
  - 기술 역량 (코드 품질, 문제 해결, 기술 습득)
  - 기여도 (프로젝트 기여, 팀 협업, 업무 완성도)
  - 성장 및 발전 (자기 개발, 목표 달성, 혁신성)
- **AI 기반 피드백**: OpenAI API를 활용한 맞춤형 피드백 생성
- **목표 설정 및 추적**: 개인별 목표 설정 및 달성률 모니터링

### 2. 업무 관리
- 업무 할당 및 추적
- 우선순위 관리
- 진행 상황 모니터링
- 완료율 통계

### 3. 실시간 알림 시스템
- WebSocket 기반 실시간 알림
- 평가 상태 변경 알림
- 업무 할당 알림
- 피드백 수신 알림

### 4. 대시보드 및 분석
- 개인/팀 성과 대시보드
- 성과 추세 차트
- 카테고리별 점수 분석
- 업무 완료율 통계

### 5. 사용자 역할 관리
- Employee (직원)
- Evaluator (평가자)
- HR Manager (인사 관리자)
- Administrator (관리자)

## 기술 스택

### Backend
- Django 5.2
- Django REST Framework
- PostgreSQL/SQLite
- Channels (WebSocket)
- OpenAI API
- Redis (캐싱 및 WebSocket)

### Frontend
- React 18 with TypeScript
- Material-UI (MUI)
- React Router
- React Query
- Chart.js
- Socket.io Client

## 설치 및 실행

### 요구사항
- Python 3.10+
- Node.js 16+
- Redis (선택사항, WebSocket용)

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd EHR_project
```

### 2. 환경 설정
`.env` 파일을 생성하고 다음 내용을 설정:
```
SECRET_KEY=your-secret-key
DEBUG=True
OPENAI_API_KEY=your-openai-api-key
```

### 3. Backend 실행
```bash
# Windows
run_server.bat

# Linux/Mac
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 4. Frontend 실행
```bash
# Windows
run_frontend.bat

# Linux/Mac
cd frontend
npm install
npm start
```

### 5. 접속 정보
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin
- 기여도 평가: http://localhost:3000/evaluations/contribution

## API 엔드포인트

### 인증
- `POST /api/token/` - 로그인 토큰 발급
- `GET /api/users/me/` - 현재 사용자 정보

### 평가 관리
- `GET/POST /api/evaluations/evaluations/` - 평가 목록/생성
- `GET/PATCH /api/evaluations/evaluations/{id}/` - 평가 상세/수정
- `POST /api/evaluations/evaluations/{id}/submit/` - 평가 제출
- `POST /api/evaluations/evaluations/{id}/approve/` - 평가 승인
- `GET /api/evaluations/evaluations/{id}/analytics/` - 평가 분석

### 업무 관리
- `GET/POST /api/evaluations/tasks/` - 업무 목록/생성
- `POST /api/evaluations/tasks/{id}/complete/` - 업무 완료

### AI 피드백
- `POST /api/evaluations/feedbacks/generate_ai/` - AI 피드백 생성

### 알림
- `GET /api/notifications/` - 알림 목록
- `POST /api/notifications/{id}/mark_as_read/` - 읽음 표시

## 프로젝트 구조
```
EHR_project/
├── ehr_evaluation/         # Django 프로젝트 설정
├── users/                  # 사용자 관리 앱
├── evaluations/           # 평가 시스템 앱
├── notifications/         # 알림 시스템 앱
├── frontend/              # React 프론트엔드
│   ├── src/
│   │   ├── components/    # 재사용 컴포넌트
│   │   ├── pages/        # 페이지 컴포넌트
│   │   │   └── ContributionEvaluation.tsx  # 기여도 평가 페이지
│   │   └── services/      # API 서비스
├── static/                # 정적 파일
├── media/                 # 업로드 파일
├── manage.py             # Django 관리 스크립트
├── run_server.bat        # Backend 실행 스크립트
└── run_frontend.bat      # Frontend 실행 스크립트
```

## 주요 모델

### User (사용자)
- 확장된 Django User 모델
- 역할, 부서, 직급, 입사일 등 추가 필드

### Evaluation (평가)
- 평가 기간, 직원, 평가자
- 상태 관리 (draft, submitted, approved, rejected)
- 종합 점수 자동 계산

### Task (업무)
- 업무 제목, 설명, 할당자
- 우선순위, 상태, 기한
- 가중치 설정

### Score (점수)
- 평가별 세부 점수
- 평가 기준별 점수
- 코멘트

### Feedback (피드백)
- AI 생성 및 수동 피드백
- 강점, 개선점, 추천사항
- OpenAI API 연동

### Goal (목표)
- 개인별 목표 설정
- 진행률 추적
- 달성 상태 관리

## 보안 고려사항
- Token 기반 인증
- CORS 설정
- 역할 기반 접근 제어
- 환경 변수를 통한 민감 정보 관리

## 향후 개선 계획
- [ ] 다국어 지원 확대
- [ ] 모바일 앱 개발
- [ ] 고급 분석 대시보드
- [ ] 360도 피드백 시스템
- [ ] 성과 예측 AI 모델
- [ ] 팀 협업 도구 통합

## 라이선스
MIT License

## 문의
프로젝트 관련 문의는 GitHub Issues를 통해 제출해주세요.