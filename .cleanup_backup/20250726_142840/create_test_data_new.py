#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation, ContributionEvaluation, ExpertiseEvaluation, ImpactEvaluation
from compensation.models import EmployeeCompensation
from promotions.models import PromotionRequest
from permissions.models import Permission, HRRole, EmployeeRole

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
    
    # 성장 레벨 (숫자)
    growth_levels = [1, 2, 3, 4, 5, 6]
    
    # 직종
    job_types = ['IT기획', 'IT개발', 'IT운영', '경영관리', '기업영업', '기업금융', '리테일금융', '투자금융', '고객지원']
    
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
        print(f"직원 {i+1} 생성 시작...")
        
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
            print(f"사용자 {username} 이미 존재")
            continue
            
        print(f"사용자 {username} 생성 완료")
        
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
        print(f"직원 {employees_created} 생성 완료: {employee.name}")
        
        # 평가 데이터 생성
        for year in range(2022, 2025):
            # 평가 기간 생성 또는 조회
            from evaluations.models import EvaluationPeriod
            period, _ = EvaluationPeriod.objects.get_or_create(
                year=year,
                period_type='ANNUAL',
                defaults={
                    'start_date': datetime(year, 1, 1),
                    'end_date': datetime(year, 12, 31),
                    'is_active': False,
                    'status': 'COMPLETED',
                }
            )
            # 기여도 평가
            contribution_eval = ContributionEvaluation.objects.create(
                employee=employee,
                evaluation_period=period,
                total_achievement_rate=random.uniform(80, 100),
                contribution_score=random.uniform(2, 4),
                is_achieved=True,
                evaluator=None,
                evaluated_date=datetime(year, 12, 15),
                comments=f"{year}년 기여도 평가 코멘트"
            )
            # 전문성 평가
            expertise_eval = ExpertiseEvaluation.objects.create(
                employee=employee,
                evaluation_period=period,
                required_level=random.randint(1, 6),
                expertise_focus=random.choice(['hard_skill', 'balanced']),
                creative_solution=random.randint(1, 4),
                technical_innovation=random.randint(1, 4),
                process_improvement=random.randint(1, 4),
                knowledge_sharing=random.randint(1, 4),
                mentoring=random.randint(1, 4),
                cross_functional=random.randint(1, 4),
                strategic_thinking=random.randint(1, 4),
                business_acumen=random.randint(1, 4),
                industry_trend=random.randint(1, 4),
                continuous_learning=random.randint(1, 4),
                strategic_contribution=random.randint(1, 4),
                interactive_contribution=random.randint(1, 4),
                technical_expertise=random.randint(1, 4),
                business_understanding=random.randint(1, 4),
                total_score=random.uniform(2, 4),
                is_achieved=True,
                evaluator=None,
                evaluated_date=datetime(year, 12, 20),
                comments=f"{year}년 전문성 평가 코멘트"
            )
            # 영향력 평가
            impact_eval = ImpactEvaluation.objects.create(
                employee=employee,
                evaluation_period=period,
                impact_scope=random.choice(['market', 'corp', 'org', 'individual']),
                core_values_practice=random.choice(['exemplary_values', 'limited_values']),
                leadership_demonstration=random.choice(['exemplary_leadership', 'limited_leadership']),
                customer_focus=random.randint(1, 4),
                collaboration=random.randint(1, 4),
                innovation=random.randint(1, 4),
                team_leadership=random.randint(1, 4),
                organizational_impact=random.randint(1, 4),
                external_networking=random.randint(1, 4),
                total_score=random.uniform(2, 4),
                is_achieved=True,
                evaluator=None,
                evaluated_date=datetime(year, 12, 25),
                comments=f"{year}년 영향력 평가 코멘트"
            )
            # 종합 평가
            ComprehensiveEvaluation.objects.create(
                employee=employee,
                evaluation_period=period,
                contribution_evaluation=contribution_eval,
                expertise_evaluation=expertise_eval,
                impact_evaluation=impact_eval,
                contribution_achieved=True,
                expertise_achieved=True,
                impact_achieved=True,
                manager=None,
                manager_grade=random.choice(['S', 'A+', 'A', 'B+', 'B', 'C']),
                manager_comments=f"{year}년 1차 평가 의견",
                manager_evaluated_date=datetime(year, 12, 28),
                final_grade=random.choice(['S', 'A+', 'A', 'B+', 'B', 'C']),
                calibration_comments=f"{year}년 조정 의견",
                status='COMPLETED'
            )
        
        # 보상 데이터 생성
        base_salary = random.randint(30000000, 80000000)
        competency_pay = random.randint(5000000, 20000000)
        position_allowance = random.randint(0, 10000000)
        pi_amount = random.randint(0, 50000000)
        
        EmployeeCompensation.objects.create(
            employee=employee,
            year=2024,
            month=random.randint(1, 12),
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
                    status=random.choice(['PENDING', 'APPROVED', 'REJECTED'])
                )
    
    print(f"총 {employees_created}명의 직원과 관련 데이터가 생성되었습니다.")
    print("대규모 테스트 데이터 생성이 완료되었습니다!")

if __name__ == "__main__":
    create_test_data() 