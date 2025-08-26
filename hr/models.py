"""
포괄적인 인사정보 관리 시스템 모델
- 급여, 직급, 경력, 교육, 평가 등 종합 관리
"""

from django.db import models
from django.contrib.auth import get_user_model
from datetime import date
from decimal import Decimal

User = get_user_model()

# ========================================
# 1. 직급/직군 체계 (Job Structure)
# ========================================

class JobFamily(models.Model):
    """직군 (Job Family) - 대분류"""
    code = models.CharField(max_length=10, unique=True, verbose_name='직군코드')
    name = models.CharField(max_length=50, verbose_name='직군명')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='사용여부')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '직군'
        verbose_name_plural = '직군'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class JobCategory(models.Model):
    """직종 (Job Category) - 중분류"""
    job_family = models.ForeignKey(JobFamily, on_delete=models.CASCADE, related_name='categories')
    code = models.CharField(max_length=10, unique=True, verbose_name='직종코드')
    name = models.CharField(max_length=50, verbose_name='직종명')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='사용여부')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '직종'
        verbose_name_plural = '직종'
        ordering = ['job_family', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class JobPosition(models.Model):
    """직무 (Job Position) - 소분류"""
    job_category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='positions')
    code = models.CharField(max_length=20, unique=True, verbose_name='직무코드')
    name = models.CharField(max_length=100, verbose_name='직무명')
    description = models.TextField(blank=True, verbose_name='직무설명')
    required_skills = models.TextField(blank=True, verbose_name='필요역량')
    is_active = models.BooleanField(default=True, verbose_name='사용여부')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '직무'
        verbose_name_plural = '직무'
        ordering = ['job_category', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class JobGrade(models.Model):
    """직급 (Job Grade)"""
    code = models.CharField(max_length=10, unique=True, verbose_name='직급코드')
    name = models.CharField(max_length=50, verbose_name='직급명')
    level = models.IntegerField(verbose_name='직급레벨')  # 1: 회장, 2: 사장, ... 10: 사원
    min_years = models.IntegerField(default=0, verbose_name='최소근속년수')
    max_years = models.IntegerField(null=True, blank=True, verbose_name='최대근속년수')
    is_executive = models.BooleanField(default=False, verbose_name='임원여부')
    is_active = models.BooleanField(default=True, verbose_name='사용여부')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '직급'
        verbose_name_plural = '직급'
        ordering = ['level']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ========================================
# 2. 급여 관리 (Compensation)
# ========================================

class SalaryGrade(models.Model):
    """급여 등급 테이블"""
    grade_code = models.CharField(max_length=10, unique=True, verbose_name='급여등급')
    grade_name = models.CharField(max_length=50, verbose_name='등급명')
    min_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='최소금액')
    max_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='최대금액')
    midpoint = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='중간값')
    is_active = models.BooleanField(default=True, verbose_name='사용여부')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '급여등급'
        verbose_name_plural = '급여등급'
        ordering = ['grade_code']
    
    def __str__(self):
        return f"{self.grade_code} - {self.grade_name}"


class BaseSalary(models.Model):
    """기본급 테이블"""
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='base_salaries')
    salary_grade = models.ForeignKey(SalaryGrade, on_delete=models.PROTECT, null=True, blank=True)
    base_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='기본급')
    effective_date = models.DateField(verbose_name='적용시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='적용종료일')
    adjustment_reason = models.CharField(max_length=200, blank=True, verbose_name='조정사유')
    is_active = models.BooleanField(default=True, verbose_name='현재적용여부')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = '기본급'
        verbose_name_plural = '기본급'
        ordering = ['-effective_date']
        unique_together = ['employee', 'effective_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.base_amount:,.0f}원"


class PerformanceBonus(models.Model):
    """성과급 테이블"""
    BONUS_TYPE_CHOICES = [
        ('ANNUAL', '연간성과급'),
        ('QUARTERLY', '분기성과급'),
        ('PROJECT', '프로젝트성과급'),
        ('SPECIAL', '특별성과급'),
        ('INCENTIVE', '인센티브'),
    ]
    
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='performance_bonuses')
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPE_CHOICES, verbose_name='성과급유형')
    evaluation_period = models.CharField(max_length=50, verbose_name='평가기간')
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='성과점수')
    bonus_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='성과급액')
    payment_date = models.DateField(verbose_name='지급일')
    description = models.TextField(blank=True, verbose_name='설명')
    is_paid = models.BooleanField(default=False, verbose_name='지급완료여부')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = '성과급'
        verbose_name_plural = '성과급'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.get_bonus_type_display()} - {self.bonus_amount:,.0f}원"


class Allowance(models.Model):
    """수당 테이블"""
    ALLOWANCE_TYPE_CHOICES = [
        ('MEAL', '식대'),
        ('TRANSPORT', '교통비'),
        ('HOUSING', '주택수당'),
        ('FAMILY', '가족수당'),
        ('OVERTIME', '시간외수당'),
        ('POSITION', '직책수당'),
        ('SKILL', '자격수당'),
        ('DANGER', '위험수당'),
        ('NIGHT', '야간수당'),
        ('OTHER', '기타'),
    ]
    
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='allowances')
    allowance_type = models.CharField(max_length=20, choices=ALLOWANCE_TYPE_CHOICES, verbose_name='수당유형')
    amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='수당금액')
    effective_date = models.DateField(verbose_name='적용시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='적용종료일')
    is_taxable = models.BooleanField(default=True, verbose_name='과세여부')
    is_active = models.BooleanField(default=True, verbose_name='현재적용여부')
    note = models.TextField(blank=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '수당'
        verbose_name_plural = '수당'
        ordering = ['employee', 'allowance_type']
        unique_together = ['employee', 'allowance_type', 'effective_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.get_allowance_type_display()} - {self.amount:,.0f}원"


# ========================================
# 3. 경력 관리 (Career Management)
# ========================================

class CareerHistory(models.Model):
    """경력 이력 테이블"""
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='career_histories')
    company = models.CharField(max_length=100, verbose_name='회사명')
    department = models.CharField(max_length=100, verbose_name='부서')
    position = models.CharField(max_length=100, verbose_name='직위')
    job_description = models.TextField(verbose_name='담당업무')
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='종료일')
    is_current = models.BooleanField(default=False, verbose_name='현재재직중')
    reason_for_leaving = models.TextField(blank=True, verbose_name='퇴사사유')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '경력이력'
        verbose_name_plural = '경력이력'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.company} - {self.position}"


class PromotionHistory(models.Model):
    """승진 이력 테이블"""
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='promotion_histories')
    from_grade = models.ForeignKey(JobGrade, on_delete=models.PROTECT, related_name='promotions_from', verbose_name='이전직급')
    to_grade = models.ForeignKey(JobGrade, on_delete=models.PROTECT, related_name='promotions_to', verbose_name='승진직급')
    promotion_date = models.DateField(verbose_name='승진일')
    promotion_type = models.CharField(max_length=50, verbose_name='승진유형')  # 정기승진, 특별승진 등
    evaluation_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='평가점수')
    note = models.TextField(blank=True, verbose_name='비고')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '승진이력'
        verbose_name_plural = '승진이력'
        ordering = ['-promotion_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.from_grade.name} → {self.to_grade.name}"


# ========================================
# 4. 교육 및 자격 (Education & Certification)
# ========================================

class Education(models.Model):
    """학력 정보 테이블"""
    DEGREE_CHOICES = [
        ('HIGH', '고졸'),
        ('COLLEGE', '전문대졸'),
        ('BACHELOR', '대졸'),
        ('MASTER', '석사'),
        ('DOCTOR', '박사'),
    ]
    
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES, verbose_name='학위')
    school_name = models.CharField(max_length=100, verbose_name='학교명')
    major = models.CharField(max_length=100, blank=True, verbose_name='전공')
    graduation_date = models.DateField(null=True, blank=True, verbose_name='졸업일')
    is_graduated = models.BooleanField(default=True, verbose_name='졸업여부')
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name='학점')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '학력'
        verbose_name_plural = '학력'
        ordering = ['-graduation_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.school_name} - {self.get_degree_display()}"


class Certification(models.Model):
    """자격증 정보 테이블"""
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='certifications')
    cert_name = models.CharField(max_length=100, verbose_name='자격증명')
    issuing_org = models.CharField(max_length=100, verbose_name='발급기관')
    cert_number = models.CharField(max_length=50, blank=True, verbose_name='자격증번호')
    issue_date = models.DateField(verbose_name='취득일')
    expiry_date = models.DateField(null=True, blank=True, verbose_name='만료일')
    is_valid = models.BooleanField(default=True, verbose_name='유효여부')
    cert_allowance = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='자격수당')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '자격증'
        verbose_name_plural = '자격증'
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.cert_name}"


class Training(models.Model):
    """교육 이수 테이블"""
    TRAINING_TYPE_CHOICES = [
        ('INTERNAL', '사내교육'),
        ('EXTERNAL', '사외교육'),
        ('ONLINE', '온라인교육'),
        ('CONFERENCE', '컨퍼런스'),
        ('WORKSHOP', '워크샵'),
    ]
    
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='trainings')
    training_name = models.CharField(max_length=200, verbose_name='교육명')
    training_type = models.CharField(max_length=20, choices=TRAINING_TYPE_CHOICES, verbose_name='교육유형')
    institution = models.CharField(max_length=100, verbose_name='교육기관')
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    hours = models.IntegerField(verbose_name='교육시간')
    cost = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='교육비')
    is_completed = models.BooleanField(default=False, verbose_name='수료여부')
    certificate_issued = models.BooleanField(default=False, verbose_name='수료증발급여부')
    note = models.TextField(blank=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '교육이수'
        verbose_name_plural = '교육이수'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.training_name}"


# ========================================
# 5. 평가 관리 (Performance Evaluation)
# ========================================

class PerformanceEvaluation(models.Model):
    """인사평가 테이블"""
    EVALUATION_TYPE_CHOICES = [
        ('ANNUAL', '연간평가'),
        ('MID_YEAR', '중간평가'),
        ('QUARTERLY', '분기평가'),
        ('PROJECT', '프로젝트평가'),
        ('PROBATION', '수습평가'),
    ]
    
    RATING_CHOICES = [
        ('S', 'S (탁월)'),
        ('A', 'A (우수)'),
        ('B', 'B (양호)'),
        ('C', 'C (보통)'),
        ('D', 'D (미흡)'),
    ]
    
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='performance_evaluations')
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPE_CHOICES, verbose_name='평가유형')
    evaluation_period = models.CharField(max_length=50, verbose_name='평가기간')
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='evaluations_given')
    
    # 평가 항목
    job_performance_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='업무성과')
    competency_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='역량평가')
    attitude_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='태도평가')
    total_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='종합점수')
    rating = models.CharField(max_length=1, choices=RATING_CHOICES, verbose_name='등급')
    
    # 피드백
    strengths = models.TextField(blank=True, verbose_name='강점')
    improvements = models.TextField(blank=True, verbose_name='개선사항')
    development_plan = models.TextField(blank=True, verbose_name='육성계획')
    
    # 관리 필드
    is_finalized = models.BooleanField(default=False, verbose_name='확정여부')
    finalized_date = models.DateTimeField(null=True, blank=True, verbose_name='확정일')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '인사평가'
        verbose_name_plural = '인사평가'
        ordering = ['-evaluation_period']
        unique_together = ['employee', 'evaluation_type', 'evaluation_period']
    
    def __str__(self):
        return f"{self.employee.name} - {self.evaluation_period} - {self.rating}"


# ========================================
# 6. 복리후생 (Benefits)
# ========================================

class Benefit(models.Model):
    """복리후생 마스터 테이블"""
    code = models.CharField(max_length=20, unique=True, verbose_name='복리후생코드')
    name = models.CharField(max_length=100, verbose_name='복리후생명')
    category = models.CharField(max_length=50, verbose_name='카테고리')
    description = models.TextField(verbose_name='설명')
    eligibility_criteria = models.TextField(verbose_name='자격요건')
    is_active = models.BooleanField(default=True, verbose_name='사용여부')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '복리후생'
        verbose_name_plural = '복리후생'
        ordering = ['category', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class EmployeeBenefit(models.Model):
    """직원 복리후생 적용 테이블"""
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='employee_benefits')
    benefit = models.ForeignKey(Benefit, on_delete=models.CASCADE)
    enrollment_date = models.DateField(verbose_name='가입일')
    termination_date = models.DateField(null=True, blank=True, verbose_name='종료일')
    is_active = models.BooleanField(default=True, verbose_name='활성여부')
    usage_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='사용금액')
    note = models.TextField(blank=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '직원복리후생'
        verbose_name_plural = '직원복리후생'
        ordering = ['employee', 'benefit']
        unique_together = ['employee', 'benefit', 'enrollment_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.benefit.name}"


# ========================================
# 7. 급여 계산 통합 뷰
# ========================================

class MonthlySalary(models.Model):
    """월급여 계산 테이블 (통합 급여 정보)"""
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='monthly_salaries')
    year = models.IntegerField(verbose_name='년도')
    month = models.IntegerField(verbose_name='월')
    
    # 급여 구성
    base_salary = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='기본급')
    position_allowance = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='직책수당')
    meal_allowance = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='식대')
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='교통비')
    other_allowances = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='기타수당')
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='시간외수당')
    bonus = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='상여금')
    
    # 공제 항목
    income_tax = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='소득세')
    local_tax = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='지방소득세')
    national_pension = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='국민연금')
    health_insurance = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='건강보험')
    employment_insurance = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='고용보험')
    other_deductions = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='기타공제')
    
    # 총계
    gross_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='총지급액')
    total_deductions = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='총공제액')
    net_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='실지급액')
    
    # 관리 필드
    is_paid = models.BooleanField(default=False, verbose_name='지급완료')
    payment_date = models.DateField(null=True, blank=True, verbose_name='지급일')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '월급여'
        verbose_name_plural = '월급여'
        ordering = ['-year', '-month']
        unique_together = ['employee', 'year', 'month']
    
    def __str__(self):
        return f"{self.employee.name} - {self.year}년 {self.month}월 - {self.net_amount:,.0f}원"
    
    def calculate_totals(self):
        """급여 총계 자동 계산"""
        # 총 지급액 계산
        self.gross_amount = (
            self.base_salary + 
            self.position_allowance + 
            self.meal_allowance + 
            self.transport_allowance + 
            self.other_allowances + 
            self.overtime_pay + 
            self.bonus
        )
        
        # 총 공제액 계산
        self.total_deductions = (
            self.income_tax + 
            self.local_tax + 
            self.national_pension + 
            self.health_insurance + 
            self.employment_insurance + 
            self.other_deductions
        )
        
        # 실지급액 계산
        self.net_amount = self.gross_amount - self.total_deductions
        
    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)
