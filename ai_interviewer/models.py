"""
AI Interviewer Models - AI 채용 면접관 모델
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from job_profiles.models import JobProfile
from employees.models import Employee
import uuid


class InterviewSession(models.Model):
    """면접 세션 모델"""
    
    SESSION_STATUS_CHOICES = [
        ('SCHEDULED', '예정됨'),
        ('IN_PROGRESS', '진행 중'),
        ('COMPLETED', '완료됨'),
        ('CANCELLED', '취소됨'),
        ('PAUSED', '일시중단'),
        ('FAILED', '실패')
    ]
    
    SESSION_TYPE_CHOICES = [
        ('SCREENING', '서류심사'),
        ('TECHNICAL', '기술면접'),
        ('BEHAVIORAL', '인성면접'),
        ('FINAL', '최종면접'),
        ('PRACTICAL', '실무면접'),
        ('CULTURAL_FIT', '문화적합성')
    ]
    
    DIFFICULTY_CHOICES = [
        ('BEGINNER', '초급'),
        ('INTERMEDIATE', '중급'),
        ('ADVANCED', '고급'),
        ('EXPERT', '전문가')
    ]
    
    # 기본 정보
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=200, verbose_name="면접 제목")
    job_profile = models.ForeignKey(JobProfile, on_delete=models.CASCADE, verbose_name="채용 공고")
    
    # 응답자 정보 (실제 채용시에는 지원자, 테스트시에는 기존 직원)
    candidate_name = models.CharField(max_length=100, verbose_name="응답자 이름")
    candidate_email = models.EmailField(verbose_name="응답자 이메일")
    candidate_phone = models.CharField(max_length=20, blank=True, verbose_name="응답자 전화번호")
    test_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, 
                                     verbose_name="테스트 직원")
    
    # 면접 설정
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, 
                                  default='BEHAVIORAL', verbose_name="면접 유형")
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, 
                                      default='INTERMEDIATE', verbose_name="난이도")
    expected_duration = models.IntegerField(default=30, verbose_name="예상 소요시간(분)")
    max_questions = models.IntegerField(default=10, verbose_name="최대 질문 수")
    
    # 상태 정보
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, 
                            default='SCHEDULED', verbose_name="상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="시작일시")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="완료일시")
    
    # AI 설정
    ai_personality = models.CharField(max_length=50, default='PROFESSIONAL', verbose_name="AI 성격")
    ai_model_version = models.CharField(max_length=20, default='gpt-3.5-turbo', verbose_name="AI 모델")
    custom_instructions = models.TextField(blank=True, verbose_name="커스텀 지시사항")
    
    # 결과
    total_questions_asked = models.IntegerField(default=0, verbose_name="총 질문 수")
    total_responses = models.IntegerField(default=0, verbose_name="총 응답 수")
    average_response_time = models.FloatField(default=0.0, verbose_name="평균 응답 시간(초)")
    overall_score = models.FloatField(default=0.0, verbose_name="종합 점수")
    ai_assessment = models.JSONField(default=dict, verbose_name="AI 평가")
    
    # 메타데이터
    interview_language = models.CharField(max_length=10, default='ko', verbose_name="면접 언어")
    recording_enabled = models.BooleanField(default=False, verbose_name="녹음 활성화")
    session_notes = models.TextField(blank=True, verbose_name="세션 노트")
    
    class Meta:
        verbose_name = "면접 세션"
        verbose_name_plural = "면접 세션"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.candidate_name}"
    
    def get_duration_minutes(self):
        """실제 면접 시간 계산(분)"""
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            return int(duration.total_seconds() / 60)
        return 0
    
    def get_completion_rate(self):
        """완료율 계산"""
        if self.max_questions > 0:
            return (self.total_questions_asked / self.max_questions) * 100
        return 0
    
    def is_active(self):
        """활성 세션 여부"""
        return self.status in ['SCHEDULED', 'IN_PROGRESS', 'PAUSED']


class InterviewQuestion(models.Model):
    """면접 질문 모델"""
    
    QUESTION_TYPE_CHOICES = [
        ('OPEN_ENDED', '개방형'),
        ('BEHAVIORAL', '행동면접'),
        ('SITUATIONAL', '상황면접'),
        ('TECHNICAL', '기술면접'),
        ('COMPETENCY', '역량평가'),
        ('CULTURAL_FIT', '문화적합성'),
        ('FOLLOW_UP', '후속질문')
    ]
    
    EVALUATION_CRITERIA_CHOICES = [
        ('COMMUNICATION', '의사소통'),
        ('PROBLEM_SOLVING', '문제해결'),
        ('LEADERSHIP', '리더십'),
        ('TEAMWORK', '팀워크'),
        ('CREATIVITY', '창의성'),
        ('TECHNICAL_SKILLS', '기술역량'),
        ('CULTURAL_FIT', '문화적합성'),
        ('ADAPTABILITY', '적응력'),
        ('WORK_ETHIC', '직업윤리')
    ]
    
    # 기본 정보
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, 
                              related_name='questions', verbose_name="면접 세션")
    question_number = models.IntegerField(verbose_name="질문 순서")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, 
                                   verbose_name="질문 유형")
    
    # 질문 내용
    question_text = models.TextField(verbose_name="질문 내용")
    question_context = models.TextField(blank=True, verbose_name="질문 맥락")
    expected_answer_points = models.JSONField(default=list, verbose_name="예상 답변 포인트")
    
    # AI 생성 정보
    generated_by_ai = models.BooleanField(default=True, verbose_name="AI 생성 여부")
    ai_reasoning = models.TextField(blank=True, verbose_name="AI 생성 근거")
    adapted_from_previous = models.BooleanField(default=False, verbose_name="이전 응답 기반 적응")
    
    # 평가 기준
    evaluation_criteria = models.CharField(max_length=20, choices=EVALUATION_CRITERIA_CHOICES, 
                                         verbose_name="평가 기준")
    max_score = models.IntegerField(default=10, verbose_name="최대 점수")
    weight = models.FloatField(default=1.0, verbose_name="가중치")
    
    # 시간 정보
    asked_at = models.DateTimeField(auto_now_add=True, verbose_name="질문 시간")
    response_deadline = models.DateTimeField(null=True, blank=True, verbose_name="응답 마감시간")
    
    # 메타데이터
    difficulty_score = models.FloatField(default=5.0, verbose_name="난이도 점수")
    estimated_response_time = models.IntegerField(default=120, verbose_name="예상 응답시간(초)")
    tags = models.JSONField(default=list, verbose_name="태그")
    
    class Meta:
        verbose_name = "면접 질문"
        verbose_name_plural = "면접 질문"
        ordering = ['session', 'question_number']
        unique_together = ['session', 'question_number']
    
    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}..."
    
    def is_expired(self):
        """응답 시간 초과 여부"""
        if self.response_deadline:
            return timezone.now() > self.response_deadline
        return False


class InterviewResponse(models.Model):
    """면접 응답 모델"""
    
    RESPONSE_TYPE_CHOICES = [
        ('TEXT', '텍스트'),
        ('VOICE', '음성'),
        ('VIDEO', '영상'),
        ('FILE', '파일'),
        ('MIXED', '복합')
    ]
    
    QUALITY_RATING_CHOICES = [
        ('EXCELLENT', '매우 우수'),
        ('GOOD', '우수'),
        ('AVERAGE', '보통'),
        ('BELOW_AVERAGE', '미흡'),
        ('POOR', '부족')
    ]
    
    # 기본 정보
    question = models.OneToOneField(InterviewQuestion, on_delete=models.CASCADE, 
                                  related_name='response', verbose_name="질문")
    response_type = models.CharField(max_length=10, choices=RESPONSE_TYPE_CHOICES, 
                                   default='TEXT', verbose_name="응답 유형")
    
    # 응답 내용
    response_text = models.TextField(verbose_name="응답 내용")
    response_file = models.FileField(upload_to='interview_responses/', null=True, blank=True, 
                                   verbose_name="응답 파일")
    
    # 시간 정보
    started_at = models.DateTimeField(verbose_name="응답 시작시간")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="제출시간")
    response_time_seconds = models.FloatField(verbose_name="응답 소요시간(초)")
    
    # AI 평가
    ai_score = models.FloatField(default=0.0, verbose_name="AI 점수")
    ai_feedback = models.TextField(blank=True, verbose_name="AI 피드백")
    ai_analysis = models.JSONField(default=dict, verbose_name="AI 분석")
    quality_rating = models.CharField(max_length=20, choices=QUALITY_RATING_CHOICES, 
                                    blank=True, verbose_name="품질 평가")
    
    # 상세 분석
    keyword_matches = models.JSONField(default=list, verbose_name="키워드 매칭")
    sentiment_score = models.FloatField(default=0.0, verbose_name="감정 점수")
    confidence_level = models.FloatField(default=0.0, verbose_name="자신감 수준")
    clarity_score = models.FloatField(default=0.0, verbose_name="명확성 점수")
    relevance_score = models.FloatField(default=0.0, verbose_name="관련성 점수")
    
    # 추가 메타데이터
    word_count = models.IntegerField(default=0, verbose_name="단어 수")
    revision_count = models.IntegerField(default=0, verbose_name="수정 횟수")
    flagged_for_review = models.BooleanField(default=False, verbose_name="검토 필요")
    
    class Meta:
        verbose_name = "면접 응답"
        verbose_name_plural = "면접 응답"
        ordering = ['question__question_number']
    
    def __str__(self):
        return f"{self.question.session.candidate_name} - Q{self.question.question_number} 응답"
    
    def get_response_time_display(self):
        """응답시간 표시용"""
        minutes = int(self.response_time_seconds // 60)
        seconds = int(self.response_time_seconds % 60)
        return f"{minutes}분 {seconds}초"
    
    def is_within_time_limit(self):
        """시간 제한 내 응답 여부"""
        if hasattr(self.question, 'estimated_response_time'):
            return self.response_time_seconds <= self.question.estimated_response_time * 1.5
        return True


class InterviewFeedback(models.Model):
    """면접 피드백 모델"""
    
    FEEDBACK_TYPE_CHOICES = [
        ('OVERALL', '종합평가'),
        ('QUESTION_SPECIFIC', '질문별'),
        ('IMPROVEMENT', '개선사항'),
        ('STRENGTH', '강점'),
        ('RECOMMENDATION', '추천사항')
    ]
    
    RATING_SCALE_CHOICES = [
        (5, '매우 우수'),
        (4, '우수'),
        (3, '보통'),
        (2, '미흡'),
        (1, '부족')
    ]
    
    # 기본 정보
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, 
                              related_name='feedback', verbose_name="면접 세션")
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, 
                                   verbose_name="피드백 유형")
    specific_question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE, 
                                        null=True, blank=True, verbose_name="특정 질문")
    
    # 피드백 내용
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="피드백 내용")
    rating = models.IntegerField(choices=RATING_SCALE_CHOICES, null=True, blank=True, 
                               verbose_name="평점")
    
    # AI 생성 정보
    generated_by_ai = models.BooleanField(default=True, verbose_name="AI 생성")
    confidence_score = models.FloatField(default=0.0, verbose_name="신뢰도 점수")
    
    # 개선사항
    improvement_suggestions = models.JSONField(default=list, verbose_name="개선 제안사항")
    followup_resources = models.JSONField(default=list, verbose_name="후속 자료")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    priority_level = models.IntegerField(default=3, verbose_name="우선순위")
    tags = models.JSONField(default=list, verbose_name="태그")
    
    class Meta:
        verbose_name = "면접 피드백"
        verbose_name_plural = "면접 피드백"
        ordering = ['-priority_level', '-created_at']
    
    def __str__(self):
        return f"{self.session.candidate_name} - {self.title}"


class InterviewTemplate(models.Model):
    """면접 템플릿 모델"""
    
    TEMPLATE_CATEGORY_CHOICES = [
        ('GENERAL', '일반'),
        ('TECHNICAL', '기술직'),
        ('MANAGEMENT', '관리직'),
        ('SALES', '영업직'),
        ('CREATIVE', '창작직'),
        ('CUSTOMER_SERVICE', '고객서비스'),
        ('ENTRY_LEVEL', '신입직')
    ]
    
    # 기본 정보
    name = models.CharField(max_length=200, verbose_name="템플릿 이름")
    category = models.CharField(max_length=20, choices=TEMPLATE_CATEGORY_CHOICES, 
                              verbose_name="카테고리")
    description = models.TextField(verbose_name="설명")
    
    # 템플릿 설정
    target_duration = models.IntegerField(default=30, verbose_name="목표 시간(분)")
    question_count = models.IntegerField(default=10, verbose_name="질문 수")
    difficulty_level = models.CharField(max_length=20, 
                                      choices=InterviewSession.DIFFICULTY_CHOICES, 
                                      verbose_name="난이도")
    
    # 질문 템플릿
    question_templates = models.JSONField(default=list, verbose_name="질문 템플릿")
    evaluation_criteria = models.JSONField(default=list, verbose_name="평가 기준")
    
    # 사용 통계
    usage_count = models.IntegerField(default=0, verbose_name="사용 횟수")
    average_rating = models.FloatField(default=0.0, verbose_name="평균 평점")
    
    # 메타데이터
    created_by = models.CharField(max_length=100, default='SYSTEM', verbose_name="생성자")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    
    class Meta:
        verbose_name = "면접 템플릿"
        verbose_name_plural = "면접 템플릿"
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def increment_usage(self):
        """사용 횟수 증가"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class InterviewMetrics(models.Model):
    """면접 지표 모델"""
    
    # 기본 정보
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, 
                                 related_name='metrics', verbose_name="면접 세션")
    
    # 시간 지표
    total_duration_minutes = models.FloatField(default=0.0, verbose_name="총 소요시간(분)")
    average_question_time = models.FloatField(default=0.0, verbose_name="평균 질문당 시간(분)")
    thinking_time_ratio = models.FloatField(default=0.0, verbose_name="사고시간 비율")
    
    # 응답 품질 지표
    response_completeness = models.FloatField(default=0.0, verbose_name="응답 완성도")
    average_response_length = models.IntegerField(default=0, verbose_name="평균 응답 길이")
    vocabulary_diversity = models.FloatField(default=0.0, verbose_name="어휘 다양성")
    
    # 역량 평가
    communication_score = models.FloatField(default=0.0, verbose_name="의사소통 점수")
    problem_solving_score = models.FloatField(default=0.0, verbose_name="문제해결 점수")
    technical_competence = models.FloatField(default=0.0, verbose_name="기술역량 점수")
    cultural_fit_score = models.FloatField(default=0.0, verbose_name="문화적합성 점수")
    
    # AI 분석 지표
    confidence_consistency = models.FloatField(default=0.0, verbose_name="자신감 일관성")
    stress_level_indicator = models.FloatField(default=0.0, verbose_name="스트레스 지표")
    engagement_level = models.FloatField(default=0.0, verbose_name="참여도")
    
    # 종합 평가
    overall_recommendation = models.CharField(max_length=30, 
                                            choices=[
                                                ('STRONGLY_RECOMMEND', '적극 추천'),
                                                ('RECOMMEND', '추천'),
                                                ('NEUTRAL', '보통'),
                                                ('NOT_RECOMMEND', '비추천'),
                                                ('STRONGLY_NOT_RECOMMEND', '적극 비추천')
                                            ], 
                                            blank=True, verbose_name="종합 추천도")
    risk_factors = models.JSONField(default=list, verbose_name="리스크 요소")
    strength_points = models.JSONField(default=list, verbose_name="강점")
    
    # 메타데이터
    calculated_at = models.DateTimeField(auto_now=True, verbose_name="계산일시")
    algorithm_version = models.CharField(max_length=20, default='1.0', verbose_name="알고리즘 버전")
    
    class Meta:
        verbose_name = "면접 지표"
        verbose_name_plural = "면접 지표"
    
    def __str__(self):
        return f"{self.session.candidate_name} 면접 지표"
    
    def get_overall_score(self):
        """종합 점수 계산"""
        scores = [
            self.communication_score,
            self.problem_solving_score,
            self.technical_competence,
            self.cultural_fit_score
        ]
        valid_scores = [s for s in scores if s > 0]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0