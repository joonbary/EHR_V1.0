"""
보상 계산 엔진 서비스
작업지시서 기반 구현 - 모든 산식 로직
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from django.db import transaction
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.exceptions import ValidationError

from employees.models import Employee
from compensation.models_enhanced import (
    GradeMaster, PositionMaster, JobProfileMaster,
    BaseSalaryTable, PositionAllowanceTable, CompetencyAllowanceTable,
    PITable, MonthlyPITable,
    CompensationSnapshot, CalcRunLog, EmployeeCompensationProfile
)

logger = logging.getLogger(__name__)


class CompensationCalculationService:
    """보상 계산 엔진"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.changes = {}
        
    def calculate_monthly_compensation(self, employee_id: int, pay_period: str) -> CompensationSnapshot:
        """
        월별 보상 계산 메인 함수
        순서: 기본급 → 고정OT → 직책급 → 직무역량급 → PI/월성과급/추석상여
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            profile = self.get_or_create_profile(employee)
            
            # 기준일 설정 (급여기산: 전월 21일 ~ 당월 20일)
            year, month = map(int, pay_period.split('-'))
            reference_date = date(year, month, 20)
            
            # 1. 기본급 계산
            base_salary = self.calculate_base_salary(profile, reference_date)
            
            # 2. 직책급 계산 (초임 80% 반영)
            position_allowance = self.calculate_position_allowance(profile, reference_date)
            
            # 3. 직무역량급 계산
            competency_allowance = self.calculate_competency_allowance(profile, reference_date)
            
            # 4. 추석상여 계산 (해당 월만)
            holiday_bonus = self.calculate_holiday_bonus(
                base_salary, position_allowance, competency_allowance, 
                employee, pay_period
            )
            
            # 5. 통상임금 계산 (기본급 + 직책급 + 직무역량급 + 추석상여)
            ordinary_wage = base_salary + position_allowance + competency_allowance + holiday_bonus
            
            # 6. 고정OT 계산 (통상시급 × 20 × 1.5)
            fixed_ot = self.calculate_fixed_ot(ordinary_wage)
            
            # 7. 변동급 계산 (PI 또는 월성과급)
            pi_amount = Decimal('0')
            monthly_pi_amount = Decimal('0')
            
            if employee.employment_type == 'PL':
                # PL: 월성과급 적용
                monthly_pi_amount = self.calculate_monthly_pi(profile, pay_period)
            elif employee.employment_type == 'Non-PL':
                # Non-PL: PI 적용 (연 1회, 1월 지급)
                if month == 1:
                    pi_amount = self.calculate_pi(profile, employee, year)
            
            # 스냅샷 생성/업데이트
            snapshot, created = CompensationSnapshot.objects.update_or_create(
                employee=employee,
                pay_period=pay_period,
                defaults={
                    'base_salary': base_salary,
                    'fixed_ot': fixed_ot,
                    'position_allowance': position_allowance,
                    'competency_allowance': competency_allowance,
                    'pi_amount': pi_amount,
                    'monthly_pi_amount': monthly_pi_amount,
                    'holiday_bonus': holiday_bonus,
                    'calc_run_id': self.generate_run_id(),
                }
            )
            
            return snapshot
            
        except Employee.DoesNotExist:
            raise ValidationError(f"Employee {employee_id} not found")
        except Exception as e:
            logger.error(f"Compensation calculation error for {employee_id}: {str(e)}")
            self.errors.append({
                'employee_id': employee_id,
                'error': str(e)
            })
            raise
    
    def get_or_create_profile(self, employee: Employee) -> EmployeeCompensationProfile:
        """직원 보상 프로파일 조회/생성"""
        profile, created = EmployeeCompensationProfile.objects.get_or_create(
            employee=employee,
            defaults={
                'grade_code': self.get_default_grade(),
                'job_profile_id': self.get_default_job_profile(),
                'competency_tier': 'T3',  # 기본값
                'position_tier': 'B',  # 기본값
            }
        )
        return profile
    
    def calculate_base_salary(self, profile: EmployeeCompensationProfile, reference_date: date) -> Decimal:
        """기본급 계산"""
        try:
            base_salary_entry = BaseSalaryTable.objects.filter(
                grade_code=profile.grade_code,
                employment_type=profile.employee.employment_type,
                valid_from__lte=reference_date
            ).filter(
                Q(valid_to__isnull=True) | Q(valid_to__gte=reference_date)
            ).first()
            
            if base_salary_entry:
                return base_salary_entry.base_salary
            
            # 기본값 반환
            logger.warning(f"No base salary found for grade {profile.grade_code}")
            return Decimal('3000000')  # 최소 기본급
            
        except Exception as e:
            logger.error(f"Base salary calculation error: {str(e)}")
            return Decimal('3000000')
    
    def calculate_position_allowance(self, profile: EmployeeCompensationProfile, reference_date: date) -> Decimal:
        """
        직책급 계산
        - 초임: 직책 부여 후 1년간 80% 지급
        - 영업조직: 단일 테이블 적용
        """
        if not profile.position_code:
            return Decimal('0')
        
        try:
            # 직책급 테이블 조회
            allowance_entry = PositionAllowanceTable.objects.filter(
                position_code=profile.position_code,
                allowance_tier=profile.position_tier or 'B',
                valid_from__lte=reference_date
            ).filter(
                Q(valid_to__isnull=True) | Q(valid_to__gte=reference_date)
            ).first()
            
            if not allowance_entry:
                # 영업조직은 N/A tier 사용
                allowance_entry = PositionAllowanceTable.objects.filter(
                    position_code=profile.position_code,
                    allowance_tier='N/A',
                    valid_from__lte=reference_date
                ).filter(
                    Q(valid_to__isnull=True) | Q(valid_to__gte=reference_date)
                ).first()
            
            if allowance_entry:
                amount = allowance_entry.monthly_amount
                
                # 초임 80% 적용 체크
                if profile.is_initial_position and profile.position_start_date:
                    days_since_start = (reference_date - profile.position_start_date).days
                    if days_since_start < 365:
                        amount = amount * Decimal('0.8')
                        self.warnings.append(f"Initial position rate (80%) applied for {profile.employee.name}")
                
                return amount
            
            return Decimal('0')
            
        except Exception as e:
            logger.error(f"Position allowance calculation error: {str(e)}")
            return Decimal('0')
    
    def calculate_competency_allowance(self, profile: EmployeeCompensationProfile, reference_date: date) -> Decimal:
        """직무역량급 계산"""
        try:
            competency_entry = CompetencyAllowanceTable.objects.filter(
                job_profile_id=profile.job_profile_id,
                competency_tier=profile.competency_tier,
                valid_from__lte=reference_date
            ).filter(
                Q(valid_to__isnull=True) | Q(valid_to__gte=reference_date)
            ).first()
            
            if competency_entry:
                return competency_entry.monthly_amount
            
            return Decimal('0')
            
        except Exception as e:
            logger.error(f"Competency allowance calculation error: {str(e)}")
            return Decimal('0')
    
    def calculate_fixed_ot(self, ordinary_wage: Decimal) -> Decimal:
        """
        고정OT 계산
        통상시급 = 통상임금 ÷ 209
        고정OT = 통상시급 × 20 × 1.5
        """
        hourly_rate = ordinary_wage / Decimal('209')
        fixed_ot = hourly_rate * Decimal('20') * Decimal('1.5')
        return fixed_ot.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    
    def calculate_pi(self, profile: EmployeeCompensationProfile, employee: Employee, year: int) -> Decimal:
        """
        PI(Performance Incentive) 계산 - Non-PL 전용
        기준: 기본급 + 직책급 + 직무역량급
        지급률: 조직/역할/평가등급별 차등
        """
        try:
            # 전년도 평가등급 조회 (실제 구현시 평가 테이블 연동)
            evaluation_grade = self.get_evaluation_grade(employee, year - 1)
            if not evaluation_grade:
                return Decimal('0')
            
            # 조직구분 (본사/영업) 판단
            org_type = '영업' if employee.department and '영업' in employee.department else '본사'
            
            # 역할구분 (팀원/직책자) 판단
            role_type = '직책자' if profile.position_code else '팀원'
            
            # PI 지급률 조회
            pi_rate_entry = PITable.objects.filter(
                organization_type=org_type,
                role_type=role_type,
                evaluation_grade=evaluation_grade,
                valid_from__lte=date(year, 1, 1)
            ).filter(
                Q(valid_to__isnull=True) | Q(valid_to__gte=date(year, 1, 1))
            ).first()
            
            if pi_rate_entry:
                # PI 기준금액 = 기본급 + 직책급 + 직무역량급
                reference_date = date(year - 1, 12, 31)
                base_salary = self.calculate_base_salary(profile, reference_date)
                position_allowance = self.calculate_position_allowance(profile, reference_date)
                competency_allowance = self.calculate_competency_allowance(profile, reference_date)
                
                pi_base = base_salary + position_allowance + competency_allowance
                
                # PI 금액 = 기준금액 × 지급률(%)
                pi_amount = pi_base * pi_rate_entry.payment_rate / Decimal('100')
                return pi_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            
            return Decimal('0')
            
        except Exception as e:
            logger.error(f"PI calculation error: {str(e)}")
            return Decimal('0')
    
    def calculate_monthly_pi(self, profile: EmployeeCompensationProfile, pay_period: str) -> Decimal:
        """
        월성과급 계산 - PL 전용
        역할레벨별 차등 지급
        """
        try:
            # 당월 평가등급 조회 (실제 구현시 월별 평가 테이블 연동)
            year, month = map(int, pay_period.split('-'))
            evaluation_grade = self.get_monthly_evaluation_grade(profile.employee, year, month)
            if not evaluation_grade:
                return Decimal('0')
            
            # 역할레벨 결정
            role_level = self.determine_role_level(profile)
            
            # 월성과급 지급액 조회
            monthly_pi_entry = MonthlyPITable.objects.filter(
                role_level=role_level,
                evaluation_grade=evaluation_grade,
                valid_from__lte=date(year, month, 1)
            ).filter(
                Q(valid_to__isnull=True) | Q(valid_to__gte=date(year, month, 1))
            ).first()
            
            if monthly_pi_entry:
                return monthly_pi_entry.payment_amount
            
            return Decimal('0')
            
        except Exception as e:
            logger.error(f"Monthly PI calculation error: {str(e)}")
            return Decimal('0')
    
    def calculate_holiday_bonus(self, base_salary: Decimal, position_allowance: Decimal,
                                competency_allowance: Decimal, employee: Employee, pay_period: str) -> Decimal:
        """
        추석상여 계산
        추석상여 = 통상임금 × 100% × (실근무일 ÷ (1/1~지급일 총 근무일수))
        """
        year, month = map(int, pay_period.split('-'))
        
        # 추석이 있는 월인지 확인 (일반적으로 9월 또는 10월)
        if month not in [9, 10]:
            return Decimal('0')
        
        # 추석 날짜 확인 (실제 구현시 음력 계산 필요)
        # 임시로 9월로 가정
        if month != 9:
            return Decimal('0')
        
        try:
            # 통상임금 = 기본급 + 직책급 + 직무역량급
            ordinary_wage = base_salary + position_allowance + competency_allowance
            
            # 근무일수 계산
            holiday_date = date(year, 9, 15)  # 임시 추석 날짜
            year_start = date(year, 1, 1)
            
            # 입사일 고려
            if employee.hire_date and employee.hire_date > year_start:
                start_date = employee.hire_date
            else:
                start_date = year_start
            
            # 실근무일수 계산 (주말 제외)
            worked_days = self.calculate_working_days(start_date, holiday_date)
            total_days = self.calculate_working_days(year_start, holiday_date)
            
            if total_days > 0:
                ratio = Decimal(worked_days) / Decimal(total_days)
                holiday_bonus = ordinary_wage * ratio
                return holiday_bonus.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            
            return Decimal('0')
            
        except Exception as e:
            logger.error(f"Holiday bonus calculation error: {str(e)}")
            return Decimal('0')
    
    def determine_role_level(self, profile: EmployeeCompensationProfile) -> str:
        """PL 역할레벨 결정"""
        if not profile.position_code:
            # 직책이 없는 경우 성장레벨로 판단
            if profile.grade_code:
                level = profile.grade_code.level
                if level <= 1:
                    return 'Lv.1'
                elif level <= 3:
                    return 'Lv.2-3'
            return 'Lv.1'
        
        # 직책으로 판단
        position_name = profile.position_code.position_name
        if '센터장' in position_name:
            return '센터장'
        elif '팀장' in position_name:
            return '팀장'
        
        # 성장레벨로 재판단
        if profile.grade_code:
            level = profile.grade_code.level
            if level <= 1:
                return 'Lv.1'
            elif level <= 3:
                return 'Lv.2-3'
        
        return 'Lv.1'
    
    def calculate_working_days(self, start_date: date, end_date: date) -> int:
        """주말을 제외한 근무일수 계산"""
        days = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:  # 월-금
                days += 1
            current += timedelta(days=1)
        return days
    
    def get_evaluation_grade(self, employee: Employee, year: int) -> Optional[str]:
        """연간 평가등급 조회 (임시 구현)"""
        # 실제 구현시 평가 테이블과 연동
        # 임시로 B+ 반환
        return 'B+'
    
    def get_monthly_evaluation_grade(self, employee: Employee, year: int, month: int) -> Optional[str]:
        """월별 평가등급 조회 (임시 구현)"""
        # 실제 구현시 월별 평가 테이블과 연동
        # 임시로 A 반환
        return 'A'
    
    def get_default_grade(self) -> str:
        """기본 등급 반환"""
        grade = GradeMaster.objects.filter(grade_code='GRD11').first() or \
               GradeMaster.objects.create(
                   grade_code='GRD11', 
                   level=1, 
                   step=1, 
                   title='주임',
                   valid_from=date(2024, 1, 1)
               )
        return grade.grade_code
    
    def get_default_job_profile(self) -> str:
        """기본 직무 프로파일 반환"""
        job_profile = JobProfileMaster.objects.filter(job_profile_id='JP001').first() or \
               JobProfileMaster.objects.create(
                   job_profile_id='JP001',
                   job_family='경영관리',
                   job_series='일반',
                   job_role='일반',
                   valid_from=date(2024, 1, 1)
               )
        return job_profile.job_profile_id
    
    def generate_run_id(self) -> str:
        """계산 실행 ID 생성"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"CALC_{timestamp}"
    
    @transaction.atomic
    def run_monthly_calculation(self, pay_period: str, employee_ids: Optional[List[int]] = None) -> CalcRunLog:
        """
        월별 보상 계산 일괄 실행
        """
        run_id = self.generate_run_id()
        run_log = CalcRunLog.objects.create(
            run_id=run_id,
            run_type='monthly',
            pay_period=pay_period,
            formula_version='v1.0',
            status='running'
        )
        
        try:
            # 대상 직원 조회
            if employee_ids:
                employees = Employee.objects.filter(id__in=employee_ids, is_active=True)
            else:
                employees = Employee.objects.filter(is_active=True)
            
            success_count = 0
            
            for employee in employees:
                try:
                    snapshot = self.calculate_monthly_compensation(employee.id, pay_period)
                    success_count += 1
                    
                    # 변경사항 기록
                    self.changes[employee.id] = {
                        'total': float(snapshot.total_compensation),
                        'base': float(snapshot.base_salary),
                        'ot': float(snapshot.fixed_ot)
                    }
                    
                except Exception as e:
                    logger.error(f"Failed to calculate for employee {employee.id}: {str(e)}")
                    self.errors.append({
                        'employee_id': employee.id,
                        'error': str(e)
                    })
            
            # 실행 로그 업데이트
            run_log.affected_count = success_count
            run_log.changes = self.changes
            run_log.errors = self.errors
            run_log.status = 'completed' if not self.errors else 'completed_with_errors'
            run_log.save()
            
            logger.info(f"Monthly calculation completed: {success_count}/{employees.count()} successful")
            
            return run_log
            
        except Exception as e:
            run_log.status = 'failed'
            run_log.errors = [{'critical': str(e)}]
            run_log.save()
            logger.error(f"Monthly calculation failed: {str(e)}")
            raise
    
    def validate_compensation_changes(self, employee_id: int, pay_period: str) -> List[str]:
        """
        보상 변경 검증
        - 전월 대비 ±20% 이상 변동 시 경고
        - 직책/등급 변경 시 검증
        """
        warnings = []
        
        try:
            year, month = map(int, pay_period.split('-'))
            
            # 이번 달 스냅샷
            current = CompensationSnapshot.objects.filter(
                employee_id=employee_id,
                pay_period=pay_period
            ).first()
            
            if not current:
                return warnings
            
            # 전월 스냅샷
            if month == 1:
                prev_period = f"{year-1}-12"
            else:
                prev_period = f"{year}-{month-1:02d}"
            
            previous = CompensationSnapshot.objects.filter(
                employee_id=employee_id,
                pay_period=prev_period
            ).first()
            
            if not previous:
                return warnings
            
            # 총 보상 변동률 체크
            if previous.total_compensation > 0:
                change_rate = (current.total_compensation - previous.total_compensation) / previous.total_compensation
                
                if abs(change_rate) > Decimal('0.2'):  # ±20%
                    warnings.append(
                        f"Total compensation changed by {change_rate*100:.1f}% "
                        f"({previous.total_compensation:,} → {current.total_compensation:,})"
                    )
            
            # 기본급 변동 체크
            if current.base_salary != previous.base_salary:
                warnings.append(
                    f"Base salary changed: {previous.base_salary:,} → {current.base_salary:,}"
                )
            
            # 직책급 변동 체크
            if abs(current.position_allowance - previous.position_allowance) > Decimal('100000'):
                warnings.append(
                    f"Position allowance changed: {previous.position_allowance:,} → {current.position_allowance:,}"
                )
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
        
        return warnings


class CompensationReportService:
    """보상 리포트 서비스"""
    
    def get_compensation_statement(self, employee_id: int, pay_period: str) -> Dict:
        """직원 보상 명세서 조회"""
        try:
            snapshot = CompensationSnapshot.objects.get(
                employee_id=employee_id,
                pay_period=pay_period
            )
            
            employee = snapshot.employee
            
            return {
                'employee': {
                    'id': employee.id,
                    'name': employee.name,
                    'department': employee.department,
                    'position': employee.new_position if hasattr(employee, 'new_position') else employee.position,
                    'employment_type': employee.employment_type,
                },
                'pay_period': pay_period,
                'compensation': {
                    'base_salary': float(snapshot.base_salary),
                    'fixed_ot': float(snapshot.fixed_ot),
                    'position_allowance': float(snapshot.position_allowance),
                    'competency_allowance': float(snapshot.competency_allowance),
                    'pi_amount': float(snapshot.pi_amount),
                    'monthly_pi_amount': float(snapshot.monthly_pi_amount),
                    'holiday_bonus': float(snapshot.holiday_bonus),
                    'ordinary_wage': float(snapshot.ordinary_wage),
                    'total_compensation': float(snapshot.total_compensation),
                },
                'calculated_at': snapshot.created_at.isoformat(),
            }
            
        except CompensationSnapshot.DoesNotExist:
            return None
    
    def get_compensation_mix_ratio(self, pay_period: str) -> Dict:
        """보상 구성 비율 KPI"""
        snapshots = CompensationSnapshot.objects.filter(pay_period=pay_period)
        
        total_base = snapshots.aggregate(Sum('base_salary'))['base_salary__sum'] or Decimal('0')
        total_fixed_ot = snapshots.aggregate(Sum('fixed_ot'))['fixed_ot__sum'] or Decimal('0')
        total_allowances = snapshots.aggregate(
            total=Sum('position_allowance') + Sum('competency_allowance')
        )['total'] or Decimal('0')
        total_variable = snapshots.aggregate(
            total=Sum('pi_amount') + Sum('monthly_pi_amount')
        )['total'] or Decimal('0')
        
        grand_total = total_base + total_fixed_ot + total_allowances + total_variable
        
        if grand_total > 0:
            return {
                'base_salary_ratio': float(total_base / grand_total * 100),
                'fixed_ot_ratio': float(total_fixed_ot / grand_total * 100),
                'allowances_ratio': float(total_allowances / grand_total * 100),
                'variable_ratio': float(total_variable / grand_total * 100),
                'total_amount': float(grand_total),
                'employee_count': snapshots.count(),
            }
        
        return {
            'base_salary_ratio': 0,
            'fixed_ot_ratio': 0,
            'allowances_ratio': 0,
            'variable_ratio': 0,
            'total_amount': 0,
            'employee_count': 0,
        }
    
    def get_variance_alerts(self, pay_period: str, threshold: float = 0.2) -> List[Dict]:
        """보상 변동 경고 조회"""
        service = CompensationCalculationService()
        alerts = []
        
        snapshots = CompensationSnapshot.objects.filter(pay_period=pay_period)
        
        for snapshot in snapshots:
            warnings = service.validate_compensation_changes(
                snapshot.employee_id, 
                pay_period
            )
            
            if warnings:
                alerts.append({
                    'employee_id': snapshot.employee_id,
                    'employee_name': snapshot.employee.name,
                    'warnings': warnings,
                    'total_compensation': float(snapshot.total_compensation),
                })
        
        return alerts