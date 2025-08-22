#!/usr/bin/env python
"""
Railway 테이블에 누락된 컬럼 추가
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 테이블 컬럼 추가")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection

def add_missing_columns():
    """누락된 컬럼 추가"""
    print("누락된 컬럼 추가 중...")
    
    with connection.cursor() as cursor:
        # 1. full_path 컬럼 추가
        try:
            cursor.execute("""
                ALTER TABLE employees_organizationstructure 
                ADD COLUMN IF NOT EXISTS full_path VARCHAR(500);
            """)
            print("[OK] full_path 컬럼 추가")
        except Exception as e:
            print(f"[INFO] full_path: {e}")
        
        # 2. level_name 컬럼 추가
        try:
            cursor.execute("""
                ALTER TABLE employees_organizationstructure 
                ADD COLUMN IF NOT EXISTS level_name VARCHAR(50);
            """)
            print("[OK] level_name 컬럼 추가")
        except Exception as e:
            print(f"[INFO] level_name: {e}")
        
        # 3. employee_count 컬럼 추가
        try:
            cursor.execute("""
                ALTER TABLE employees_organizationstructure 
                ADD COLUMN IF NOT EXISTS employee_count INTEGER DEFAULT 0;
            """)
            print("[OK] employee_count 컬럼 추가")
        except Exception as e:
            print(f"[INFO] employee_count: {e}")
        
        # 4. is_active 컬럼 추가
        try:
            cursor.execute("""
                ALTER TABLE employees_organizationstructure 
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
            """)
            print("[OK] is_active 컬럼 추가")
        except Exception as e:
            print(f"[INFO] is_active: {e}")
        
        # 5. 현재 컬럼 확인
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'employees_organizationstructure'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        
        print(f"\n현재 컬럼 목록 ({len(columns)}개):")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")

def create_initial_data():
    """초기 데이터 생성"""
    print("\n초기 데이터 생성 시도...")
    
    try:
        from employees.models_organization import OrganizationStructure
        
        # 기존 데이터 확인
        existing = OrganizationStructure.objects.count()
        if existing > 0:
            print(f"[INFO] 이미 {existing}개의 조직 존재")
            
            # full_path 업데이트
            for org in OrganizationStructure.objects.all():
                if not org.full_path:
                    if org.parent:
                        org.full_path = f"{org.parent.org_name} > {org.org_name}"
                    else:
                        org.full_path = org.org_name
                    org.save()
                    print(f"  [UPDATE] {org.org_name} full_path 설정")
            
            return True
        
        # 새 데이터 생성
        print("새 조직 데이터 생성...")
        
        # 그룹
        group = OrganizationStructure.objects.create(
            org_code='GRP001',
            org_name='OK금융그룹',
            org_level=1,
            status='active',
            sort_order=1,
            description='OK금융그룹 지주회사',
            full_path='OK금융그룹',
            level_name='그룹',
            employee_count=0,
            is_active=True
        )
        print(f"[OK] {group.org_name} 생성")
        
        # 계열사
        company = OrganizationStructure.objects.create(
            org_code='COM001',
            org_name='OK저축은행',
            org_level=2,
            parent=group,
            status='active',
            sort_order=1,
            description='OK저축은행',
            full_path='OK금융그룹 > OK저축은행',
            level_name='계열사',
            employee_count=0,
            is_active=True
        )
        print(f"[OK] {company.org_name} 생성")
        
        # 본부
        hq = OrganizationStructure.objects.create(
            org_code='HQ001',
            org_name='리테일본부',
            org_level=3,
            parent=company,
            status='active',
            sort_order=1,
            description='리테일 금융 서비스 본부',
            full_path='OK금융그룹 > OK저축은행 > 리테일본부',
            level_name='본부',
            employee_count=0,
            is_active=True
        )
        print(f"[OK] {hq.org_name} 생성")
        
        print("\n[SUCCESS] 초기 데이터 생성 완료")
        return True
        
    except Exception as e:
        print(f"[WARNING] 초기 데이터 생성 실패: {e}")
        
        # 직접 SQL로 삽입
        print("\nSQL로 직접 삽입 시도...")
        with connection.cursor() as cursor:
            try:
                # 기존 데이터 확인
                cursor.execute("SELECT COUNT(*) FROM employees_organizationstructure")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    # 그룹 삽입
                    cursor.execute("""
                        INSERT INTO employees_organizationstructure 
                        (org_code, org_name, org_level, parent_id, status, sort_order, 
                         description, full_path, level_name, employee_count, is_active)
                        VALUES 
                        ('GRP001', 'OK금융그룹', 1, NULL, 'active', 1, 
                         'OK금융그룹 지주회사', 'OK금융그룹', '그룹', 0, TRUE)
                        ON CONFLICT (org_code) DO NOTHING
                        RETURNING id;
                    """)
                    group_id = cursor.fetchone()
                    if group_id:
                        print(f"[OK] OK금융그룹 생성 (ID: {group_id[0]})")
                        
                        # 계열사 삽입
                        cursor.execute("""
                            INSERT INTO employees_organizationstructure 
                            (org_code, org_name, org_level, parent_id, status, sort_order, 
                             description, full_path, level_name, employee_count, is_active)
                            VALUES 
                            ('COM001', 'OK저축은행', 2, %s, 'active', 1, 
                             'OK저축은행', 'OK금융그룹 > OK저축은행', '계열사', 0, TRUE)
                            ON CONFLICT (org_code) DO NOTHING;
                        """, [group_id[0]])
                        print("[OK] OK저축은행 생성")
                    
                    print("\n[SUCCESS] SQL 직접 삽입 완료")
                else:
                    print(f"[INFO] 이미 {count}개의 조직 존재")
                    
            except Exception as e2:
                print(f"[ERROR] SQL 삽입 실패: {e2}")
                return False
        
        return True

def test_api():
    """API 테스트"""
    print("\nAPI 테스트...")
    
    try:
        from django.test import RequestFactory
        from employees.views import get_organization_stats
        
        factory = RequestFactory()
        request = factory.get('/api/organization-stats/')
        
        response = get_organization_stats(request)
        print(f"[TEST] organization-stats API: {response.status_code}")
        
        if response.status_code == 200:
            import json
            data = json.loads(response.content)
            print(f"  - 전체 조직: {data.get('total_orgs', 0)}개")
            print(f"  - 활성 조직: {data.get('active_orgs', 0)}개")
            print("[SUCCESS] API 정상 작동!")
            return True
        else:
            print("[WARNING] API 응답 이상")
            return False
            
    except Exception as e:
        print(f"[ERROR] API 테스트 실패: {e}")
        return False

def main():
    """메인 실행"""
    
    # 1. 컬럼 추가
    add_missing_columns()
    
    # 2. 초기 데이터 생성
    create_initial_data()
    
    # 3. API 테스트
    test_api()
    
    print("\n" + "="*60)
    print("완료! 다음 명령 실행:")
    print("="*60)
    print("1. railway restart")
    print("2. 브라우저에서 조직 구조 업로드 테스트")

if __name__ == "__main__":
    main()