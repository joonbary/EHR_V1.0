#!/usr/bin/env python
"""
승진/이동 시스템 초기 데이터 생성 스크립트
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from evaluations.models import EvaluationPeriod, ComprehensiveEvaluation
from promotions.models import (
    PromotionRequirement, PromotionRequest, JobTransfer, OrganizationChart
)


def create_promotion_requirements():
    """승진 요건 데이터 생성"""
    print("승진 요건 데이터 생성 중...")
    
    requirements_data = [
        # Level 1 → 2
        {
            'from_level': 1, 'to_level': 2,
            'min_years_required': Decimal('2.0'),
            'consecutive_a_grades': 2,
            'min_performance_score': Decimal('2.5'),
            'department_recommendation_required': True,
            'hr_committee_required': False,
        },
        # Level 2 → 3
        {
            'from_level': 2, 'to_level': 3,
            'min_years_required': Decimal('3.0'),
            'consecutive_a_grades': 2,
            'min_performance_score': Decimal('3.0'),
            'department_recommendation_required': True,
            'hr_committee_required': True,
        },
        # Level 3 → 4
        {
            'from_level': 3, 'to_level': 4,
            'min_years_required': Decimal('4.0'),
            'consecutive_a_grades': 3,
            'min_performance_score': Decimal('3.0'),
            'department_recommendation_required': True,
            'hr_committee_required': True,
        },
        # Level 4 → 5
        {
            'from_level': 4, 'to_level': 5,
            'min_years_required': Decimal('5.0'),
            'consecutive_a_grades': 3,
            'min_performance_score': Decimal('3.5'),
            'department_recommendation_required': True,
            'hr_committee_required': True,
        },
        # Level 5 → 6
        {
            'from_level': 5, 'to_level': 6,
            'min_years_required': Decimal('6.0'),
            'consecutive_a_grades': 4,
            'min_performance_score': Decimal('3.5'),
            'department_recommendation_required': True,
            'hr_committee_required': True,
        },
    ]
    
    for data in requirements_data:
        requirement, created = PromotionRequirement.objects.get_or_create(
            from_level=data['from_level'],
            to_level=data['to_level'],
            defaults=data
        )
        if created:
            print(f"  ✓ Level {data['from_level']} → {data['to_level']} 요건 생성")
        else:
            print(f"  - Level {data['from_level']} → {data['to_level']} 요건 이미 존재")


def create_organization_chart():
    """조직도 데이터 생성"""
    print("\n조직도 데이터 생성 중...")
    
    departments_data = [
        {
            'department': '경영지원팀',
            'parent_department': None,
            'display_order': 1,
        },
        {
            'department': '인사팀',
            'parent_department': None,
            'display_order': 2,
        },
        {
            'department': 'IT팀',
            'parent_department': None,
            'display_order': 3,
        },
        {
            'department': '영업팀',
            'parent_department': None,
            'display_order': 4,
        },
        {
            'department': '마케팅팀',
            'parent_department': None,
            'display_order': 5,
        },
        {
            'department': '재무팀',
            'parent_department': None,
            'display_order': 6,
        },
    ]
    
    for data in departments_data:
        org, created = OrganizationChart.objects.get_or_create(
            department=data['department'],
            defaults=data
        )
        if created:
            print(f"  ✓ {data['department']} 부서 생성")
        else:
            print(f"  - {data['department']} 부서 이미 존재")


def create_sample_promotion_requests():
    """샘플 승진 요청 데이터 생성"""
    print("\n샘플 승진 요청 데이터 생성 중...")
    
    # 평가 기간 확인
    evaluation_period = EvaluationPeriod.objects.filter(is_active=True).first()
    if not evaluation_period:
        print("  - 활성화된 평가 기간이 없습니다.")
        return
    
    # 직원 목록 (Level 1-5)
    employees = Employee.objects.filter(
        growth_level__lt=6,
        employment_status='ACTIVE'
    )[:5]  # 상위 5명만
    
    for employee in employees:
        current_level = employee.growth_level
        target_level = current_level + 1
        
        # 기존 요청이 있는지 확인
        existing_request = PromotionRequest.objects.filter(
            employee=employee,
            status__in=['PENDING', 'UNDER_REVIEW']
        ).first()
        
        if existing_request:
            print(f"  - {employee.name}의 진행 중인 요청이 이미 존재")
            continue
        
        # 승진 요청 생성
        request = PromotionRequest.objects.create(
            employee=employee,
            current_level=current_level,
            target_level=target_level,
            employee_comments=f"{employee.name}의 승진 요청입니다.",
            status='PENDING'
        )
        
        # 요건 계산
        request.calculate_requirements()
        
        print(f"  ✓ {employee.name} (Level {current_level} → {target_level}) 승진 요청 생성")


def create_sample_job_transfers():
    """샘플 인사이동 데이터 생성"""
    print("\n샘플 인사이동 데이터 생성 중...")
    
    # 직원 목록
    employees = Employee.objects.filter(employment_status='ACTIVE')[:3]
    
    transfer_data = [
        {
            'transfer_type': 'PROMOTION',
            'from_department': 'IT팀',
            'to_department': 'IT팀',
            'from_position': '사원',
            'to_position': '대리',
            'reason': '업무 성과 우수로 인한 승진',
        },
        {
            'transfer_type': 'LATERAL',
            'from_department': '영업팀',
            'to_department': '마케팅팀',
            'from_position': '대리',
            'to_position': '대리',
            'reason': '부서 간 순환 이동',
        },
        {
            'transfer_type': 'ROTATION',
            'from_department': '인사팀',
            'to_department': '경영지원팀',
            'from_position': '사원',
            'to_position': '사원',
            'reason': '업무 경험 확대를 위한 순환',
        },
    ]
    
    for i, data in enumerate(transfer_data):
        if i < len(employees):
            employee = employees[i]
            
            transfer = JobTransfer.objects.create(
                employee=employee,
                transfer_type=data['transfer_type'],
                from_department=data['from_department'],
                to_department=data['to_department'],
                from_position=data['from_position'],
                to_position=data['to_position'],
                effective_date=date.today() + timedelta(days=30),
                announcement_date=date.today(),
                reason=data['reason'],
                status='APPROVED'
            )
            
            print(f"  ✓ {employee.name} {data['from_department']} → {data['to_department']} 이동 생성")


def main():
    """메인 실행 함수"""
    print("=== 승진/이동 시스템 초기 데이터 생성 ===")
    
    try:
        # 승진 요건 생성
        create_promotion_requirements()
        
        # 조직도 생성
        create_organization_chart()
        
        # 샘플 승진 요청 생성
        create_sample_promotion_requests()
        
        # 샘플 인사이동 생성
        create_sample_job_transfers()
        
        print("\n=== 초기 데이터 생성 완료 ===")
        print("이제 /promotions/ 경로에서 승진/이동 시스템을 확인할 수 있습니다.")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 