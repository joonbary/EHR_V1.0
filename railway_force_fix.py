#!/usr/bin/env python
"""
Railway 강제 수정 - 모든 알려진 문제 해결
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 강제 수정 시작")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection
from django.core.management import call_command

def step1_force_migrate():
    """강제 마이그레이션"""
    print("Step 1: 강제 마이그레이션")
    print("-" * 40)
    
    try:
        # 1. migrate --run-syncdb
        print("Executing: migrate --run-syncdb")
        call_command('migrate', '--run-syncdb', verbosity=2)
        print("[OK] migrate --run-syncdb 완료")
    except Exception as e:
        print(f"[WARNING] migrate --run-syncdb: {e}")
    
    try:
        # 2. 개별 앱 마이그레이션
        print("\nExecuting: migrate employees")
        call_command('migrate', 'employees', verbosity=2)
        print("[OK] migrate employees 완료")
    except Exception as e:
        print(f"[WARNING] migrate employees: {e}")
    
    return True

def step2_verify_tables():
    """테이블 검증"""
    print("\nStep 2: 테이블 검증")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 테이블 목록
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'employees_%'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"테이블 ({len(tables)}개):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} 레코드")
        
        # 필수 테이블 체크
        required = [
            'employees_employee',
            'employees_organizationstructure',
            'employees_organizationuploadhistory',
            'employees_employeeorganizationmapping'
        ]
        
        table_names = [t[0] for t in tables]
        missing = [r for r in required if r not in table_names]
        
        if missing:
            print(f"\n[ERROR] 누락된 테이블: {missing}")
            return False
        else:
            print("\n[OK] 모든 필수 테이블 존재")
            return True

def step3_fix_employee_fields():
    """Employee 모델 필드 수정"""
    print("\nStep 3: Employee 필드 수정")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # employment_status 필드 확인
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee'
            AND column_name = 'employment_status';
        """)
        
        if not cursor.fetchone():
            print("employment_status 필드 추가 중...")
            try:
                cursor.execute("""
                    ALTER TABLE employees_employee 
                    ADD COLUMN IF NOT EXISTS employment_status VARCHAR(20) DEFAULT '재직';
                """)
                print("[OK] employment_status 필드 추가")
            except Exception as e:
                print(f"[INFO] employment_status: {e}")
        else:
            print("[OK] employment_status 필드 존재")
        
        # 기본값 설정
        cursor.execute("""
            UPDATE employees_employee 
            SET employment_status = '재직' 
            WHERE employment_status IS NULL;
        """)
        print("[OK] employment_status 기본값 설정")

def step4_create_test_data():
    """테스트 데이터 생성"""
    print("\nStep 4: 테스트 데이터 생성")
    print("-" * 40)
    
    from employees.models_organization import OrganizationStructure
    from employees.models import Employee
    from django.contrib.auth.models import User
    
    # 1. 조직 데이터
    print("조직 데이터 생성...")
    orgs_created = []
    
    # 그룹
    grp, created = OrganizationStructure.objects.get_or_create(
        org_code='GRP001',
        defaults={
            'org_name': 'OK금융그룹',
            'org_level': 1,
            'status': 'active',
            'sort_order': 1,
            'description': 'OK금융그룹'
        }
    )
    if created:
        orgs_created.append(grp.org_name)
    
    # 계열사
    com, created = OrganizationStructure.objects.get_or_create(
        org_code='COM001',
        defaults={
            'org_name': 'OK저축은행',
            'org_level': 2,
            'parent': grp,
            'status': 'active',
            'sort_order': 1,
            'description': 'OK저축은행'
        }
    )
    if created:
        orgs_created.append(com.org_name)
    
    # 본부
    hq, created = OrganizationStructure.objects.get_or_create(
        org_code='HQ001',
        defaults={
            'org_name': '리테일본부',
            'org_level': 3,
            'parent': com,
            'status': 'active',
            'sort_order': 1,
            'description': '리테일본부'
        }
    )
    if created:
        orgs_created.append(hq.org_name)
    
    # 부서
    dept, created = OrganizationStructure.objects.get_or_create(
        org_code='DEPT001',
        defaults={
            'org_name': 'IT개발부',
            'org_level': 4,
            'parent': hq,
            'status': 'active',
            'sort_order': 1,
            'description': 'IT개발부'
        }
    )
    if created:
        orgs_created.append(dept.org_name)
    
    # 팀
    team, created = OrganizationStructure.objects.get_or_create(
        org_code='TEAM001',
        defaults={
            'org_name': '개발1팀',
            'org_level': 5,
            'parent': dept,
            'status': 'active',
            'sort_order': 1,
            'description': '개발1팀'
        }
    )
    if created:
        orgs_created.append(team.org_name)
    
    if orgs_created:
        print(f"[OK] {len(orgs_created)}개 조직 생성")
        for org in orgs_created:
            print(f"  - {org}")
    else:
        print("[INFO] 조직이 이미 존재합니다")
    
    # 2. 직원 데이터
    print("\n직원 데이터 확인...")
    if Employee.objects.count() == 0:
        # Admin 사용자
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if not admin_user.check_password('admin123'):
            admin_user.set_password('admin123')
            admin_user.save()
        
        # 테스트 직원
        emp, created = Employee.objects.get_or_create(
            employee_id='EMP001',
            defaults={
                'user': admin_user,
                'name': '홍길동',
                'email': 'hong@example.com',
                'department': 'IT개발부',
                'position': '과장',
                'employment_status': '재직'
            }
        )
        if created:
            print(f"[OK] 테스트 직원 생성: {emp.name}")
    else:
        print(f"[INFO] {Employee.objects.count()}명의 직원 존재")
    
    return True

def step5_test_apis():
    """API 테스트"""
    print("\nStep 5: API 최종 테스트")
    print("-" * 40)
    
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    import json
    
    factory = RequestFactory()
    
    # Admin 사용자
    try:
        user = User.objects.get(username='admin')
    except:
        user = None
    
    # 1. Stats API
    print("Stats API 테스트:")
    try:
        from employees.views import get_organization_stats
        request = factory.get('/api/organization-stats/')
        if user:
            request.user = user
        
        response = get_organization_stats(request)
        print(f"  응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  [OK] 조직: {data.get('total_orgs')}, 직원: {data.get('total_employees')}")
        else:
            print(f"  [ERROR] {response.content.decode('utf-8')[:100]}")
    except Exception as e:
        print(f"  [ERROR] {str(e)[:100]}")
    
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
                '설명': '테스트'
            }]
        }
        
        request = factory.post(
            '/api/upload-organization-structure/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        if user:
            request.user = user
        request._dont_enforce_csrf_checks = True
        
        response = upload_organization_structure(request)
        print(f"  응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  [OK] 생성: {data.get('created')}, 업데이트: {data.get('updated')}")
        else:
            print(f"  [ERROR] {response.content.decode('utf-8')[:100]}")
    except Exception as e:
        print(f"  [ERROR] {str(e)[:100]}")
    
    return True

def main():
    """메인 실행"""
    
    print("\n시작: Railway 강제 수정\n")
    
    # Step 1: 마이그레이션
    step1_force_migrate()
    
    # Step 2: 테이블 검증
    if not step2_verify_tables():
        print("\n[CRITICAL] 테이블 생성 실패. 수동 개입 필요.")
        return False
    
    # Step 3: Employee 필드 수정
    step3_fix_employee_fields()
    
    # Step 4: 테스트 데이터
    step4_create_test_data()
    
    # Step 5: API 테스트
    step5_test_apis()
    
    print("\n" + "="*60)
    print("강제 수정 완료!")
    print("="*60)
    print("\n최종 단계:")
    print("1. railway restart")
    print("2. 브라우저에서 테스트")
    print("\n문제 지속 시:")
    print("1. railway logs --tail 200")
    print("2. Railway 콘솔에서 데이터베이스 직접 확인")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)