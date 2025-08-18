"""
HR Dashboard Models
OK금융그룹 인력현황 관리를 위한 데이터베이스 모델
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class HREmployee(models.Model):
    """HR 직원 마스터 (국내/해외 통합)"""
    
    LOCATION_TYPE_CHOICES = [
        ('domestic', '국내'),
        ('overseas', '해외'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('regular', '정규직'),
        ('PL', 'PL'),
        ('Non-PL', 'Non-PL'),
    ]
    
    STATUS_CHOICES = [
        ('active', '재직'),
        ('resigned', '퇴직'),
        ('new_hire', '신규입사'),
    ]
    
    # 기본 정보
    employee_no = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='사번')
    name = models.CharField(max_length=100, verbose_name='성명')
    company = models.CharField(max_length=100, verbose_name='회사')
    department = models.CharField(max_length=100, null=True, blank=True, verbose_name='부서')
    position = models.CharField(max_length=50, null=True, blank=True, verbose_name='직책')
    job_level = models.CharField(max_length=50, null=True, blank=True, verbose_name='직급')
    
    # 위치 정보
    location_type = models.CharField(
        max_length=20, 
        choices=LOCATION_TYPE_CHOICES, 
        default='domestic',
        verbose_name='위치 구분'
    )
    country = models.CharField(max_length=50, null=True, blank=True, verbose_name='국가')
    branch = models.CharField(max_length=100, null=True, blank=True, verbose_name='지점')
    
    # 고용 정보
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='regular',
        verbose_name='고용 형태'
    )
    hire_date = models.DateField(null=True, blank=True, verbose_name='입사일')
    resignation_date = models.DateField(null=True, blank=True, verbose_name='퇴사일')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='상태'
    )
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        db_table = 'hr_employees'
        verbose_name = 'HR 직원'
        verbose_name_plural = 'HR 직원들'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['company']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.company})'
    
    @property
    def is_active(self):
        """현재 재직 중인지 확인"""
        return self.status == 'active' and not self.resignation_date


class HRMonthlySnapshot(models.Model):
    """월간 스냅샷 (시점 데이터)"""
    
    # 스냅샷 정보
    snapshot_date = models.DateField(verbose_name='스냅샷 날짜')
    employee = models.ForeignKey(
        HREmployee, 
        on_delete=models.CASCADE,
        related_name='monthly_snapshots',
        verbose_name='직원'
    )
    
    # 시점 데이터
    company = models.CharField(max_length=100, verbose_name='회사')
    department = models.CharField(max_length=100, null=True, blank=True, verbose_name='부서')
    position = models.CharField(max_length=50, null=True, blank=True, verbose_name='직책')
    job_level = models.CharField(max_length=50, null=True, blank=True, verbose_name='직급')
    location_type = models.CharField(max_length=20, verbose_name='위치 구분')
    country = models.CharField(max_length=50, null=True, blank=True, verbose_name='국가')
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    
    class Meta:
        db_table = 'hr_monthly_snapshots'
        verbose_name = '월간 스냅샷'
        verbose_name_plural = '월간 스냅샷들'
        unique_together = ['snapshot_date', 'employee']
        indexes = [
            models.Index(fields=['snapshot_date']),
        ]
    
    def __str__(self):
        return f'{self.employee.name} - {self.snapshot_date}'


class HRContractor(models.Model):
    """외주 인력"""
    
    STATUS_CHOICES = [
        ('active', '진행중'),
        ('completed', '종료'),
        ('pending', '예정'),
    ]
    
    # 기본 정보
    contractor_name = models.CharField(max_length=100, verbose_name='성명')
    vendor_company = models.CharField(max_length=200, verbose_name='소속업체')
    project_name = models.CharField(max_length=200, verbose_name='프로젝트명')
    department = models.CharField(max_length=100, null=True, blank=True, verbose_name='투입부서')
    role = models.CharField(max_length=100, null=True, blank=True, verbose_name='담당업무')
    
    # 계약 정보
    start_date = models.DateField(null=True, blank=True, verbose_name='투입일')
    end_date = models.DateField(null=True, blank=True, verbose_name='종료일')
    daily_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='일단가'
    )
    monthly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='월단가'
    )
    
    # 상태
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='상태'
    )
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        db_table = 'hr_contractors'
        verbose_name = '외주 인력'
        verbose_name_plural = '외주 인력들'
        indexes = [
            models.Index(fields=['vendor_company']),
            models.Index(fields=['project_name']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f'{self.contractor_name} - {self.project_name}'
    
    @property
    def project_status(self):
        """프로젝트 상태 확인"""
        today = timezone.now().date()
        if self.end_date and self.end_date < today:
            return '종료'
        elif self.start_date and self.start_date > today:
            return '예정'
        else:
            return '진행중'


class OutsourcedStaff(models.Model):
    """외주인력 현황 (요구사항 기반)"""
    
    BASE_TYPE_CHOICES = [
        ('week', '전주'),
        ('month', '전월'),
        ('year_end', '전년말'),
    ]
    
    STAFF_TYPE_CHOICES = [
        ('resident', '상주'),
        ('non_resident', '비상주'),
        ('project', '프로젝트'),
    ]
    
    # 기본 정보
    company_name = models.CharField(max_length=100, verbose_name='계열사명')
    project_name = models.CharField(max_length=200, verbose_name='프로젝트명')
    staff_type = models.CharField(
        max_length=20,
        choices=STAFF_TYPE_CHOICES,
        default='resident',
        verbose_name='인력구분'
    )
    headcount = models.IntegerField(default=0, verbose_name='외주인원 수')
    report_date = models.DateField(verbose_name='기준일')
    base_type = models.CharField(
        max_length=20,
        choices=BASE_TYPE_CHOICES,
        default='week',
        verbose_name='기준유형'
    )
    
    # 증감 정보
    previous_headcount = models.IntegerField(default=0, verbose_name='이전 인원수')
    headcount_change = models.IntegerField(default=0, verbose_name='증감 인원')
    change_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        verbose_name='증감율(%)'
    )
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='업로드 사용자'
    )
    
    class Meta:
        db_table = 'hr_outsourced_staff'
        verbose_name = '외주인력 현황'
        verbose_name_plural = '외주인력 현황들'
        unique_together = ['company_name', 'project_name', 'report_date', 'staff_type']
        indexes = [
            models.Index(fields=['company_name']),
            models.Index(fields=['report_date']),
            models.Index(fields=['staff_type']),
        ]
    
    def __str__(self):
        return f'{self.company_name} - {self.project_name} ({self.report_date})'
    
    def calculate_change(self, previous_record=None):
        """증감 계산"""
        if previous_record:
            self.previous_headcount = previous_record.headcount
            self.headcount_change = self.headcount - previous_record.headcount
            if previous_record.headcount > 0:
                self.change_rate = (self.headcount_change / previous_record.headcount) * 100
            else:
                self.change_rate = 100 if self.headcount > 0 else 0
        else:
            self.previous_headcount = 0
            self.headcount_change = self.headcount
            self.change_rate = 100 if self.headcount > 0 else 0
    
    @property
    def change_status(self):
        """증감 상태 (증가/감소/유지)"""
        if self.headcount_change > 0:
            return 'increase'
        elif self.headcount_change < 0:
            return 'decrease'
        else:
            return 'maintain'


class HRFileUpload(models.Model):
    """파일 업로드 이력"""
    
    FILE_TYPE_CHOICES = [
        ('domestic', '국내 인력현황'),
        ('overseas', '해외 인력현황'),
        ('contractor', '외주 현황'),
    ]
    
    PROCESS_STATUS_CHOICES = [
        ('pending', '대기중'),
        ('processing', '처리중'),
        ('completed', '완료'),
        ('failed', '실패'),
    ]
    
    # 파일 정보
    file_name = models.CharField(max_length=255, verbose_name='파일명')
    file_type = models.CharField(
        max_length=50,
        choices=FILE_TYPE_CHOICES,
        verbose_name='파일 유형'
    )
    report_date = models.DateField(verbose_name='보고서 날짜')
    
    # 업로드 정보
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='업로드 일시')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='업로드 사용자'
    )
    
    # 처리 정보
    processed_status = models.CharField(
        max_length=20,
        choices=PROCESS_STATUS_CHOICES,
        default='pending',
        verbose_name='처리 상태'
    )
    total_records = models.IntegerField(null=True, blank=True, verbose_name='전체 레코드')
    success_records = models.IntegerField(null=True, blank=True, verbose_name='성공 레코드')
    error_records = models.IntegerField(null=True, blank=True, verbose_name='오류 레코드')
    error_log = models.TextField(null=True, blank=True, verbose_name='오류 로그')
    
    class Meta:
        db_table = 'hr_file_uploads'
        verbose_name = '파일 업로드 이력'
        verbose_name_plural = '파일 업로드 이력들'
        ordering = ['-upload_date']
    
    def __str__(self):
        return f'{self.file_name} - {self.get_file_type_display()}'


class OverseasWorkforce(models.Model):
    """해외 인력 현황"""
    
    CORPORATION_CHOICES = [
        ('OK Bank (인니)', 'OK Bank (인니)'),
        ('OK Asset (인니)', 'OK Asset (인니)'),
        ('PPCBank (캄보디아)', 'PPCBank (캄보디아)'),
        ('천진법인 (중국)', '천진법인 (중국)'),
    ]
    
    POSITION_CHOICES = [
        ('이사', '이사'),
        ('부장급', '부장급'),
        ('차장', '차장'),
        ('과장', '과장'),
        ('대리', '대리'),
        ('사원', '사원'),
    ]
    
    # 기본 정보
    corporation = models.CharField(
        max_length=100, 
        choices=CORPORATION_CHOICES,
        verbose_name='법인'
    )
    report_date = models.DateField(verbose_name='기준일')
    
    # 직급별 인원 수
    executive_count = models.IntegerField(default=0, verbose_name='이사')
    general_manager_count = models.IntegerField(default=0, verbose_name='부장급')
    deputy_manager_count = models.IntegerField(default=0, verbose_name='차장')
    manager_count = models.IntegerField(default=0, verbose_name='과장')
    assistant_manager_count = models.IntegerField(default=0, verbose_name='대리')
    staff_count = models.IntegerField(default=0, verbose_name='사원')
    
    # 직책별 인원 수 (OK Bank 인니)
    ceo_count = models.IntegerField(default=0, verbose_name='대표이사')
    division_head_count = models.IntegerField(default=0, verbose_name='본부장')
    department_head_count = models.IntegerField(default=0, verbose_name='부서장')
    branch_manager_count = models.IntegerField(default=0, verbose_name='지점장/Br.Mg')
    team_leader_count = models.IntegerField(default=0, verbose_name='팀장/T.leader/Staff')
    
    # 직책별 인원 수 (OK Asset 인니)
    cbo_count = models.IntegerField(default=0, verbose_name='최고사업책임자')
    
    # 직책별 인원 수 (PPCBank 캄보디아)
    evp_count = models.IntegerField(default=0, verbose_name='부문장/수석부사장')
    svp_count = models.IntegerField(default=0, verbose_name='상무이사/수석부사장')
    vp_count = models.IntegerField(default=0, verbose_name='상무이사')
    
    # 합계
    total_count = models.IntegerField(default=0, verbose_name='합계')
    
    # 원본 데이터 저장 (엑셀 형식 그대로)
    raw_data = models.JSONField(default=dict, blank=True, verbose_name='원본 데이터')
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='업로드 사용자'
    )
    
    class Meta:
        db_table = 'hr_overseas_workforce'
        verbose_name = '해외 인력 현황'
        verbose_name_plural = '해외 인력 현황들'
        unique_together = ['corporation', 'report_date']
        indexes = [
            models.Index(fields=['corporation']),
            models.Index(fields=['report_date']),
        ]
    
    def calculate_total(self):
        """전체 인원 계산"""
        self.total_count = (
            self.executive_count + 
            self.general_manager_count + 
            self.deputy_manager_count + 
            self.manager_count + 
            self.assistant_manager_count + 
            self.staff_count
        )
        return self.total_count
    
    def save(self, *args, **kwargs):
        """저장 시 자동으로 합계 계산"""
        self.calculate_total()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.corporation} - {self.report_date} ({self.total_count}명)"