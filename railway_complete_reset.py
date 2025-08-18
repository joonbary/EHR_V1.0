#!/usr/bin/env python
"""
Railway PostgreSQL 데이터베이스 완전 초기화 스크립트
모든 테이블과 마이그레이션 기록을 삭제하고 처음부터 다시 시작합니다.
"""

import os
import sys
import django
from django.db import connection, transaction
from django.core.management import call_command

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def drop_all_tables():
    """모든 테이블을 안전하게 삭제합니다."""
    print("=" * 60)
    print("1단계: 모든 테이블 삭제")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # 외래키 제약 조건 일시적으로 비활성화
        cursor.execute("SET session_replication_role = 'replica';")
        
        # 모든 테이블 목록 가져오기
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"총 {len(tables)}개의 테이블을 발견했습니다.")
            for table in tables:
                table_name = table[0]
                try:
                    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
                    print(f"  ✓ {table_name} 삭제 완료")
                except Exception as e:
                    print(f"  ✗ {table_name} 삭제 실패: {e}")
        else:
            print("삭제할 테이블이 없습니다.")
        
        # 외래키 제약 조건 다시 활성화
        cursor.execute("SET session_replication_role = 'origin';")
    
    print("\n모든 테이블 삭제 완료!\n")

def create_migration_order():
    """올바른 마이그레이션 순서를 반환합니다."""
    return [
        # 1. 독립적인 앱들 (의존성 없음)
        'employees',
        'organization',
        
        # 2. employees에 의존하는 앱들
        'notifications',
        'compensation',
        'permissions',
        'promotions',
        'reports',
        'selfservice',
        
        # 3. job_profiles (employees 의존)
        'job_profiles',
        
        # 4. evaluations (employees, organization 의존)
        'evaluations',
        
        # 5. certifications (employees, job_profiles 의존)
        'certifications',
        
        # 6. recruitment (job_profiles 의존)
        'recruitment',
        
        # 7. AI 관련 앱들 (employees 의존)
        'ai_chatbot',
        'ai_insights',
        'ai_predictions',
        'ai_coaching',
        'ai_interviewer',
        'ai_team_optimizer',
        
        # 8. 통합 앱
        'airiss',
        
        # 9. 기타 앱들
        'access_control',
        'search',
    ]

def run_migrations_safely():
    """안전하게 마이그레이션을 실행합니다."""
    print("=" * 60)
    print("2단계: 마이그레이션 실행")
    print("=" * 60)
    
    # 먼저 Django 내장 앱들 마이그레이션
    print("\n[Django 내장 앱 마이그레이션]")
    try:
        call_command('migrate', 'contenttypes', verbosity=1)
        call_command('migrate', 'auth', verbosity=1)
        call_command('migrate', 'admin', verbosity=1)
        call_command('migrate', 'sessions', verbosity=1)
        print("✓ Django 내장 앱 마이그레이션 완료")
    except Exception as e:
        print(f"✗ Django 내장 앱 마이그레이션 실패: {e}")
        return False
    
    # 커스텀 앱들을 순서대로 마이그레이션
    print("\n[커스텀 앱 마이그레이션]")
    app_order = create_migration_order()
    
    for app_name in app_order:
        try:
            print(f"\n마이그레이션 중: {app_name}")
            call_command('migrate', app_name, verbosity=0)
            print(f"  ✓ {app_name} 완료")
        except Exception as e:
            print(f"  ✗ {app_name} 실패: {str(e)[:100]}")
            # 실패해도 계속 진행 (일부 앱은 마이그레이션이 없을 수 있음)
    
    print("\n모든 마이그레이션 완료!\n")
    return True

def verify_database():
    """데이터베이스 상태를 검증합니다."""
    print("=" * 60)
    print("3단계: 데이터베이스 검증")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # 생성된 테이블 수 확인
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        table_count = cursor.fetchone()[0]
        print(f"\n생성된 테이블 수: {table_count}")
        
        # 주요 테이블 확인
        important_tables = [
            'django_migrations',
            'employees_employee',
            'organization_department',
            'evaluations_evaluation',
            'notifications_notification',
            'job_profiles_jobprofile'
        ]
        
        print("\n주요 테이블 확인:")
        for table in important_tables:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename = '{table}'
                )
            """)
            exists = cursor.fetchone()[0]
            status = "✓" if exists else "✗"
            print(f"  {status} {table}")
    
    print("\n데이터베이스 검증 완료!\n")

def main():
    """메인 실행 함수"""
    print("\n" + "=" * 60)
    print("Railway PostgreSQL 데이터베이스 완전 초기화")
    print("=" * 60)
    
    # Railway 환경 확인
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    database_url = os.environ.get('DATABASE_URL', 'Not set')
    
    print(f"\n환경 정보:")
    print(f"  - Railway 환경: {'예' if is_railway else '아니오'}")
    print(f"  - Database URL: {database_url[:50]}..." if len(database_url) > 50 else f"  - Database URL: {database_url}")
    
    if not is_railway:
        print("\n⚠️  경고: Railway 환경이 아닙니다!")
        response = input("계속하시겠습니까? (yes/no): ")
        if response.lower() != 'yes':
            print("작업이 취소되었습니다.")
            return
    
    try:
        # 1. 모든 테이블 삭제
        drop_all_tables()
        
        # 2. 마이그레이션 실행
        success = run_migrations_safely()
        
        if success:
            # 3. 데이터베이스 검증
            verify_database()
            
            print("=" * 60)
            print("✅ 데이터베이스 초기화 성공!")
            print("=" * 60)
            print("\n다음 단계:")
            print("1. Railway에 배포: git push origin main")
            print("2. 초기 데이터 생성: python setup_initial_data.py")
        else:
            print("\n⚠️  일부 마이그레이션이 실패했습니다.")
            print("로그를 확인하고 필요한 조치를 취하세요.")
    
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()