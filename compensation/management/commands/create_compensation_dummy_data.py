"""
보상 더미데이터 생성 커맨드
PL직군: 700명 (2,400만원 ~ 6,000만원)
Non-PL직군: 1,000명
- 사원: 8% (80명) - 5,000~6,000만원
- 대리: 30% (300명) - 5,500~7,000만원
- 차장: 27% (270명) - 6,500~8,500만원
- 부장: 9% (90명) - 7,000~9,000만원
- 팀장: 16% (160명) - 9,500~13,000만원
- 부장(직책): 7% (70명) - 10,000~15,000만원
- 임원: 3% (30명)
  - 이사: 12,000~18,000만원
  - 상무: 15,000~25,000만원
  - 전무: 17,000~30,000만원
  - 부사장: 20,000~50,000만원
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from employees.models import Employee
from compensation.models import (
    EmployeeCompensation, 
    SalaryTable,
    CompetencyPayTable,
    PositionAllowance,
    PerformanceIncentiveRate,
    JOB_TYPE_CHOICES,
    POSITION_CHOICES,
    EVALUATION_GRADE_CHOICES
)
from decimal import Decimal
import random
from datetime import datetime


class Command(BaseCommand):
    help = '보상 더미데이터 생성'

    def handle(self, *args, **options):
        self.stdout.write('보상 더미데이터 생성 시작...')
        
        # 먼저 보상 테이블 설정
        self.setup_compensation_tables()
        
        # 직원 데이터 생성 건너뛰기 (기존 직원 사용)
        # self.create_employees()
        
        # 보상 데이터 생성 (기존 직원 대상)
        self.create_compensation_data()
        
        self.stdout.write(self.style.SUCCESS('보상 더미데이터 생성 완료!'))

    def setup_compensation_tables(self):
        """보상 관련 테이블 초기 설정"""
        self.stdout.write('보상 테이블 설정 중...')
        
        # 기본급 테이블 설정 (성장레벨 1~6)
        base_salaries = [
            (1, 3000000),  # 레벨 1: 300만원
            (2, 3500000),  # 레벨 2: 350만원
            (3, 4000000),  # 레벨 3: 400만원
            (4, 5000000),  # 레벨 4: 500만원
            (5, 6000000),  # 레벨 5: 600만원
            (6, 7000000),  # 레벨 6: 700만원
        ]
        
        for level, salary in base_salaries:
            SalaryTable.objects.get_or_create(
                growth_level=level,
                defaults={'base_salary': Decimal(salary)}
            )
        
        # 역량급 테이블 설정
        for level in range(1, 7):
            for job_type, _ in JOB_TYPE_CHOICES:
                competency_amount = Decimal(500000 + (level - 1) * 200000)
                if job_type == 'IT':
                    competency_amount *= Decimal('1.2')  # IT는 20% 추가
                
                CompetencyPayTable.objects.get_or_create(
                    growth_level=level,
                    job_type=job_type,
                    defaults={'competency_pay': competency_amount}
                )
        
        # 직책급 테이블 설정
        position_allowances = [
            ('팀장', 2000000),
            ('지점장', 2000000),
            ('부서장', 3000000),
            ('이사', 4000000),
            ('상무', 5000000),
            ('전무', 6000000),
            ('부사장', 8000000),
            ('사장', 10000000),
        ]
        
        for position, allowance in position_allowances:
            PositionAllowance.objects.get_or_create(
                position=position,
                defaults={'allowance_amount': Decimal(allowance)}
            )
        
        # 성과급 지급률 설정
        for level in range(1, 7):
            incentive_rates = [
                ('S', 200),
                ('A+', 180),
                ('A', 150),
                ('B+', 120),
                ('B', 100),
                ('C', 50),
                ('D', 0),
            ]
            
            for grade, rate in incentive_rates:
                # 레벨이 높을수록 성과급 비율 증가
                adjusted_rate = rate * (1 + (level - 1) * 0.1)
                PerformanceIncentiveRate.objects.get_or_create(
                    growth_level=level,
                    evaluation_grade=grade,
                    defaults={'incentive_rate': Decimal(str(adjusted_rate))}
                )

    def create_employees(self):
        """직원 데이터 생성"""
        self.stdout.write('직원 데이터 생성 중...')
        
        # 기존 직원 데이터는 유지하고 새로운 직원만 추가
        # Employee.objects.all().delete()  # 주석 처리
        
        departments = ['IT개발본부', '영업본부', '마케팅본부', '재무본부', '인사본부', '전략기획본부', '리스크관리본부']
        
        # PL직군 700명 생성
        pl_positions = ['PL1', 'PL2', 'PL3', 'PL4', 'PL5']
        for i in range(700):
            Employee.objects.create(
                name=f'PL직원{i+1:04d}',
                email=f'pl{i+1:04d}@okfn.com',
                department=random.choice(departments),
                position=random.choice(pl_positions),
                job_group='PL',
                hire_date=timezone.now().date(),
                growth_level=random.randint(1, 5),
                employment_status='재직'
            )
        
        # Non-PL직군 1,000명 생성
        non_pl_distribution = [
            ('사원', 80, 1),
            ('대리', 300, 2),
            ('차장', 270, 3),
            ('부장', 90, 4),
            ('팀장', 160, 5),
            ('부장(직책)', 70, 5),
            ('이사', 10, 6),
            ('상무', 10, 6),
            ('전무', 7, 6),
            ('부사장', 3, 6),
        ]
        
        employee_count = 0
        for position, count, growth_level in non_pl_distribution:
            for i in range(count):
                employee_count += 1
                Employee.objects.create(
                    name=f'직원{employee_count:04d}',
                    email=f'emp{employee_count:04d}@okfn.com',
                    department=random.choice(departments),
                    position=position,
                    job_group='Non-PL',
                    hire_date=timezone.now().date(),
                    growth_level=growth_level,
                    employment_status='재직'
                )
        
        self.stdout.write(f'총 {Employee.objects.count()}명의 직원 생성 완료')

    def create_compensation_data(self):
        """보상 데이터 생성"""
        self.stdout.write('보상 데이터 생성 중...')
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # 기존 보상 데이터 삭제
        EmployeeCompensation.objects.all().delete()
        
        employees = Employee.objects.all()
        
        with transaction.atomic():
            for employee in employees:
                # 연봉 범위 결정
                annual_salary = self.get_annual_salary(employee)
                monthly_salary = annual_salary / 12
                
                # 기본급 (월급여의 60%)
                base_salary = Decimal(str(monthly_salary * 0.6))
                
                # 역량급 (월급여의 20%)
                competency_pay = Decimal(str(monthly_salary * 0.2))
                
                # 직책급 (해당되는 경우)
                position_allowance = self.get_position_allowance(employee.position)
                
                # 평가 등급 랜덤 설정
                evaluation_grade = random.choice(['S', 'A+', 'A', 'B+', 'B', 'C', 'D'])
                
                # 보상 데이터 생성
                compensation = EmployeeCompensation(
                    employee=employee,
                    year=current_year,
                    month=current_month,
                    base_salary=base_salary,
                    competency_pay=competency_pay,
                    position_allowance=position_allowance
                )
                
                # 고정OT 계산
                compensation.calculate_fixed_overtime()
                
                # 성과급 계산
                compensation.calculate_pi_amount(evaluation_grade)
                
                # 총 보상 계산
                compensation.calculate_total_compensation()
                
                compensation.save()
        
        self.stdout.write(f'총 {EmployeeCompensation.objects.count()}개의 보상 데이터 생성 완료')

    def get_annual_salary(self, employee):
        """직급별 연봉 범위 반환 (단위: 원)"""
        # job_group이 없는 경우 처리
        job_group = getattr(employee, 'job_group', None)
        
        if job_group == 'PL':
            # PL직군: 2,400만원 ~ 6,000만원
            return random.randint(24000000, 60000000)
        
        # Non-PL직군 및 기타
        position = getattr(employee, 'position', '')
        
        salary_ranges = {
            '사원': (50000000, 60000000),
            '대리': (55000000, 70000000),
            '차장': (65000000, 85000000),
            '부장': (70000000, 90000000),
            '팀장': (95000000, 130000000),
            '부장(직책)': (100000000, 150000000),
            '이사': (120000000, 180000000),
            '상무': (150000000, 250000000),
            '전무': (170000000, 300000000),
            '부사장': (200000000, 500000000),
        }
        
        # 직급별 매칭 시도
        for key in salary_ranges:
            if key in position:
                min_salary, max_salary = salary_ranges[key]
                return random.randint(min_salary, max_salary)
        
        # 기본값 (일반 직원)
        return random.randint(50000000, 80000000)

    def get_position_allowance(self, position):
        """직책급 반환"""
        executive_positions = {
            '팀장': 2000000,
            '부장(직책)': 3000000,
            '이사': 4000000,
            '상무': 5000000,
            '전무': 6000000,
            '부사장': 8000000,
        }
        
        monthly_allowance = executive_positions.get(position, 0)
        return Decimal(str(monthly_allowance)) if monthly_allowance > 0 else None