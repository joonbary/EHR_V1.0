from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid


class SearchIndex(models.Model):
    """통합 검색 인덱스"""
    CONTENT_TYPE_CHOICES = [
        ('EMPLOYEE', '직원'),
        ('DEPARTMENT', '부서'),
        ('POSITION', '직위'),
        ('ANNOUNCEMENT', '공지사항'),
        ('EVALUATION', '평가'),
        ('TRAINING', '교육'),
        ('JOB_PROFILE', '직무'),
        ('RECRUITMENT', '채용'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 검색 대상 객체
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 검색 분류
    search_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        verbose_name="검색 분류"
    )
    
    # 검색 가능한 텍스트
    title = models.CharField(max_length=500, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    keywords = models.TextField(
        blank=True,
        verbose_name="키워드",
        help_text="검색용 키워드 (공백으로 구분)"
    )
    
    # 메타데이터
    url = models.URLField(blank=True, verbose_name="링크 URL")
    image_url = models.URLField(blank=True, verbose_name="이미지 URL")
    
    # 접근 권한
    department_restricted = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="부서 제한",
        help_text="특정 부서만 검색 가능"
    )
    position_restricted = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="직위 제한",
        help_text="특정 직위 이상만 검색 가능"
    )
    is_public = models.BooleanField(default=True, verbose_name="공개 여부")
    
    # 검색 통계
    search_count = models.IntegerField(default=0, verbose_name="검색 횟수")
    last_searched = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="마지막 검색일"
    )
    
    # 우선순위 (검색 결과 정렬용)
    priority = models.IntegerField(default=1, verbose_name="우선순위")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '검색 인덱스'
        verbose_name_plural = '검색 인덱스 관리'
        ordering = ['-priority', '-updated_at']
        indexes = [
            models.Index(fields=['search_type', 'is_public']),
            models.Index(fields=['title']),
            models.Index(fields=['content']),
            models.Index(fields=['keywords']),
            models.Index(fields=['search_count', 'last_searched']),
        ]
    
    def __str__(self):
        return f"{self.get_search_type_display()} - {self.title}"
    
    def increment_search_count(self):
        """검색 횟수 증가"""
        self.search_count += 1
        self.last_searched = timezone.now()
        self.save(update_fields=['search_count', 'last_searched'])
    
    def can_access(self, employee: Employee) -> bool:
        """직원의 접근 권한 확인"""
        if not self.is_public:
            return False
        
        if self.department_restricted and employee.department != self.department_restricted:
            return False
        
        if self.position_restricted:
            # 직위별 권한 레벨 확인 (추후 구현)
            pass
        
        return True


class SearchQuery(models.Model):
    """검색 쿼리 로그"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 검색자
    user = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='search_queries',
        verbose_name="검색자"
    )
    
    # 검색어
    query = models.CharField(max_length=500, verbose_name="검색어")
    query_normalized = models.CharField(
        max_length=500,
        verbose_name="정규화된 검색어",
        help_text="공백 제거, 소문자 변환 등"
    )
    
    # 검색 옵션
    search_type = models.CharField(
        max_length=20,
        choices=SearchIndex.CONTENT_TYPE_CHOICES,
        blank=True,
        verbose_name="검색 분류"
    )
    
    # 검색 결과
    results_count = models.IntegerField(default=0, verbose_name="결과 수")
    selected_result_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name="선택한 결과 ID"
    )
    
    # 검색 성능
    execution_time = models.FloatField(
        default=0.0,
        verbose_name="실행 시간(초)"
    )
    
    # 메타데이터
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP 주소"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '검색 로그'
        verbose_name_plural = '검색 로그 관리'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['query', 'created_at']),
            models.Index(fields=['search_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.query}"


class PopularSearch(models.Model):
    """인기 검색어"""
    query = models.CharField(max_length=500, unique=True, verbose_name="검색어")
    search_count = models.IntegerField(default=0, verbose_name="검색 횟수")
    
    # 기간별 통계
    daily_count = models.IntegerField(default=0, verbose_name="일일 검색 수")
    weekly_count = models.IntegerField(default=0, verbose_name="주간 검색 수")
    monthly_count = models.IntegerField(default=0, verbose_name="월간 검색 수")
    
    # 최근 검색
    last_searched = models.DateTimeField(auto_now=True, verbose_name="마지막 검색일")
    
    # 트렌드 스코어 (검색 빈도 + 최근성)
    trend_score = models.FloatField(default=0.0, verbose_name="트렌드 스코어")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '인기 검색어'
        verbose_name_plural = '인기 검색어 관리'
        ordering = ['-trend_score', '-search_count']
    
    def __str__(self):
        return f"{self.query} ({self.search_count}회)"
    
    def increment_count(self):
        """검색 횟수 증가"""
        self.search_count += 1
        self.daily_count += 1
        self.weekly_count += 1
        self.monthly_count += 1
        self.calculate_trend_score()
        self.save()
    
    def calculate_trend_score(self):
        """트렌드 스코어 계산"""
        now = timezone.now()
        days_since_last = (now - self.last_searched).days
        
        # 최근성 가중치 (최근일수록 높은 점수)
        recency_weight = max(0, 1 - (days_since_last / 30))
        
        # 트렌드 스코어 = 검색 횟수 * 최근성 가중치
        self.trend_score = self.search_count * recency_weight


class SearchSuggestion(models.Model):
    """검색 제안/자동완성"""
    query = models.CharField(max_length=500, verbose_name="제안 검색어")
    display_text = models.CharField(max_length=500, verbose_name="표시 텍스트")
    
    # 분류
    suggestion_type = models.CharField(
        max_length=20,
        choices=[
            ('QUERY', '검색어'),
            ('EMPLOYEE', '직원명'),
            ('DEPARTMENT', '부서명'),
            ('POSITION', '직위명'),
            ('KEYWORD', '키워드'),
        ],
        default='QUERY',
        verbose_name="제안 유형"
    )
    
    # 우선순위
    priority = models.IntegerField(default=1, verbose_name="우선순위")
    
    # 사용 통계
    usage_count = models.IntegerField(default=0, verbose_name="사용 횟수")
    
    # 상태
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '검색 제안'
        verbose_name_plural = '검색 제안 관리'
        ordering = ['-priority', '-usage_count']
        unique_together = ['query', 'suggestion_type']
    
    def __str__(self):
        return f"{self.display_text} ({self.get_suggestion_type_display()})"


class SavedSearch(models.Model):
    """저장된 검색"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 사용자
    user = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='saved_searches',
        verbose_name="사용자"
    )
    
    # 검색 조건
    name = models.CharField(max_length=200, verbose_name="검색명")
    query = models.CharField(max_length=500, verbose_name="검색어")
    search_type = models.CharField(
        max_length=20,
        choices=SearchIndex.CONTENT_TYPE_CHOICES,
        blank=True,
        verbose_name="검색 분류"
    )
    
    # 알림 설정
    enable_alerts = models.BooleanField(
        default=False,
        verbose_name="새 결과 알림"
    )
    alert_frequency = models.CharField(
        max_length=10,
        choices=[
            ('DAILY', '매일'),
            ('WEEKLY', '매주'),
            ('MONTHLY', '매월'),
        ],
        default='WEEKLY',
        verbose_name="알림 주기"
    )
    last_alert_sent = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="마지막 알림 발송일"
    )
    
    # 사용 통계
    usage_count = models.IntegerField(default=0, verbose_name="사용 횟수")
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="마지막 사용일"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '저장된 검색'
        verbose_name_plural = '저장된 검색 관리'
        ordering = ['-last_used', '-usage_count']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.name} - {self.name}"
    
    def execute_search(self):
        """저장된 검색 실행"""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])
        
        # 실제 검색 실행은 SearchService에서 처리
        from .services import SearchService
        return SearchService.search(
            query=self.query,
            search_type=self.search_type,
            user=self.user
        )
