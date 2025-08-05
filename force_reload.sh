#!/bin/bash
# Django 강제 리로드 스크립트

echo "Django 변경사항 강제 적용 중..."

# 1. Python 캐시 삭제
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# 2. 마이그레이션 파일 재생성 (필요시)
# python manage.py makemigrations
# python manage.py migrate

# 3. Static 파일 재수집
python manage.py collectstatic --noinput --clear

# 4. 서버 재시작
echo ""
echo "이제 서버를 재시작하세요:"
echo "python manage.py runserver"
