from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from employees.models import Employee
# from evaluations.models import ComprehensiveEvaluation  # 일시적으로 주석 처리

# 직종 선택지
JOB_TYPE_CHOICES = [
    ('경영관리', '경영관리'),
    ('기업영업', '기업영업'),
    ('IT', 'IT'),
    ('리테일영업', '리테일영업'),
]

# 직책 선택지
POSITION_CHOICES = [
    ('팀장', '팀장'),
    ('지점장', '지점장'),
    ('부서장', '부서장'),
    ('이사', '이사'),
    ('상무', '상무'),
    ('전무', '전무'),
    ('부사장', '부사장'),
    ('사장', '사장'),
]

# 평가등급 선택지
EVALUATION_GRADE_CHOICES = [
    ('S', 'S등급'),
    ('A+', 'A+등급'),
    ('A', 'A등급'),
    ('B+', 'B+등급'),
    ('B', 'B등급'),
    ('C', 'C등급'),
    ('D', 'D등급'),
]


class SalaryTable(models.Model):
    """기본급 테이블 (성장레벨별)"""
    growth_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name='성장레벨'
    )
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='기본급 (원)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '기본급 테이블'
        verbose_name_plural = '기본급 테이블'
        unique_together = ['growth_level']
        ordering = ['growth_level']

    def __str__(self):
        return f"레벨 {self.growth_level} - {self.base_salary:,}원"


class CompetencyPayTable(models.Model):
    """역량급 테이블 (성장레벨 × 직종별)"""
    growth_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name='성장레벨'
    )
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        verbose_name='직종'
    )
    competency_pay = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='역량급 (원)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '역량급 테이블'
        verbose_name_plural = '역량급 테이블'
        unique_together = ['growth_level', 'job_type']
        ordering = ['growth_level', 'job_type']

    def __str__(self):
        return f"레벨 {self.growth_level} {self.job_type} - {self.competency_pay:,}원"


class PositionAllowance(models.Model):
    """직책급 테이블"""
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        unique=True,
        verbose_name='직책'
    )
    allowance_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='직책급 (원)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '직책급 테이블'
        verbose_name_plural = '직책급 테이블'
        ordering = ['allowance_amount']

    def __str__(self):
        return f"{self.position} - {self.allowance_amount:,}원"


class PerformanceIncentiveRate(models.Model):
    """성과급 지급률 테이블 (성장레벨별)"""
    growth_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name='성장레벨',
        default=1
    )
    evaluation_grade = models.CharField(
        max_length=5,
        choices=EVALUATION_GRADE_CHOICES,
        verbose_name='평가등급'
    )
    incentive_rate = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        verbose_name='지급률 (%)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '성과급 지급률'
        verbose_name_plural = '성과급 지급률'
        unique_together = ['growth_level', 'evaluation_grade']
        ordering = ['growth_level', '-incentive_rate']

    def __str__(self):
        return f"레벨 {self.growth_level} {self.evaluation_grade}등급 - {self.incentive_rate}%"


class EmployeeCompensation(models.Model):
    """직원별 보상"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='compensations',
        verbose_name='직원'
    )
    year = models.IntegerField(verbose_name='연도')
    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name='월'
    )
    
    # 기본급 정보
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='기본급 (원)'
    )
    
    # 고정OT (20시간)
    fixed_overtime = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='고정OT (원)'
    )
    
    # 역량급
    competency_pay = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='역량급 (원)'
    )
    
    # 직책급 (선택사항)
    position_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='직책급 (원)'
    )
    
    # 성과급 (PI)
    pi_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name='성과급 (원)'
    )
    
    # 총 보상
    total_compensation = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='총 보상 (원)'
    )
    
    # 평가 정보 (참조용) - 일시적으로 주석 처리
    # evaluation = models.ForeignKey(
    #     ComprehensiveEvaluation,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name='평가 정보'
    # )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '직원 보상'
        verbose_name_plural = '직원 보상'
        unique_together = ['employee', 'year', 'month']
        ordering = ['-year', '-month', 'employee__name']

    def __str__(self):
        return f"{self.employee.name} - {self.year}년 {self.month}월"

    def calculate_fixed_overtime(self):
        """고정OT 계산: 기본급 ÷ 209 × 1.5 × 20"""
        if self.base_salary:
            hourly_rate = self.base_salary / Decimal('209')
            overtime_rate = hourly_rate * Decimal('1.5')
            self.fixed_overtime = overtime_rate * Decimal('20')
        return self.fixed_overtime

    def calculate_pi_amount(self, evaluation_grade):
        """성과급 계산: 기본급 × (지급률 ÷ 100) ÷ 12 (성장레벨별)"""
        try:
            # 직원의 성장레벨 가져오기
            growth_level = self.employee.growth_level
            
            pi_rate = PerformanceIncentiveRate.objects.get(
                growth_level=growth_level,
                evaluation_grade=evaluation_grade
            )
            self.pi_amount = (self.base_salary * pi_rate.incentive_rate / Decimal('100')) / Decimal('12')
        except PerformanceIncentiveRate.DoesNotExist:
            # 해당 성장레벨의 지급률이 없으면 기본 지급률 사용
            try:
                pi_rate = PerformanceIncentiveRate.objects.get(
                    growth_level=1,  # 기본 레벨
                    evaluation_grade=evaluation_grade
                )
                self.pi_amount = (self.base_salary * pi_rate.incentive_rate / Decimal('100')) / Decimal('12')
            except PerformanceIncentiveRate.DoesNotExist:
                self.pi_amount = Decimal('0')
        return self.pi_amount

    def calculate_total_compensation(self):
        """총 보상 계산"""
        total = self.base_salary + self.fixed_overtime + self.competency_pay
        if self.position_allowance:
            total += self.position_allowance
        if self.pi_amount:
            total += self.pi_amount
        self.total_compensation = total
        return self.total_compensation

    def save(self, *args, **kwargs):
        """저장 시 자동 계산"""
        # 고정OT 계산
        self.calculate_fixed_overtime()
        
        # 총 보상 계산
        self.calculate_total_compensation()
        
        super().save(*args, **kwargs)
