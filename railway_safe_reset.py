#!/usr/bin/env python
"""
Railway PostgreSQL 안전 초기화 스크립트
권한 문제 없이 Django 마이그레이션만으로 안전하게 초기화합니다.
"""

import os
import sys
import django
from django.core.management import call_command
from django.db import connection

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_evaluation.settings')
django.setup()

def reset_migrations():
    """모든 앱의 마이그레이션을 초기화합니다."""
    print("=" * 60)
    print("Django 마이그레이션 안전 초기화")
    print("=" * 60)
    
    # Django 앱 목록
    apps = [
        'employees',
        'evaluations',
        'notifications',
        'users',
        'organization',
        'ai_chatbot',
        'ai_coaching',
        'ai_insights',
        'ai_interviewer',
        'ai_predictions',
        'ai_team_optimizer',
        'airiss',
        'access_control',
        'certifications',
        'compensation',
        'job_profiles',
        'permissions',
        'promotions',
        'recruitment',
        'reports',
        'search',
    ]
    
    print("1단계: 마이그레이션 초기 상태로 되돌리기")
    for app in apps:
        try:
            print(f"  📱 {app} 앱 초기화 중...")
            call_command('migrate', app, 'zero', verbosity=0, interactive=False)
            print(f"  ✅ {app} 초기화 완료")
        except Exception as e:
            print(f"  ⚠️ {app} 초기화 건너뜀: {str(e)}")
    
    print("\n2단계: 모든 마이그레이션 재적용")
    try:
        call_command('migrate', verbosity=1, interactive=False)
        print("✅ 모든 마이그레이션 적용 완료")
    except Exception as e:
        print(f"❌ 마이그레이션 오류: {e}")
        return False
    
    return True

def create_superuser():
    """관리자 계정을 생성합니다."""
    print("\n3단계: 관리자 계정 생성")
    
    try:
        from django.contrib.auth.models import User
        
        # 기존 admin 계정이 있는지 확인
        if User.objects.filter(username='admin').exists():
            print("  ℹ️ admin 계정이 이미 존재합니다.")
            return True
        
        # 새 admin 계정 생성
        User.objects.create_superuser(
            username='admin',
            email='admin@okfinance.co.kr',
            password='admin123'
        )
        print("  ✅ admin 계정 생성 완료 (admin/admin123)")
        return True
        
    except Exception as e:
        print(f"  ❌ 관리자 계정 생성 실패: {e}")
        return False

def load_initial_data():
    """초기 데이터를 로드합니다."""
    print("\n4단계: 초기 데이터 로드")
    
    try:
        # 기본 직원 데이터가 있는지 확인
        from employees.models import Employee
        
        if Employee.objects.count() > 0:
            print("  ℹ️ 직원 데이터가 이미 존재합니다.")
            return True
        
        # setup_initial_data.py 실행
        exec(open('setup_initial_data.py').read())
        print("  ✅ 초기 데이터 로드 완료")
        return True
        
    except Exception as e:
        print(f"  ⚠️ 초기 데이터 로드 실패: {e}")
        print("  💡 수동으로 setup_initial_data.py를 실행해주세요.")
        return False

def verify_setup():
    """설정이 제대로 되었는지 확인합니다."""
    print("\n5단계: 설정 검증")
    
    try:
        from django.contrib.auth.models import User
        from employees.models import Employee
        from employees.models_organization import OrganizationStructure
        
        # 사용자 수
        user_count = User.objects.count()
        print(f"  👥 사용자: {user_count}명")
        
        # 직원 수
        employee_count = Employee.objects.count()
        print(f"  🏢 직원: {employee_count}명")
        
        # 조직 수
        org_count = OrganizationStructure.objects.count()
        print(f"  🏗️ 조직: {org_count}개")
        
        # 테이블 수
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """)
            table_count = cursor.fetchone()[0]
            print(f"  📊 테이블: {table_count}개")
        
        print("  ✅ 설정 검증 완료")
        return True
        
    except Exception as e:
        print(f"  ❌ 설정 검증 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 Railway PostgreSQL 안전 초기화 시작")
    print("=" * 60)
    
    success = True
    
    # 1. 마이그레이션 초기화 및 재적용
    if not reset_migrations():
        success = False
    
    # 2. 관리자 계정 생성
    if not create_superuser():
        success = False
    
    # 3. 초기 데이터 로드
    if not load_initial_data():
        success = False  # 경고만, 실패로 처리하지 않음
    
    # 4. 설정 검증
    if not verify_setup():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 초기화 완료!")
        print("📱 웹사이트: https://ehrv10-production.up.railway.app")
        print("👤 관리자: admin / admin123")
    else:
        print("⚠️ 일부 단계에서 오류가 발생했습니다.")
        print("📝 수동으로 확인이 필요할 수 있습니다.")
    print("=" * 60)

if __name__ == '__main__':
    main()