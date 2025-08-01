from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid


class Role(models.Model):
    """역할 정의"""
    ROLE_TYPE_CHOICES = [
        ('SYSTEM', '시스템 역할'),
        ('DEPARTMENT', '부서 역할'),
        ('PROJECT', '프로젝트 역할'),
        ('CUSTOM', '사용자 정의'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="역할명")
    description = models.TextField(blank=True, verbose_name="설명")
    
    # 역할 분류
    role_type = models.CharField(
        max_length=20,
        choices=ROLE_TYPE_CHOICES,
        default='CUSTOM',
        verbose_name="역할 유형"
    )
    
    # 계층 구조
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="상위 역할"
    )
    level = models.IntegerField(default=1, verbose_name="역할 레벨")
    
    # 권한 상속
    inherit_permissions = models.BooleanField(
        default=True,
        verbose_name="권한 상속",
        help_text="상위 역할의 권한을 상속받을지 여부"
    )
    
    # 상태
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    is_system = models.BooleanField(
        default=False,
        verbose_name="시스템 역할",
        help_text="시스템에서 관리하는 역할 (수정 불가)"
    )
    
    # 제한 조건
    max_assignees = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="최대 할당 인원",
        help_text="0이면 무제한"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_roles',
        verbose_name="생성자"
    )
    
    class Meta:
        verbose_name = '역할'
        verbose_name_plural = '역할 관리'
        ordering = ['level', 'name']
    
    def __str__(self):
        return self.name
    
    def get_all_permissions(self):
        """역할의 모든 권한 조회 (상속 포함)"""
        permissions = set(self.role_permissions.filter(is_granted=True).values_list('permission_id', flat=True))
        
        if self.inherit_permissions and self.parent:
            permissions.update(self.parent.get_all_permissions())
        
        return permissions
    
    def can_assign_to_employee(self, employee: Employee) -> bool:
        """직원에게 역할 할당 가능 여부 확인"""
        if not self.is_active:
            return False
        
        if self.max_assignees:
            current_count = self.user_roles.filter(is_active=True).count()
            if current_count >= self.max_assignees:
                return False
        
        return True


class Permission(models.Model):
    """권한 정의"""
    PERMISSION_TYPE_CHOICES = [
        ('CREATE', '생성'),
        ('READ', '조회'),
        ('UPDATE', '수정'),
        ('DELETE', '삭제'),
        ('APPROVE', '승인'),
        ('MANAGE', '관리'),
        ('EXECUTE', '실행'),
        ('ADMIN', '관리자'),
    ]
    
    RESOURCE_TYPE_CHOICES = [
        ('EMPLOYEE', '직원 정보'),
        ('DEPARTMENT', '부서 정보'),
        ('EVALUATION', '평가'),
        ('COMPENSATION', '보상'),
        ('TRAINING', '교육'),
        ('RECRUITMENT', '채용'),
        ('ANNOUNCEMENT', '공지사항'),
        ('REPORT', '보고서'),
        ('SYSTEM', '시스템'),
        ('ALL', '전체'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="권한명")
    codename = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="권한 코드",
        help_text="프로그래밍에서 사용하는 고유 코드"
    )
    description = models.TextField(blank=True, verbose_name="설명")
    
    # 권한 분류
    permission_type = models.CharField(
        max_length=20,
        choices=PERMISSION_TYPE_CHOICES,
        verbose_name="권한 유형"
    )
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        verbose_name="리소스 유형"
    )
    
    # 권한 레벨
    level = models.IntegerField(
        default=1,
        verbose_name="권한 레벨",
        help_text="1: 일반, 5: 관리자, 10: 시스템"
    )
    
    # 상태
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    is_system = models.BooleanField(
        default=False,
        verbose_name="시스템 권한",
        help_text="시스템에서 관리하는 권한 (수정 불가)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '권한'
        verbose_name_plural = '권한 관리'
        ordering = ['resource_type', 'permission_type', 'level']
        unique_together = ['permission_type', 'resource_type']
    
    def __str__(self):
        return f"{self.get_resource_type_display()} {self.get_permission_type_display()}"


class RolePermission(models.Model):
    """역할-권한 매핑"""
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions',
        verbose_name="역할"
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions',
        verbose_name="권한"
    )
    
    # 권한 상태
    is_granted = models.BooleanField(default=True, verbose_name="권한 부여")
    is_denied = models.BooleanField(default=False, verbose_name="권한 거부")
    
    # 조건부 권한
    conditions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="조건",
        help_text="권한 적용 조건 (JSON)"
    )
    
    # 메타데이터
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name="부여일")
    granted_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="부여자"
    )
    
    class Meta:
        verbose_name = '역할 권한'
        verbose_name_plural = '역할 권한 관리'
        unique_together = ['role', 'permission']
    
    def __str__(self):
        status = "부여" if self.is_granted else "거부" if self.is_denied else "미설정"
        return f"{self.role.name} - {self.permission.name} ({status})"


class UserRole(models.Model):
    """사용자-역할 할당"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name="사용자"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name="역할"
    )
    
    # 할당 범위
    scope_type = models.CharField(
        max_length=20,
        choices=[
            ('GLOBAL', '전체'),
            ('DEPARTMENT', '부서'),
            ('PROJECT', '프로젝트'),
            ('CUSTOM', '사용자 정의'),
        ],
        default='GLOBAL',
        verbose_name="적용 범위"
    )
    scope_value = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="범위 값",
        help_text="부서 코드, 프로젝트 ID 등"
    )
    
    # 기간
    start_date = models.DateTimeField(default=timezone.now, verbose_name="시작일")
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="종료일"
    )
    
    # 상태
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    is_primary = models.BooleanField(
        default=False,
        verbose_name="기본 역할",
        help_text="사용자의 주요 역할"
    )
    
    # 할당 정보
    assigned_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_roles',
        verbose_name="할당자"
    )
    assigned_reason = models.TextField(blank=True, verbose_name="할당 사유")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '사용자 역할'
        verbose_name_plural = '사용자 역할 관리'
        ordering = ['-is_primary', '-start_date']
        unique_together = ['user', 'role', 'scope_type', 'scope_value']
    
    def __str__(self):
        scope_info = f" ({self.scope_value})" if self.scope_value else ""
        return f"{self.user.name} - {self.role.name}{scope_info}"
    
    @property
    def is_expired(self):
        """만료 여부 확인"""
        if self.end_date:
            return timezone.now() > self.end_date
        return False
    
    def deactivate(self, reason: str = ""):
        """역할 비활성화"""
        self.is_active = False
        self.end_date = timezone.now()
        if reason:
            self.assigned_reason += f"\n비활성화: {reason}"
        self.save()


class AccessLog(models.Model):
    """접근 로그"""
    ACTION_CHOICES = [
        ('LOGIN', '로그인'),
        ('LOGOUT', '로그아웃'),
        ('VIEW', '조회'),
        ('CREATE', '생성'),
        ('UPDATE', '수정'),
        ('DELETE', '삭제'),
        ('APPROVE', '승인'),
        ('DOWNLOAD', '다운로드'),
        ('EXPORT', '내보내기'),
        ('DENIED', '접근 거부'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 사용자 정보
    user = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='access_logs',
        verbose_name="사용자"
    )
    
    # 접근 정보
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="액션"
    )
    resource_type = models.CharField(
        max_length=50,
        verbose_name="리소스 유형"
    )
    resource_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="리소스 ID"
    )
    
    # 접근 대상 객체 (Generic Foreign Key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=100, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 접근 결과
    is_successful = models.BooleanField(default=True, verbose_name="성공 여부")
    error_message = models.TextField(blank=True, verbose_name="오류 메시지")
    
    # 권한 정보
    used_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="사용된 역할"
    )
    used_permission = models.ForeignKey(
        Permission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="사용된 권한"
    )
    
    # 요청 정보
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP 주소"
    )
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    request_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="요청 경로"
    )
    request_method = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="요청 메서드"
    )
    
    # 세션 정보
    session_key = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="세션 키"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '접근 로그'
        verbose_name_plural = '접근 로그 관리'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['resource_type', 'created_at']),
            models.Index(fields=['is_successful', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.get_action_display()} - {self.resource_type}"


class SecurityPolicy(models.Model):
    """보안 정책"""
    POLICY_TYPE_CHOICES = [
        ('PASSWORD', '패스워드 정책'),
        ('SESSION', '세션 정책'),
        ('ACCESS', '접근 정책'),
        ('DATA', '데이터 정책'),
        ('AUDIT', '감사 정책'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="정책명")
    description = models.TextField(verbose_name="설명")
    
    # 정책 분류
    policy_type = models.CharField(
        max_length=20,
        choices=POLICY_TYPE_CHOICES,
        verbose_name="정책 유형"
    )
    
    # 정책 설정
    settings = models.JSONField(
        default=dict,
        verbose_name="정책 설정",
        help_text="정책별 상세 설정 (JSON)"
    )
    
    # 적용 범위
    applies_to_all = models.BooleanField(
        default=True,
        verbose_name="전체 적용"
    )
    target_roles = models.ManyToManyField(
        Role,
        blank=True,
        verbose_name="대상 역할"
    )
    target_departments = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="대상 부서",
        help_text="부서 코드 (쉼표로 구분)"
    )
    
    # 상태
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    is_enforced = models.BooleanField(
        default=True,
        verbose_name="강제 적용",
        help_text="정책 위반시 접근 차단"
    )
    
    # 시행 기간
    effective_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="시행일"
    )
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="만료일"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="생성자"
    )
    
    class Meta:
        verbose_name = '보안 정책'
        verbose_name_plural = '보안 정책 관리'
        ordering = ['policy_type', 'name']
    
    def __str__(self):
        return f"{self.get_policy_type_display()} - {self.name}"
    
    def is_applicable_to_user(self, user: Employee) -> bool:
        """사용자에게 정책이 적용되는지 확인"""
        if not self.is_active:
            return False
        
        if self.applies_to_all:
            return True
        
        # 역할 기반 확인
        if self.target_roles.exists():
            user_role_ids = user.user_roles.filter(
                is_active=True
            ).values_list('role_id', flat=True)
            if self.target_roles.filter(id__in=user_role_ids).exists():
                return True
        
        # 부서 기반 확인
        if self.target_departments and user.department:
            dept_codes = [code.strip() for code in self.target_departments.split(',')]
            if user.department in dept_codes:
                return True
        
        return False


class AuditTrail(models.Model):
    """감사 추적"""
    AUDIT_TYPE_CHOICES = [
        ('ROLE_CHANGE', '역할 변경'),
        ('PERMISSION_CHANGE', '권한 변경'),
        ('POLICY_CHANGE', '정책 변경'),
        ('USER_ACCESS', '사용자 접근'),
        ('DATA_EXPORT', '데이터 내보내기'),
        ('SYSTEM_CONFIG', '시스템 설정'),
        ('SECURITY_INCIDENT', '보안 사고'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 감사 분류
    audit_type = models.CharField(
        max_length=20,
        choices=AUDIT_TYPE_CHOICES,
        verbose_name="감사 유형"
    )
    
    # 액션 정보
    action = models.CharField(max_length=100, verbose_name="액션")
    description = models.TextField(verbose_name="설명")
    
    # 관련 사용자
    user = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='audit_trails',
        verbose_name="실행자"
    )
    target_user = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='target_audit_trails',
        verbose_name="대상 사용자"
    )
    
    # 변경 내용
    old_value = models.JSONField(
        null=True,
        blank=True,
        verbose_name="이전 값"
    )
    new_value = models.JSONField(
        null=True,
        blank=True,
        verbose_name="새 값"
    )
    
    # 관련 객체
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=100, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 위험도
    risk_level = models.CharField(
        max_length=10,
        choices=[
            ('LOW', '낮음'),
            ('MEDIUM', '보통'),
            ('HIGH', '높음'),
            ('CRITICAL', '매우 높음'),
        ],
        default='LOW',
        verbose_name="위험도"
    )
    
    # 요청 정보
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP 주소"
    )
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '감사 추적'
        verbose_name_plural = '감사 추적 관리'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['audit_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['risk_level', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.action} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
