"""
보상 관리 서비스
"""
from typing import Dict, List, Optional, Tuple
from django.db import transaction, models
from datetime import date, datetime
from decimal import Decimal
import logging

from compensation.models import (
    EmployeeCompensation, SalaryTable, PITable,
    TaxBracket, PayrollHistory
)
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from core.exceptions import ValidationError, CompensationError
from core.utils import NumberUtils, DateCalculator


logger = logging.getLogger(__name__)


class CompensationService:
    """보상 관리 비즈니스 로직"""
    
    def __init__(self):
        # 급여 구성 비율
        self.salary_components = {
            'base_ratio': 0.60,      # 기본급 60%
            'competency_ratio': 0.25, # 역량급 25%
            'position_ratio': 0.15    # 직책급 15%
        }
        
        # 고정 OT 기준
        self.fixed_ot_hours = {
            'Level_1': 20,
            'Level_2': 30,
            'Level_3': 40,
            'Level_4': 40,
            'Level_5': 30,
            'Level_6': 20
        }
    
    @transaction.atomic
    def calculate_employee_compensation(
        self,
        employee_id: int,
        effective_date: date = None
    ) -> EmployeeCompensation:
        """직원 보상 계산"""
        try:
            employee = Employee.objects.get(id=employee_id)
            
            if not effective_date:
                effective_date = date.today()
            
            # 기존 보상 정보 조회 또는 생성
            compensation, created = EmployeeCompensation.objects.get_or_create(
                employee=employee,
                defaults={'effective_date': effective_date}
            )
            
            # 급여 테이블에서 정보 조회
            salary_info = self._get_salary_info(employee)
            
            # 기본급 계산
            compensation.base_salary = salary_info['total'] * Decimal(str(self.salary_components['base_ratio']))
            
            # 역량급 계산
            compensation.competency_pay = salary_info['total'] * Decimal(str(self.salary_components['competency_ratio']))
            
            # 직책급 계산
            compensation.position_pay = self._calculate_position_pay(employee)
            
            # 고정 OT 계산
            compensation.fixed_ot = self._calculate_fixed_ot(employee)
            
            # 성과급(PI) 계산
            compensation.performance_incentive = self._calculate_pi(employee)
            
            # 총 보상 계산
            compensation.total_compensation = (
                compensation.base_salary +
                compensation.competency_pay +
                compensation.position_pay +
                compensation.fixed_ot +
                compensation.performance_incentive
            )
            
            compensation.save()
            
            logger.info(f"Compensation calculated for employee: {employee.employee_number}")
            return compensation
            
        except Employee.DoesNotExist:
            raise CompensationError(f"직원 ID {employee_id}를 찾을 수 없습니다.")
    
    def _get_salary_info(self, employee: Employee) -> Dict:
        """급여 테이블 정보 조회"""
        try:
            salary_table = SalaryTable.objects.get(
                job_family=employee.job_family,
                growth_level=employee.growth_level
            )
            
            return {
                'min': salary_table.min_salary,
                'max': salary_table.max_salary,
                'total': salary_table.standard_salary
            }
        except SalaryTable.DoesNotExist:
            # 기본값 반환
            logger.warning(f"Salary table not found for {employee.job_family}/{employee.growth_level}")
            return {
                'min': Decimal('50000000'),
                'max': Decimal('80000000'),
                'total': Decimal('65000000')
            }
    
    def _calculate_position_pay(self, employee: Employee) -> Decimal:
        """직책급 계산"""
        position_allowances = {
            '부서장': Decimal('10000000'),
            '팀장': Decimal('5000000'),
            '파트장': Decimal('3000000'),
            'TF장': Decimal('2000000')
        }
        
        for position, allowance in position_allowances.items():
            if position in employee.position:
                return allowance
        
        return Decimal('0')
    
    def _calculate_fixed_ot(self, employee: Employee) -> Decimal:
        """고정 OT 계산"""
        ot_hours = self.fixed_ot_hours.get(employee.growth_level, 20)
        
        # 시간당 급여 계산 (연봉 / 2080시간)
        try:
            compensation = EmployeeCompensation.objects.get(employee=employee)
            hourly_rate = (compensation.base_salary + compensation.competency_pay) / Decimal('2080')
            
            # OT는 시간당 급여의 1.5배
            ot_amount = hourly_rate * Decimal('1.5') * Decimal(str(ot_hours)) * Decimal('12')  # 연간
            
            return ot_amount.quantize(Decimal('1'))
        except:
            return Decimal('0')
    
    def _calculate_pi(self, employee: Employee) -> Decimal:
        """성과급(PI) 계산"""
        try:
            # 최근 평가 결과 조회
            latest_evaluation = ComprehensiveEvaluation.objects.filter(
                employee=employee,
                is_completed=True
            ).order_by('-evaluation_period__end_date').first()
            
            if not latest_evaluation:
                return Decimal('0')
            
            grade = latest_evaluation.final_grade or latest_evaluation.manager_grade
            
            # PI 테이블에서 지급률 조회
            pi_rate = PITable.objects.get(
                growth_level=employee.growth_level,
                performance_grade=grade
            ).payment_rate
            
            # 기준 금액 계산 (기본급 + 역량급)
            compensation = EmployeeCompensation.objects.get(employee=employee)
            base_amount = compensation.base_salary + compensation.competency_pay
            
            # PI 금액 계산
            pi_amount = base_amount * (pi_rate / Decimal('100'))
            
            return pi_amount.quantize(Decimal('1'))
            
        except (PITable.DoesNotExist, EmployeeCompensation.DoesNotExist):
            return Decimal('0')
    
    def calculate_net_salary(
        self,
        employee_id: int,
        year: int,
        month: int
    ) -> Dict:
        """실수령액 계산"""
        try:
            employee = Employee.objects.get(id=employee_id)
            compensation = EmployeeCompensation.objects.get(employee=employee)
            
            # 월 급여 계산
            monthly_gross = compensation.total_compensation / Decimal('12')
            
            # 공제 항목 계산
            deductions = self._calculate_deductions(monthly_gross, employee)
            
            # 실수령액
            net_salary = monthly_gross - deductions['total']
            
            return {
                'gross_salary': monthly_gross,
                'deductions': deductions,
                'net_salary': net_salary,
                'payment_date': date(year, month, 25)  # 급여일
            }
            
        except (Employee.DoesNotExist, EmployeeCompensation.DoesNotExist):
            raise CompensationError("보상 정보를 찾을 수 없습니다.")
    
    def _calculate_deductions(self, gross_salary: Decimal, employee: Employee) -> Dict:
        """공제 항목 계산"""
        deductions = {}
        
        # 소득세 (간이세액표 기준 - 실제로는 더 복잡함)
        income_tax = self._calculate_income_tax(gross_salary)
        deductions['income_tax'] = income_tax
        
        # 지방소득세 (소득세의 10%)
        deductions['local_income_tax'] = income_tax * Decimal('0.1')
        
        # 국민연금 (4.5%)
        deductions['national_pension'] = gross_salary * Decimal('0.045')
        
        # 건강보험 (3.495%)
        deductions['health_insurance'] = gross_salary * Decimal('0.03495')
        
        # 장기요양보험 (건강보험의 12.27%)
        deductions['long_term_care'] = deductions['health_insurance'] * Decimal('0.1227')
        
        # 고용보험 (0.9%)
        deductions['employment_insurance'] = gross_salary * Decimal('0.009')
        
        # 총 공제액
        deductions['total'] = sum(deductions.values())
        
        return deductions
    
    def _calculate_income_tax(self, gross_salary: Decimal) -> Decimal:
        """소득세 계산 (간이세액표 기준)"""
        # 실제로는 간이세액표를 사용해야 하지만, 여기서는 간단한 계산식 사용
        annual_income = gross_salary * 12
        
        # 과세표준 구간별 세율 적용
        tax_brackets = [
            (12000000, 0.06),    # 1200만원 이하 6%
            (46000000, 0.15),    # 4600만원 이하 15%
            (88000000, 0.24),    # 8800만원 이하 24%
            (150000000, 0.35),   # 1.5억 이하 35%
            (300000000, 0.38),   # 3억 이하 38%
            (500000000, 0.40),   # 5억 이하 40%
            (1000000000, 0.42),  # 10억 이하 42%
            (float('inf'), 0.45) # 10억 초과 45%
        ]
        
        tax = Decimal('0')
        prev_bracket = 0
        
        for bracket_limit, rate in tax_brackets:
            if annual_income <= bracket_limit:
                tax += (annual_income - prev_bracket) * Decimal(str(rate))
                break
            else:
                tax += (bracket_limit - prev_bracket) * Decimal(str(rate))
                prev_bracket = bracket_limit
        
        # 월 소득세로 변환
        monthly_tax = tax / 12
        
        return monthly_tax.quantize(Decimal('1'))
    
    def get_compensation_statistics(self, department: Optional[str] = None) -> Dict:
        """보상 통계 조회"""
        queryset = EmployeeCompensation.objects.select_related('employee')
        
        if department:
            queryset = queryset.filter(employee__department=department)
        
        # 기본 통계
        stats = queryset.aggregate(
            total_count=models.Count('id'),
            avg_total=models.Avg('total_compensation'),
            min_total=models.Min('total_compensation'),
            max_total=models.Max('total_compensation'),
            avg_base=models.Avg('base_salary'),
            avg_pi=models.Avg('performance_incentive')
        )
        
        # 성장레벨별 평균
        level_stats = {}
        for level in ['Level_1', 'Level_2', 'Level_3', 'Level_4', 'Level_5', 'Level_6']:
            level_data = queryset.filter(
                employee__growth_level=level
            ).aggregate(
                count=models.Count('id'),
                avg_total=models.Avg('total_compensation')
            )
            if level_data['count'] > 0:
                level_stats[level] = level_data
        
        # 부서별 평균
        dept_stats = {}
        departments = Employee.objects.values_list('department', flat=True).distinct()
        for dept in departments:
            dept_data = queryset.filter(
                employee__department=dept
            ).aggregate(
                count=models.Count('id'),
                avg_total=models.Avg('total_compensation')
            )
            if dept_data['count'] > 0:
                dept_stats[dept] = dept_data
        
        return {
            'overall': stats,
            'by_level': level_stats,
            'by_department': dept_stats,
            'salary_range': {
                'min': NumberUtils.format_currency(stats['min_total'] or 0),
                'max': NumberUtils.format_currency(stats['max_total'] or 0),
                'avg': NumberUtils.format_currency(stats['avg_total'] or 0)
            }
        }
    
    @transaction.atomic
    def process_payroll(self, year: int, month: int) -> Dict:
        """급여 처리"""
        processed_count = 0
        errors = []
        
        # 활성 직원 조회
        active_employees = Employee.objects.filter(is_active=True)
        
        for employee in active_employees:
            try:
                # 급여 계산
                salary_info = self.calculate_net_salary(employee.id, year, month)
                
                # 급여 이력 저장
                PayrollHistory.objects.create(
                    employee=employee,
                    year=year,
                    month=month,
                    gross_salary=salary_info['gross_salary'],
                    deductions=salary_info['deductions']['total'],
                    net_salary=salary_info['net_salary'],
                    payment_date=salary_info['payment_date'],
                    is_paid=False
                )
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Payroll processing error for {employee.employee_number}: {str(e)}")
                errors.append({
                    'employee': employee.employee_number,
                    'error': str(e)
                })
        
        return {
            'processed_count': processed_count,
            'error_count': len(errors),
            'errors': errors[:10],  # 최대 10개 에러만
            'processing_date': datetime.now()
        }
    
    def generate_payslip(self, employee_id: int, year: int, month: int) -> Dict:
        """급여명세서 생성"""
        try:
            payroll = PayrollHistory.objects.get(
                employee_id=employee_id,
                year=year,
                month=month
            )
            
            employee = payroll.employee
            compensation = EmployeeCompensation.objects.get(employee=employee)
            
            # 급여 상세 내역
            salary_details = self.calculate_net_salary(employee_id, year, month)
            
            return {
                'employee': {
                    'name': employee.name,
                    'employee_number': employee.employee_number,
                    'department': employee.department,
                    'position': employee.position
                },
                'period': f"{year}년 {month}월",
                'payment_date': payroll.payment_date,
                'earnings': {
                    '기본급': compensation.base_salary / 12,
                    '역량급': compensation.competency_pay / 12,
                    '직책급': compensation.position_pay / 12,
                    '고정OT': compensation.fixed_ot / 12,
                    '성과급': compensation.performance_incentive / 12
                },
                'deductions': salary_details['deductions'],
                'summary': {
                    '지급총액': salary_details['gross_salary'],
                    '공제총액': salary_details['deductions']['total'],
                    '실수령액': salary_details['net_salary']
                }
            }
            
        except PayrollHistory.DoesNotExist:
            raise CompensationError("급여 이력을 찾을 수 없습니다.")