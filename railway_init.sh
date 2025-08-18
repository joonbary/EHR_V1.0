#!/bin/bash
# Railway 초기화 스크립트

echo "=== Starting Railway Initialization ==="

# 1. Static 파일 수집
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 2. 데이터베이스 초기화
echo "Initializing database..."
# 기존 데이터베이스 파일 삭제 (있으면)
rm -f db.sqlite3

# 3. 마이그레이션 실행
echo "Running migrations..."
python manage.py migrate --noinput

# 4. 데이터 로드
echo "Loading employee data..."
if [ -f "employees_only.json" ]; then
    python manage.py loaddata employees_only.json
    echo "Data loaded successfully"
else
    echo "employees_only.json not found"
fi

# 5. 데이터 확인
echo "Checking data..."
python manage.py shell -c "from employees.models import Employee; print(f'Total employees: {Employee.objects.count()}')"

# 6. 서버 시작
echo "Starting server..."
gunicorn ehr_system.wsgi --bind 0.0.0.0:$PORT