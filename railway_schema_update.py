#!/usr/bin/env python
"""
Railway PostgreSQL 안전한 스키마 업데이트 스크립트
새로운 조직 구조 모델을 안전하게 배포합니다.
"""

import os
import sys
import django
from django.core.management import call_command
from django.db import connection, transaction

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_evaluation.settings')
django.setup()

def check_current_schema():
    """현재 데이터베이스 스키마 상태를 확인합니다."""
    print("=" * 60)
    print("1단계: 현재 스키마 상태 확인")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # 테이블 존재 여부 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'employees_%organization%'
        """)
        org_tables = cursor.fetchall()
        
        print(f"📊 조직 관련 테이블 수: {len(org_tables)}")
        for table in org_tables:
            print(f"  - {table[0]}")
        
        # 마이그레이션 상태 확인
        cursor.execute("""
            SELECT app, name 
            FROM django_migrations 
            WHERE app = 'employees' 
            ORDER BY applied DESC 
            LIMIT 5
        """)
        migrations = cursor.fetchall()
        
        print(f"\n📋 최근 employees 마이그레이션:")
        for app, name in migrations:
            print(f"  - {name}")
        
        # OrganizationStructure 테이블 존재 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'employees_organizationstructure'
            )
        """)
        org_table_exists = cursor.fetchone()[0]
        
        return org_table_exists

def apply_migration_safely():
    """안전하게 마이그레이션을 적용합니다."""
    print("\n=" * 60)
    print("2단계: 안전한 마이그레이션 적용")
    print("=" * 60)
    
    try:
        # 1. 마이그레이션 상태 확인
        print("📋 마이그레이션 상태 확인 중...")
        call_command('showmigrations', 'employees', verbosity=1)
        
        # 2. 새로운 마이그레이션 적용
        print("\n🚀 새로운 마이그레이션 적용 중...")
        call_command('migrate', 'employees', verbosity=2, interactive=False)
        
        print("✅ 마이그레이션 적용 완료")
        return True
        
    except Exception as e:
        print(f"❌ 마이그레이션 오류: {e}")
        return False

def verify_new_models():
    """새로운 모델이 제대로 생성되었는지 확인합니다."""
    print("\n=" * 60)
    print("3단계: 새 모델 검증")
    print("=" * 60)
    
    try:
        from employees.models_organization import (
            OrganizationStructure, 
            OrganizationUploadHistory, 
            EmployeeOrganizationMapping
        )
        
        # 모델 접근 테스트
        org_count = OrganizationStructure.objects.count()
        upload_count = OrganizationUploadHistory.objects.count()
        mapping_count = EmployeeOrganizationMapping.objects.count()
        
        print(f"🏗️ OrganizationStructure: {org_count}개")
        print(f"📤 OrganizationUploadHistory: {upload_count}개")
        print(f"🔗 EmployeeOrganizationMapping: {mapping_count}개")
        
        # Employee 모델의 organization 필드 확인
        from employees.models import Employee
        
        # organization 필드가 있는 직원 수 확인
        org_employees = Employee.objects.filter(organization__isnull=False).count()
        total_employees = Employee.objects.count()
        
        print(f"👥 전체 직원: {total_employees}명")
        print(f"🏢 조직 배정 직원: {org_employees}명")
        
        print("✅ 새 모델 검증 완료")
        return True
        
    except Exception as e:
        print(f"❌ 모델 검증 실패: {e}")
        return False

def create_sample_organization():
    """샘플 조직 구조를 생성합니다."""
    print("\n=" * 60)
    print("4단계: 샘플 조직 구조 생성")
    print("=" * 60)
    
    try:
        from employees.models_organization import OrganizationStructure
        
        # 이미 조직이 있는지 확인
        if OrganizationStructure.objects.exists():
            print("ℹ️ 기존 조직 구조가 존재합니다. 건너뜁니다.")
            return True
        
        # OK금융그룹 기본 구조 생성
        print("🏗️ OK금융그룹 기본 구조 생성 중...")
        
        # 그룹 (레벨 1)
        group = OrganizationStructure.objects.create(
            org_code='GRP001',
            org_name='OK금융그룹',
            org_level=1,
            status='active',
            sort_order=1,
            description='OK금융그룹 지주회사'
        )
        print("  ✓ OK금융그룹 생성")
        
        # 계열사 (레벨 2)
        bank = OrganizationStructure.objects.create(
            org_code='COM001',
            org_name='OK저축은행',
            org_level=2,
            parent=group,
            status='active',
            sort_order=1,
            description='저축은행 계열사'
        )
        print("  ✓ OK저축은행 생성")
        
        # 본부 (레벨 3)
        digital_hq = OrganizationStructure.objects.create(
            org_code='HQ001',
            org_name='디지털본부',
            org_level=3,
            parent=bank,
            status='active',
            sort_order=1,
            description='디지털 혁신 담당 본부'
        )
        print("  ✓ 디지털본부 생성")
        
        # 부 (레벨 4)
        it_dept = OrganizationStructure.objects.create(
            org_code='DEPT001',
            org_name='IT개발부',
            org_level=4,
            parent=digital_hq,
            status='active',
            sort_order=1,
            description='IT 시스템 개발'
        )
        print("  ✓ IT개발부 생성")
        
        # 팀 (레벨 5)
        dev_team = OrganizationStructure.objects.create(
            org_code='TEAM001',
            org_name='개발1팀',
            org_level=5,
            parent=it_dept,
            status='active',
            sort_order=1,
            description='핵심 시스템 개발팀'
        )
        print("  ✓ 개발1팀 생성")
        
        total_orgs = OrganizationStructure.objects.count()
        print(f"✅ 총 {total_orgs}개 조직 생성 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 샘플 조직 생성 실패: {e}")
        return False

def verify_urls():
    """URL 접근 가능 여부를 확인합니다."""
    print("\n=" * 60)
    print("5단계: URL 접근성 확인")
    print("=" * 60)
    
    try:
        from django.urls import reverse
        
        # 새로운 URL들 확인
        urls_to_check = [
            ('employees:organization_structure', '조직 구조 관리'),
            ('employees:organization_input', '조직 정보 입력'),
            ('employees:upload_organization_structure', '조직 구조 업로드 API'),
            ('employees:get_organization_tree', '조직 트리 API'),
        ]
        
        for url_name, description in urls_to_check:
            try:
                url = reverse(url_name)
                print(f"  ✅ {description}: {url}")
            except Exception as e:
                print(f"  ❌ {description}: {e}")
        
        print("✅ URL 확인 완료")
        return True
        
    except Exception as e:
        print(f"❌ URL 확인 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 Railway PostgreSQL 안전 스키마 업데이트 시작")
    print("=" * 60)
    
    # 1. 현재 스키마 상태 확인
    org_table_exists = check_current_schema()
    
    if org_table_exists:
        print("✅ OrganizationStructure 테이블이 이미 존재합니다.")
        print("🎉 스키마 업데이트가 이미 완료된 것 같습니다.")
    else:
        print("⚠️ OrganizationStructure 테이블이 없습니다. 마이그레이션 필요.")
        
        # 2. 마이그레이션 적용
        if not apply_migration_safely():
            print("❌ 마이그레이션 실패. 중단합니다.")
            return False
    
    # 3. 새 모델 검증
    if not verify_new_models():
        print("❌ 모델 검증 실패. 중단합니다.")
        return False
    
    # 4. 샘플 조직 생성
    if not create_sample_organization():
        print("⚠️ 샘플 조직 생성 실패. 계속 진행합니다.")
    
    # 5. URL 확인
    if not verify_urls():
        print("⚠️ URL 확인 실패. 계속 진행합니다.")
    
    print("\n" + "=" * 60)
    print("🎉 스키마 업데이트 완료!")
    print("📱 웹사이트: https://ehrv10-production.up.railway.app")
    print("🏗️ 조직 관리: /employees/organization/structure/")
    print("✏️ 조직 입력: /employees/organization/input/")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    main()