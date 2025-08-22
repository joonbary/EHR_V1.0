# Railway 500 오류 해결 가이드

## 문제 상황
- `/employees/api/organization-stats/` API에서 500 오류 발생
- `/employees/api/upload-organization-structure/` API에서 400 오류 발생
- 로컬에서는 정상 작동하나 Railway 배포 환경에서만 오류 발생

## 근본 원인
1. **모델 Import 문제**: views.py에서 모델을 함수 내부에서 import하여 모듈 로딩 실패
2. **데이터베이스 마이그레이션**: PostgreSQL과 SQLite 간 차이로 인한 테이블 구조 문제
3. **초기 데이터 부재**: OrganizationStructure 테이블에 데이터가 없어 통계 API 실패

## 해결 단계

### 1단계: 현재 상태 진단
```bash
# Railway 환경에서 실행
railway run python railway_final_fix.py
```

이 스크립트는 다음을 확인합니다:
- 데이터베이스 연결 상태
- 필수 테이블 존재 여부
- 모델 import 가능 여부
- API 엔드포인트 작동 상태

### 2단계: 마이그레이션 실행
```bash
# 마이그레이션 상태 확인
railway run python manage.py showmigrations employees

# 마이그레이션 실행
railway run python manage.py migrate

# 특정 앱만 마이그레이션
railway run python manage.py migrate employees
```

### 3단계: 초기 데이터 생성
```bash
# 초기 조직 데이터 생성
railway run python railway_final_fix.py

# 또는 전체 초기 데이터 설정
railway run python setup_initial_data.py
```

### 4단계: 정적 파일 처리
```bash
# 정적 파일 수집
railway run python manage.py collectstatic --noinput
```

### 5단계: 서버 재시작
```bash
# Railway 서버 재시작
railway restart

# 로그 확인
railway logs --tail 100
```

## 추가 확인 사항

### 환경 변수 확인
```bash
railway variables
```

필수 환경 변수:
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `DJANGO_SETTINGS_MODULE`: ehr_system.settings
- `SECRET_KEY`: Django 시크릿 키
- `DEBUG`: False (프로덕션)

### 데이터베이스 직접 확인
```bash
# PostgreSQL 접속
railway run python manage.py dbshell

# 테이블 목록 확인
\dt employees_*

# 레코드 수 확인
SELECT COUNT(*) FROM employees_organizationstructure;
```

## 작성된 디버깅 스크립트

1. **railway_final_fix.py**: 통합 진단 및 수정 스크립트
2. **railway_debug_500.py**: 상세 디버깅 스크립트
3. **test_local_api.py**: 로컬 환경 테스트
4. **railway_fix_api.py**: API 수정 스크립트

## 예상 결과

성공적으로 수정되면:
- `/employees/api/organization-stats/` API가 200 응답 반환
- `/employees/api/upload-organization-structure/` API가 정상 작동
- 조직 구조 Excel 업로드 기능 정상 작동

## 문제 지속 시

1. Railway 콘솔에서 직접 Python 셸 실행:
```bash
railway run python manage.py shell
```

2. 수동으로 import 테스트:
```python
from employees.models_organization import OrganizationStructure
OrganizationStructure.objects.count()
```

3. Railway 지원팀 문의 또는 PostgreSQL 연결 문자열 재확인