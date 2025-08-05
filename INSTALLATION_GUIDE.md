
# EHR 시스템 미연동 기능 자동 설치 가이드

## 설치 완료 항목

### 1. 생성된 파일들
- URL 패턴: `generated_url_patterns.py`
- 뷰 함수: `generated_views/` 디렉토리
- 템플릿: `generated_templates/` 디렉토리
- 메뉴 업데이트: `menu_updates.html`

### 2. 수동 작업 필요 항목

#### A. urls.py 업데이트
1. `ehr_system/urls.py` 파일을 열고
2. `generated_url_patterns.py`의 내용을 추가
3. 필요한 import 문 추가

#### B. 뷰 파일 복사
1. `generated_views/` 디렉토리의 파일들을 적절한 앱으로 복사
2. 필요한 import 문 조정

#### C. 템플릿 복사
1. `generated_templates/` 디렉토리의 파일들을 `templates/` 디렉토리로 복사
2. 디렉토리 구조 유지

#### D. base.html 업데이트
1. `templates/base.html` 파일을 열고
2. `menu_updates.html`의 내용을 사이드바 메뉴에 추가
3. 적절한 위치에 삽입 (AI 도구 섹션 다음)

### 3. 마이그레이션 (필요시)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 정적 파일 수집 (프로덕션)
```bash
python manage.py collectstatic
```

### 5. 서버 재시작
```bash
python manage.py runserver
```

## 연결된 기능 목록

총 5개 기능이 연결되었습니다:

- **통합 테스트 시스템**: 시나리오별 QA 및 AI 품질/성능/보안 테스트
  - URL: `/testing/`
  - 메뉴: dev_tools

- **직무 매칭 시스템**: 직무-인재 자동 매칭 및 추천
  - URL: `/matching/`
  - 메뉴: talent_management

- **자격증 관리**: 자격증 및 성장레벨 관리 시스템
  - URL: `/certifications/`
  - 메뉴: talent_management

- **ESS 확장 기능**: 개인 성장경로 및 맞춤 추천
  - URL: `/ess-plus/`
  - 메뉴: self_service

- **고급 분석 도구**: 전략 리포트 및 승진 분석
  - URL: `/analytics/`
  - 메뉴: analytics

