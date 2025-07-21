# Step 4: 성과평가 모델 8개 구현 지시서

## 🎯 **작업 목표**
OK금융그룹 신인사제도 성과평가 프로세스를 완전 구현하는 8개 모델 생성

---

## 📝 **Cursor AI 작업 지시**

### **파일: `performance/models.py`**

아래 전체 코드를 `performance/models.py` 파일에 작성해주세요:

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from employees.models import Employee

# ============================================================================
# 1. 성장레벨별 평가 기준 모델
# ============================================================================

class GrowthLevelStandard(models.Model):
    """성장레벨별 평가 기준 정의"""
    job_group = models.CharField(
        max_length=20, 
        choices=[
            ('PL', 'PL직군'),
            ('Non-PL', 'Non-PL직군'),
        ]
    )
    job_type = models.CharField(max_length=50)
    level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text="성장레벨 1-6"
    )
    
    # 각 평가축별 기준
    contribution_criteria = models.TextField(
        help_text="기여도 평가 기준 및 요구 수준"
    )
    expertise_criteria = models.TextField(
        help_text="전문성 평가 기준 및 요구 수준"
    )
    impact_criteria = models.TextField(
        help_text="영향력 평가 기준 및 요구 수준"
    )
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.job_type} Level {self.level} 평가기준"
    
    class Meta:
        unique_together = ['job_type', 'level']
        ordering = ['job_type', 'level']
        verbose_name = '성장레벨 기준'
        verbose_name_plural = '성장레벨 기준 관리'


# ============================================================================
# 2. 평가 기간 관리 모델
# ============================================================================

class EvaluationPeriod(models.Model):
    """평가 기간 정의 및 관리"""
    year = models.IntegerField(help_text="평가 연도")
    period_type = models.CharField(
        max_length=20, 
        choices=[
            ('Q1', '1분기'),
            ('Q2', '2분기'), 
            ('Q3', '3분기'),
            ('Q4', '4분기'),
            ('H1', '상반기'),
            ('H2', '하반기'),
            ('ANNUAL', '연간'),
        ]
    )
    period_number = models.IntegerField(
        default=1,
        help_text="분기 번호 (1,2,3,4)"
    )
    
    # 기간 설정
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(
        default=False,
        help_text="현재 활성 평가기간 여부"
    )
    
    # 평가 상태
    status = models.CharField(
        max_length=20,
        choices=[
            ('PLANNING', '계획'),
            ('ONGOING', '진행중'),
            ('EVALUATION', '평가중'),
            ('COMPLETED', '완료'),
        ],
        default='PLANNING'
    )
    
    def __str__(self):
        return f"{self.year}년 {self.get_period_type_display()}"
    
    class Meta:
        unique_together = ['year', 'period_type', 'period_number']
        ordering = ['-year', 'period_type']
        verbose_name = '평가기간'
        verbose_name_plural = '평가기간 관리'


# ============================================================================
# 3. 업무 과제 관리 모델
# ============================================================================

class Task(models.Model):
    """개별 업무 과제 정의"""
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )
    evaluation_period = models.ForeignKey(
        EvaluationPeriod, 
        on_delete=models.CASCADE
    )
    
    # Task 기본 정보
    title = models.CharField(max_length=200, help_text="Task명")
    description = models.TextField(blank=True, help_text="상세 내용")
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="비중 (%)"
    )
    
    # OK금융그룹 기여방식 분류
    contribution_method = models.CharField(
        max_length=20, 
        choices=[
            ('충분', '충분'),
            ('리딩', '리딩'),
            ('실무', '실무'),
            ('지원', '지원'),
        ], 
        help_text="OK금융그룹 기여방식 분류"
    )
    
    # 목표 설정
    target_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="목표 수치"
    )
    target_unit = models.CharField(
        max_length=50, 
        default='억원', 
        help_text="목표 단위 (억원, 건수, % 등)"
    )
    
    # 실적 입력
    actual_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="실제 달성 수치"
    )
    achievement_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="달성률 (%)"
    )
    
    # 승인 워크플로우
    status = models.CharField(
        max_length=20, 
        choices=[
            ('DRAFT', '등록'),
            ('SUBMITTED', '제출'),
            ('APPROVED', '승인'),
            ('REJECTED', '반려'),
            ('COMPLETED', '완료'),
        ], 
        default='DRAFT'
    )
    
    approved_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_tasks',
        help_text="승인자"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_achievement_rate(self):
        """달성률 자동 계산"""
        if self.target_value and self.target_value > 0 and self.actual_value:
            self.achievement_rate = (self.actual_value / self.target_value) * 100
        return self.achievement_rate
    
    def get_contribution_score(self):
        """OK금융그룹 Scoring Chart 기반 점수 산출"""
        if not self.achievement_rate:
            return 0
            
        # OK금융그룹 실제 Scoring Chart 로직
        scoring_matrix = {
            '충분': {80: 2, 90: 3, 100: 4},
            '리딩': {70: 2, 80: 3, 90: 4}, 
            '실무': {60: 1, 70: 2, 80: 3},
            '지원': {50: 1, 60: 1, 70: 2},
        }
        
        method_scores = scoring_matrix.get(self.contribution_method, {})
        score = 1  # 기본 점수
        
        for threshold, points in sorted(method_scores.items()):
            if self.achievement_rate >= threshold:
                score = points
        
        return score
    
    def __str__(self):
        return f"{self.employee.name} - {self.title} ({self.weight}%)"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '업무과제'
        verbose_name_plural = '업무과제 관리'


# ============================================================================
# 4. 기여도 평가 모델
# ============================================================================

class ContributionEvaluation(models.Model):
    """기여도 평가 (업무 실적 기반)"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    evaluation_period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE)
    
    # 전체 성과 지표
    total_achievement_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="전체 Task 가중평균 달성률"
    )
    
    # OK금융그룹 기여도 점수 (1-4점)
    contribution_score = models.DecimalField(
        max_digits=3, 
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="기여도 종합 점수 (1-4점)"
    )
    
    # 달성 여부 (성장레벨 기준 대비)
    is_achieved = models.BooleanField(
        default=False,
        help_text="성장레벨 요구수준 달성 여부"
    )
    
    # 평가자 정보
    evaluator = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='contribution_evaluations_done'
    )
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    # 평가 의견
    comments = models.TextField(blank=True, help_text="평가 의견 및 피드백")
    
    def __str__(self):
        return f"{self.employee.name} 기여도평가 ({self.evaluation_period})"
    
    class Meta:
        unique_together = ['employee', 'evaluation_period']
        verbose_name = '기여도 평가'
        verbose_name_plural = '기여도 평가 관리'


# ============================================================================
# 5. 전문성 평가 모델
# ============================================================================

class ExpertiseEvaluation(models.Model):
    """전문성 평가 (직무 역량 기반)"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    evaluation_period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE)
    
    # 성장레벨 요구수준
    required_level = models.IntegerField(
        help_text="평가 기준이 되는 성장레벨"
    )
    
    # OK금융그룹 전문성 평가 항목
    strategic_contribution = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="전략적 기여 수준 (1-4점)"
    )
    interactive_contribution = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="상호적 기여 수준 (1-4점)"
    )
    
    # 추가 전문성 영역 (직종별 커스터마이징 가능)
    technical_expertise = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        default=3,
        help_text="기술적 전문성 (1-4점)"
    )
    business_understanding = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        default=3,
        help_text="업무 이해도 (1-4점)"
    )
    
    # 자가진단 의견
    self_assessment = models.TextField(
        blank=True, 
        help_text="자가진단 의견 및 근거"
    )
    
    # 총합 평가
    total_score = models.DecimalField(
        max_digits=3, 
        decimal_places=1,
        help_text="전문성 종합 점수"
    )
    is_achieved = models.BooleanField(
        default=False,
        help_text="성장레벨 요구수준 달성 여부"
    )
    
    # 평가자 정보
    evaluator = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='expertise_evaluations_done'
    )
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_total_score(self):
        """전문성 총점 자동 계산"""
        self.total_score = (
            self.strategic_contribution + 
            self.interactive_contribution + 
            self.technical_expertise + 
            self.business_understanding
        ) / 4
        return self.total_score
    
    def __str__(self):
        return f"{self.employee.name} 전문성평가 ({self.evaluation_period})"
    
    class Meta:
        unique_together = ['employee', 'evaluation_period']
        verbose_name = '전문성 평가'
        verbose_name_plural = '전문성 평가 관리'


# ============================================================================
# 6. 영향력 평가 모델
# ============================================================================

class ImpactEvaluation(models.Model):
    """영향력 평가 (핵심가치 및 리더십 기반)"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    evaluation_period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE)
    
    # OK금융그룹 핵심가치 평가 (각각 1-4점)
    customer_focus = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="고객중심 실천 수준 (1-4점)"
    )
    collaboration = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="상생협력 실천 수준 (1-4점)"
    )
    innovation = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="혁신도전 실천 수준 (1-4점)"
    )
    
    # 리더십 평가 (직급별 차등 적용)
    team_leadership = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="팀 리더십 발휘 수준 (1-4점)"
    )
    organizational_impact = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="조직 영향력 수준 (1-4점)"
    )
    external_networking = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="대외 네트워킹 수준 (1-4점)"
    )
    
    # 영향력 발휘 사례
    impact_examples = models.TextField(
        blank=True, 
        help_text="구체적인 영향력 발휘 사례"
    )
    
    # 총합 평가
    total_score = models.DecimalField(
        max_digits=3, 
        decimal_places=1,
        help_text="영향력 종합 점수"
    )
    is_achieved = models.BooleanField(
        default=False,
        help_text="성장레벨 요구수준 달성 여부"
    )
    
    # 평가자 정보
    evaluator = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='impact_evaluations_done'
    )
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_total_score(self):
        """영향력 총점 자동 계산"""
        core_values_avg = (
            self.customer_focus + 
            self.collaboration + 
            self.innovation
        ) / 3
        
        leadership_avg = (
            self.team_leadership + 
            self.organizational_impact + 
            self.external_networking
        ) / 3
        
        self.total_score = (core_values_avg + leadership_avg) / 2
        return self.total_score
    
    def __str__(self):
        return f"{self.employee.name} 영향력평가 ({self.evaluation_period})"
    
    class Meta:
        unique_together = ['employee', 'evaluation_period']
        verbose_name = '영향력 평가'
        verbose_name_plural = '영향력 평가 관리'


# ============================================================================
# 7. 종합 평가 모델 (최종 결과)
# ============================================================================

class ComprehensiveEvaluation(models.Model):
    """종합 평가 - 3대 평가축 통합 및 최종 등급 결정"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    evaluation_period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE)
    
    # 3대 평가 결과 참조
    contribution_evaluation = models.ForeignKey(
        ContributionEvaluation, 
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    expertise_evaluation = models.ForeignKey(
        ExpertiseEvaluation, 
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    impact_evaluation = models.ForeignKey(
        ImpactEvaluation, 
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    
    # 3대 평가축 달성 현황
    contribution_achieved = models.BooleanField(default=False)
    expertise_achieved = models.BooleanField(default=False)
    impact_achieved = models.BooleanField(default=False)
    
    # 1차 부서장 등급 (A/B/C - 자동 산출)
    manager_grade = models.CharField(
        max_length=1, 
        choices=[
            ('A', 'A - 기대 수준 초과 (2개 이상 달성)'),
            ('B', 'B - 기대 수준 상응 (1개 달성)'), 
            ('C', 'C - 기대 수준 이하 (전체 미달성)'),
        ],
        null=True, blank=True
    )
    manager_comments = models.TextField(
        blank=True, 
        help_text="부서장 평가 의견"
    )
    
    # 2차 Calibration Session 결과
    final_grade = models.CharField(
        max_length=2, 
        choices=[
            ('S', 'S - 업계 최고수준'),
            ('A+', 'A+ - 기대수준 매우 초과'),
            ('A', 'A - 기대수준 초과'),
            ('B+', 'B+ - 기대수준 이상'),
            ('B', 'B - 기대수준 부합'),
            ('C', 'C - 기대수준 미만'),
            ('D', 'D - 개선필요'),
        ], 
        null=True, blank=True
    )
    
    calibration_comments = models.TextField(
        blank=True, 
        help_text="Calibration Session 논의 내용"
    )
    
    # 평가자 정보
    manager = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='managed_evaluations'
    )
    calibration_committee = models.TextField(
        blank=True, 
        help_text="Calibration 참여 위원 목록"
    )
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def auto_calculate_manager_grade(self):
        """OK금융그룹 1차 등급 자동 산출 로직"""
        achieved_count = sum([
            self.contribution_achieved,
            self.expertise_achieved, 
            self.impact_achieved
        ])
        
        if achieved_count >= 2:
            self.manager_grade = 'A'
        elif achieved_count == 1:
            self.manager_grade = 'B'
        else:
            self.manager_grade = 'C'
        
        return self.manager_grade
    
    def get_calibration_target_group(self):
        """Calibration Session 논의 대상 그룹 확인"""
        calibration_groups = {
            'A': 'A등급 대상자 (S/A+/A 중 결정)',
            'B': 'B등급 대상자 (B+/B 중 결정)', 
            'C': 'C등급 대상자 (C/D 중 결정)'
        }
        return calibration_groups.get(self.manager_grade, '미분류')
    
    def __str__(self):
        grade_display = self.final_grade or self.manager_grade or '평가중'
        return f"{self.employee.name} 종합평가 ({self.evaluation_period}) - {grade_display}"
    
    class Meta:
        unique_together = ['employee', 'evaluation_period']
        ordering = ['-evaluation_period__year', '-updated_at']
        verbose_name = '종합 평가'
        verbose_name_plural = '종합 평가 관리'


# ============================================================================
# 8. 수시 Check-in 기록 모델
# ============================================================================

class CheckInRecord(models.Model):
    """수시 성과 관리를 위한 Check-in 기록"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    
    # Check-in 기본 정보
    check_date = models.DateField(help_text="체크인 날짜")
    progress_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="진행률 (%)"
    )
    current_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="현재 달성 수치"
    )
    
    # 상황 보고
    issues = models.TextField(
        blank=True, 
        help_text="현재 이슈사항 및 장애요인"
    )
    support_needed = models.TextField(
        blank=True, 
        help_text="필요한 지원사항"
    ) 
    next_action = models.TextField(
        blank=True, 
        help_text="향후 액션 플랜"
    )
    
    # 관리자 피드백
    manager_feedback = models.TextField(
        blank=True, 
        help_text="관리자 피드백 및 조언"
    )
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.task.title} Check-in ({self.check_date})"
    
    class Meta:
        ordering = ['-check_date']
        verbose_name = 'Check-in 기록'
        verbose_name_plural = 'Check-in 기록 관리'
```

---

## ✅ **완료 확인 체크리스트**

Step 4 구현 후 다음 사항들을 확인해주세요:

- [ ] `performance/models.py` 파일에 8개 모델 작성 완료
- [ ] 모든 모델에 적절한 필드 및 제약조건 설정
- [ ] OK금융그룹 평가 로직 (Scoring Chart, 1차/2차 평가) 반영
- [ ] 각 모델별 `__str__` 메서드 및 Meta 클래스 설정
- [ ] 문법 오류 없이 파일 저장 완료

---

## 🚀 **다음 단계: Admin 페이지 설정**

모델 구현 완료 후 **Admin 페이지 설정**을 진행하겠습니다!

**이 단계 완료되면 알려주세요!** 💪