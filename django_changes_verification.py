#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Django 변경사항 확인 및 강제 적용 스크립트
- 캐시 정리
- 파일 확인
- 서버 재시작
- 경로 검증
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 베이스 디렉토리
BASE_DIR = Path(__file__).parent

def clear_cache():
    """Python 캐시 파일 모두 삭제"""
    print("\n1. Python 캐시 정리 중...")
    
    # __pycache__ 디렉토리 찾아서 삭제
    cache_dirs = []
    for root, dirs, files in os.walk(BASE_DIR):
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            cache_dirs.append(cache_path)
            shutil.rmtree(cache_path, ignore_errors=True)
    
    # .pyc 파일 삭제
    pyc_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                pyc_files.append(file_path)
                try:
                    os.remove(file_path)
                except:
                    pass
    
    print(f"  - {len(cache_dirs)}개의 __pycache__ 디렉토리 삭제")
    print(f"  - {len(pyc_files)}개의 .pyc 파일 삭제")

def check_static_files():
    """Static 파일 재수집"""
    print("\n2. Static 파일 재수집...")
    
    try:
        # collectstatic 실행
        subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput', '--clear'
        ], cwd=BASE_DIR)
        print("  ✓ Static 파일 수집 완료")
    except Exception as e:
        print(f"  ✗ Static 파일 수집 실패: {e}")

def verify_files():
    """중요 파일 존재 여부 확인"""
    print("\n3. 파일 존재 여부 확인...")
    
    required_files = [
        # 템플릿
        'templates/base_simple.html',
        'templates/dashboard.html',
        'job_profiles/templates/job_profiles/job_treemap.html',
        
        # Views
        'job_profiles/views.py',
        'ehr_system/views.py',
        
        # URLs
        'job_profiles/urls.py',
        'ehr_system/urls.py',
        
        # Static
        'static/css/job_treemap_unified.css',
        'static/js/job_treemap_unified.js',
    ]
    
    for file_path in required_files:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - 파일 없음!")

def check_legacy_files():
    """레거시 파일 남아있는지 확인"""
    print("\n4. 레거시 파일 확인...")
    
    legacy_files = [
        'job_profiles/templates/job_profiles/job_tree.html',
        'job_profiles/templates/job_profiles/job_tree_map.html',
        'job_profiles/templates/job_profiles/job_tree_map_simple.html',
        'job_profiles/templates/job_profiles/job_profile_list.html',
        'static/js/JobProfileTreeMap.js',
        'static/css/JobProfileTreeMap.css',
    ]
    
    found_legacy = []
    for file_path in legacy_files:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            found_legacy.append(file_path)
            print(f"  ⚠️  {file_path} - 레거시 파일 발견!")
    
    if not found_legacy:
        print("  ✓ 레거시 파일 없음")
    
    return found_legacy

def check_urls():
    """URL 설정 확인"""
    print("\n5. URL 설정 확인...")
    
    # ehr_system/urls.py 내용 확인
    main_urls = BASE_DIR / 'ehr_system' / 'urls.py'
    if main_urls.exists():
        with open(main_urls, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("\n  [ehr_system/urls.py]")
        if "path('', DashboardView.as_view(), name='home')" in content:
            print("  ✓ 홈 URL이 대시보드로 설정됨")
        else:
            print("  ✗ 홈 URL 설정 확인 필요")
            
        if "path('job-profiles/', include('job_profiles.urls'))" in content:
            print("  ✓ job-profiles URL 연결됨")
        else:
            print("  ✗ job-profiles URL 연결 확인 필요")
    
    # job_profiles/urls.py 내용 확인
    job_urls = BASE_DIR / 'job_profiles' / 'urls.py'
    if job_urls.exists():
        with open(job_urls, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("\n  [job_profiles/urls.py]")
        if "JobTreeMapView" in content:
            print("  ✓ TreeMap 뷰 설정됨")
        else:
            print("  ✗ TreeMap 뷰 설정 확인 필요")

def restart_server_instructions():
    """서버 재시작 안내"""
    print("\n6. 서버 재시작 안내")
    print("="*60)
    print("서버를 완전히 재시작하세요:")
    print("\n[개발 서버]")
    print("1. Ctrl+C로 서버 중지")
    print("2. python manage.py runserver")
    print("\n[프로덕션 서버]")
    print("- Gunicorn: sudo systemctl restart gunicorn")
    print("- uWSGI: sudo systemctl restart uwsgi")
    print("- Docker: docker-compose restart")
    print("="*60)

def create_force_reload_script():
    """강제 리로드 스크립트 생성"""
    script_content = '''#!/bin/bash
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
'''
    
    script_path = BASE_DIR / 'force_reload.sh'
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # 실행 권한 부여 (Linux/Mac)
    if os.name != 'nt':
        os.chmod(script_path, 0o755)
    
    return script_path

def main():
    print("="*60)
    print("Django 변경사항 확인 및 적용")
    print("="*60)
    print(f"프로젝트 경로: {BASE_DIR}")
    
    # 1. 캐시 정리
    clear_cache()
    
    # 2. Static 파일 재수집
    check_static_files()
    
    # 3. 파일 확인
    verify_files()
    
    # 4. 레거시 파일 확인
    legacy_files = check_legacy_files()
    
    # 5. URL 확인
    check_urls()
    
    # 6. 서버 재시작 안내
    restart_server_instructions()
    
    # 7. 강제 리로드 스크립트 생성
    script_path = create_force_reload_script()
    print(f"\n강제 리로드 스크립트 생성: {script_path}")
    
    # 결과 요약
    print("\n" + "="*60)
    print("결과 요약")
    print("="*60)
    
    if legacy_files:
        print("\n⚠️  레거시 파일이 남아있습니다:")
        for f in legacy_files:
            print(f"   - {f}")
        print("\n다음 명령으로 삭제하세요:")
        for f in legacy_files:
            print(f"   rm {f}")
    
    print("\n✅ 체크리스트:")
    print("1. [ ] Python 캐시 삭제됨")
    print("2. [ ] Static 파일 재수집됨")
    print("3. [ ] 필수 파일 확인됨")
    print("4. [ ] 레거시 파일 제거됨")
    print("5. [ ] URL 설정 확인됨")
    print("6. [ ] 서버 재시작됨")
    
    print("\n다음 단계:")
    print("1. 위 체크리스트 확인")
    print("2. python manage.py runserver")
    print("3. http://localhost:8000/ 접속")
    print("="*60)

if __name__ == '__main__':
    main()