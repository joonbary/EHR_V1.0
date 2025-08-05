"""
Railway 프로덕션 환경용 샘플 직원 데이터 생성 스크립트
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from employees.models import Employee
from django.contrib.auth.models import User
from datetime import date, timedelta
import random

def create_sample_employees():
    """샘플 직원 데이터 생성"""
    
    # 기존 데이터 확인
    existing_count = Employee.objects.count()
    print(f"현재 직원 수: {existing_count}명")
    
    if existing_count > 100:
        print("이미 충분한 데이터가 있습니다.")
        return
    
    # 부서 및 직급 옵션
    departments = ['IT', 'HR', 'FINANCE', 'MARKETING', 'SALES', 'OPERATIONS']
    positions = ['INTERN', 'STAFF', 'SENIOR', 'MANAGER', 'DIRECTOR']
    
    # 샘플 직원 생성
    created_count = 0
    for i in range(1, 101):  # 100명 생성
        email = f"employee{i:03d}@okgroup.com"
        
        # 이메일 중복 체크
        if Employee.objects.filter(email=email).exists():
            print(f"이미 존재하는 이메일: {email}")
            continue
        
        try:
            employee = Employee.objects.create(
                name=f"직원{i:03d}",
                email=email,
                department=random.choice(departments),
                position=random.choice(positions),
                hire_date=date.today() - timedelta(days=random.randint(30, 1825)),
                phone=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                employment_status='재직',
                growth_level=random.randint(1, 5),
                address=f"서울시 강남구 테헤란로 {i}번지",
                emergency_contact=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                emergency_relationship='가족'
            )
            created_count += 1
            print(f"✓ 생성됨: {employee.name} ({employee.email})")
            
        except Exception as e:
            print(f"✗ 생성 실패: {email} - {str(e)}")
    
    print(f"\n총 {created_count}명의 직원이 생성되었습니다.")
    print(f"현재 총 직원 수: {Employee.objects.count()}명")

if __name__ == "__main__":
    create_sample_employees()