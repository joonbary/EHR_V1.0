from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from django.utils import timezone
import uuid


class Department(models.Model):
    """부서 정보"""
    DEPARTMENT_TYPE_CHOICES = [
        ('HQ', '본사'),
        ('BRANCH', '지점'),
        ('DIVISION', '사업부'),
        ('TEAM', '팀'),
        ('CENTER', '센터'),
        ('LAB', '연구소'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name="부서 코드")
    name = models.CharField(max_length=100, verbose_name="부서명")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="부서명(영문)")
    
    # 계층 구조
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="상위 부서"
    )
    level = models.IntegerField(default=1, verbose_name="조직 레벨")
    department_type = models.CharField(
        max_length=20,
        choices=DEPARTMENT_TYPE_CHOICES,
        default='TEAM',
        verbose_name="부서 유형"
    )
    
    # 부서장
    manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name="부서장"
    )
    
    # 부서 정보
    description = models.TextField(blank=True, verbose_name="부서 설명")
    location = models.CharField(max_length=100, blank=True, verbose_name="위치")
    phone = models.CharField(max_length=20, blank=True, verbose_name="대표 전화")
    email = models.EmailField(blank=True, verbose_name="대표 이메일")
    
    # 상태
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    established_date = models.DateField(null=True, blank=True, verbose_name="설립일")
    closed_date = models.DateField(null=True, blank=True, verbose_name="폐쇄일")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_departments',
        verbose_name="생성자"
    )
    
    class Meta:
        verbose_name = '부서'
        verbose_name_plural = '부서 관리'
        ordering = ['level', 'code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['parent', 'level']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_full_path(self):
        """전체 부서 경로 반환"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_employee_count(self):
        """부서 직원 수 반환"""
        return self.employees.filter(employment_status='재직').count()
    
    def get_all_employees(self):
        """하위 부서 포함 모든 직원 반환"""
        employees = list(self.employees.filter(employment_status='재직'))
        for child in self.children.all():
            employees.extend(child.get_all_employees())
        return employees
    
    def get_descendants(self):
        """모든 하위 부서 반환"""
        descendants = list(self.children.all())
        for child in self.children.all():
            descendants.extend(child.get_descendants())
        return descendants


class Position(models.Model):
    """직위/직책 정보"""
    POSITION_TYPE_CHOICES = [
        ('EXECUTIVE', '임원'),
        ('MANAGEMENT', '관리직'),
        ('PROFESSIONAL', '전문직'),
        ('GENERAL', '일반직'),
        ('TECHNICAL', '기술직'),
        ('SUPPORT', '지원직'),
    ]
    
    code = models.CharField(max_length=20, unique=True, verbose_name="직위 코드")
    name = models.CharField(max_length=50, verbose_name="직위명")
    name_en = models.CharField(max_length=50, blank=True, verbose_name="직위명(영문)")
    
    # 직위 정보
    position_type = models.CharField(
        max_length=20,
        choices=POSITION_TYPE_CHOICES,
        default='GENERAL',
        verbose_name="직위 유형"
    )
    rank = models.IntegerField(
        default=1,
        verbose_name="직급 순위",
        help_text="낮을수록 높은 직급"
    )
    growth_level_min = models.IntegerField(
        default=1,
        verbose_name="최소 성장레벨"
    )
    growth_level_max = models.IntegerField(
        default=6,
        verbose_name="최대 성장레벨"
    )
    
    # 권한 및 역할
    is_manager = models.BooleanField(default=False, verbose_name="관리자 여부")
    can_approve = models.BooleanField(default=False, verbose_name="결재 권한")
    can_evaluate = models.BooleanField(default=False, verbose_name="평가 권한")
    
    # 설명
    description = models.TextField(blank=True, verbose_name="직위 설명")
    responsibilities = models.TextField(blank=True, verbose_name="주요 책임")
    requirements = models.TextField(blank=True, verbose_name="자격 요건")
    
    # 상태
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '직위'
        verbose_name_plural = '직위 관리'
        ordering = ['rank', 'code']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_employee_count(self):
        """해당 직위 직원 수"""
        return Employee.objects.filter(
            new_position=self.name,
            employment_status='재직'
        ).count()


class OrganizationChart(models.Model):
    """조직도 버전 관리"""
    version = models.CharField(max_length=20, unique=True, verbose_name="버전")
    name = models.CharField(max_length=100, verbose_name="조직도명")
    description = models.TextField(blank=True, verbose_name="설명")
    
    # 상태
    is_active = models.BooleanField(default=False, verbose_name="활성 버전")
    effective_date = models.DateField(verbose_name="시행일")
    end_date = models.DateField(null=True, blank=True, verbose_name="종료일")
    
    # 승인 정보
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_org_charts',
        verbose_name="승인자"
    )
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="승인일")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_org_charts',
        verbose_name="생성자"
    )
    
    class Meta:
        verbose_name = '조직도'
        verbose_name_plural = '조직도 관리'
        ordering = ['-effective_date', '-version']
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
    
    def activate(self):
        """조직도 활성화"""
        # 기존 활성 조직도 비활성화
        OrganizationChart.objects.filter(is_active=True).update(
            is_active=False,
            end_date=timezone.now().date()
        )
        # 현재 조직도 활성화
        self.is_active = True
        self.save()


class DepartmentHistory(models.Model):
    """부서 변경 이력"""
    CHANGE_TYPE_CHOICES = [
        ('CREATE', '신설'),
        ('MERGE', '통합'),
        ('SPLIT', '분할'),
        ('RENAME', '명칭변경'),
        ('REORGANIZE', '개편'),
        ('CLOSE', '폐쇄'),
    ]
    
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="부서"
    )
    organization_chart = models.ForeignKey(
        OrganizationChart,
        on_delete=models.CASCADE,
        verbose_name="조직도 버전"
    )
    
    # 변경 정보
    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPE_CHOICES,
        verbose_name="변경 유형"
    )
    old_name = models.CharField(max_length=100, blank=True, verbose_name="이전 명칭")
    new_name = models.CharField(max_length=100, blank=True, verbose_name="새 명칭")
    old_parent = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='old_parent_history',
        verbose_name="이전 상위부서"
    )
    new_parent = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='new_parent_history',
        verbose_name="새 상위부서"
    )
    
    # 변경 사유
    reason = models.TextField(verbose_name="변경 사유")
    
    # 메타데이터
    changed_date = models.DateField(verbose_name="변경일")
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="변경자"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '부서 변경 이력'
        verbose_name_plural = '부서 변경 이력'
        ordering = ['-changed_date', 'department']
    
    def __str__(self):
        return f"{self.department.name} - {self.get_change_type_display()} ({self.changed_date})"


class EmployeeTransfer(models.Model):
    """인사 이동 기록"""
    TRANSFER_TYPE_CHOICES = [
        ('PROMOTION', '승진'),
        ('TRANSFER', '전보'),
        ('ASSIGNMENT', '배치'),
        ('SECONDMENT', '파견'),
        ('RETURN', '복귀'),
        ('DEMOTION', '강등'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='transfers',
        verbose_name="직원"
    )
    
    # 이동 정보
    transfer_type = models.CharField(
        max_length=20,
        choices=TRANSFER_TYPE_CHOICES,
        verbose_name="이동 유형"
    )
    transfer_date = models.DateField(verbose_name="이동일")
    
    # 이전 정보
    old_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transfers_from',
        verbose_name="이전 부서"
    )
    old_position = models.CharField(max_length=50, verbose_name="이전 직위")
    old_growth_level = models.IntegerField(verbose_name="이전 성장레벨")
    
    # 새 정보
    new_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transfers_to',
        verbose_name="새 부서"
    )
    new_position = models.CharField(max_length=50, verbose_name="새 직위")
    new_growth_level = models.IntegerField(verbose_name="새 성장레벨")
    
    # 상세 정보
    reason = models.TextField(verbose_name="이동 사유")
    remarks = models.TextField(blank=True, verbose_name="비고")
    
    # 승인 정보
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_transfers',
        verbose_name="승인자"
    )
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="승인일")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="생성자"
    )
    
    class Meta:
        verbose_name = '인사 이동'
        verbose_name_plural = '인사 이동 관리'
        ordering = ['-transfer_date', 'employee']
        indexes = [
            models.Index(fields=['employee', 'transfer_date']),
            models.Index(fields=['transfer_type', 'transfer_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.name} - {self.get_transfer_type_display()} ({self.transfer_date})"
    
    def execute_transfer(self):
        """인사 이동 실행"""
        if self.approved_date:
            # 직원 정보 업데이트
            self.employee.department = self.new_department.code if self.new_department else None
            self.employee.new_position = self.new_position
            self.employee.growth_level = self.new_growth_level
            self.employee.save()
            return True
        return False


class TeamAssignment(models.Model):
    """팀 배치 (한 직원이 여러 팀에 속할 수 있음)"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='team_assignments',
        verbose_name="직원"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='team_members',
        verbose_name="팀/부서"
    )
    
    # 배치 정보
    role = models.CharField(max_length=100, verbose_name="역할")
    is_primary = models.BooleanField(default=True, verbose_name="주 소속")
    assignment_ratio = models.IntegerField(
        default=100,
        verbose_name="업무 비중(%)",
        help_text="해당 팀에서의 업무 비중"
    )
    
    # 기간
    start_date = models.DateField(verbose_name="시작일")
    end_date = models.DateField(null=True, blank=True, verbose_name="종료일")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="생성자"
    )
    
    class Meta:
        verbose_name = '팀 배치'
        verbose_name_plural = '팀 배치 관리'
        ordering = ['-is_primary', '-assignment_ratio', 'employee']
        unique_together = ['employee', 'department', 'start_date']
    
    def __str__(self):
        primary = "주" if self.is_primary else "부"
        return f"{self.employee.name} - {self.department.name} ({primary}, {self.assignment_ratio}%)"
    
    @property
    def is_active(self):
        """현재 활성 상태 여부"""
        if self.end_date:
            return self.end_date >= timezone.now().date()
        return True