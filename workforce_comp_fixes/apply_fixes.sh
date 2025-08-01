#!/bin/bash
# 인력/보상 대시보드 데이터 바인딩 수정 적용 스크립트

echo "=== 인력/보상 대시보드 데이터 바인딩 수정 시작 ==="

# 1. 백업 생성
echo "1. 기존 파일 백업 중..."
mkdir -p backup/$(date +%Y%m%d)
cp -r static/js backup/$(date +%Y%m%d)/
cp -r compensation/views.py backup/$(date +%Y%m%d)/

# 2. JavaScript 유틸리티 복사
echo "2. JavaScript 유틸리티 파일 복사 중..."
mkdir -p static/js/utils
cp workforce_comp_fixes/api_transformer.js static/js/utils/
cp workforce_comp_fixes/safe_data_accessor.js static/js/utils/

# 3. Django View 업데이트
echo "3. Django View 업데이트 중..."
cp workforce_comp_fixes/workforce_comp_views.py compensation/views.py

# 4. 정적 파일 수집
echo "4. 정적 파일 수집 중..."
python manage.py collectstatic --noinput

# 5. 캐시 클리어
echo "5. 캐시 클리어 중..."
python manage.py clear_cache

# 6. 테스트 실행
echo "6. 테스트 실행 중..."
python workforce_comp_fixes/test_dashboard_binding.py

echo "=== 수정 적용 완료 ==="
echo "브라우저 캐시를 클리어하고 대시보드를 새로고침하세요."
