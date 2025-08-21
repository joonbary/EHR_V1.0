from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class OrganizationStructure(models.Model):
    """
    조직 구조 마스터 테이블
    5단계 체계: 그룹 > 계열사 > 본부 > 부 > 팀
    """
    
    LEVEL_CHOICES = [
        (1, '그룹'),
        (2, '계열사'),
        (3, '본부'),
        (4, '부'),
        (5, '팀'),
    ]
    
    STATUS_CHOICES = [
        ('active', '활성'),
        ('inactive', '비활성'),
        ('pending', '준비중'),
    ]
    
    # 조직 기본 정보
    org_code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='조직코드',
        help_text='예: GRP001, COM001, HQ001, DEPT001, TEAM001'
    )
    org_name = models.CharField(max_length=100, verbose_name='조직명')
    org_level = models.IntegerField(choices=LEVEL_CHOICES, verbose_name='조직레벨')
    
    # 계층 구조 (상위 조직)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children',
        verbose_name='상위조직'
    )
    
    # 조직 경로 (전체 계층 경로 저장 - 빠른 조회용)
    full_path = models.CharField(
        max_length=500, 
        blank=True,
        verbose_name='전체경로',
        help_text='예: OK금융그룹 > OK저축은행 > 디지털본부 > IT개발부 > 개발1팀'
    )
    
    # 각 레벨별 명칭 (빠른 필터링용)
    group_name = models.CharField(max_length=100, blank=True, verbose_name='그룹명')
    company_name = models.CharField(max_length=100, blank=True, verbose_name='계열사명')
    headquarters_name = models.CharField(max_length=100, blank=True, verbose_name='본부명')
    department_name = models.CharField(max_length=100, blank=True, verbose_name='부서명')
    team_name = models.CharField(max_length=100, blank=True, verbose_name='팀명')
    
    # 조직 상세 정보
    description = models.TextField(blank=True, verbose_name='설명')
    establishment_date = models.DateField(null=True, blank=True, verbose_name='설립일')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name='상태'
    )
    
    # 조직장 정보
    leader = models.ForeignKey(
        'Employee', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='leading_organizations',
        verbose_name='조직장'
    )
    
    # 정렬 순서
    sort_order = models.IntegerField(default=0, verbose_name='정렬순서')
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_organizations',
        verbose_name='생성자'
    )
    
    class Meta:
        verbose_name = '조직구조'
        verbose_name_plural = '조직구조'
        ordering = ['org_level', 'sort_order', 'org_code']
        indexes = [
            models.Index(fields=['org_code']),
            models.Index(fields=['org_level', 'status']),
            models.Index(fields=['parent']),
        ]
        
    def __str__(self):
        return f"[{self.get_org_level_display()}] {self.org_name}"
    
    def save(self, *args, **kwargs):
        """저장 시 full_path 자동 생성"""
        # 전체 경로 생성
        path_parts = []
        current = self
        while current:
            path_parts.insert(0, current.org_name)
            current = current.parent
        self.full_path = ' > '.join(path_parts)
        
        # 각 레벨별 명칭 저장
        self._set_level_names(path_parts)
        
        super().save(*args, **kwargs)
    
    def _set_level_names(self, path_parts):
        """레벨별 명칭 설정"""
        level_mapping = {
            1: 'group_name',
            2: 'company_name',
            3: 'headquarters_name',
            4: 'department_name',
            5: 'team_name'
        }
        
        # 현재 조직의 레벨에 따라 해당 필드 설정
        if self.org_level in level_mapping:
            setattr(self, level_mapping[self.org_level], self.org_name)
        
        # 상위 조직들의 명칭도 저장
        current = self.parent
        while current:
            if current.org_level in level_mapping:
                setattr(self, level_mapping[current.org_level], current.org_name)
            current = current.parent
    
    def get_descendants(self, include_self=False):
        """하위 조직 전체 조회"""
        descendants = []
        if include_self:
            descendants.append(self)
        
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        
        return descendants
    
    def get_ancestors(self, include_self=False):
        """상위 조직 전체 조회"""
        ancestors = []
        if include_self:
            ancestors.append(self)
        
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        
        return ancestors
    
    def get_employee_count(self):
        """소속 직원 수 (하위 조직 포함)"""
        from .models import Employee
        org_ids = [org.id for org in self.get_descendants(include_self=True)]
        return Employee.objects.filter(
            organization__in=org_ids,
            employment_status='재직'
        ).count()


class OrganizationUploadHistory(models.Model):
    """조직 구조 업로드 이력"""
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('processing', '처리중'),
        ('completed', '완료'),
        ('failed', '실패'),
    ]
    
    # 업로드 정보
    file_name = models.CharField(max_length=255, verbose_name='파일명')
    file_path = models.FileField(
        upload_to='organization_uploads/%Y/%m/', 
        verbose_name='업로드파일'
    )
    
    # 처리 상태
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='상태'
    )
    total_rows = models.IntegerField(default=0, verbose_name='전체 행수')
    processed_rows = models.IntegerField(default=0, verbose_name='처리된 행수')
    success_count = models.IntegerField(default=0, verbose_name='성공 건수')
    error_count = models.IntegerField(default=0, verbose_name='오류 건수')
    
    # 오류 상세
    error_details = models.JSONField(
        default=list, 
        blank=True,
        verbose_name='오류상세',
        help_text='[{"row": 2, "error": "중복된 조직코드"}]'
    )
    
    # 메타데이터
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드일시')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='처리완료일시')
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='업로드자'
    )
    
    # 처리 옵션
    options = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name='처리옵션',
        help_text='{"update_existing": true, "create_missing": true}'
    )
    
    class Meta:
        verbose_name = '조직구조 업로드이력'
        verbose_name_plural = '조직구조 업로드이력'
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.file_name} - {self.get_status_display()} ({self.uploaded_at})"


class EmployeeOrganizationMapping(models.Model):
    """직원-조직 매핑 테이블"""
    
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='organization_mappings',
        verbose_name='직원'
    )
    
    organization = models.ForeignKey(
        OrganizationStructure,
        on_delete=models.CASCADE,
        related_name='employee_mappings',
        verbose_name='조직'
    )
    
    # 매핑 정보
    is_primary = models.BooleanField(
        default=True, 
        verbose_name='주소속여부',
        help_text='기본 소속 조직 여부'
    )
    
    role = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name='역할',
        help_text='해당 조직에서의 역할'
    )
    
    # 기간 정보
    start_date = models.DateField(
        default=datetime.now,
        verbose_name='시작일'
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name='종료일'
    )
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '직원-조직 매핑'
        verbose_name_plural = '직원-조직 매핑'
        unique_together = [['employee', 'organization', 'is_primary']]
        ordering = ['-is_primary', '-start_date']
        
    def __str__(self):
        return f"{self.employee.name} - {self.organization.org_name}"
    
    def is_active(self):
        """현재 활성 매핑인지 확인"""
        from datetime import date
        today = date.today()
        return self.start_date <= today and (not self.end_date or self.end_date >= today)