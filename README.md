# OK금융그룹 eHR 시스템

## 프로젝트 개요
OK금융그룹의 신인사제도를 반영한 종합 인사관리 시스템입니다.

## 주요 기능
- **직원 관리**: 직원 정보 CRUD, 프로필 관리, 대량 등록
- **평가 관리**: 3대 평가축(기여도, 전문성, 영향력) 기반 성과 평가
- **보상 관리**: 급여 계산, 성과급(PI) 산정, 급여명세서 생성
- **승진/인사이동**: 승진 요건 검증, 인사이동 이력 관리
- **셀프서비스**: 개인 정보 조회 및 수정

## 기술 스택
- **Backend**: Django 5.2.4
- **Database**: SQLite (개발), PostgreSQL (운영 권장)
- **Frontend**: Bootstrap 5, Chart.js
- **MCP Integration**: 파일서버, 시퀀셜싱킹, 태스크 매니저

## 프로젝트 구조
```
EHR_V1.0/
├── core/                   # 공통 모듈 (예외, 데코레이터, 유틸리티)
│   ├── mcp/               # MCP 통합 레이어
│   ├── decorators.py      # 공통 데코레이터
│   ├── exceptions.py      # 커스텀 예외
│   ├── validators.py      # 검증 유틸리티
│   └── utils.py          # 공통 유틸리티
├── services/              # 비즈니스 로직 서비스
│   ├── employee_service.py
│   ├── evaluation_service.py
│   ├── compensation_service.py
│   └── promotion_service.py
├── employees/             # 직원 관리 앱
├── evaluations/          # 평가 관리 앱
├── compensation/         # 보상 관리 앱
├── promotions/           # 승진/인사이동 앱
├── selfservice/          # 셀프서비스 앱
├── permissions/          # 권한 관리 앱
├── reports/              # 리포트 앱
└── templates/            # 템플릿 파일
```

## 설치 및 실행

### 1. 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 슈퍼유저 생성
```bash
python manage.py createsuperuser
```

### 5. 정적 파일 수집
```bash
python manage.py collectstatic
```

### 6. 개발 서버 실행
```bash
python manage.py runserver
```

### 7. 태스크 매니저 실행 (별도 터미널)
```bash
python manage.py start_task_manager
```

## MCP 서버 설정
`.claude/claude_desktop_config.json` 파일이 자동으로 생성되어 있습니다.
필요에 따라 경로를 수정하세요.

## 환경 설정

### 개발 환경
```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### 운영 환경
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# PostgreSQL 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ehr_db',
        'USER': 'ehr_user',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 주요 개선사항 (리팩터링)

### 1. 공통 모듈화
- 중복 코드를 core 패키지로 통합
- 재사용 가능한 데코레이터, 유틸리티 구현

### 2. MCP 통합 레이어
- 파일 처리: MCPFileService
- 복잡한 로직 처리: MCPSequentialService  
- 백그라운드 작업: MCPTaskService

### 3. 서비스 레이어 도입
- 비즈니스 로직을 뷰에서 분리
- 테스트 가능하고 유지보수가 쉬운 구조

### 4. 에러 처리 개선
- 커스텀 예외 계층 구조
- 전역 에러 핸들러
- 사용자 친화적인 에러 페이지

### 5. 로깅 시스템
- 모듈별 로거 설정
- 보안, 성능 로깅
- 로그 로테이션

## API 엔드포인트

### 직원 관리
- `GET /employees/` - 직원 목록
- `POST /employees/create/` - 직원 생성
- `GET /employees/<id>/` - 직원 상세
- `PUT /employees/<id>/edit/` - 직원 수정

### 평가 관리
- `GET /evaluations/` - 평가 대시보드
- `POST /evaluations/process/<period_id>/` - 평가 처리
- `GET /evaluations/insights/` - 평가 인사이트

### 백그라운드 작업
- `GET /tasks/` - 작업 대시보드
- `POST /tasks/submit/` - 작업 제출
- `GET /tasks/status/<task_id>/` - 작업 상태

## 테스트
```bash
# 전체 테스트 실행
python manage.py test

# 특정 앱 테스트
python manage.py test employees
```

## 문제 해결

### 1. 마이그레이션 오류
```bash
python manage.py migrate --run-syncdb
```

### 2. 정적 파일 로드 실패
```bash
python manage.py collectstatic --clear --noinput
```

### 3. 태스크 매니저 오류
로그 파일 확인: `logs/task_manager.log`

## 라이센스
이 프로젝트는 OK금융그룹 내부용으로 개발되었습니다.

## 문의
시스템 관련 문의는 IT 지원팀으로 연락주세요.