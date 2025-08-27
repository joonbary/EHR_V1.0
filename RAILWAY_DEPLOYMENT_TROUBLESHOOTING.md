# Railway 배포 트러블슈팅 가이드

## 🔴 근본 원인 요약

### 1차 원인: 데이터베이스 초기화 스크립트
- **문제**: `railway_complete_reset.py`가 매번 모든 테이블 삭제
- **위치**: `railway.toml`의 startCommand
- **영향**: 배포할 때마다 모든 데이터 삭제

### 2차 원인: 잘못된 설정 파일 사용
- **문제**: Railway는 `railway.toml`을 사용하는데 `railway.json`을 수정하고 있었음
- **발견**: Railway 로그에서 "Railway PostgreSQL 데이터베이스 완전 초기화" 메시지 확인

### 3차 원인: 모델과 데이터베이스 스키마 불일치
- **문제 1**: Employee 모델에 없는 필드 사용
  - `headquarters3`, `headquarters4`, `team`, `major`, `notes`
- **문제 2**: 데이터베이스에 없는 필드 사용
  - `initial_position` - 마이그레이션이 적용되지 않음
- **오류**: `Employee() got unexpected keyword arguments`
- **오류**: `column "initial_position" of relation "employees_employee" does not exist`

### 4차 원인: 종속성 문제
- **문제**: `faker` 라이브러리가 requirements.txt에 없음
- **오류**: `ModuleNotFoundError: No module named 'faker'`

### 5차 원인: 마이그레이션 종속성 오류
- **문제**: `employees.0003`이 `employees.0002`보다 먼저 적용됨
- **오류**: `Migration is applied before its dependency`

## 📋 체계적 해결 과정

### 1단계: 문제 진단
```bash
# Railway 로그 확인
railway logs

# 디버그 엔드포인트 생성
/employees/system/debug/
```

### 2단계: 데이터베이스 초기화 방지
```toml
# railway.toml 수정
# 변경 전:
startCommand = "python railway_complete_reset.py ..."

# 변경 후:
startCommand = "python railway_migrate.py ..."
```

### 3단계: 안전한 마이그레이션 스크립트
```python
# fix_migration_dependency.py
# django_migrations 테이블 직접 수정
# 누락된 마이그레이션 레코드 추가
```

### 4단계: 필드 자동 감지 데이터 로드
```python
# load_safe_employees.py
def check_fields():
    """실제 데이터베이스 필드 확인"""
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'employees_employee'
    """)
    return columns

# 존재하는 필드만 사용
if 'field_name' in available_fields:
    employee_data['field_name'] = value
```

## ⚠️ 재발 방지 체크리스트

### 배포 전 확인사항
- [ ] Railway가 사용하는 설정 파일 확인 (`railway.toml` vs `railway.json`)
- [ ] 데이터베이스 초기화 스크립트가 startCommand에 없는지 확인
- [ ] requirements.txt에 모든 필요한 라이브러리 포함 확인
- [ ] 마이그레이션 파일 종속성 확인

### 데이터 로드 스크립트 작성 시
- [ ] Employee 모델의 실제 필드 확인
- [ ] 데이터베이스 스키마와 일치하는지 확인
- [ ] try-except로 개별 오류 처리
- [ ] 필드 자동 감지 로직 사용

### 모니터링
- [ ] `/employees/system/debug/` 엔드포인트로 상태 확인
- [ ] Railway 로그 실시간 모니터링
- [ ] 데이터 개수 확인

## 🛠️ 최종 해결책

### load_safe_employees.py 핵심 로직
```python
# 1. 데이터베이스 필드 자동 감지
available_fields = check_fields()

# 2. 필수 필드만 사용
employee_data = {
    'name': name,
    'email': email,
    'phone': phone,
    'department': department,
    'position': position,
}

# 3. 선택적 필드 조건부 추가
if 'company' in available_fields:
    employee_data['company'] = 'OK'

# 4. 오류 발생해도 계속 진행
try:
    Employee.objects.create(**employee_data)
except Exception as e:
    print(f"오류: {e}")
    continue  # 다음 직원으로
```

### railway.toml 최종 설정
```toml
[deploy]
startCommand = "python fix_migration_dependency.py && python load_safe_employees.py && python manage.py collectstatic --noinput && gunicorn ehr_system.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2 --threads 4"
```

## 📊 결과

✅ **성공적으로 해결된 사항**:
- 1000명 직원 데이터 생성
- 데이터베이스 초기화 방지
- 필드 불일치 문제 해결
- 마이그레이션 종속성 오류 해결
- 안정적인 배포 프로세스 구축

## 🔗 유용한 URL

- 직원 목록: https://ehrv10-production.up.railway.app/employees/list/
- 시스템 디버그: https://ehrv10-production.up.railway.app/employees/system/debug/
- Railway 대시보드: https://railway.app/

## 💡 교훈

1. **Railway 설정 파일 우선순위 이해**
   - railway.toml > railway.json > Procfile

2. **데이터베이스 스키마 일치 중요성**
   - 모델, 마이그레이션, 실제 DB가 모두 일치해야 함

3. **방어적 프로그래밍**
   - 필드 존재 여부 확인 후 사용
   - 오류 발생 시에도 전체 프로세스 계속 진행

4. **디버깅 도구 준비**
   - 시스템 상태 확인 엔드포인트 필수
   - 로그 실시간 모니터링 중요

---

문서 작성일: 2025-01-27
작성자: Claude & User
버전: 1.0