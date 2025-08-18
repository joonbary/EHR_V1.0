# Railway 콘솔에서 직접 실행할 명령어

Railway 대시보드에서 프로젝트 선택 후 Console/Shell 탭에서 실행하세요.

## 1. 현재 상태 확인
```bash
python manage.py shell -c "from employees.models import Employee; print(f'Current employees: {Employee.objects.count()}')"
```

## 2. 데이터베이스 리셋 및 마이그레이션
```bash
# SQLite 데이터베이스 파일 삭제 (있으면)
rm -f db.sqlite3

# 마이그레이션 실행
python manage.py migrate --noinput
```

## 3. 직원 데이터 로드
```bash
# 1,383명의 직원 데이터 로드
python manage.py loaddata employees_only.json
```

## 4. 결과 확인
```bash
python manage.py shell -c "from employees.models import Employee; print(f'Total employees loaded: {Employee.objects.count()}')"
```

## 5. 한 번에 모두 실행 (복사해서 붙여넣기)
```bash
rm -f db.sqlite3 && python manage.py migrate --noinput && python manage.py loaddata employees_only.json && python manage.py shell -c "from employees.models import Employee; print(f'Success! Total employees: {Employee.objects.count()}')"
```

## 문제 해결

### 마이그레이션 오류가 발생하는 경우:
```bash
python manage.py migrate --fake-initial
```

### 데이터 로드가 실패하는 경우:
```bash
# 파일 존재 확인
ls employees_only.json

# 직접 Python 스크립트 실행
python reset_and_load.py
```

### 완전 초기화가 필요한 경우:
```bash
# 모든 테이블 삭제 후 재생성
python manage.py flush --noinput
python manage.py migrate --noinput
python manage.py loaddata employees_only.json
```