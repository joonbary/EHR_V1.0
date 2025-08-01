"""
주간 인력현황 관리 모델
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class WeeklyWorkforceSnapshot(models.Model):
    """주간 인력현황 스냅샷"""
    
    # 기준일자
    snapshot_date = models.DateField(verbose_name='기준일자')
    
    # 인력 정보
    company = models.CharField(max_length=100, verbose_name='계열사명')
    job_group = models.CharField(
        max_length=50, 
        verbose_name='직군',
        help_text='PL / Non-PL'
    )
    grade = models.CharField(
        max_length=50, 
        verbose_name='직급',
        help_text='대리 / 과장 / 차장 / 부장 등'
    )
    position = models.CharField(
        max_length=50, 
        blank=True,
        null=True,
        verbose_name='직책',
        help_text='팀장 / 매니저 등'
    )
    contract_type = models.CharField(
        max_length=50,
        verbose_name='신분',
        help_text='별정직, 전문계약직, 인턴/계약직, 외주인력 등'
    )
    
    # 인원수
    headcount = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='인원수'
    )
    
    # 메타 정보
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드일시')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='업로드자'
    )
    
    class Meta:
        db_table = 'weekly_workforce_snapshot'
        verbose_name = '주간 인력현황 스냅샷'
        verbose_name_plural = '주간 인력현황 스냅샷들'
        unique_together = ['snapshot_date', 'company', 'job_group', 'grade', 'position', 'contract_type']
        indexes = [
            models.Index(fields=['snapshot_date']),
            models.Index(fields=['company']),
            models.Index(fields=['job_group']),
            models.Index(fields=['contract_type']),
        ]
    
    def __str__(self):
        return f'{self.snapshot_date} - {self.company} {self.job_group} {self.grade}'


class WeeklyJoinLeave(models.Model):
    """주간 입/퇴사자 정보"""
    
    TYPE_CHOICES = [
        ('join', '입사'),
        ('leave', '퇴사'),
        ('leave_planned', '퇴사예정'),
    ]
    
    # 구분
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='구분'
    )
    
    # 인적사항
    name = models.CharField(max_length=50, verbose_name='성명')
    company = models.CharField(max_length=100, verbose_name='계열사명')
    org_unit = models.CharField(max_length=100, verbose_name='소속부서')
    grade = models.CharField(max_length=50, verbose_name='직급')
    position = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='직책'
    )
    job_group = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='직군'
    )
    
    # 일자 및 사유
    date = models.DateField(verbose_name='일자')
    reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='사유',
        help_text='퇴사 사유 등'
    )
    
    # 메타 정보
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드일시')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='업로드자'
    )
    
    class Meta:
        db_table = 'weekly_join_leave'
        verbose_name = '주간 입/퇴사자'
        verbose_name_plural = '주간 입/퇴사자들'
        indexes = [
            models.Index(fields=['type', 'date']),
            models.Index(fields=['company']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f'{self.get_type_display()} - {self.name} ({self.date})'


class WeeklyWorkforceChange(models.Model):
    """주간 인력 증감 분석 (캐시)"""
    
    BASE_TYPE_CHOICES = [
        ('week', '전주 대비'),
        ('month', '전월 대비'),
        ('year_end', '전년말 대비'),
    ]
    
    # 기준 정보
    current_date = models.DateField(verbose_name='현재 기준일')
    base_date = models.DateField(verbose_name='비교 기준일')
    base_type = models.CharField(
        max_length=20,
        choices=BASE_TYPE_CHOICES,
        verbose_name='비교 기준'
    )
    
    # 그룹 정보
    company = models.CharField(max_length=100, verbose_name='계열사명')
    job_group = models.CharField(max_length=50, verbose_name='직군')
    grade = models.CharField(max_length=50, verbose_name='직급')
    position = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='직책'
    )
    contract_type = models.CharField(max_length=50, verbose_name='신분')
    
    # 인원 및 증감
    current_headcount = models.IntegerField(verbose_name='현재 인원')
    base_headcount = models.IntegerField(verbose_name='기준 인원')
    change_count = models.IntegerField(verbose_name='증감 인원')
    change_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='증감율(%)'
    )
    
    # 메타 정보
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name='계산일시')
    
    class Meta:
        db_table = 'weekly_workforce_change'
        verbose_name = '주간 인력 증감'
        verbose_name_plural = '주간 인력 증감들'
        unique_together = ['current_date', 'base_date', 'company', 'job_group', 'grade', 'position', 'contract_type']
        indexes = [
            models.Index(fields=['current_date', 'base_type']),
            models.Index(fields=['company']),
        ]
    
    def __str__(self):
        return f'{self.current_date} {self.get_base_type_display()}: {self.change_count:+d}명'
    
    def save(self, *args, **kwargs):
        """증감 및 증감율 자동 계산"""
        self.change_count = self.current_headcount - self.base_headcount
        if self.base_headcount > 0:
            self.change_rate = (self.change_count / self.base_headcount) * 100
        else:
            self.change_rate = 100 if self.current_headcount > 0 else 0
        super().save(*args, **kwargs)