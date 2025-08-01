from django.db import models
from django.contrib.auth.models import User
from datetime import date

# HR Dashboard models import
from .models_hr import HREmployee, HRMonthlySnapshot, HRContractor, HRFileUpload

# Weekly Workforce models import
from .models_workforce import WeeklyWorkforceSnapshot, WeeklyJoinLeave, WeeklyWorkforceChange

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
    
    # === 추가할 OK금융그룹 신인사제도 필드들 ===
    
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
        return f"{self.name} ({self.job_type}/{self.new_position}/Lv.{self.growth_level})"
    
    def get_full_position(self):
        """전체 직책 정보 반환"""
        return f"{self.job_group} > {self.job_type} > {self.new_position} (Level {self.growth_level})"
    
    def get_subordinates(self):
        """부하직원 목록 반환"""
        return self.subordinates.filter(employment_status='재직')
    
    def is_manager(self):
        """관리자 여부 확인"""
        return self.subordinates.exists()
    
    class Meta:
        db_table = 'employees_employee'  # 기존 테이블명 유지
        ordering = ['department', 'growth_level', 'name']
        verbose_name = '직원'
        verbose_name_plural = '직원관리'
