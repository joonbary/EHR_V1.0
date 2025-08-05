from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from job_profiles.models import JobRole
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class JobPosting(models.Model):
    """채용공고 모델"""
    STATUS_CHOICES = [
        ('draft', '초안'),
        ('open', '진행중'),
        ('closed', '마감'),
        ('cancelled', '취소')
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('permanent', '정규직'),
        ('contract', '계약직'),
        ('intern', '인턴'),
        ('parttime', '파트타임')
    ]
    
    # 부서 선택지 (Employee 모델과 동일)
    DEPARTMENT_CHOICES = [
        ('IT', 'IT'),
        ('HR', '인사'),
        ('FINANCE', '재무'),
        ('MARKETING', '마케팅'),
        ('SALES', '영업'),
        ('OPERATIONS', '운영'),
    ]
    
    # 직급 선택지 (Employee 모델과 동일)
    POSITION_CHOICES = [
        ('INTERN', '인턴'),
        ('STAFF', '사원'),
        ('SENIOR', '대리'),
        ('MANAGER', '과장'),
        ('DIRECTOR', '부장'),
        ('EXECUTIVE', '임원'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('공고 제목', max_length=200)
    position = models.CharField('채용 직급', max_length=20, choices=POSITION_CHOICES)
    department = models.CharField('채용 부서', max_length=20, choices=DEPARTMENT_CHOICES)
    employment_type = models.CharField('고용 형태', max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='직무')
    
    description = models.TextField('직무 설명')
    requirements = models.TextField('자격 요건')
    preferred_qualifications = models.TextField('우대 사항', blank=True)
    
    min_experience_years = models.IntegerField('최소 경력 연수', default=0, validators=[MinValueValidator(0)])
    max_experience_years = models.IntegerField('최대 경력 연수', null=True, blank=True, validators=[MinValueValidator(0)])
    
    vacancies = models.IntegerField('채용 인원', default=1, validators=[MinValueValidator(1)])
    location = models.CharField('근무 지역', max_length=100)
    salary_range_min = models.DecimalField('최소 급여', max_digits=10, decimal_places=0, null=True, blank=True)
    salary_range_max = models.DecimalField('최대 급여', max_digits=10, decimal_places=0, null=True, blank=True)
    
    posted_date = models.DateTimeField('공고 게시일', null=True, blank=True)
    closing_date = models.DateTimeField('마감일')
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings', verbose_name='작성자', null=True, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '채용공고'
        verbose_name_plural = '채용공고'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_department_display()}"
    
    def save(self, *args, **kwargs):
        if self.status == 'open' and not self.posted_date:
            self.posted_date = timezone.now()
        super().save(*args, **kwargs)


class Applicant(models.Model):
    """지원자 모델"""
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField('이름', max_length=50)
    last_name = models.CharField('성', max_length=50)
    email = models.EmailField('이메일', unique=True)
    phone = models.CharField('전화번호', max_length=20)
    
    gender = models.CharField('성별', max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    birth_date = models.DateField('생년월일', null=True, blank=True)
    
    address = models.TextField('주소', blank=True)
    linkedin_url = models.URLField('LinkedIn URL', blank=True)
    portfolio_url = models.URLField('포트폴리오 URL', blank=True)
    
    resume_file = models.FileField('이력서 파일', upload_to='resumes/%Y/%m/', null=True, blank=True)
    cover_letter = models.TextField('자기소개서', blank=True)
    
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '지원자'
        verbose_name_plural = '지원자'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.last_name}{self.first_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.last_name}{self.first_name}"


class RecruitmentStage(models.Model):
    """채용 단계 모델"""
    name = models.CharField('단계명', max_length=50)
    order = models.IntegerField('순서', default=0)
    description = models.TextField('설명', blank=True)
    is_active = models.BooleanField('활성화', default=True)
    
    class Meta:
        verbose_name = '채용 단계'
        verbose_name_plural = '채용 단계'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.order}. {self.name}"


class Application(models.Model):
    """지원서 모델"""
    STATUS_CHOICES = [
        ('submitted', '접수'),
        ('reviewing', '검토중'),
        ('interview_scheduled', '면접예정'),
        ('interviewed', '면접완료'),
        ('offer_made', '합격'),
        ('rejected', '불합격'),
        ('withdrawn', '지원취소')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications', verbose_name='채용공고')
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='applications', verbose_name='지원자')
    
    current_stage = models.ForeignKey(RecruitmentStage, on_delete=models.SET_NULL, null=True, verbose_name='현재 단계')
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    applied_date = models.DateTimeField('지원일', auto_now_add=True)
    
    # 평가 관련 필드
    technical_score = models.IntegerField('기술 점수', null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    cultural_fit_score = models.IntegerField('조직 적합도', null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    overall_rating = models.IntegerField('종합 평가', null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    notes = models.TextField('메모', blank=True)
    rejection_reason = models.TextField('불합격 사유', blank=True)
    
    # 담당자
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_applications', verbose_name='담당자')
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '지원서'
        verbose_name_plural = '지원서'
        ordering = ['-applied_date']
        unique_together = ['job_posting', 'applicant']
    
    def __str__(self):
        return f"{self.applicant.full_name} - {self.job_posting.title}"


class InterviewSchedule(models.Model):
    """면접 일정 모델"""
    INTERVIEW_TYPE_CHOICES = [
        ('phone', '전화 면접'),
        ('video', '화상 면접'),
        ('onsite', '대면 면접'),
        ('technical', '기술 면접'),
        ('hr', '인사 면접'),
        ('final', '최종 면접')
    ]
    
    STATUS_CHOICES = [
        ('scheduled', '예정'),
        ('completed', '완료'),
        ('cancelled', '취소'),
        ('rescheduled', '일정변경')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews', verbose_name='지원서')
    interview_type = models.CharField('면접 유형', max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    
    scheduled_date = models.DateTimeField('면접 일시')
    duration_minutes = models.IntegerField('소요 시간(분)', default=60)
    location = models.CharField('장소', max_length=200, blank=True)
    meeting_link = models.URLField('미팅 링크', blank=True)
    
    # 면접관
    interviewers = models.ManyToManyField(Employee, related_name='interviews_conducted', verbose_name='면접관')
    
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # 평가
    interview_notes = models.TextField('면접 내용', blank=True)
    technical_assessment = models.TextField('기술 평가', blank=True)
    cultural_assessment = models.TextField('인성 평가', blank=True)
    recommendation = models.CharField('추천 여부', max_length=20, blank=True, choices=[
        ('strong_yes', '적극 추천'),
        ('yes', '추천'),
        ('neutral', '보통'),
        ('no', '비추천'),
        ('strong_no', '적극 비추천')
    ])
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_interviews', verbose_name='일정 생성자', null=True, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '면접 일정'
        verbose_name_plural = '면접 일정'
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.application.applicant.full_name} - {self.get_interview_type_display()} ({self.scheduled_date.strftime('%Y-%m-%d %H:%M')})"


class ApplicationHistory(models.Model):
    """지원서 이력 모델"""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history', verbose_name='지원서')
    stage = models.ForeignKey(RecruitmentStage, on_delete=models.SET_NULL, null=True, verbose_name='단계')
    status = models.CharField('상태', max_length=20)
    notes = models.TextField('메모', blank=True)
    
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='변경자', null=True, blank=True)
    changed_at = models.DateTimeField('변경일시', auto_now_add=True)
    
    class Meta:
        verbose_name = '지원서 이력'
        verbose_name_plural = '지원서 이력'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.application} - {self.status} ({self.changed_at})"
