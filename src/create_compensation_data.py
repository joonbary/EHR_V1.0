# create_compensation_data.py
import os
import django
from decimal import Decimal

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from compensation.models import (
    SalaryTable, CompetencyPayTable, PositionAllowance,
    PerformanceIncentiveRate, EmployeeCompensation
)
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation

def create_compensation_data():
    """보상 데이터 생성"""
    print("\n=== OK금융그룹 보상 데이터 생성 시작 ===\n")
    
    # 1. 기본급 테이블 생성
    print("1. 기본급 테이블 생성")
    salary_data = [
        {'level': 1, 'salary': 30000000},  # 3,000만원
        {'level': 2, 'salary': 36000000},  # 3,600만원
        {'level': 3, 'salary': 42000000},  # 4,200만원
        {'level': 4, 'salary': 50000000},  # 5,000만원
        {'level': 5, 'salary': 60000000},  # 6,000만원
        {'level': 6, 'salary': 75000000},  # 7,500만원
    ]
    
    for data in salary_data:
        salary, created = SalaryTable.objects.get_or_create(
            growth_level=data['level'],
            defaults={'base_salary': data['salary']}
        )
        print(f"  {'✓ 생성' if created else '○ 이미 존재'}: 레벨 {data['level']} - {data['salary']:,}원")
    
    # 2. 역량급 테이블 생성
    print("\n2. 역량급 테이블 생성")
    competency_data = [
        # 레벨 1
        {'level': 1, 'job_type': '경영관리', 'pay': 5000000},
        {'level': 1, 'job_type': '기업영업', 'pay': 6000000},
        {'level': 1, 'job_type': 'IT', 'pay': 7000000},
        {'level': 1, 'job_type': '리테일영업', 'pay': 5500000},
        # 레벨 2
        {'level': 2, 'job_type': '경영관리', 'pay': 6000000},
        {'level': 2, 'job_type': '기업영업', 'pay': 7200000},
        {'level': 2, 'job_type': 'IT', 'pay': 8400000},
        {'level': 2, 'job_type': '리테일영업', 'pay': 6600000},
        # 레벨 3
        {'level': 3, 'job_type': '경영관리', 'pay': 7000000},
        {'level': 3, 'job_type': '기업영업', 'pay': 8400000},
        {'level': 3, 'job_type': 'IT', 'pay': 9800000},
        {'level': 3, 'job_type': '리테일영업', 'pay': 7700000},
        # 레벨 4
        {'level': 4, 'job_type': '경영관리', 'pay': 8000000},
        {'level': 4, 'job_type': '기업영업', 'pay': 10000000},
        {'level': 4, 'job_type': 'IT', 'pay': 12000000},
        {'level': 4, 'job_type': '리테일영업', 'pay': 9000000},
        # 레벨 5
        {'level': 5, 'job_type': '경영관리', 'pay': 10000000},
        {'level': 5, 'job_type': '기업영업', 'pay': 12000000},
        {'level': 5, 'job_type': 'IT', 'pay': 14000000},
        {'level': 5, 'job_type': '리테일영업', 'pay': 11000000},
        # 레벨 6
        {'level': 6, 'job_type': '경영관리', 'pay': 12000000},
        {'level': 6, 'job_type': '기업영업', 'pay': 15000000},
        {'level': 6, 'job_type': 'IT', 'pay': 17500000},
        {'level': 6, 'job_type': '리테일영업', 'pay': 13000000},
    ]
    
    for data in competency_data:
        competency, created = CompetencyPayTable.objects.get_or_create(
            growth_level=data['level'],
            job_type=data['job_type'],
            defaults={'competency_pay': data['pay']}
        )
        if created:
            print(f"  ✓ 레벨 {data['level']} {data['job_type']} - {data['pay']:,}원")
    
    # 3. 직책급 테이블 생성
    print("\n3. 직책급 테이블 생성")
    position_data = [
        {'position': '팀장', 'allowance': 3000000},      # 300만원
        {'position': '지점장', 'allowance': 5000000},    # 500만원
        {'position': '부서장', 'allowance': 8000000},    # 800만원
        {'position': '이사', 'allowance': 12000000},     # 1,200만원
        {'position': '상무', 'allowance': 15000000},     # 1,500만원
        {'position': '전무', 'allowance': 20000000},     # 2,000만원
        {'position': '부사장', 'allowance': 30000000},   # 3,000만원
        {'position': '사장', 'allowance': 50000000},     # 5,000만원
    ]
    
    for data in position_data:
        position, created = PositionAllowance.objects.get_or_create(
            position=data['position'],
            defaults={'allowance_amount': data['allowance']}
        )
        print(f"  {'✓ 생성' if created else '○ 이미 존재'}: {data['position']} - {data['allowance']:,}원")
    
    # 4. 성과급 지급률 테이블 생성
    print("\n4. 성과급 지급률 테이블 생성")
    pi_data = [
        {'grade': 'S', 'rate': 280.0},    # 280%
        {'grade': 'A+', 'rate': 200.0},   # 200%
        {'grade': 'A', 'rate': 100.0},    # 100%
        {'grade': 'B+', 'rate': 80.0},    # 80%
        {'grade': 'B', 'rate': 50.0},     # 50%
        {'grade': 'C', 'rate': 20.0},     # 20%
        {'grade': 'D', 'rate': 0.0},      # 0%
    ]
    
    for data in pi_data:
        pi_rate, created = PerformanceIncentiveRate.objects.get_or_create(
            evaluation_grade=data['grade'],
            defaults={'incentive_rate': data['rate']}
        )
        print(f"  {'✓ 생성' if created else '○ 이미 존재'}: {data['grade']}등급 - {data['rate']}%")
    
    # 5. 직원별 보상 생성
    print("\n5. 직원별 보상 생성")
    try:
        # 직원 조회
        kim_cs = Employee.objects.get(email='kim.cs@okfinance.co.kr')
        park_yh = Employee.objects.get(email='park.yh@okfinance.co.kr')
        
        # 평가 정보 조회
        kim_evaluation = ComprehensiveEvaluation.objects.get(employee=kim_cs)
        park_evaluation = ComprehensiveEvaluation.objects.get(employee=park_yh)
        
        # 김철수 보상 생성 (2024년 12월)
        kim_salary = SalaryTable.objects.get(growth_level=kim_cs.growth_level)
        kim_competency = CompetencyPayTable.objects.get(
            growth_level=kim_cs.growth_level,
            job_type=kim_cs.job_type
        )
        kim_position = PositionAllowance.objects.get(position=kim_cs.position)
        
        kim_comp, created = EmployeeCompensation.objects.get_or_create(
            employee=kim_cs,
            year=2024,
            month=12,
            defaults={
                'base_salary': kim_salary.base_salary,
                'competency_pay': kim_competency.competency_pay,
                'position_allowance': kim_position.allowance_amount,
                'evaluation': kim_evaluation
            }
        )
        
        if created:
            # 성과급 계산
            kim_comp.calculate_pi_amount(kim_evaluation.manager_grade)
            kim_comp.save()
            
            print(f"  ✓ 김철수 보상 생성:")
            print(f"    - 기본급: {kim_comp.base_salary:,}원")
            print(f"    - 고정OT: {kim_comp.fixed_overtime:,}원")
            print(f"    - 역량급: {kim_comp.competency_pay:,}원")
            print(f"    - 직책급: {kim_comp.position_allowance:,}원")
            print(f"    - 성과급: {kim_comp.pi_amount:,}원")
            print(f"    - 총 보상: {kim_comp.total_compensation:,}원")
        
        # 박영희 보상 생성 (2024년 12월)
        park_salary = SalaryTable.objects.get(growth_level=park_yh.growth_level)
        park_competency = CompetencyPayTable.objects.get(
            growth_level=park_yh.growth_level,
            job_type=park_yh.job_type
        )
        
        park_comp, created = EmployeeCompensation.objects.get_or_create(
            employee=park_yh,
            year=2024,
            month=12,
            defaults={
                'base_salary': park_salary.base_salary,
                'competency_pay': park_competency.competency_pay,
                'evaluation': park_evaluation
            }
        )
        
        if created:
            # 성과급 계산
            park_comp.calculate_pi_amount(park_evaluation.manager_grade)
            park_comp.save()
            
            print(f"  ✓ 박영희 보상 생성:")
            print(f"    - 기본급: {park_comp.base_salary:,}원")
            print(f"    - 고정OT: {park_comp.fixed_overtime:,}원")
            print(f"    - 역량급: {park_comp.competency_pay:,}원")
            print(f"    - 직책급: {park_comp.position_allowance or 0:,}원")
            print(f"    - 성과급: {park_comp.pi_amount:,}원")
            print(f"    - 총 보상: {park_comp.total_compensation:,}원")
            
    except (Employee.DoesNotExist, ComprehensiveEvaluation.DoesNotExist) as e:
        print(f"  ❌ 오류: {e}")
        print("  먼저 직원 데이터와 평가 데이터를 생성해주세요.")
    
    # 6. 결과 요약
    print("\n=== 보상 데이터 생성 완료 ===")
    print(f"기본급 테이블: {SalaryTable.objects.count()}개")
    print(f"역량급 테이블: {CompetencyPayTable.objects.count()}개")
    print(f"직책급 테이블: {PositionAllowance.objects.count()}개")
    print(f"성과급 지급률: {PerformanceIncentiveRate.objects.count()}개")
    print(f"직원 보상: {EmployeeCompensation.objects.count()}개")
    
    print("\n보상 계산 규칙:")
    print("- 고정OT = 기본급 ÷ 209 × 1.5 × 20")
    print("- 성과급 = 기본급 × (평가등급별 지급률 ÷ 100) ÷ 12")
    print("- 총 보상 = 기본급 + 고정OT + 역량급 + 직책급 + 성과급")

if __name__ == '__main__':
    create_compensation_data() 