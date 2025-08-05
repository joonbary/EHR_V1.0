from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import date
from employees.models import Employee

# Scoring Chart 데이터 추가
CONTRIBUTION_SCORING_CHART = {
    'strategic': {'directing': 4, 'leading': 4, 'individual': 3, 'support': 2},
    'mutual': {'directing': 3, 'leading': 3, 'individual': 3, 'support': 2},
    'independent': {'directing': 2, 'leading': 3, 'individual': 2, 'support': 1},
    'dependent': {'directing': 2, 'leading': 2, 'individual': 1, 'support': 1}
}

EXPERTISE_SCORING_CHART = {
    'hard_skill': {
        'creative': 4, 'advisory': 3, 'apply': 2, 'understand': 1
    },
    'balanced': {
        'creative': 4, 'advisory': 4, 'apply': 3, 'understand': 2
    }
}

IMPACT_SCORING_CHART = {
    'market': {'exemplary_leadership': 4, 'limited_leadership': 4, 
               'exemplary_values': 3, 'limited_values': 2},
    'corp': {'exemplary_leadership': 3, 'limited_leadership': 4, 
             'exemplary_values': 3, 'limited_values': 2},
    'org': {'exemplary_leadership': 2, 'limited_leadership': 3, 
            'exemplary_values': 3, 'limited_values': 3},
    'individual': {'exemplary_leadership': 1, 'limited_leadership': 2, 
                   'exemplary_values': 2, 'limited_values': 2}
}

# 평가 등급 선택지
GRADE_CHOICES = [
    ('S', 'S등급'),
    ('A+', 'A+등급'),
    ('A', 'A등급'),
    ('B+', 'B+등급'),
    ('B', 'B등급'),
    ('C', 'C등급'),
    ('D', 'D등급'),
]

# 평가 상태
EVALUATION_STATUS = [
    ('DRAFT', '작성중'),
    ('SUBMITTED', '제출완료'),
    ('IN_REVIEW', '검토중'),
    ('COMPLETED', '확정'),
]

# 평가 기간 타입
PERIOD_TYPE_CHOICES = [
    ('Q1', '1분기'),
    ('Q2', '2분기'),
    ('Q3', '3분기'),
    ('Q4', '4분기'),
    ('HALF1', '상반기'),
    ('HALF2', '하반기'),
    ('ANNUAL', '연간'),
]


class EvaluationPeriod(models.Model):
    """평가 기간"""
    year = models.IntegerField(verbose_name='연도')
    period_type = models.CharField(
        max_length=10,
        choices=PERIOD_TYPE_CHOICES,
        verbose_name='평가기간 타입'
    )
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    is_active = models.BooleanField(default=False, verbose_name='활성화')
    status = models.CharField(
        max_length=20,
        choices=[
            ('PLANNING', '계획중'),
            ('ONGOING', '진행중'),
            ('COMPLETED', '완료'),
        ],
        default='PLANNING',
        verbose_name='상태'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '평가기간'
        verbose_name_plural = '평가기간'
        unique_together = ['year', 'period_type']
        ordering = ['-year', 'period_type']

    def __str__(self):
        return f"{self.year}년 {self.get_period_type_display()}"


class Task(models.Model):
    """업무 과제 (기여도 평가용)"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='직원'
    )
    evaluation_period = models.ForeignKey(
        EvaluationPeriod,
        on_delete=models.CASCADE,
        verbose_name='평가기간'
    )
    title = models.CharField(max_length=200, verbose_name='과제명')
    description = models.TextField(blank=True, verbose_name='과제설명')
    
    # Task 유형 추가
    contribution_type = models.CharField(
        max_length=20,
        choices=[
            ('strategic', '전략과제'),
            ('improvement', '개선과제'),
            ('operation', '운영과제'),
            ('project', '프로젝트'),
        ],
        default='operation',
        verbose_name='과제유형'
    )
    
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='비중(%)'
    )
    contribution_method = models.CharField(
        max_length=20,
        choices=[
            ('directing', '총괄'),
            ('leading', '리딩'),
            ('individual', '실무'),
            ('support', '지원'),
        ],
        default='leading',
        verbose_name='기여방식'
    )
    contribution_scope = models.CharField(
        max_length=20,
        choices=[
            ('strategic', '전략적'),
            ('mutual', '상호적'),
            ('independent', '독립적'),
            ('dependent', '의존적'),
        ],
        default='independent',
        verbose_name='기여범위'
    )
    
    # 목표 및 실적
    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='목표값'
    )
    target_unit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='단위'
    )
    actual_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='실적값'
    )
    achievement_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='달성률(%)'
    )
    
    # Scoring 관련 필드 추가
    base_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        null=True,
        blank=True,
        verbose_name='기본점수',
        help_text='Scoring Chart 기반 기본점수'
    )
    
    final_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        null=True,
        blank=True,
        verbose_name='최종점수',
        help_text='달성률을 반영한 최종점수'
    )
    
    # Check-in 기록
    last_checkin_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='마지막 체크인'
    )
    checkin_count = models.IntegerField(
        default=0,
        verbose_name='체크인 횟수'
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('PLANNED', '계획'),
            ('IN_PROGRESS', '진행중'),
            ('COMPLETED', '완료'),
        ],
        default='PLANNED',
        verbose_name='상태'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-weight', 'title']

    def __str__(self):
        return f"{self.employee.name} - {self.title}"

    def calculate_achievement_rate(self):
        """달성률 계산"""
        if self.target_value and self.actual_value and self.target_value > 0:
            rate = (self.actual_value / self.target_value) * 100
            self.achievement_rate = round(rate, 2)
        return self.achievement_rate

    def calculate_contribution_score(self):
        """Scoring Chart를 활용한 기여도 점수 계산"""
        if self.contribution_scope in CONTRIBUTION_SCORING_CHART:
            scope_chart = CONTRIBUTION_SCORING_CHART[self.contribution_scope]
            if self.contribution_method in scope_chart:
                base_score = scope_chart[self.contribution_method]
                self.base_score = base_score
                
                # 달성률에 따른 점수 조정
                if self.achievement_rate:
                    if self.achievement_rate >= 100:
                        final_score = base_score
                    elif self.achievement_rate >= 90:
                        final_score = base_score - 0.5
                    elif self.achievement_rate >= 80:
                        final_score = base_score - 1.0
                    elif self.achievement_rate >= 70:
                        final_score = base_score - 1.5
                    else:
                        final_score = max(1.0, base_score - 2.0)
                    
                    self.final_score = round(final_score, 1)
                    self.save()
                    return self.final_score
                else:
                    self.final_score = base_score
                    self.save()
                    return base_score
        
        # 기본값
        self.base_score = 2.0
        self.final_score = 2.0
        self.save()
        return 2.0
    
    def checkin(self, progress_note=None):
        """Task Check-in 수행"""
        from django.utils import timezone
        
        self.last_checkin_date = timezone.now()
        self.checkin_count += 1
        
        # 진행중 상태로 자동 변경
        if self.status == 'PLANNED':
            self.status = 'IN_PROGRESS'
        
        self.save()
        
        # TODO: Check-in 이력 기록 (별도 모델 필요시)
        return True


class ContributionEvaluation(models.Model):
    """기여도 평가"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='contribution_evaluations',
        verbose_name='직원'
    )
    evaluation_period = models.ForeignKey(
        EvaluationPeriod,
        on_delete=models.CASCADE,
        verbose_name='평가기간'
    )
    
    # 평가 결과
    total_achievement_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='종합달성률(%)'
    )
    contribution_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='기여도 점수'
    )
    is_achieved = models.BooleanField(
        default=False,
        verbose_name='달성여부'
    )
    
    # 평가자 정보
    evaluator = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contribution_evaluations_given',
        verbose_name='평가자'
    )
    evaluated_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='평가일'
    )
    comments = models.TextField(blank=True, verbose_name='평가의견')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '기여도 평가'
        verbose_name_plural = '기여도 평가'
        unique_together = ['employee', 'evaluation_period']

    def __str__(self):
        return f"{self.employee.name} - {self.evaluation_period} 기여도"

    def calculate_from_tasks(self):
        """Task 기반으로 기여도 평가 자동 계산"""
        tasks = self.employee.tasks.filter(evaluation_period=self.evaluation_period)
        
        if not tasks.exists():
            return
        
        # 종합 달성률 계산
        total_weight = sum(task.weight for task in tasks)
        weighted_achievement = 0
        
        for task in tasks:
            task.calculate_achievement_rate()
            if task.achievement_rate:
                weighted_achievement += (task.achievement_rate * task.weight)
        
        if total_weight > 0:
            self.total_achievement_rate = round(weighted_achievement / total_weight, 2)
        
        # 기여도 점수 계산 (Task별 점수의 가중 평균)
        weighted_score = 0
        for task in tasks:
            task_score = task.calculate_contribution_score()
            weighted_score += (task_score * task.weight)
        
        if total_weight > 0:
            self.contribution_score = round(weighted_score / total_weight, 1)
        
        # 달성 여부 판정 (점수 3.0 이상 또는 달성률 100% 이상)
        self.is_achieved = (self.contribution_score >= 3.0 or 
                           (self.total_achievement_rate and self.total_achievement_rate >= 100))
        
        self.save()


class ExpertiseEvaluation(models.Model):
    """전문성 평가"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='expertise_evaluations',
        verbose_name='직원'
    )
    evaluation_period = models.ForeignKey(
        EvaluationPeriod,
        on_delete=models.CASCADE,
        verbose_name='평가기간'
    )
    
    # 평가 항목 (1-4점)
    required_level = models.IntegerField(
        verbose_name='요구 레벨',
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    
    # 전문성 평가 체크리스트 (10개 항목)
    expertise_focus = models.CharField(
        max_length=20,
        choices=[
            ('hard_skill', 'Hard Skill Focused'),
            ('balanced', 'Balanced'),
        ],
        default='balanced',
        verbose_name='전문성 초점'
    )
    
    # 10개 체크리스트 항목
    creative_solution = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='창의적 해결방안 제시',
        help_text='1: 이해, 2: 적용, 3: 자문, 4: 창의',
        default=2
    )
    technical_innovation = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='기술적 혁신',
        help_text='1: 이해, 2: 적용, 3: 자문, 4: 창의',
        default=2
    )
    process_improvement = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='프로세스 개선',
        help_text='1: 이해, 2: 적용, 3: 자문, 4: 창의',
        default=2
    )
    knowledge_sharing = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='지식 공유',
        help_text='1: 이해, 2: 적용, 3: 자문, 4: 창의',
        default=2
    )
    mentoring = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='멘토링',
        help_text='1: 이해, 2: 적용, 3: 자문, 4: 창의',
        default=2
    )
    cross_functional = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='크로스펑셔널 협업',
        help_text='1: 이해, 2: 적용, 3: 자문, 4: 창의',
        default=2
    )
    strategic_thinking = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='전략적 사고',
        help_text='1: 이해, 2: 적용, 3: 자문, 4: 창의',
        default=2
    )
    business_acumen = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='비즈니스 감각',
        help_text='1: 이해, 2: 적용, 3: 자문, 4: 창의',
        default=2
    )
    industry_trend = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='산업 트렌드 파악',
        help_text='1: 이해, 2: 적용, 3: 자문, 4: 창의',
        default=2
    )
    continuous_learning = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='지속적 학습',
        help_text='1: 이해, 2: 적용, 3: 자문, 4: 창의',
        default=2
    )
    
    # 기존 필드들 (하위 호환성 유지)
    strategic_contribution = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='전략적 기여'
    )
    interactive_contribution = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='상호작용 기여'
    )
    technical_expertise = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='기술 전문성'
    )
    business_understanding = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='비즈니스 이해'
    )
    
    # 평가 결과
    total_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name='종합점수'
    )
    is_achieved = models.BooleanField(
        default=False,
        verbose_name='달성여부'
    )
    
    # 평가자 정보
    evaluator = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='expertise_evaluations_given',
        verbose_name='평가자'
    )
    evaluated_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='평가일'
    )
    comments = models.TextField(blank=True, verbose_name='평가의견')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '전문성 평가'
        verbose_name_plural = '전문성 평가'
        unique_together = ['employee', 'evaluation_period']

    def __str__(self):
        return f"{self.employee.name} - {self.evaluation_period} 전문성"

    def calculate_total_score(self):
        """종합점수 계산 - 새로운 체크리스트 기반"""
        # 10개 체크리스트 항목 점수
        checklist_scores = [
            self.creative_solution,
            self.technical_innovation,
            self.process_improvement,
            self.knowledge_sharing,
            self.mentoring,
            self.cross_functional,
            self.strategic_thinking,
            self.business_acumen,
            self.industry_trend,
            self.continuous_learning
        ]
        
        # 체크리스트 평균 점수
        checklist_avg = sum(checklist_scores) / len(checklist_scores)
        
        # 기존 4개 항목 점수 (하위 호환성)
        legacy_scores = [
            self.strategic_contribution,
            self.interactive_contribution,
            self.technical_expertise,
            self.business_understanding
        ]
        legacy_avg = sum(legacy_scores) / len(legacy_scores)
        
        # 체크리스트 점수 우선 적용 (새로운 평가 방식)
        self.total_score = round(checklist_avg, 1)
        
        # 달성 여부 판정 (점수 3.0 이상)
        self.is_achieved = self.total_score >= 3.0
        
        return self.total_score


class ImpactEvaluation(models.Model):
    """영향력 평가"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='impact_evaluations',
        verbose_name='직원'
    )
    evaluation_period = models.ForeignKey(
        EvaluationPeriod,
        on_delete=models.CASCADE,
        verbose_name='평가기간'
    )
    
    # 영향력 범위
    impact_scope = models.CharField(
        max_length=20,
        choices=[
            ('market', '조직외'),
            ('corp', '조직간'),
            ('org', '조직내'),
            ('individual', '개인간'),
        ],
        default='org',
        verbose_name='영향력 범위'
    )
    
    # 핵심가치 실천 + 리더십 발휘 평가
    core_values_practice = models.CharField(
        max_length=20,
        choices=[
            ('exemplary_values', '핵심가치 모범 실천'),
            ('limited_values', '핵심가치 제한적 실천'),
        ],
        default='limited_values',
        verbose_name='핵심가치 실천'
    )
    leadership_demonstration = models.CharField(
        max_length=20,
        choices=[
            ('exemplary_leadership', '리더십 모범 발휘'),
            ('limited_leadership', '리더십 제한적 발휘'),
        ],
        default='limited_leadership',
        verbose_name='리더십 발휘'
    )
    
    # 기존 평가 항목들 (하위 호환성 유지)
    customer_focus = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='고객중심'
    )
    collaboration = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='협업'
    )
    innovation = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='혁신'
    )
    team_leadership = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='팀 리더십'
    )
    organizational_impact = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='조직 영향력'
    )
    external_networking = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='대외 네트워킹'
    )
    
    # 평가 결과
    total_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name='종합점수'
    )
    is_achieved = models.BooleanField(
        default=False,
        verbose_name='달성여부'
    )
    
    # 평가자 정보
    evaluator = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='impact_evaluations_given',
        verbose_name='평가자'
    )
    evaluated_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='평가일'
    )
    comments = models.TextField(blank=True, verbose_name='평가의견')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '영향력 평가'
        verbose_name_plural = '영향력 평가'
        unique_together = ['employee', 'evaluation_period']

    def __str__(self):
        return f"{self.employee.name} - {self.evaluation_period} 영향력"

    def calculate_total_score(self):
        """종합점수 계산 - 새로운 영향력 평가 방식"""
        from .models import IMPACT_SCORING_CHART
        
        # Scoring Chart 기반 점수 계산
        if self.impact_scope in IMPACT_SCORING_CHART:
            scope_chart = IMPACT_SCORING_CHART[self.impact_scope]
            
            # 핵심가치 실천 점수
            values_score = scope_chart.get(self.core_values_practice, 2)
            
            # 리더십 발휘 점수
            leadership_score = scope_chart.get(self.leadership_demonstration, 2)
            
            # 새로운 평가 방식 점수 (가중 평균)
            new_score = (values_score + leadership_score) / 2
            
            # 기존 6개 항목 점수 (하위 호환성)
            legacy_scores = [
                self.customer_focus,
                self.collaboration,
                self.innovation,
                self.team_leadership,
                self.organizational_impact,
                self.external_networking
            ]
            legacy_avg = sum(legacy_scores) / len(legacy_scores)
            
            # 새로운 평가 방식 우선 적용
            self.total_score = round(new_score, 1)
            
            # 달성 여부 판정 (점수 3.0 이상)
            self.is_achieved = self.total_score >= 3.0
            
            return self.total_score
        
        # Scoring Chart에 없는 경우 기존 방식 사용
        scores = [
            self.customer_focus,
            self.collaboration,
            self.innovation,
            self.team_leadership,
            self.organizational_impact,
            self.external_networking
        ]
        self.total_score = round(sum(scores) / len(scores), 1)
        return self.total_score


class ComprehensiveEvaluation(models.Model):
    """종합 평가"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='comprehensive_evaluations',
        verbose_name='직원'
    )
    evaluation_period = models.ForeignKey(
        EvaluationPeriod,
        on_delete=models.CASCADE,
        verbose_name='평가기간'
    )
    
    # 각 평가 연결
    contribution_evaluation = models.ForeignKey(
        ContributionEvaluation,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='기여도 평가'
    )
    expertise_evaluation = models.ForeignKey(
        ExpertiseEvaluation,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='전문성 평가'
    )
    impact_evaluation = models.ForeignKey(
        ImpactEvaluation,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='영향력 평가'
    )
    
    # 각 평가 점수 (캐시용)
    contribution_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='기여도 점수'
    )
    expertise_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='전문성 점수'
    )
    impact_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='영향력 점수'
    )
    
    # 달성 여부
    contribution_achieved = models.BooleanField(
        default=False,
        verbose_name='기여도 달성'
    )
    expertise_achieved = models.BooleanField(
        default=False,
        verbose_name='전문성 달성'
    )
    impact_achieved = models.BooleanField(
        default=False,
        verbose_name='영향력 달성'
    )
    
    # 1차 평가 (관리자)
    manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evaluations_as_manager',
        verbose_name='1차 평가자'
    )
    manager_grade = models.CharField(
        max_length=5,
        choices=GRADE_CHOICES,
        null=True,
        blank=True,
        verbose_name='1차 평가등급'
    )
    manager_comments = models.TextField(
        blank=True,
        verbose_name='1차 평가의견'
    )
    manager_evaluated_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='1차 평가일'
    )
    
    # 2차 평가 (Calibration)
    final_grade = models.CharField(
        max_length=5,
        choices=GRADE_CHOICES,
        null=True,
        blank=True,
        verbose_name='최종등급'
    )
    calibration_comments = models.TextField(
        blank=True,
        verbose_name='조정의견'
    )
    calibration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Calibration 완료일'
    )
    
    # Calibration Session 정보
    calibration_session = models.ForeignKey(
        'CalibrationSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluations',
        verbose_name='Calibration Session'
    )
    
    # 상태
    status = models.CharField(
        max_length=20,
        choices=EVALUATION_STATUS,
        default='DRAFT',
        verbose_name='상태'
    )
    
    # 종합 점수 (평균)
    overall_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='종합점수',
        help_text='3대 평가 평균 점수'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '종합평가'
        verbose_name_plural = '종합평가'
        unique_together = ['employee', 'evaluation_period']
        ordering = ['-evaluation_period__year', 'employee__name']

    def __str__(self):
        return f"{self.employee.name} - {self.evaluation_period} 종합평가"

    def auto_calculate_manager_grade(self):
        """1차 평가등급 자동 산출 (OK금융 규칙)"""
        achieved_count = sum([
            self.contribution_achieved,
            self.expertise_achieved,
            self.impact_achieved
        ])
        
        if achieved_count == 3:
            self.manager_grade = 'S'
        elif achieved_count == 2:
            self.manager_grade = 'A'
        elif achieved_count == 1:
            self.manager_grade = 'B'
        else:
            self.manager_grade = 'C'
            
        return self.manager_grade
    
    def sync_evaluation_scores(self):
        """각 평가의 점수를 동기화"""
        if self.contribution_evaluation:
            self.contribution_score = self.contribution_evaluation.contribution_score
            self.contribution_achieved = self.contribution_evaluation.is_achieved
        
        if self.expertise_evaluation:
            self.expertise_score = self.expertise_evaluation.total_score
            self.expertise_achieved = self.expertise_evaluation.is_achieved
        
        if self.impact_evaluation:
            self.impact_score = self.impact_evaluation.total_score
            self.impact_achieved = self.impact_evaluation.is_achieved
        
        # 종합 점수 계산
        scores = []
        if self.contribution_score:
            scores.append(self.contribution_score)
        if self.expertise_score:
            scores.append(self.expertise_score)
        if self.impact_score:
            scores.append(self.impact_score)
        
        if scores:
            self.overall_score = round(sum(scores) / len(scores), 1)
        
        self.save()
    
    def can_be_calibrated(self):
        """Calibration 가능 여부 확인"""
        return all([
            self.contribution_evaluation,
            self.expertise_evaluation,
            self.impact_evaluation,
            self.manager_grade,
            self.status in ['SUBMITTED', 'IN_REVIEW']
        ])


class CalibrationSession(models.Model):
    """Calibration Session"""
    evaluation_period = models.ForeignKey(
        EvaluationPeriod,
        on_delete=models.CASCADE,
        verbose_name='평가기간'
    )
    session_name = models.CharField(
        max_length=200,
        verbose_name='세션명'
    )
    session_date = models.DateField(
        verbose_name='세션 날짜'
    )
    
    # 참여자
    facilitator = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='calibration_sessions_facilitated',
        verbose_name='진행자'
    )
    participants = models.ManyToManyField(
        Employee,
        related_name='calibration_sessions_participated',
        verbose_name='참여자'
    )
    
    # 대상
    department = models.CharField(
        max_length=20,
        choices=[
            ('IT', 'IT'),
            ('HR', '인사'),
            ('FINANCE', '재무'),
            ('MARKETING', '마케팅'),
            ('SALES', '영업'),
            ('OPERATIONS', '운영'),
        ],
        null=True,
        blank=True,
        verbose_name='대상 부서'
    )
    
    # 세션 정보
    agenda = models.TextField(
        blank=True,
        verbose_name='안건'
    )
    minutes = models.TextField(
        blank=True,
        verbose_name='회의록'
    )
    
    # 상태
    status = models.CharField(
        max_length=20,
        choices=[
            ('SCHEDULED', '예정'),
            ('IN_PROGRESS', '진행중'),
            ('COMPLETED', '완료'),
            ('CANCELLED', '취소'),
        ],
        default='SCHEDULED',
        verbose_name='상태'
    )
    
    # 등급 분포 가이드라인
    s_grade_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.0,
        verbose_name='S등급 비율(%)'
    )
    a_grade_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.0,
        verbose_name='A등급 비율(%)'
    )
    b_grade_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50.0,
        verbose_name='B등급 비율(%)'
    )
    c_grade_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.0,
        verbose_name='C등급 비율(%)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Calibration Session'
        verbose_name_plural = 'Calibration Sessions'
        ordering = ['-session_date']

    def __str__(self):
        return f"{self.session_name} - {self.session_date}"
    
    def get_grade_distribution(self):
        """현재 등급 분포 계산"""
        evaluations = self.evaluations.filter(final_grade__isnull=False)
        total = evaluations.count()
        
        if total == 0:
            return {}
        
        distribution = {}
        for grade, _ in GRADE_CHOICES:
            count = evaluations.filter(final_grade=grade).count()
            distribution[grade] = {
                'count': count,
                'ratio': round((count / total) * 100, 1)
            }
        
        return distribution
    
    def check_grade_guideline_compliance(self):
        """등급 가이드라인 준수 여부 확인"""
        distribution = self.get_grade_distribution()
        
        compliance = {
            'S': abs(distribution.get('S', {}).get('ratio', 0) - float(self.s_grade_ratio)) <= 5,
            'A': abs(distribution.get('A', {}).get('ratio', 0) - float(self.a_grade_ratio)) <= 5,
            'B': abs(distribution.get('B', {}).get('ratio', 0) - float(self.b_grade_ratio)) <= 5,
            'C': abs(distribution.get('C', {}).get('ratio', 0) - float(self.c_grade_ratio)) <= 5,
        }
        
        return compliance


class GrowthLevel(models.Model):
    """성장레벨 정의"""
    level = models.IntegerField(
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='레벨'
    )
    name = models.CharField(
        max_length=50,
        verbose_name='레벨명'
    )
    description = models.TextField(
        verbose_name='레벨 설명'
    )
    
    # 레벨별 요구사항
    min_contribution_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=2.0,
        verbose_name='최소 기여도 점수'
    )
    min_expertise_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=2.0,
        verbose_name='최소 전문성 점수'
    )
    min_impact_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=2.0,
        verbose_name='최소 영향력 점수'
    )
    
    # 승급 조건
    required_evaluation_periods = models.IntegerField(
        default=2,
        verbose_name='필요 평가기간 수',
        help_text='해당 레벨에서 몇 번의 평가를 받아야 하는지'
    )
    min_consecutive_achievements = models.IntegerField(
        default=1,
        verbose_name='연속 달성 필요 횟수',
        help_text='연속으로 목표를 달성해야 하는 횟수'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '성장레벨'
        verbose_name_plural = '성장레벨'
        ordering = ['level']

    def __str__(self):
        return f"Level {self.level}: {self.name}"
    
    def get_next_level(self):
        """다음 레벨 가져오기"""
        return GrowthLevel.objects.filter(level__gt=self.level).first()


class EmployeeGrowthHistory(models.Model):
    """직원 성장레벨 이력"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='growth_history',
        verbose_name='직원'
    )
    evaluation_period = models.ForeignKey(
        EvaluationPeriod,
        on_delete=models.CASCADE,
        verbose_name='평가기간'
    )
    previous_level = models.ForeignKey(
        GrowthLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_employees',
        verbose_name='이전 레벨'
    )
    current_level = models.ForeignKey(
        GrowthLevel,
        on_delete=models.CASCADE,
        related_name='current_employees',
        verbose_name='현재 레벨'
    )
    
    # 승급/강등 정보
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('PROMOTION', '승급'),
            ('DEMOTION', '강등'),
            ('MAINTAIN', '유지'),
            ('INITIAL', '초기설정'),
        ],
        verbose_name='변경 유형'
    )
    change_reason = models.TextField(
        blank=True,
        verbose_name='변경 사유'
    )
    
    # 해당 기간 성과
    contribution_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='기여도 점수'
    )
    expertise_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='전문성 점수'
    )
    impact_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='영향력 점수'
    )
    overall_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='종합 점수'
    )
    
    # 승급 자격 정보
    meets_score_requirement = models.BooleanField(
        default=False,
        verbose_name='점수 요구사항 충족'
    )
    consecutive_achievements = models.IntegerField(
        default=0,
        verbose_name='연속 달성 횟수'
    )
    is_promotion_eligible = models.BooleanField(
        default=False,
        verbose_name='승급 자격 충족'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '성장레벨 이력'
        verbose_name_plural = '성장레벨 이력'
        unique_together = ['employee', 'evaluation_period']
        ordering = ['-evaluation_period__year', '-evaluation_period__period_type']

    def __str__(self):
        return f"{self.employee.name} - {self.evaluation_period} (Level {self.current_level.level})"
    
    def calculate_promotion_eligibility(self):
        """승급 자격 계산"""
        next_level = self.current_level.get_next_level()
        if not next_level:
            self.is_promotion_eligible = False
            return False
        
        # 점수 요구사항 확인
        score_met = all([
            self.contribution_score and self.contribution_score >= next_level.min_contribution_score,
            self.expertise_score and self.expertise_score >= next_level.min_expertise_score,
            self.impact_score and self.impact_score >= next_level.min_impact_score
        ])
        
        self.meets_score_requirement = score_met
        
        # 연속 달성 횟수 확인
        if score_met:
            # 이전 이력에서 연속 달성 횟수 계산
            previous_histories = EmployeeGrowthHistory.objects.filter(
                employee=self.employee,
                current_level=self.current_level,
                meets_score_requirement=True,
                evaluation_period__end_date__lt=self.evaluation_period.end_date
            ).order_by('-evaluation_period__end_date')
            
            consecutive_count = 1  # 현재 기간 포함
            for history in previous_histories:
                if history.meets_score_requirement:
                    consecutive_count += 1
                else:
                    break
            
            self.consecutive_achievements = consecutive_count
            
            # 승급 자격 판정
            self.is_promotion_eligible = consecutive_count >= next_level.min_consecutive_achievements
        else:
            self.consecutive_achievements = 0
            self.is_promotion_eligible = False
        
        return self.is_promotion_eligible


class GrowthLevelRequirement(models.Model):
    """성장레벨별 세부 요구사항"""
    growth_level = models.ForeignKey(
        GrowthLevel,
        on_delete=models.CASCADE,
        related_name='requirements',
        verbose_name='성장레벨'
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ('TECHNICAL', '기술역량'),
            ('LEADERSHIP', '리더십'),
            ('BUSINESS', '비즈니스'),
            ('COMMUNICATION', '소통'),
            ('PROBLEM_SOLVING', '문제해결'),
        ],
        verbose_name='역량 카테고리'
    )
    requirement = models.TextField(
        verbose_name='요구사항 설명'
    )
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='우선순위',
        help_text='1=낮음, 5=높음'
    )
    is_mandatory = models.BooleanField(
        default=True,
        verbose_name='필수 여부'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '성장레벨 요구사항'
        verbose_name_plural = '성장레벨 요구사항'
        ordering = ['growth_level__level', '-priority', 'category']

    def __str__(self):
        return f"Level {self.growth_level.level} - {self.get_category_display()}"


class PerformanceTrend(models.Model):
    """성과 트렌드 분석"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='performance_trends',
        verbose_name='직원'
    )
    evaluation_period = models.ForeignKey(
        EvaluationPeriod,
        on_delete=models.CASCADE,
        verbose_name='평가기간'
    )
    
    # 트렌드 분석 데이터
    contribution_trend = models.CharField(
        max_length=20,
        choices=[
            ('IMPROVING', '개선'),
            ('STABLE', '안정'),
            ('DECLINING', '하락'),
            ('VOLATILE', '변동'),
        ],
        null=True,
        blank=True,
        verbose_name='기여도 트렌드'
    )
    expertise_trend = models.CharField(
        max_length=20,
        choices=[
            ('IMPROVING', '개선'),
            ('STABLE', '안정'),
            ('DECLINING', '하락'),
            ('VOLATILE', '변동'),
        ],
        null=True,
        blank=True,
        verbose_name='전문성 트렌드'
    )
    impact_trend = models.CharField(
        max_length=20,
        choices=[
            ('IMPROVING', '개선'),
            ('STABLE', '안정'),
            ('DECLINING', '하락'),
            ('VOLATILE', '변동'),
        ],
        null=True,
        blank=True,
        verbose_name='영향력 트렌드'
    )
    overall_trend = models.CharField(
        max_length=20,
        choices=[
            ('IMPROVING', '개선'),
            ('STABLE', '안정'),
            ('DECLINING', '하락'),
            ('VOLATILE', '변동'),
        ],
        null=True,
        blank=True,
        verbose_name='종합 트렌드'
    )
    
    # 변화율 (이전 기간 대비 %)
    contribution_change_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='기여도 변화율(%)'
    )
    expertise_change_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='전문성 변화율(%)'
    )
    impact_change_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='영향력 변화율(%)'
    )
    overall_change_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='종합 변화율(%)'
    )
    
    # AI 인사이트
    insights = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='분석 인사이트',
        help_text='AI 분석 결과 저장'
    )
    recommendations = models.JSONField(
        default=list,
        blank=True,
        verbose_name='개선 추천사항',
        help_text='개인 성장을 위한 추천사항'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '성과 트렌드'
        verbose_name_plural = '성과 트렌드'
        unique_together = ['employee', 'evaluation_period']
        ordering = ['-evaluation_period__year', '-evaluation_period__period_type']

    def __str__(self):
        return f"{self.employee.name} - {self.evaluation_period} 트렌드"
    """성장레벨 정의"""
    level = models.IntegerField(
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='레벨'
    )
    name = models.CharField(max_length=50, verbose_name='레벨명')
    description = models.TextField(verbose_name='레벨 설명')
    
    # 기존 마이그레이션에서 생성된 필드들
    min_contribution_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=2.0,
        verbose_name='최소 기여도 점수'
    )
    min_expertise_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=2.0,
        verbose_name='최소 전문성 점수'
    )
    min_impact_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=2.0,
        verbose_name='최소 영향력 점수'
    )
    required_evaluation_periods = models.IntegerField(
        default=2,
        verbose_name='필요 평가기간 수',
        help_text='해당 레벨에서 몇 번의 평가를 받아야 하는지'
    )
    min_consecutive_achievements = models.IntegerField(
        default=1,
        verbose_name='연속 달성 필요 횟수',
        help_text='연속으로 목표를 달성해야 하는 횟수'
    )
    
    # 새로 추가된 필드들
    min_score_requirement = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=3.0,
        verbose_name='최소 점수 요구사항'
    )
    consecutive_achievements_required = models.IntegerField(
        default=3,
        verbose_name='연속 달성 횟수 요구'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '성장레벨'
        verbose_name_plural = '성장레벨'
        ordering = ['level']

    def __str__(self):
        return f"레벨 {self.level}: {self.name}"


