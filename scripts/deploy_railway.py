#!/usr/bin/env python
"""
Railway 배포 자동화 스크립트
- 마이그레이션 실행
- 테스트 데이터 생성
- 헬스체크
"""

import os
import sys
import subprocess
import time
import requests
from datetime import datetime

# 프로젝트 루트 디렉토리 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_command(command, check=True):
    """명령 실행 및 결과 반환"""
    print(f"실행: {command}")
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=check
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"에러: {result.stderr}", file=sys.stderr)
    return result.returncode == 0

def check_railway_cli():
    """Railway CLI 설치 확인"""
    try:
        subprocess.run(['railway', '--version'], capture_output=True, check=True)
        print("✅ Railway CLI 설치 확인")
        return True
    except:
        print("❌ Railway CLI가 설치되지 않았습니다.")
        print("설치: npm install -g @railway/cli")
        return False

def run_migrations():
    """데이터베이스 마이그레이션 실행"""
    print("\n📦 마이그레이션 실행 중...")
    
    # 마이그레이션 생성
    if not run_command("railway run python manage.py makemigrations --noinput", check=False):
        print("⚠️ 새로운 마이그레이션이 없습니다.")
    
    # 마이그레이션 적용
    if run_command("railway run python manage.py migrate --noinput"):
        print("✅ 마이그레이션 완료")
        return True
    else:
        print("❌ 마이그레이션 실패")
        return False

def collect_static():
    """정적 파일 수집"""
    print("\n🎨 정적 파일 수집 중...")
    
    if run_command("railway run python manage.py collectstatic --noinput"):
        print("✅ 정적 파일 수집 완료")
        return True
    else:
        print("❌ 정적 파일 수집 실패")
        return False

def create_superuser():
    """관리자 계정 생성"""
    print("\n👤 관리자 계정 확인 중...")
    
    check_cmd = """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@ehrv10.com', 'admin123')
    print('관리자 계정 생성됨')
else:
    print('관리자 계정 이미 존재')
"""
    
    result = subprocess.run(
        f'railway run python -c "{check_cmd}"',
        shell=True,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    return True

def load_initial_data():
    """초기 데이터 로드"""
    print("\n📊 초기 데이터 로드 중...")
    
    # 카테고리 데이터 생성
    if run_command("railway run python create_talent_tables_railway.py", check=False):
        print("✅ 인재 관리 테이블 생성")
    
    # 샘플 데이터 생성 (필요시)
    if os.getenv('CREATE_SAMPLE_DATA', 'false').lower() == 'true':
        if run_command("railway run python railway_simple_init.py", check=False):
            print("✅ 샘플 데이터 생성")
    
    return True

def health_check(url="https://ehrv10-production.up.railway.app/health/", retries=5):
    """헬스체크 실행"""
    print(f"\n🏥 헬스체크 실행 중... ({url})")
    
    for i in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ 헬스체크 성공 (상태 코드: {response.status_code})")
                return True
            else:
                print(f"⚠️ 헬스체크 응답: {response.status_code}")
        except Exception as e:
            print(f"⚠️ 시도 {i+1}/{retries}: {e}")
        
        if i < retries - 1:
            time.sleep(10)
    
    print("❌ 헬스체크 실패")
    return False

def deploy_to_railway():
    """Railway 배포 실행"""
    print("\n🚀 Railway 배포 시작...")
    
    if run_command("railway up"):
        print("✅ 배포 완료")
        return True
    else:
        print("❌ 배포 실패")
        return False

def main():
    """메인 배포 프로세스"""
    print("=" * 60)
    print(f"Railway 배포 스크립트 - {datetime.now()}")
    print("=" * 60)
    
    # Railway CLI 확인
    if not check_railway_cli():
        sys.exit(1)
    
    # 배포 단계
    steps = [
        ("배포", deploy_to_railway),
        ("마이그레이션", run_migrations),
        ("정적 파일", collect_static),
        ("관리자 계정", create_superuser),
        ("초기 데이터", load_initial_data),
        ("헬스체크", health_check),
    ]
    
    results = []
    for step_name, step_func in steps:
        print(f"\n[{step_name}]")
        success = step_func()
        results.append((step_name, success))
        
        if not success and step_name in ["배포", "마이그레이션"]:
            print(f"\n❌ 중요 단계 실패: {step_name}")
            break
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("배포 결과 요약")
    print("=" * 60)
    
    for step_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {step_name}")
    
    # 전체 성공 여부
    all_success = all(success for _, success in results)
    if all_success:
        print("\n🎉 배포 완료!")
        print(f"URL: https://ehrv10-production.up.railway.app/")
    else:
        print("\n⚠️ 일부 단계에서 문제가 발생했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()