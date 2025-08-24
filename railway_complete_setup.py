#!/usr/bin/env python
"""
Railway 완전한 설정 - 모든 테이블 생성 및 데이터 설정
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 완전 설정")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection

def create_all_tables():
    """모든 필수 테이블 생성"""
    print("1. 모든 테이블 생성")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 1. OrganizationStructure (이미 생성됨)
        print("OrganizationStructure 테이블 확인...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'employees_organizationstructure'
            );
        """)
        if cursor.fetchone()[0]:
            print("[OK] employees_organizationstructure 존재")
        
        # 2. OrganizationUploadHistory
        print("\nOrganizationUploadHistory 테이블 생성...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_organizationuploadhistory (
                id SERIAL PRIMARY KEY,
                uploaded_by_id INTEGER REFERENCES auth_user(id),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_name VARCHAR(255),
                total_records INTEGER DEFAULT 0,
                success_records INTEGER DEFAULT 0,
                failed_records INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                error_message TEXT
            );
        """)
        print("[OK] employees_organizationuploadhistory 생성")
        
        # 3. EmployeeOrganizationMapping
        print("\nEmployeeOrganizationMapping 테이블 생성...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_employeeorganizationmapping (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees_employee(id),
                organization_id INTEGER REFERENCES employees_organizationstructure(id),
                is_primary BOOLEAN DEFAULT FALSE,
                assigned_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(employee_id, organization_id)
            );
        """)
        print("[OK] employees_employeeorganizationmapping 생성")
        
        # 테이블 목록 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'employees_%'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n현재 employees 테이블 ({len(tables)}개):")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} 레코드")

def complete_organization_data():
    """완전한 조직 데이터 생성"""
    print("\n2. 완전한 5단계 조직 구조 생성")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 현재 데이터 확인
        cursor.execute("SELECT org_code, org_name, org_level FROM employees_organizationstructure ORDER BY org_level")
        existing = cursor.fetchall()
        
        if existing:
            print(f"현재 {len(existing)}개 조직 존재:")
            for org in existing:
                print(f"  레벨{org[2]}: {org[0]} - {org[1]}")
        
        # 부족한 레벨 추가
        # 부서 레벨 (4)
        cursor.execute("""
            SELECT id FROM employees_organizationstructure 
            WHERE org_code = 'HQ001'
        """)
        hq_result = cursor.fetchone()
        
        if hq_result:
            hq_id = hq_result[0]
            
            # 부서 추가
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                VALUES 
                ('DEPT001', 'IT개발부', 4, %s, 'active', 1, 'IT개발부', 
                 'OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부')
                ON CONFLICT (org_code) DO NOTHING
                RETURNING id;
            """, [hq_id])
            dept_result = cursor.fetchone()
            
            if dept_result:
                dept_id = dept_result[0]
                print(f"[OK] IT개발부 생성 (ID: {dept_id})")
                
                # 팀 추가
                cursor.execute("""
                    INSERT INTO employees_organizationstructure 
                    (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                    VALUES 
                    ('TEAM001', '개발1팀', 5, %s, 'active', 1, '개발1팀', 
                     'OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부 > 개발1팀'),
                    ('TEAM002', '개발2팀', 5, %s, 'active', 2, '개발2팀', 
                     'OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부 > 개발2팀')
                    ON CONFLICT (org_code) DO NOTHING;
                """, [dept_id, dept_id])
                print("[OK] 개발1팀, 개발2팀 생성")
            else:
                print("[INFO] DEPT001이 이미 존재함")
        
        # 최종 확인
        cursor.execute("""
            SELECT org_level, COUNT(*) 
            FROM employees_organizationstructure 
            GROUP BY org_level 
            ORDER BY org_level;
        """)
        level_counts = cursor.fetchall()
        
        print("\n최종 조직 구조:")
        level_names = {1: '그룹', 2: '계열사', 3: '본부', 4: '부서', 5: '팀'}
        for level, count in level_counts:
            print(f"  레벨{level} ({level_names.get(level, '기타')}): {count}개")

def test_final_api():
    """최종 API 테스트"""
    print("\n3. 최종 API 테스트")
    print("-" * 40)
    
    import json
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    
    factory = RequestFactory()
    
    # Admin 사용자 확인/생성
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created or not admin_user.check_password('admin123'):
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"[OK] Admin 사용자 준비")
    
    # 1. Stats API
    print("\nStats API 테스트:")
    try:
        from employees.views import get_organization_stats
        
        request = factory.get('/api/organization-stats/')
        request.user = admin_user
        
        response = get_organization_stats(request)
        print(f"  응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  [SUCCESS] API 정상 작동")
            print(f"    - 전체 조직: {data.get('total_orgs')}")
            print(f"    - 활성 조직: {data.get('active_orgs')}")
            print(f"    - 전체 직원: {data.get('total_employees')}")
            print(f"    - 최종 업데이트: {data.get('last_update')}")
        else:
            print(f"  [ERROR] {response.content.decode('utf-8')[:200]}")
    except Exception as e:
        print(f"  [ERROR] {str(e)[:200]}")
    
    # 2. Upload API
    print("\nUpload API 테스트:")
    try:
        from employees.views import upload_organization_structure
        
        test_data = {
            'data': [{
                '조직코드': 'TEAM999',
                '조직명': '테스트팀',
                '조직레벨': 5,
                '상위조직코드': 'DEPT001',
                '상태': 'active',
                '정렬순서': 999,
                '설명': '테스트팀'
            }]
        }
        
        request = factory.post(
            '/api/upload-organization-structure/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        request.user = admin_user
        request._dont_enforce_csrf_checks = True
        
        response = upload_organization_structure(request)
        print(f"  응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  [SUCCESS] Upload API 정상 작동")
            print(f"    - 성공: {data.get('success')}")
            print(f"    - 생성: {data.get('created')}")
            print(f"    - 업데이트: {data.get('updated')}")
        else:
            print(f"  [ERROR] {response.content.decode('utf-8')[:200]}")
    except Exception as e:
        print(f"  [ERROR] {str(e)[:200]}")

def main():
    """메인 실행"""
    
    # 1. 모든 테이블 생성
    create_all_tables()
    
    # 2. 완전한 조직 데이터
    complete_organization_data()
    
    # 3. API 테스트
    test_final_api()
    
    print("\n" + "="*60)
    print("✅ 완전 설정 완료!")
    print("="*60)
    print("\n최종 단계:")
    print("1. railway restart")
    print("2. 약 30초 대기")
    print("3. 브라우저에서 조직 구조 업로드 테스트")
    print("\n접속 URL:")
    print("https://[your-app].up.railway.app/employees/organization-structure/")

if __name__ == "__main__":
    main()