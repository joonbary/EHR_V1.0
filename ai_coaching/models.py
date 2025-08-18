"""
AI Coaching Models - AI 실시간 코칭 어시스턴트 모델
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from employees.models import Employee
import uuid


class CoachingSession(models.Model):
    """코칭 세션 모델"""
    
    SESSION_TYPE_CHOICES = [
        ('PERFORMANCE', '성과 코칭'),
        ('LEADERSHIP', '리더십 코칭'),
        ('SKILL_DEVELOPMENT', '역량 개발'),
        ('CAREER_PATH', '커리어 패스'),
        ('COMMUNICATION', '소통 개선'),
        ('GOAL_SETTING', '목표 설정'),
        ('PROBLEM_SOLVING', '문제 해결'),
        ('STRESS_MANAGEMENT', '스트레스 관리')
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', '예약됨'),
        ('ACTIVE', '진행 중'),
        ('COMPLETED', '완료'),
        ('CANCELLED', '취소'),
        ('PAUSED', '일시중지')
    ]
    
    # 기본 정보
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="직원")
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, 
                                  default='PERFORMANCE', verbose_name="코칭 유형")
    
    # 세션 설정
    title = models.CharField(max_length=200, verbose_name="세션 제목")
    description = models.TextField(blank=True, verbose_name="설명")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='SCHEDULED', verbose_name="상태")
    
    # 시간 정보
    scheduled_at = models.DateTimeField(verbose_name="예약 일시")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="시작 일시")
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name="종료 일시")
    duration_minutes = models.IntegerField(default=60, verbose_name="예상 소요시간(분)")
    
    # AI 설정
    ai_personality = models.CharField(max_length=50, default='SUPPORTIVE', verbose_name="AI 성격")
    coaching_objectives = models.JSONField(default=list, verbose_name="코칭 목표")
    focus_areas = models.JSONField(default=list, verbose_name="집중 영역")
    
    # 결과
    satisfaction_score = models.FloatField(default=0.0, verbose_name="만족도 점수")
    ai_insights = models.JSONField(default=dict, verbose_name="AI 인사이트")
    action_items = models.JSONField(default=list, verbose_name="액션 아이템")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")
    notes = models.TextField(blank=True, verbose_name="노트")
    
    class Meta:
        verbose_name = "코칭 세션"
        verbose_name_plural = "코칭 세션"
        ordering = ['-scheduled_at']
    
    def __str__(self):
        return f"{self.employee.name} - {self.title}"
    
    def get_actual_duration(self):
        """실제 소요 시간 계산(분)"""
        if self.started_at and self.ended_at:
            duration = self.ended_at - self.started_at
            return int(duration.total_seconds() / 60)
        return 0
    
    def is_active(self):
        """활성 세션 여부"""
        return self.status in ['SCHEDULED', 'ACTIVE']


class CoachingMessage(models.Model):
    """코칭 메시지 모델"""
    
    SENDER_CHOICES = [
        ('EMPLOYEE', '직원'),
        ('AI_COACH', 'AI 코치'),
        ('SYSTEM', '시스템')
    ]
    
    MESSAGE_TYPE_CHOICES = [
        ('TEXT', '텍스트'),
        ('QUESTION', '질문'),
        ('SUGGESTION', '제안'),
        ('REFLECTION', '성찰'),
        ('GOAL_SETTING', '목표 설정'),
        ('ACTION_PLAN', '액션 플랜'),
        ('FEEDBACK', '피드백'),
        ('SUMMARY', '요약')
    ]
    
    # 기본 정보
    session = models.ForeignKey(CoachingSession, on_delete=models.CASCADE, 
                              related_name='messages', verbose_name="세션")
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES, verbose_name="발신자")
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, 
                                  default='TEXT', verbose_name="메시지 유형")
    
    # 메시지 내용
    content = models.TextField(verbose_name="내용")
    metadata = models.JSONField(default=dict, verbose_name="메타데이터")
    
    # AI 분석
    sentiment_score = models.FloatField(default=0.0, verbose_name="감정 점수")
    confidence_level = models.FloatField(default=0.0, verbose_name="신뢰도")
    key_insights = models.JSONField(default=list, verbose_name="핵심 인사이트")
    
    # 시간 정보
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    edited_at = models.DateTimeField(null=True, blank=True, verbose_name="수정일시")
    
    # 상호작용
    is_important = models.BooleanField(default=False, verbose_name="중요 메시지")
    requires_followup = models.BooleanField(default=False, verbose_name="후속 조치 필요")
    
    class Meta:
        verbose_name = "코칭 메시지"
        verbose_name_plural = "코칭 메시지"
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.session} - {self.get_sender_display()}: {self.content[:50]}..."


class CoachingGoal(models.Model):
    """코칭 목표 모델"""
    
    GOAL_TYPE_CHOICES = [
        ('PERFORMANCE', '성과 향상'),
        ('SKILL', '스킬 개발'),
        ('BEHAVIOR', '행동 변화'),
        ('CAREER', '커리어 발전'),
        ('RELATIONSHIP', '관계 개선'),
        ('WELLNESS', '웰빙'),
        ('LEADERSHIP', '리더십'),
        ('COMMUNICATION', '소통')
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', '낮음'),
        ('MEDIUM', '보통'),
        ('HIGH', '높음'),
        ('CRITICAL', '긴급')
    ]
    
    STATUS_CHOICES = [
        ('NOT_STARTED', '시작 전'),
        ('IN_PROGRESS', '진행 중'),
        ('COMPLETED', '완료'),
        ('ON_HOLD', '보류'),
        ('CANCELLED', '취소')
    ]
    
    # 기본 정보
    session = models.ForeignKey(CoachingSession, on_delete=models.CASCADE, 
                              related_name='goals', verbose_name="세션")
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, verbose_name="목표 유형")
    
    # 목표 설정
    title = models.CharField(max_length=200, verbose_name="목표 제목")
    description = models.TextField(verbose_name="목표 설명")
    success_criteria = models.JSONField(default=list, verbose_name="성공 기준")
    
    # 목표 속성
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, 
                              default='MEDIUM', verbose_name="우선순위")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='NOT_STARTED', verbose_name="상태")
    
    # 일정
    target_date = models.DateField(null=True, blank=True, verbose_name="목표 달성일")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="완료일시")
    
    # 진행률
    progress_percentage = models.FloatField(default=0.0, verbose_name="진행률(%)")
    milestones = models.JSONField(default=list, verbose_name="마일스톤")
    
    # AI 분석
    feasibility_score = models.FloatField(default=0.0, verbose_name="실현가능성 점수")
    ai_recommendations = models.JSONField(default=list, verbose_name="AI 추천사항")
    
    class Meta:
        verbose_name = "코칭 목표"
        verbose_name_plural = "코칭 목표"
        ordering = ['-priority', 'target_date']
    
    def __str__(self):
        return f"{self.session.employee.name} - {self.title}"
    
    def is_overdue(self):
        """목표 기한 초과 여부"""
        if self.target_date and self.status != 'COMPLETED':
            return timezone.now().date() > self.target_date
        return False


class CoachingActionItem(models.Model):
    """액션 아이템 모델"""
    
    CATEGORY_CHOICES = [
        ('TASK', '과제'),
        ('MEETING', '미팅'),
        ('TRAINING', '교육'),
        ('PRACTICE', '연습'),
        ('RESEARCH', '조사'),
        ('REFLECTION', '성찰'),
        ('FEEDBACK', '피드백'),
        ('NETWORKING', '네트워킹')
    ]
    
    STATUS_CHOICES = [
        ('PENDING', '대기'),
        ('IN_PROGRESS', '진행 중'),
        ('COMPLETED', '완료'),
        ('OVERDUE', '지연'),
        ('CANCELLED', '취소')
    ]
    
    # 기본 정보
    session = models.ForeignKey(CoachingSession, on_delete=models.CASCADE, 
                              related_name='action_items_detailed', verbose_name="세션")
    goal = models.ForeignKey(CoachingGoal, on_delete=models.SET_NULL, null=True, blank=True, 
                           related_name='action_items', verbose_name="연관 목표")
    
    # 액션 아이템 정보
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="카테고리")
    title = models.CharField(max_length=200, verbose_name="제목")
    description = models.TextField(verbose_name="설명")
    
    # 실행 계획
    steps = models.JSONField(default=list, verbose_name="실행 단계")
    resources_needed = models.JSONField(default=list, verbose_name="필요 자원")
    expected_outcome = models.TextField(blank=True, verbose_name="기대 결과")
    
    # 스케줄링
    due_date = models.DateField(verbose_name="마감일")
    estimated_hours = models.FloatField(default=0.0, verbose_name="예상 소요시간")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='PENDING', verbose_name="상태")
    
    # 진행 상황
    progress_notes = models.TextField(blank=True, verbose_name="진행 노트")
    completion_evidence = models.TextField(blank=True, verbose_name="완료 증빙")
    actual_hours = models.FloatField(default=0.0, verbose_name="실제 소요시간")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="완료일시")
    
    class Meta:
        verbose_name = "액션 아이템"
        verbose_name_plural = "액션 아이템"
        ordering = ['due_date', '-created_at']
    
    def __str__(self):
        return f"{self.session.employee.name} - {self.title}"
    
    def is_overdue(self):
        """지연 여부"""
        if self.status != 'COMPLETED':
            return timezone.now().date() > self.due_date
        return False
    
    def get_completion_rate(self):
        """완료율 계산"""
        if not self.steps:
            return 0
        
        completed_steps = sum(1 for step in self.steps if step.get('completed', False))
        return (completed_steps / len(self.steps)) * 100


class CoachingFeedback(models.Model):
    """코칭 피드백 모델"""
    
    FEEDBACK_TYPE_CHOICES = [
        ('SESSION', '세션 피드백'),
        ('PROGRESS', '진행 피드백'),
        ('GOAL', '목표 피드백'),
        ('AI_COACH', 'AI 코치 피드백'),
        ('SELF_REFLECTION', '자기 성찰')
    ]
    
    RATING_CHOICES = [
        (1, '매우 불만족'),
        (2, '불만족'),
        (3, '보통'),
        (4, '만족'),
        (5, '매우 만족')
    ]
    
    # 기본 정보
    session = models.ForeignKey(CoachingSession, on_delete=models.CASCADE, 
                              related_name='feedback', verbose_name="세션")
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, 
                                   verbose_name="피드백 유형")
    
    # 평가
    overall_rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="전체 평가")
    coaching_quality = models.IntegerField(choices=RATING_CHOICES, verbose_name="코칭 품질")
    ai_helpfulness = models.IntegerField(choices=RATING_CHOICES, verbose_name="AI 도움도")
    goal_achievement = models.IntegerField(choices=RATING_CHOICES, verbose_name="목표 달성도")
    
    # 피드백 내용
    positive_aspects = models.TextField(verbose_name="좋았던 점")
    areas_for_improvement = models.TextField(verbose_name="개선할 점")
    suggestions = models.TextField(blank=True, verbose_name="제안사항")
    
    # 추가 평가
    would_recommend = models.BooleanField(default=True, verbose_name="추천 의향")
    future_coaching_interest = models.BooleanField(default=True, verbose_name="향후 코칭 관심도")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    
    class Meta:
        verbose_name = "코칭 피드백"
        verbose_name_plural = "코칭 피드백"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.session} - {self.get_feedback_type_display()}"
    
    def get_average_rating(self):
        """평균 평점 계산"""
        ratings = [
            self.overall_rating,
            self.coaching_quality, 
            self.ai_helpfulness,
            self.goal_achievement
        ]
        return sum(ratings) / len(ratings)


class CoachingTemplate(models.Model):
    """코칭 템플릿 모델"""
    
    TEMPLATE_CATEGORY_CHOICES = [
        ('PERFORMANCE', '성과 관리'),
        ('LEADERSHIP', '리더십'),
        ('ONBOARDING', '온보딩'),
        ('CAREER_DEVELOPMENT', '커리어 개발'),
        ('SKILL_BUILDING', '스킬 구축'),
        ('PROBLEM_SOLVING', '문제 해결'),
        ('GOAL_SETTING', '목표 설정'),
        ('FEEDBACK', '피드백')
    ]
    
    # 기본 정보
    name = models.CharField(max_length=200, verbose_name="템플릿 이름")
    category = models.CharField(max_length=20, choices=TEMPLATE_CATEGORY_CHOICES, 
                              verbose_name="카테고리")
    description = models.TextField(verbose_name="설명")
    
    # 템플릿 구조
    session_structure = models.JSONField(default=list, verbose_name="세션 구조")
    suggested_questions = models.JSONField(default=list, verbose_name="제안 질문")
    goal_templates = models.JSONField(default=list, verbose_name="목표 템플릿")
    
    # 사용 통계
    usage_count = models.IntegerField(default=0, verbose_name="사용 횟수")
    success_rate = models.FloatField(default=0.0, verbose_name="성공률")
    average_satisfaction = models.FloatField(default=0.0, verbose_name="평균 만족도")
    
    # 메타데이터
    created_by = models.CharField(max_length=100, default='SYSTEM', verbose_name="생성자")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    
    class Meta:
        verbose_name = "코칭 템플릿"
        verbose_name_plural = "코칭 템플릿"
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def increment_usage(self):
        """사용 횟수 증가"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class CoachingMetrics(models.Model):
    """코칭 지표 모델"""
    
    # 기본 정보
    session = models.OneToOneField(CoachingSession, on_delete=models.CASCADE, 
                                 related_name='metrics', verbose_name="세션")
    
    # 참여도 지표
    engagement_score = models.FloatField(default=0.0, verbose_name="참여도 점수")
    interaction_count = models.IntegerField(default=0, verbose_name="상호작용 횟수")
    avg_response_time = models.FloatField(default=0.0, verbose_name="평균 응답 시간(초)")
    
    # 성과 지표
    goal_completion_rate = models.FloatField(default=0.0, verbose_name="목표 완료율")
    action_item_completion = models.FloatField(default=0.0, verbose_name="액션 아이템 완료율")
    behavioral_change_score = models.FloatField(default=0.0, verbose_name="행동 변화 점수")
    
    # AI 분석 지표
    ai_accuracy_score = models.FloatField(default=0.0, verbose_name="AI 정확도")
    personalization_score = models.FloatField(default=0.0, verbose_name="개인화 점수")
    recommendation_relevance = models.FloatField(default=0.0, verbose_name="추천 관련성")
    
    # 만족도 지표
    user_satisfaction = models.FloatField(default=0.0, verbose_name="사용자 만족도")
    perceived_value = models.FloatField(default=0.0, verbose_name="인지된 가치")
    likelihood_to_continue = models.FloatField(default=0.0, verbose_name="지속 의향")
    
    # 메타데이터
    calculated_at = models.DateTimeField(auto_now=True, verbose_name="계산일시")
    algorithm_version = models.CharField(max_length=20, default='1.0', verbose_name="알고리즘 버전")
    
    class Meta:
        verbose_name = "코칭 지표"
        verbose_name_plural = "코칭 지표"
    
    def __str__(self):
        return f"{self.session} 지표"
    
    def get_overall_effectiveness(self):
        """종합 효과성 점수"""
        scores = [
            self.engagement_score,
            self.goal_completion_rate,
            self.user_satisfaction,
            self.ai_accuracy_score
        ]
        valid_scores = [s for s in scores if s > 0]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0
