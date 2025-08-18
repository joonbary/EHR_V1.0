#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal
import re

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation, ContributionEvaluation, ExpertiseEvaluation, ImpactEvaluation
from compensation.models import EmployeeCompensation
from promotions.models import PromotionRequest
from permissions.models import Permission, HRRole, EmployeeRole

# employee_id 필드 사용 제거 및 대체
with open('create_full_test_data.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. 직원 생성 시 employee_id 인자 제거
code = re.sub(r"employee_id\s*=\s*f?['\"]?EMP\{?i\+1:?0?4?d?\}?['\"]?,?\s*", "", code)

# 2. emp.id → emp.id (혹은 emp.name)
code = re.sub(r"emp\.employee_id", "emp.id", code)

# 3. Employee.objects.create\(([^)]*)\) 내 employee_id=... 제거
code = re.sub(r"(Employee\.objects\.create\([^)]*)employee_id\s*=\s*[^,]+,?\s*", r"\1", code)

with open('create_full_test_data.py', 'w', encoding='utf-8') as f:
    f.write(code)


def create_test_data():
    print("대규모 테스트 데이터 생성을 시작합니다...")
    
    # 기존 데이터 확인
    employee_count = Employee.objects.count()
    print(f"현재 직원 수: {employee_count}")
    
    if employee_count >= 100:
        print("이미 충분한 테스트 데이터가 존재합니다.")
        return
    
    # 부서
    departments = ['IT', 'HR', 'FINANCE', 'MARKETING', 'SALES', 'OPERATIONS']
    
    # 직책
    positions = ['INTERN', 'STAFF', 'SENIOR', 'MANAGER', 'DIRECTOR', 'EXECUTIVE']
    
    # 성장 레벨
    growth_levels = [1, 2, 3, 4, 5, 6]
    
    # 직종
    job_types = ['IT기획', 'IT개발', 'IT운영', '경영관리', '기업영업', '기업금융', '리테일금융', '투자금융', '고객지원']
    
    # 성별
    genders = ['남성', '여성']
    
    # 이름 샘플
    first_names = [
        '김', '이', '박', '최', '정', '강', '조', '윤', '장', '임',
        '한', '오', '서', '신', '권', '황', '안', '송', '류', '전'
    ]
    
    last_names = [
        '민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호', '지후', '준서',
        '준우', '현우', '도현', '지훈', '우진', '민재', '건우', '서진', '현준', '도훈',
        '지원', '재원', '재민', '재현', '재준', '재호', '재후', '재우', '재훈', '재원',
        '서연', '지우', '서현', '민서', '지민', '예은', '하은', '지은', '예원', '하린',
        '지원', '서영', '민지', '예진', '하영', '지영', '예지', '하진', '지현', '서진'
    ]
    
    # 직원 생성
    employees_created = 0
    for i in range(100 - employee_count):
        try:
            # 사용자 계정 생성
            username = f"employee{i+1:03d}"
            email = f"{username}@okfinance.com"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': random.choice(first_names),
                    'last_name': random.choice(last_names),
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            
            if not created:
                continue
                
            # 직원 정보 생성
            employee = Employee.objects.create(
                user=user,
                name=f"{user.last_name}{user.first_name}",
                department=random.choice(departments),
                position=random.choice(positions),
                growth_level=random.choice(growth_levels),
                job_type=random.choice(job_types),
                hire_date=datetime.now() - timedelta(days=random.randint(365, 3650)),
                phone=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                email=email,
                address=f"서울시 강남구 테헤란로 {random.randint(1, 999)}",
                emergency_contact=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                emergency_phone=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            )
            
            employees_created += 1
            
            # 평가 데이터 생성
            for year in range(2022, 2025):
                # 종합 평가
                comp_eval = ComprehensiveEvaluation.objects.create(
                    employee=employee,
                    year=year,
                    contribution_score=random.randint(70, 100),
                    expertise_score=random.randint(70, 100),
                    impact_score=random.randint(70, 100),
                    final_grade=random.choice(['S', 'A+', 'A', 'B+', 'B', 'C']),
                    evaluation_date=datetime(year, 12, 31),
                    evaluator=User.objects.filter(is_staff=True).first() or user
                )
                
                # 기여도 평가
                ContributionEvaluation.objects.create(
                    employee=employee,
                    year=year,
                    score=comp_eval.contribution_score,
                    comments=f"{year}년 기여도 평가 코멘트",
                    evaluator=User.objects.filter(is_staff=True).first() or user
                )
                
                # 전문성 평가
                ExpertiseEvaluation.objects.create(
                    employee=employee,
                    year=year,
                    score=comp_eval.expertise_score,
                    comments=f"{year}년 전문성 평가 코멘트",
                    evaluator=User.objects.filter(is_staff=True).first() or user
                )
                
                # 영향력 평가
                ImpactEvaluation.objects.create(
                    employee=employee,
                    year=year,
                    score=comp_eval.impact_score,
                    comments=f"{year}년 영향력 평가 코멘트",
                    evaluator=User.objects.filter(is_staff=True).first() or user
                )
            
            # 보상 데이터 생성
            base_salary = random.randint(30000000, 80000000)
            competency_pay = random.randint(5000000, 20000000)
            position_allowance = random.randint(0, 10000000)
            pi_amount = random.randint(0, 50000000)
            
            EmployeeCompensation.objects.create(
                employee=employee,
                year=2024,
                base_salary=base_salary,
                competency_pay=competency_pay,
                position_allowance=position_allowance,
                pi_amount=pi_amount,
                total_compensation=base_salary + competency_pay + position_allowance + pi_amount
            )
            
            # 승진 요청 생성 (일부 직원만)
            if random.random() < 0.3:  # 30% 확률
                current_level = employee.growth_level
                level_mapping = {
                    1: 2,
                    2: 3, 
                    3: 4,
                    4: 5,
                    5: 6,
                    6: 6
                }
                target_level = level_mapping.get(current_level, current_level)
                
                if target_level != current_level:
                    PromotionRequest.objects.create(
                        employee=employee,
                        current_level=current_level,
                        target_level=target_level,
                        years_of_service=random.randint(1, 10),
                        consecutive_a_grades=random.randint(0, 3),
                        average_performance_score=random.randint(70, 100),
                        status=random.choice(['PENDING', 'APPROVED', 'REJECTED']),
                        request_date=datetime.now() - timedelta(days=random.randint(1, 365))
                    )
                    
        except Exception as e:
            print(f"직원 {i+1} 생성 중 오류: {e}")
            continue
    
    print(f"총 {employees_created}명의 직원과 관련 데이터가 생성되었습니다.")
    print("대규모 테스트 데이터 생성이 완료되었습니다!")

if __name__ == "__main__":
    create_test_data() 