from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from django.utils import timezone
import uuid


class NotificationType(models.Model):
    """알림 유형 관리"""
    CATEGORY_CHOICES = [
        ('HR', 'HR 관련'),
        ('SYSTEM', '시스템'),
        ('WORKFLOW', '업무 프로세스'),
        ('EVALUATION', '평가'),
        ('TRAINING', '교육'),
        ('ANNOUNCEMENT', '공지사항'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', '낮음'),
        ('NORMAL', '보통'),
        ('HIGH', '높음'),
        ('URGENT', '긴급'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="알림 유형명")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='SYSTEM',
        verbose_name="카테고리"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='NORMAL',
        verbose_name="우선순위"
    )
    template = models.TextField(verbose_name="메시지 템플릿")
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    auto_expire_days = models.IntegerField(
        default=30,
        verbose_name="자동 만료일",
        help_text="일 단위, 0이면 만료되지 않음"
    )
    
    # 발송 설정
    send_email = models.BooleanField(default=False, verbose_name="이메일 발송")
    send_sms = models.BooleanField(default=False, verbose_name="SMS 발송")
    send_push = models.BooleanField(default=True, verbose_name="푸시 알림")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '알림 유형'
        verbose_name_plural = '알림 유형 관리'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"


class Notification(models.Model):
    """알림 메시지"""
    STATUS_CHOICES = [
        ('PENDING', '대기'),
        ('SENT', '발송완료'),
        ('READ', '읽음'),
        ('EXPIRED', '만료'),
        ('FAILED', '실패'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        verbose_name="알림 유형"
    )
    
    # 수신자
    recipient = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='received_notifications',
        verbose_name="수신자"
    )
    
    # 발신자 (시스템 알림인 경우 null)
    sender = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name="발신자"
    )
    
    # 메시지 내용
    title = models.CharField(max_length=200, verbose_name="제목")
    message = models.TextField(verbose_name="메시지 내용")
    
    # 추가 데이터 (JSON)
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="추가 데이터",
        help_text="관련 객체 ID, URL 등"
    )
    
    # 상태 관리
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="상태"
    )
    
    # 일정 관리
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="예약 발송 시간"
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="발송 시간"
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="읽은 시간"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="만료 시간"
    )
    
    # 액션 버튼
    action_url = models.URLField(
        blank=True,
        verbose_name="액션 URL",
        help_text="클릭시 이동할 URL"
    )
    action_text = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="액션 버튼 텍스트"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '알림'
        verbose_name_plural = '알림 관리'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['notification_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient.name} - {self.title}"
    
    def mark_as_read(self):
        """알림을 읽음으로 표시"""
        if self.status in ['SENT', 'PENDING']:
            self.status = 'read'
            self.read_at = timezone.now()
            self.save()
    
    def mark_as_sent(self):
        """알림을 발송완료로 표시"""
        if self.status == 'PENDING':
            self.status = 'SENT'
            self.sent_at = timezone.now()
            self.save()
    
    def is_expired(self):
        """만료 여부 확인"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_read(self):
        return self.status == 'read'
    
    @property
    def priority_class(self):
        """CSS 클래스용 우선순위"""
        return self.notification_type.priority.lower()


class NotificationPreference(models.Model):
    """사용자별 알림 설정"""
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='notification_preference',
        verbose_name="직원"
    )
    
    # 전역 설정
    enable_notifications = models.BooleanField(default=True, verbose_name="알림 활성화")
    enable_email = models.BooleanField(default=True, verbose_name="이메일 알림")
    enable_sms = models.BooleanField(default=False, verbose_name="SMS 알림")
    enable_push = models.BooleanField(default=True, verbose_name="푸시 알림")
    
    # 카테고리별 설정
    hr_notifications = models.BooleanField(default=True, verbose_name="HR 알림")
    system_notifications = models.BooleanField(default=True, verbose_name="시스템 알림")
    workflow_notifications = models.BooleanField(default=True, verbose_name="업무 알림")
    evaluation_notifications = models.BooleanField(default=True, verbose_name="평가 알림")
    training_notifications = models.BooleanField(default=True, verbose_name="교육 알림")
    announcement_notifications = models.BooleanField(default=True, verbose_name="공지 알림")
    
    # 시간 설정
    quiet_hours_start = models.TimeField(
        default='22:00',
        verbose_name="방해금지 시작시간"
    )
    quiet_hours_end = models.TimeField(
        default='08:00',
        verbose_name="방해금지 종료시간"
    )
    weekend_notifications = models.BooleanField(default=False, verbose_name="주말 알림")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '알림 설정'
        verbose_name_plural = '알림 설정 관리'
    
    def __str__(self):
        return f"{self.employee.name} 알림 설정"
    
    def should_receive_notification(self, notification_type):
        """특정 알림 유형을 받을지 결정"""
        if not self.enable_notifications:
            return False
        
        category_map = {
            'HR': self.hr_notifications,
            'SYSTEM': self.system_notifications,
            'WORKFLOW': self.workflow_notifications,
            'EVALUATION': self.evaluation_notifications,
            'TRAINING': self.training_notifications,
            'ANNOUNCEMENT': self.announcement_notifications,
        }
        
        return category_map.get(notification_type.category, True)


class NotificationLog(models.Model):
    """알림 발송 로그"""
    CHANNEL_CHOICES = [
        ('PUSH', '푸시'),
        ('EMAIL', '이메일'),
        ('SMS', 'SMS'),
    ]
    
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name="알림"
    )
    channel = models.CharField(
        max_length=10,
        choices=CHANNEL_CHOICES,
        verbose_name="발송 채널"
    )
    status = models.CharField(
        max_length=10,
        choices=[('SUCCESS', '성공'), ('FAILED', '실패')],
        verbose_name="발송 상태"
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="오류 메시지"
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="발송 시간")
    
    class Meta:
        verbose_name = '알림 로그'
        verbose_name_plural = '알림 로그'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.notification.title} - {self.get_channel_display()}"


class AnnouncementBoard(models.Model):
    """공지사항 게시판"""
    VISIBILITY_CHOICES = [
        ('ALL', '전체'),
        ('DEPARTMENT', '부서'),
        ('POSITION', '직위'),
        ('CUSTOM', '선택'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    
    # 작성자
    author = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name="작성자"
    )
    
    # 공개 범위
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='ALL',
        verbose_name="공개 범위"
    )
    target_departments = models.ManyToManyField(
        'organization.Department',
        blank=True,
        verbose_name="대상 부서"
    )
    target_positions = models.ManyToManyField(
        'organization.Position',
        blank=True,
        verbose_name="대상 직위"
    )
    target_employees = models.ManyToManyField(
        Employee,
        blank=True,
        verbose_name="대상 직원"
    )
    
    # 중요도
    is_important = models.BooleanField(default=False, verbose_name="중요 공지")
    is_urgent = models.BooleanField(default=False, verbose_name="긴급 공지")
    
    # 기간
    publish_date = models.DateTimeField(default=timezone.now, verbose_name="게시일")
    expire_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="만료일"
    )
    
    # 상태
    is_published = models.BooleanField(default=True, verbose_name="게시 상태")
    
    # 첨부파일
    attachment = models.FileField(
        upload_to='announcements/',
        blank=True,
        verbose_name="첨부파일"
    )
    
    # 조회수
    view_count = models.IntegerField(default=0, verbose_name="조회수")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '공지사항'
        verbose_name_plural = '공지사항 관리'
        ordering = ['-is_important', '-is_urgent', '-publish_date']
    
    def __str__(self):
        return self.title
    
    def increment_view_count(self):
        """조회수 증가"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def is_visible_to_employee(self, employee):
        """특정 직원에게 공개되는지 확인"""
        if not self.is_published:
            return False
        
        if self.expire_date and timezone.now() > self.expire_date:
            return False
        
        if self.visibility == 'ALL':
            return True
        elif self.visibility == 'DEPARTMENT':
            return self.target_departments.filter(
                code=employee.department
            ).exists()
        elif self.visibility == 'POSITION':
            return self.target_positions.filter(
                name=employee.new_position
            ).exists()
        elif self.visibility == 'CUSTOM':
            return self.target_employees.filter(id=employee.id).exists()
        
        return False
