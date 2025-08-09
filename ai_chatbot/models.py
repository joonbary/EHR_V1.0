from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
import uuid


class ChatSession(models.Model):
    """채팅 세션 모델"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, default="새 대화")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    context = models.TextField(blank=True, help_text="대화 컨텍스트 저장")
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "채팅 세션"
        verbose_name_plural = "채팅 세션"
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_message_count(self):
        return self.messages.count()
    
    def get_last_message(self):
        return self.messages.last()


class ChatMessage(models.Model):
    """채팅 메시지 모델"""
    ROLE_CHOICES = [
        ('user', '사용자'),
        ('assistant', 'AI 어시스턴트'),
        ('system', '시스템'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # AI 응답 관련 필드
    tokens_used = models.IntegerField(default=0)
    model_used = models.CharField(max_length=50, blank=True)
    response_time = models.FloatField(default=0, help_text="응답 시간(초)")
    
    # 메타데이터
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "채팅 메시지"
        verbose_name_plural = "채팅 메시지"
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class AIPromptTemplate(models.Model):
    """AI 프롬프트 템플릿"""
    CATEGORY_CHOICES = [
        ('hr', 'HR 일반'),
        ('evaluation', '성과평가'),
        ('recruitment', '채용'),
        ('training', '교육'),
        ('compensation', '보상'),
        ('organization', '조직'),
        ('leadership', '리더십'),
        ('general', '일반'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    prompt_template = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 사용 통계
    usage_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = "AI 프롬프트 템플릿"
        verbose_name_plural = "AI 프롬프트 템플릿"
    
    def __str__(self):
        return f"[{self.get_category_display()}] {self.name}"


class QuickAction(models.Model):
    """빠른 액션 버튼"""
    title = models.CharField(max_length=50)
    prompt = models.TextField()
    icon = models.CharField(max_length=50, default="fas fa-comment")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=20, choices=AIPromptTemplate.CATEGORY_CHOICES, default='general')
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = "빠른 액션"
        verbose_name_plural = "빠른 액션"
    
    def __str__(self):
        return self.title


class AIConfiguration(models.Model):
    """AI 설정"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "AI 설정"
        verbose_name_plural = "AI 설정"
    
    def __str__(self):
        return self.key
    
    @classmethod
    def get_config(cls, key, default=None):
        """설정 값 가져오기"""
        try:
            config = cls.objects.get(key=key, is_active=True)
            return config.value
        except cls.DoesNotExist:
            return default