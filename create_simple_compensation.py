"""
간단한 보상 데이터 생성 스크립트
"""
import os
import sys
import django
import random
from decimal import Decimal
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from compensation.models import EmployeeCompensation

def create_compensation_data():
    """기존 직원에 대한 보상 데이터 생성"""
    
    # 기존 보상 데이터 삭제
    EmployeeCompensation.objects.all().delete()
    
    # 모든 직원 ID만 가져오기
    employee_ids = Employee.objects.values_list('id', flat=True)[:100]  # 처음 100명만
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    created_count = 0
    
    for emp_id in employee_ids:
        try:
            # Employee 객체 가져오기 (특정 필드만)
            employee = Employee.objects.only('id', 'name', 'position').get(id=emp_id)
            
            # 직급별 연봉 설정
            position = employee.position if hasattr(employee, 'position') else '사원'
            
            # 연봉 범위 (단위: 원)
            salary_ranges = {
                '사원': (50000000, 60000000),
                '대리': (55000000, 70000000),
                '차장': (65000000, 85000000),
                '부장': (70000000, 90000000),
                '팀장': (95000000, 130000000),
                '이사': (120000000, 180000000),
                '상무': (150000000, 250000000),
                '전무': (170000000, 300000000),
                '부사장': (200000000, 500000000),
            }
            
            # 직급 매칭
            annual_salary = 60000000  # 기본값
            for key, (min_sal, max_sal) in salary_ranges.items():
                if key in position:
                    annual_salary = random.randint(min_sal, max_sal)
                    break
            
            # 월 급여 계산
            monthly_salary = annual_salary / 12
            
            # 기본급 (월급여의 60%)
            base_salary = Decimal(str(monthly_salary * 0.6))
            
            # 역량급 (월급여의 20%)
            competency_pay = Decimal(str(monthly_salary * 0.2))
            
            # 직책급 (직책이 있는 경우)
            position_allowance = None
            executive_positions = {
                '팀장': 2000000,
                '이사': 4000000,
                '상무': 5000000,
                '전무': 6000000,
                '부사장': 8000000,
            }
            
            for exec_pos, allowance in executive_positions.items():
                if exec_pos in position:
                    position_allowance = Decimal(str(allowance))
                    break
            
            # 보상 데이터 생성
            compensation = EmployeeCompensation(
                employee=employee,
                year=current_year,
                month=current_month,
                base_salary=base_salary,
                competency_pay=competency_pay,
                position_allowance=position_allowance,
                fixed_overtime=Decimal('0'),  # 임시로 0 설정
                pi_amount=Decimal('0'),  # 임시로 0 설정
                total_compensation=base_salary + competency_pay + (position_allowance or Decimal('0'))
            )
            
            compensation.save()
            created_count += 1
            
        except Exception as e:
            print(f"Error creating compensation for employee: {e}")
            continue
    
    print(f"Successfully created {created_count} compensation records")

if __name__ == '__main__':
    create_compensation_data()