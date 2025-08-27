# 🎯 OK금융그룹 보상체계 모델 (Enhanced Version)
# 작업지시서 기반 완전 구현

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import datetime, date
from employees.models import Employee
import json

# ========================================
# 1. 마스터 데이터 모델
# ========================================

class GradeMaster(models.Model):
    """성장레벨/직급 마스터"""
    grade_code = models.CharField(max_length=10, primary_key=True, verbose_name='등급코드')  # GRD01~GRD99
    level = models.IntegerField(verbose_name='성장레벨')  # 1~9
    step = models.IntegerField(verbose_name='급호')  # 1~99
    title = models.CharField(max_length=50, verbose_name='직급명')  # 주임, 대리, 과장 등
    valid_from = models.DateField(verbose_name='유효시작일')
    valid_to = models.DateField(null=True, blank=True, verbose_name='유효종료일')
    
    class Meta:
        db_table = 'comp_grade_master'
        verbose_name = '등급 마스터'
        verbose_name_plural = '등급 마스터'
        ordering = ['level', 'step']
    
    def __str__(self):
        return f"{self.grade_code}: Lv{self.level}-{self.step}호 ({self.title})"


class PositionMaster(models.Model):
    """직책 마스터"""
    DOMAIN_CHOICES = [
        ('HQ', '본사'),
        ('Non-PL', 'Non-PL'),
        ('PL', 'PL'),
    ]
    
    position_code = models.CharField(max_length=10, primary_key=True, verbose_name='직책코드')  # POS01~POS99
    position_name = models.CharField(max_length=50, verbose_name='직책명')
    domain = models.CharField(max_length=10, choices=DOMAIN_CHOICES, verbose_name='도메인')
    manager_level = models.IntegerField(null=True, blank=True, verbose_name='관리자레벨')
    valid_from = models.DateField(verbose_name='유효시작일')
    valid_to = models.DateField(null=True, blank=True, verbose_name='유효종료일')
    
    class Meta:
        db_table = 'comp_position_master'
        verbose_name = '직책 마스터'
        verbose_name_plural = '직책 마스터'
        ordering = ['position_code']
    
    def __str__(self):
        return f"{self.position_code}: {self.position_name} ({self.domain})"


class JobProfileMaster(models.Model):
    """직무 프로파일 마스터"""
    job_profile_id = models.CharField(max_length=20, primary_key=True, verbose_name='직무프로파일ID')
    job_family = models.CharField(max_length=50, verbose_name='직군')
    job_series = models.CharField(max_length=50, verbose_name='직렬')
    job_role = models.CharField(max_length=50, verbose_name='직무')
    description = models.TextField(blank=True, verbose_name='설명')
    valid_from = models.DateField(verbose_name='유효시작일')
    valid_to = models.DateField(null=True, blank=True, verbose_name='유효종료일')
    
    class Meta:
        db_table = 'comp_job_profile_master'
        verbose_name = '직무 프로파일'
        verbose_name_plural = '직무 프로파일'
        ordering = ['job_profile_id']
    
    def __str__(self):
        return f"{self.job_profile_id}: {self.job_family}/{self.job_series}/{self.job_role}"


# ========================================
# 2. 보상 구성요소 테이블
# ========================================

class BaseSalaryTable(models.Model):
    """기본급 테이블 (성장레벨별)"""
    EMPLOYMENT_TYPE_CHOICES = [
        ('정규직', '정규직'),
        ('PL', 'PL'),
        ('Non-PL', 'Non-PL'),
        ('별정직', '별정직'),
    ]
    
    grade_code = models.ForeignKey(GradeMaster, on_delete=models.CASCADE, verbose_name='등급코드')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, verbose_name='고용형태')
    base_salary = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='기본급')
    valid_from = models.DateField(verbose_name='유효시작일')
    valid_to = models.DateField(null=True, blank=True, verbose_name='유효종료일')
    
    class Meta:
        db_table = 'comp_base_salary_table'
        verbose_name = '기본급 테이블'
        verbose_name_plural = '기본급 테이블'
        unique_together = ['grade_code', 'employment_type', 'valid_from']
        ordering = ['grade_code', 'employment_type']
    
    def __str__(self):
        return f"{self.grade_code} {self.employment_type}: {self.base_salary:,}원"


class PositionAllowanceTable(models.Model):
    """직책급 테이블"""
    TIER_CHOICES = [
        ('A', 'A등급'),
        ('B+', 'B+등급'),
        ('B', 'B등급'),
        ('N/A', '해당없음'),  # 영업조직
    ]
    
    RATE_CHOICES = [
        (0.8, '초임(80%)'),
        (1.0, '일반(100%)'),
    ]
    
    position_code = models.ForeignKey(PositionMaster, on_delete=models.CASCADE, verbose_name='직책코드')
    allowance_tier = models.CharField(max_length=5, choices=TIER_CHOICES, verbose_name='수당등급')
    monthly_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='월지급액')
    allowance_rate = models.DecimalField(max_digits=3, decimal_places=1, choices=RATE_CHOICES, default=1.0, verbose_name='지급률')
    valid_from = models.DateField(verbose_name='유효시작일')
    valid_to = models.DateField(null=True, blank=True, verbose_name='유효종료일')
    
    class Meta:
        db_table = 'comp_position_allowance'
        verbose_name = '직책급 테이블'
        verbose_name_plural = '직책급 테이블'
        unique_together = ['position_code', 'allowance_tier', 'valid_from']
        ordering = ['position_code', 'allowance_tier']
    
    def __str__(self):
        return f"{self.position_code} {self.allowance_tier}: {self.monthly_amount:,}원"


class CompetencyAllowanceTable(models.Model):
    """직무역량급 테이블"""
    TIER_CHOICES = [
        ('T1', 'Tier 1'),
        ('T2', 'Tier 2'),
        ('T3', 'Tier 3'),
    ]
    
    job_profile_id = models.ForeignKey(JobProfileMaster, on_delete=models.CASCADE, verbose_name='직무프로파일')
    competency_tier = models.CharField(max_length=5, choices=TIER_CHOICES, verbose_name='역량등급')
    monthly_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='월지급액')
    valid_from = models.DateField(verbose_name='유효시작일')
    valid_to = models.DateField(null=True, blank=True, verbose_name='유효종료일')
    
    class Meta:
        db_table = 'comp_competency_allowance'
        verbose_name = '직무역량급 테이블'
        verbose_name_plural = '직무역량급 테이블'
        unique_together = ['job_profile_id', 'competency_tier', 'valid_from']
        ordering = ['job_profile_id', 'competency_tier']
    
    def __str__(self):
        return f"{self.job_profile_id} {self.competency_tier}: {self.monthly_amount:,}원"


# ========================================
# 3. 변동급 테이블 (PI/월성과급)
# ========================================

class PITable(models.Model):
    """PI(Performance Incentive) 지급률 테이블 - Non-PL 전용"""
    EVALUATION_GRADES = [
        ('S', 'S'),
        ('A+', 'A+'),
        ('A', 'A'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    
    ORGANIZATION_TYPE = [
        ('본사', '본사'),
        ('영업', '영업'),
    ]
    
    ROLE_TYPE = [
        ('팀원', '팀원'),
        ('직책자', '직책자'),
    ]
    
    organization_type = models.CharField(max_length=10, choices=ORGANIZATION_TYPE, verbose_name='조직구분')
    role_type = models.CharField(max_length=10, choices=ROLE_TYPE, verbose_name='역할구분')
    evaluation_grade = models.CharField(max_length=5, choices=EVALUATION_GRADES, verbose_name='평가등급')
    payment_rate = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='지급률(%)')
    valid_from = models.DateField(verbose_name='유효시작일')
    valid_to = models.DateField(null=True, blank=True, verbose_name='유효종료일')
    
    class Meta:
        db_table = 'comp_pi_table'
        verbose_name = 'PI 지급률'
        verbose_name_plural = 'PI 지급률'
        unique_together = ['organization_type', 'role_type', 'evaluation_grade', 'valid_from']
        ordering = ['organization_type', 'role_type', '-payment_rate']
    
    def __str__(self):
        return f"{self.organization_type} {self.role_type} {self.evaluation_grade}: {self.payment_rate}%"


class MonthlyPITable(models.Model):
    """월성과급 지급액 테이블 - PL 전용"""
    EVALUATION_GRADES = [
        ('S', 'S'),
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('B-', 'B-'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    
    ROLE_LEVELS = [
        ('센터장', '센터장'),
        ('팀장', '팀장'),
        ('Lv.2-3', 'Lv.2-3(프로/책임/선임)'),
        ('Lv.1', 'Lv.1(전임/주임)'),
    ]
    
    role_level = models.CharField(max_length=20, choices=ROLE_LEVELS, verbose_name='역할레벨')
    evaluation_grade = models.CharField(max_length=5, choices=EVALUATION_GRADES, verbose_name='평가등급')
    payment_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='지급액')
    valid_from = models.DateField(verbose_name='유효시작일')
    valid_to = models.DateField(null=True, blank=True, verbose_name='유효종료일')
    
    class Meta:
        db_table = 'comp_monthly_pi_table'
        verbose_name = '월성과급'
        verbose_name_plural = '월성과급'
        unique_together = ['role_level', 'evaluation_grade', 'valid_from']
        ordering = ['role_level', '-payment_amount']
    
    def __str__(self):
        return f"{self.role_level} {self.evaluation_grade}: {self.payment_amount:,}원"


# ========================================
# 4. 보상 스냅샷 및 운영 테이블
# ========================================

class CompensationSnapshot(models.Model):
    """보상 스냅샷 (월별 정산 결과)"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='직원')
    pay_period = models.CharField(max_length=7, verbose_name='급여기간')  # YYYY-MM
    
    # 기본급 항목
    base_salary = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='기본급')
    fixed_ot = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='고정OT')
    
    # 수당 항목
    position_allowance = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='직책급')
    competency_allowance = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='직무역량급')
    
    # 변동급 항목
    pi_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='PI')
    monthly_pi_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='월성과급')
    holiday_bonus = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='추석상여')
    
    # 계산 정보
    calc_run_id = models.CharField(max_length=50, verbose_name='계산ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    
    class Meta:
        db_table = 'comp_snapshot'
        verbose_name = '보상 스냅샷'
        verbose_name_plural = '보상 스냅샷'
        unique_together = ['employee', 'pay_period']
        ordering = ['-pay_period', 'employee']
    
    def __str__(self):
        return f"{self.employee.name} {self.pay_period}"
    
    @property
    def ordinary_wage(self):
        """통상임금 계산 (기본급 + 직책급 + 직무역량급 + 추석상여)"""
        return self.base_salary + self.position_allowance + self.competency_allowance + self.holiday_bonus
    
    @property
    def total_compensation(self):
        """총 보상 계산"""
        return (self.base_salary + self.fixed_ot + self.position_allowance + 
                self.competency_allowance + self.pi_amount + self.monthly_pi_amount + 
                self.holiday_bonus)
    
    def calculate_fixed_ot(self):
        """고정OT 계산: 통상시급 × 20시간 × 1.5"""
        hourly_rate = self.ordinary_wage / Decimal('209')
        self.fixed_ot = hourly_rate * Decimal('20') * Decimal('1.5')
        return self.fixed_ot


class CalcRunLog(models.Model):
    """계산 실행 로그"""
    run_id = models.CharField(max_length=50, primary_key=True, verbose_name='실행ID')
    run_type = models.CharField(max_length=20, verbose_name='실행유형')  # monthly, pi, bonus
    pay_period = models.CharField(max_length=7, verbose_name='급여기간')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='실행일시')
    formula_version = models.CharField(max_length=20, verbose_name='산식버전')
    affected_count = models.IntegerField(default=0, verbose_name='처리건수')
    changes = models.JSONField(default=dict, verbose_name='변경내역')
    errors = models.JSONField(default=list, verbose_name='오류내역')
    status = models.CharField(max_length=20, default='running', verbose_name='상태')
    
    class Meta:
        db_table = 'comp_calc_run_log'
        verbose_name = '계산 실행 로그'
        verbose_name_plural = '계산 실행 로그'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.run_id} - {self.pay_period} ({self.status})"


# ========================================
# 5. 직원 배정 테이블
# ========================================

class EmployeeCompensationProfile(models.Model):
    """직원 보상 프로파일 (현재 상태)"""
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True, verbose_name='직원')
    grade_code = models.ForeignKey(GradeMaster, on_delete=models.PROTECT, verbose_name='등급')
    position_code = models.ForeignKey(PositionMaster, on_delete=models.PROTECT, null=True, blank=True, verbose_name='직책')
    job_profile_id = models.ForeignKey(JobProfileMaster, on_delete=models.PROTECT, verbose_name='직무프로파일')
    competency_tier = models.CharField(max_length=5, verbose_name='역량등급')
    position_tier = models.CharField(max_length=5, null=True, blank=True, verbose_name='직책등급')
    position_start_date = models.DateField(null=True, blank=True, verbose_name='직책시작일')
    is_initial_position = models.BooleanField(default=False, verbose_name='초임여부')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        db_table = 'comp_employee_profile'
        verbose_name = '직원 보상 프로파일'
        verbose_name_plural = '직원 보상 프로파일'
        ordering = ['employee']
    
    def __str__(self):
        return f"{self.employee.name} - {self.grade_code}"
    
    @property
    def position_allowance_rate(self):
        """직책급 지급률 (초임 1년간 80%)"""
        if self.position_start_date and self.is_initial_position:
            days_since_start = (date.today() - self.position_start_date).days
            if days_since_start < 365:
                return 0.8
        return 1.0