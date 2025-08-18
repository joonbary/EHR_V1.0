#!/usr/bin/env python
"""
테스트 데이터 생성 스크립트
JSON 로드 실패 시 사용할 충분한 테스트 데이터 생성
"""
import os
import sys
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def create_test_employees():
    """테스트 직원 데이터 생성"""
    from employees.models import Employee
    
    print("=" * 60)
    print("CREATING TEST EMPLOYEE DATA")
    print("=" * 60)
    
    # 부서 리스트
    departments = ['IT', 'HR', 'FINANCE', 'MARKETING', 'SALES', 'OPERATIONS']
    
    # 직종 리스트
    job_types = {
        'IT': ['IT기획', 'IT개발', 'IT운영'],
        'HR': ['경영관리'],
        'FINANCE': ['경영관리'],
        'MARKETING': ['경영관리'],
        'SALES': ['기업영업', '기업금융'],
        'OPERATIONS': ['경영관리']
    }
    
    # 직책 리스트
    positions = [
        ('사원', 1, 1),
        ('선임', 2, 2),
        ('주임', 2, 3),
        ('대리', 3, 4),
        ('과장', 4, 5),
        ('차장', 5, 6),
        ('부장', 6, 7),
    ]
    
    created_count = 0
    
    # 각 부서별로 직원 생성
    for dept in departments:
        dept_job_types = job_types[dept]
        
        # 부서별로 10-15명 생성
        for i in range(random.randint(10, 15)):
            try:
                # 랜덤 직책 선택
                position_data = random.choice(positions)
                position_name = position_data[0]
                growth_level = position_data[1]
                grade_level = position_data[2]
                
                # 이메일 생성
                email = f"test_{dept.lower()}_{i+1}@okgroup.com"
                
                # 중복 체크
                if Employee.objects.filter(email=email).exists():
                    continue
                
                # 입사일 랜덤 생성 (최근 5년 이내)
                days_ago = random.randint(0, 365 * 5)
                hire_date = date.today() - timedelta(days=days_ago)
                
                # 직원 생성
                emp = Employee.objects.create(
                    name=f"{dept} {position_name} {i+1}",
                    email=email,
                    department=dept,
                    position='STAFF' if growth_level <= 3 else 'MANAGER',
                    new_position=position_name,
                    job_group='Non-PL',
                    job_type=random.choice(dept_job_types),
                    job_role=f"{dept} 업무",
                    employment_status='재직',
                    employment_type='정규직',
                    hire_date=hire_date,
                    phone=f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                    growth_level=growth_level,
                    grade_level=grade_level
                )
                created_count += 1
                
                if created_count % 10 == 0:
                    print(f"  Created {created_count} employees...")
                    
            except Exception as e:
                print(f"  Error creating employee: {e}")
                continue
    
    # 관리자 관계 설정 (선택사항)
    try:
        print("\nSetting up manager relationships...")
        managers = Employee.objects.filter(growth_level__gte=4)
        subordinates = Employee.objects.filter(growth_level__lt=4)
        
        for sub in subordinates[:20]:  # 처음 20명만
            if managers.exists():
                manager = random.choice(managers)
                sub.manager = manager
                sub.save()
    except:
        pass
    
    # 최종 통계
    total = Employee.objects.count()
    print(f"\n✓ Created {created_count} new employees")
    print(f"✓ Total employees in database: {total}")
    
    # 샘플 출력
    print("\nSample employees:")
    for emp in Employee.objects.all()[:5]:
        print(f"  - {emp.name} ({emp.department}/{emp.new_position})")
    
    return created_count

if __name__ == "__main__":
    try:
        count = create_test_employees()
        print("\n" + "=" * 60)
        print(f"TEST DATA CREATION COMPLETE: {count} employees created")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()