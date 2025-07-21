from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import date, datetime
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation

# 승진 상태
PROMOTION_STATUS = [
    ('PENDING', '심사대기'),
    ('UNDER_REVIEW', '심사중'),
    ('APPROVED', '승인'),
    ('REJECTED', '반려'),
    ('CANCELLED', '취소'),
]

# 이동 유형
TRANSFER_TYPE = [
    ('PROMOTION', '승진'),
    ('LATERAL', '평이동'),
    ('DEMOTION', '강등'),
    ('ROTATION', '순환'),
    ('SPECIAL', '특별이동'),
]

# 승진 요건 타입
REQUIREMENT_TYPE = [
    ('YEARS_OF_SERVICE', '재직기간'),
    ('CONSECUTIVE_GRADES', '연속등급'),
    ('DEPARTMENT_RECOMMENDATION', '부서추천'),
    ('HR_COMMITTEE', 'HR위원회'),
    ('PERFORMANCE_SCORE', '성과점수'),
]


class PromotionRequirement(models.Model):
    """승진 요건 설정"""
    from_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name='현재 레벨'
    )
    to_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name='목표 레벨'
    )
    
    # 요건 설정
    min_years_required = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name='최소 재직기간 (년)'
    )
    consecutive_a_grades = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='연속 A등급 이상 (회)'
    )
    min_performance_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='최소 성과점수'
    )
    
    # 추가 요건
    department_recommendation_required = models.BooleanField(
        default=True,
        verbose_name='부서장 추천 필수'
    )
    hr_committee_required = models.BooleanField(
        default=True,
        verbose_name='HR위원회 심사 필수'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '승진 요건'
        verbose_name_plural = '승진 요건'
        unique_together = ['from_level', 'to_level']
        ordering = ['from_level', 'to_level']

    def __str__(self):
        return f"레벨 {self.from_level} → {self.to_level} 승진 요건"


class PromotionRequest(models.Model):
    """승진 심사 요청"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='promotion_requests',
        verbose_name='직원'
    )
    
    # 승진 정보
    current_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name='현재 레벨'
    )
    target_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name='목표 레벨'
    )
    
    # 평가 결과 (최근 3년)
    evaluation_results = models.JSONField(
        default=dict,
        verbose_name='평가 결과'
    )
    
    # 승진 요건 체크
    years_of_service = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name='재직기간 (년)'
    )
    consecutive_a_grades = models.IntegerField(
        verbose_name='연속 A등급 이상 (회)'
    )
    average_performance_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name='평균 성과점수'
    )
    
    # 요건 충족 여부
    years_requirement_met = models.BooleanField(
        default=False,
        verbose_name='재직기간 요건 충족'
    )
    grades_requirement_met = models.BooleanField(
        default=False,
        verbose_name='등급 요건 충족'
    )
    performance_requirement_met = models.BooleanField(
        default=False,
        verbose_name='성과 요건 충족'
    )
    
    # 심사 결과
    status = models.CharField(
        max_length=20,
        choices=PROMOTION_STATUS,
        default='PENDING',
        verbose_name='상태'
    )
    
    # 심사자 정보
    department_recommendation = models.BooleanField(
        default=False,
        verbose_name='부서장 추천'
    )
    department_recommender = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promotions_recommended',
        verbose_name='부서장'
    )
    department_recommendation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='부서장 추천일'
    )
    
    hr_committee_decision = models.CharField(
        max_length=20,
        choices=PROMOTION_STATUS,
        null=True,
        blank=True,
        verbose_name='HR위원회 결정'
    )
    hr_committee_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='HR위원회 심사일'
    )
    
    # 최종 결정
    final_decision = models.CharField(
        max_length=20,
        choices=PROMOTION_STATUS,
        null=True,
        blank=True,
        verbose_name='최종 결정'
    )
    final_decision_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='최종 결정일'
    )
    final_decision_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promotions_decided',
        verbose_name='최종 결정자'
    )
    
    # 의견
    employee_comments = models.TextField(
        blank=True,
        verbose_name='직원 의견'
    )
    department_comments = models.TextField(
        blank=True,
        verbose_name='부서장 의견'
    )
    hr_comments = models.TextField(
        blank=True,
        verbose_name='HR 의견'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '승진 요청'
        verbose_name_plural = '승진 요청'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.name} - 레벨 {self.current_level} → {self.target_level}"

    def calculate_requirements(self):
        """승진 요건 계산"""
        try:
            # 재직기간 계산
            hire_date = self.employee.hire_date
            if hire_date:
                years = (date.today() - hire_date).days / 365.25
                self.years_of_service = round(Decimal(str(years)), 1)
            else:
                self.years_of_service = Decimal('0.0')
            
            # 최근 3년 평가 결과 분석
            evaluations = ComprehensiveEvaluation.objects.filter(
                employee=self.employee
            ).order_by('-evaluation_period__year')[:3]
            
            self.evaluation_results = {}
            a_grades_count = 0
            total_score = 0
            evaluation_count = 0
            
            for eval in evaluations:
                year = eval.evaluation_period.year
                grade = eval.final_grade or eval.manager_grade
                
                # None 값 처리
                if grade is None:
                    grade = 'N/A'
                
                self.evaluation_results[year] = {
                    'grade': grade,
                    'contribution_achieved': eval.contribution_achieved or False,
                    'expertise_achieved': eval.expertise_achieved or False,
                    'impact_achieved': eval.impact_achieved or False,
                }
                
                if grade in ['S', 'A+', 'A']:
                    a_grades_count += 1
                
                # 성과점수 계산 (간단한 방식)
                score = 0
                if eval.contribution_achieved: score += 1
                if eval.expertise_achieved: score += 1
                if eval.impact_achieved: score += 1
                total_score += score
                evaluation_count += 1
            
            self.consecutive_a_grades = a_grades_count
            if evaluation_count > 0:
                self.average_performance_score = round(Decimal(str(total_score / evaluation_count)), 1)
            else:
                self.average_performance_score = Decimal('0.0')
            
            # 요건 충족 여부 확인
            requirement = PromotionRequirement.objects.filter(
                from_level=self.current_level,
                to_level=self.target_level
            ).first()
            
            if requirement:
                # None 값 안전 비교
                years_service = self.years_of_service or Decimal('0.0')
                min_years = requirement.min_years_required or Decimal('0.0')
                consecutive_grades = self.consecutive_a_grades or 0
                required_grades = requirement.consecutive_a_grades or 0
                avg_score = self.average_performance_score or Decimal('0.0')
                min_score = requirement.min_performance_score or Decimal('0.0')
                
                self.years_requirement_met = years_service >= min_years
                self.grades_requirement_met = consecutive_grades >= required_grades
                self.performance_requirement_met = avg_score >= min_score
            else:
                # 요건이 설정되지 않은 경우
                self.years_requirement_met = False
                self.grades_requirement_met = False
                self.performance_requirement_met = False
            
            self.save()
            
        except Exception as e:
            # 오류 발생 시 기본값 설정
            self.years_of_service = Decimal('0.0')
            self.consecutive_a_grades = 0
            self.average_performance_score = Decimal('0.0')
            self.years_requirement_met = False
            self.grades_requirement_met = False
            self.performance_requirement_met = False
            self.evaluation_results = {}
            self.save()
            print(f"승진 요건 계산 중 오류 발생: {str(e)}")

    def is_eligible_for_promotion(self):
        """승진 자격 여부 확인"""
        return (self.years_requirement_met and 
                self.grades_requirement_met and 
                self.performance_requirement_met)


class JobTransfer(models.Model):
    """인사이동"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='job_transfers',
        verbose_name='직원'
    )
    
    # 이동 정보
    from_department = models.CharField(
        max_length=100,
        verbose_name='이전 부서'
    )
    to_department = models.CharField(
        max_length=100,
        verbose_name='이동 부서'
    )
    from_position = models.CharField(
        max_length=100,
        verbose_name='이전 직책'
    )
    to_position = models.CharField(
        max_length=100,
        verbose_name='이동 직책'
    )
    
    # 이동 유형
    transfer_type = models.CharField(
        max_length=20,
        choices=TRANSFER_TYPE,
        verbose_name='이동 유형'
    )
    
    # 일정
    effective_date = models.DateField(
        verbose_name='발령일'
    )
    announcement_date = models.DateField(
        verbose_name='공고일'
    )
    
    # 승인 정보
    status = models.CharField(
        max_length=20,
        choices=PROMOTION_STATUS,
        default='PENDING',
        verbose_name='상태'
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers_approved',
        verbose_name='승인자'
    )
    approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='승인일'
    )
    
    # 사유
    reason = models.TextField(
        verbose_name='이동 사유'
    )
    additional_notes = models.TextField(
        blank=True,
        verbose_name='추가 비고'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '인사이동'
        verbose_name_plural = '인사이동'
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.employee.name} - {self.from_department} → {self.to_department}"

    def execute_transfer(self):
        """이동 실행"""
        if self.status == 'APPROVED':
            # 직원 정보 업데이트
            self.employee.department = self.to_department
            self.employee.position = self.to_position
            
            # 승진인 경우 레벨 업데이트
            if self.transfer_type == 'PROMOTION':
                self.employee.growth_level = min(6, self.employee.growth_level + 1)
            
            # 강등인 경우 레벨 다운데이트
            elif self.transfer_type == 'DEMOTION':
                self.employee.growth_level = max(1, self.employee.growth_level - 1)
            
            self.employee.save()
            return True
        return False


class OrganizationChart(models.Model):
    """조직도"""
    department = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='부서'
    )
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='상위 부서'
    )
    
    # 부서 정보
    department_head = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        verbose_name='부서장'
    )
    employee_count = models.IntegerField(
        default=0,
        verbose_name='직원 수'
    )
    
    # 조직도 표시 설정
    display_order = models.IntegerField(
        default=0,
        verbose_name='표시 순서'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='활성화'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '조직도'
        verbose_name_plural = '조직도'
        ordering = ['display_order', 'department']

    def __str__(self):
        return self.department

    def update_employee_count(self):
        """직원 수 업데이트"""
        count = Employee.objects.filter(department=self.department).count()
        self.employee_count = count
        self.save()
