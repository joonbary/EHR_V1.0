"""
기존 직원에 대한 보상 데이터만 생성하는 스크립트
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
    
    print("보상 데이터 생성 시작...")
    
    # 기존 보상 데이터 삭제
    EmployeeCompensation.objects.all().delete()
    
    # 모든 직원 가져오기
    employees = Employee.objects.all()
    total_employees = employees.count()
    print(f"총 {total_employees}명의 직원에 대한 보상 데이터 생성 중...")
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    created_count = 0
    
    for i, employee in enumerate(employees):
        if i % 100 == 0:
            print(f"진행중... {i}/{total_employees}")
        
        try:
            # 직급별 연봉 설정
            position = employee.position if hasattr(employee, 'position') else '사원'
            job_group = employee.job_group if hasattr(employee, 'job_group') else 'Non-PL'
            
            # PL직군 체크
            if job_group == 'PL' or 'PL' in str(position):
                # PL직군: 2,400만원 ~ 6,000만원
                annual_salary = random.randint(24000000, 60000000)
            else:
                # Non-PL직군 연봉 범위 (단위: 원)
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
                    if key in str(position):
                        annual_salary = random.randint(min_sal, max_sal)
                        break
            
            # 월 급여 계산
            monthly_salary = annual_salary / 12
            
            # 기본급 (월급여의 60%)
            base_salary = Decimal(str(int(monthly_salary * 0.6)))
            
            # 역량급 (월급여의 20%)
            competency_pay = Decimal(str(int(monthly_salary * 0.2)))
            
            # 고정OT (기본급의 약 15%)
            fixed_overtime = Decimal(str(int(float(base_salary) * 0.15)))
            
            # 직책급 (직책이 있는 경우)
            position_allowance = Decimal('0')
            executive_positions = {
                '팀장': 2000000,
                '부장(직책)': 3000000,
                '이사': 4000000,
                '상무': 5000000,
                '전무': 6000000,
                '부사장': 8000000,
            }
            
            for exec_pos, allowance in executive_positions.items():
                if exec_pos in str(position):
                    position_allowance = Decimal(str(allowance))
                    break
            
            # 성과급 (기본급의 10~30%)
            pi_amount = Decimal(str(int(float(base_salary) * random.uniform(0.1, 0.3) / 12)))
            
            # 총 보상 계산
            total_compensation = base_salary + competency_pay + fixed_overtime + position_allowance + pi_amount
            
            # 보상 데이터 생성
            compensation = EmployeeCompensation(
                employee=employee,
                year=current_year,
                month=current_month,
                base_salary=base_salary,
                competency_pay=competency_pay,
                position_allowance=position_allowance if position_allowance > 0 else None,
                fixed_overtime=fixed_overtime,
                pi_amount=pi_amount,
                total_compensation=total_compensation
            )
            
            compensation.save()
            created_count += 1
            
        except Exception as e:
            print(f"Error creating compensation for employee {employee.id}: {e}")
            continue
    
    print(f"Successfully created {created_count} compensation records")

if __name__ == '__main__':
    create_compensation_data()