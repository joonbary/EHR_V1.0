from django.db import models
from django.contrib.auth.models import User
from datetime import date

# HR Dashboard models import
from .models_hr import HREmployee, HRMonthlySnapshot, HRContractor, HRFileUpload

# Weekly Workforce models import
from .models_workforce import WeeklyWorkforceSnapshot, WeeklyJoinLeave, WeeklyWorkforceChange

# Organization Structure models import
from .models_organization import OrganizationStructure, OrganizationUploadHistory, EmployeeOrganizationMapping

# Create your models here.

class Employee(models.Model):
    DEPARTMENT_CHOICES = [
        ('IT', 'IT'),
        ('HR', '인사'),
        ('FINANCE', '재무'),
        ('MARKETING', '마케팅'),
        ('SALES', '영업'),
        ('OPERATIONS', '운영'),
    ]
    
    POSITION_CHOICES = [
        ('INTERN', '인턴'),
        ('STAFF', '사원'),
        ('SENIOR', '대리'),
        ('MANAGER', '과장'),
        ('DIRECTOR', '부장'),
        ('EXECUTIVE', '임원'),
    ]
    
    # 회사 선택지 (엑셀 데이터 기준)
    COMPANY_CHOICES = [
        ('OK', 'OK'),
        ('OCI', 'OCI'),
        ('OC', 'OC'),
        ('OFI', 'OFI'),
        ('OKDS', 'OKDS'),
        ('OKH', 'OKH'),
        ('ON', 'ON'),
        ('OKIP', 'OKIP'),
        ('OT', 'OT'),
        ('OKV', 'OKV'),
        ('EX', 'EX'),
    ]
    
    # 성별 선택지
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
    ]
    
    # 결혼여부 선택지
    MARITAL_STATUS_CHOICES = [
        ('Y', '기혼'),
        ('N', '미혼'),
        ('D', '이혼'),
        ('W', '사별'),
    ]
    
    # === User 연결 필드 추가 ===
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='employee',
        verbose_name='사용자 계정'
    )
    
    # === 기존 필드들은 그대로 유지 ===
    name = models.CharField(max_length=100, verbose_name='이름')
    email = models.EmailField(unique=True, verbose_name='이메일')
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, verbose_name='부서')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name='직급')
    hire_date = models.DateField(verbose_name='입사일', default=date.today)
    phone = models.CharField(max_length=15, verbose_name='전화번호')
    
    # === 프로필 수정용 추가 필드들 ===
    address = models.TextField(blank=True, verbose_name='주소')
    emergency_contact = models.CharField(max_length=50, blank=True, verbose_name='비상연락처(이름)')
    emergency_phone = models.CharField(max_length=15, blank=True, verbose_name='비상연락처(번호)')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name='프로필 사진')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    # === 엑셀 데이터 기반 확장 필드들 ===
    
    # 기본 정보 (익명화 필드들)
    # dummy_ssn = models.CharField(max_length=20, blank=True, null=True, verbose_name='주민번호(익명화)')  # Railway PostgreSQL 오류로 임시 제거
    dummy_chinese_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='한자명(익명화)')
    dummy_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='이름(익명화)')
    dummy_mobile = models.CharField(max_length=20, blank=True, null=True, verbose_name='휴대폰(익명화)')
    dummy_registered_address = models.TextField(blank=True, null=True, verbose_name='주민등록주소(익명화)')
    dummy_residence_address = models.TextField(blank=True, null=True, verbose_name='실거주지주소(익명화)')
    dummy_email = models.EmailField(blank=True, null=True, verbose_name='이메일(익명화)')
    
    # 일련번호 및 회사 정보
    no = models.IntegerField(blank=True, null=True, verbose_name='NO')
    company = models.CharField(max_length=10, choices=COMPANY_CHOICES, blank=True, null=True, verbose_name='회사')
    
    # 직급 정보
    previous_position = models.CharField(max_length=50, blank=True, null=True, verbose_name='직급(전)')
    current_position = models.CharField(max_length=50, blank=True, null=True, verbose_name='직급')
    
    # 조직 구조
    headquarters1 = models.CharField(max_length=100, blank=True, null=True, verbose_name='본부1')
    headquarters2 = models.CharField(max_length=100, blank=True, null=True, verbose_name='본부2')
    department1 = models.CharField(max_length=100, blank=True, null=True, verbose_name='소속1')
    department2 = models.CharField(max_length=100, blank=True, null=True, verbose_name='소속2')
    department3 = models.CharField(max_length=100, blank=True, null=True, verbose_name='소속3')
    department4 = models.CharField(max_length=100, blank=True, null=True, verbose_name='소속4')
    final_department = models.CharField(max_length=100, blank=True, null=True, verbose_name='최종소속')
    
    # 직군/계열 및 인사 정보
    job_series = models.CharField(max_length=50, blank=True, null=True, verbose_name='직군/계열')
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='호칭')
    responsibility = models.CharField(max_length=50, blank=True, null=True, verbose_name='직책')
    promotion_level = models.CharField(max_length=20, blank=True, null=True, verbose_name='승급레벨')
    salary_grade = models.CharField(max_length=20, blank=True, null=True, verbose_name='급호')
    
    # 개인 정보
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='성별')
    age = models.IntegerField(blank=True, null=True, verbose_name='나이')
    birth_date = models.DateField(blank=True, null=True, verbose_name='생일')
    
    # 입사 관련 날짜들
    group_join_date = models.DateField(blank=True, null=True, verbose_name='그룹입사일')
    career_join_date = models.DateField(blank=True, null=True, verbose_name='경력입사일')
    new_join_date = models.DateField(blank=True, null=True, verbose_name='신입입사일')
    
    # 근무 년수 및 평가
    promotion_accumulated_years = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='승급누적년수')
    final_evaluation = models.CharField(max_length=10, blank=True, null=True, verbose_name='최종평가')
    
    # 태그 정보
    job_tag_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='직무태그명')
    rank_tag_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='순위태그명')
    
    # 추가 정보
    education = models.CharField(max_length=50, blank=True, null=True, verbose_name='학력')
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES, blank=True, null=True, verbose_name='결혼여부')
    job_family = models.CharField(max_length=50, blank=True, null=True, verbose_name='직무군')
    job_field = models.CharField(max_length=50, blank=True, null=True, verbose_name='직무분야')
    classification = models.CharField(max_length=50, blank=True, null=True, verbose_name='분류')
    current_headcount = models.CharField(max_length=10, blank=True, null=True, verbose_name='현원')
    detailed_classification = models.CharField(max_length=100, blank=True, null=True, verbose_name='세부분류')
    category = models.CharField(max_length=50, blank=True, null=True, verbose_name='구분')
    diversity_years = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='다양성년수')
    
    # === 기존 OK금융그룹 신인사제도 필드들 유지 ===
    
    # 직군 분류 (PL/Non-PL)
    job_group = models.CharField(
        max_length=20, 
        choices=[
            ('PL', 'PL직군'),
            ('Non-PL', 'Non-PL직군'),
        ], 
        default='Non-PL',
        help_text="PL직군(고객지원) 또는 Non-PL직군"
    )
    
    # 직종 분류
    job_type = models.CharField(
        max_length=50, 
        choices=[
            # PL직군
            ('고객지원', '고객지원'),
            
            # Non-PL직군  
            ('IT기획', 'IT기획'),
            ('IT개발', 'IT개발'),
            ('IT운영', 'IT운영'),
            ('경영관리', '경영관리'),
            ('기업영업', '기업영업'),
            ('기업금융', '기업금융'),
            ('리테일금융', '리테일금융'),
            ('투자금융', '투자금융'),
        ], 
        default='경영관리',
        help_text="세부 직종 분류"
    )
    
    # 구체적 직무 (자유 입력)
    job_role = models.CharField(
        max_length=100, 
        blank=True,
        help_text="구체적인 직무 (예: 수신고객지원, 시스템기획, HRM 등)"
    )
    
    # 성장레벨 (기존 직급 대체)
    growth_level = models.IntegerField(
        default=1,
        choices=[
            (1, 'Level 1'),
            (2, 'Level 2'),
            (3, 'Level 3'),
            (4, 'Level 4'),
            (5, 'Level 5'),
            (6, 'Level 6'),
        ],
        help_text="성장레벨 1-6단계"
    )
    
    # 직책 (성장레벨과 분리 운영)
    new_position = models.CharField(
        max_length=50, 
        choices=[
            ('사원', '사원'),
            ('선임', '선임'),
            ('주임', '주임'),
            ('대리', '대리'),
            ('과장', '과장'),
            ('차장', '차장'),
            ('부부장', '부부장'),
            ('부장', '부장'),
            ('팀장', '팀장'),
            ('지점장', '지점장'),
            ('본부장', '본부장'),
        ], 
        default='사원',
        help_text="조직 내 직책"
    )
    
    # 직속 상사 (평가권자)
    manager = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='subordinates',
        help_text="직속 상사 (평가권자)"
    )
    
    # 소속 조직 (조직 구조 마스터와 연결)
    organization = models.ForeignKey(
        'OrganizationStructure',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='소속조직',
        help_text="조직 구조 마스터의 소속 조직"
    )
    
    # 급호 (호봉)
    grade_level = models.IntegerField(
        default=1,
        help_text="급호 (호봉)"
    )
    
    # 입사구분
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('정규직', '정규직'),
            ('계약직', '계약직'),
            ('파견', '파견'),
            ('인턴', '인턴'),
        ],
        default='정규직'
    )
    
    # 재직상태
    employment_status = models.CharField(
        max_length=20,
        choices=[
            ('재직', '재직'),
            ('휴직', '휴직'),
            ('퇴직', '퇴직'),
            ('파견', '파견'),
        ],
        default='재직'
    )
    
    def __str__(self):
        # 엑셀 데이터 기반 표시 우선, 없으면 기존 방식
        if self.company and self.current_position:
            return f"{self.name} ({self.company}/{self.current_position})"
        return f"{self.name} ({self.job_type}/{self.new_position}/Lv.{self.growth_level})"
    
    def get_full_position(self):
        """전체 직책 정보 반환"""
        if self.company and self.final_department:
            return f"{self.company} > {self.final_department} > {self.current_position or self.new_position}"
        return f"{self.job_group} > {self.job_type} > {self.new_position} (Level {self.growth_level})"
    
    def get_organization_path(self):
        """조직 경로 반환"""
        path_parts = []
        if self.company:
            path_parts.append(self.company)
        if self.headquarters1:
            path_parts.append(self.headquarters1)
        if self.headquarters2:
            path_parts.append(self.headquarters2)
        if self.final_department:
            path_parts.append(self.final_department)
        return ' > '.join(path_parts) if path_parts else '미정'
    
    def get_subordinates(self):
        """부하직원 목록 반환"""
        return self.subordinates.filter(employment_status='재직')
    
    def is_manager(self):
        """관리자 여부 확인"""
        return self.subordinates.exists()
    
    def get_service_years(self):
        """근속 년수 계산"""
        if self.hire_date:
            from datetime import date
            today = date.today()
            return (today - self.hire_date).days // 365
        return None
    
    def get_primary_hire_date(self):
        """주요 입사일 반환 (우선순위: 그룹입사일 > 입사일)"""
        return self.group_join_date or self.hire_date
    
    class Meta:
        db_table = 'employees_employee'  # 기존 테이블명 유지
        ordering = ['company', 'headquarters1', 'final_department', 'current_position', 'name']
        verbose_name = '직원'
        verbose_name_plural = '직원관리'
        indexes = [
            models.Index(fields=['company', 'final_department']),
            models.Index(fields=['current_position', 'promotion_level']),
            models.Index(fields=['employment_status']),
            models.Index(fields=['no']),
        ]
