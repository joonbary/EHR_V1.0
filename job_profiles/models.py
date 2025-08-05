from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class JobCategory(models.Model):
    """직군 (Job Category)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, verbose_name='직군명')
    code = models.CharField(max_length=10, unique=True, verbose_name='직군코드')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '직군'
        verbose_name_plural = '직군'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class JobType(models.Model):
    """직종 (Job Type)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='job_types', verbose_name='직군')
    name = models.CharField(max_length=50, verbose_name='직종명')
    code = models.CharField(max_length=10, unique=True, verbose_name='직종코드')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '직종'
        verbose_name_plural = '직종'
        ordering = ['category', 'code']
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.category.name} > {self.name}"


class JobRole(models.Model):
    """직무 (Job Role)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_type = models.ForeignKey(JobType, on_delete=models.CASCADE, related_name='job_roles', verbose_name='직종')
    name = models.CharField(max_length=100, verbose_name='직무명')
    code = models.CharField(max_length=20, unique=True, verbose_name='직무코드')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '직무'
        verbose_name_plural = '직무'
        ordering = ['job_type', 'code']
        unique_together = ['job_type', 'name']
    
    def __str__(self):
        return f"{self.job_type.category.name} > {self.job_type.name} > {self.name}"
    
    @property
    def full_path(self):
        """직군 > 직종 > 직무 전체 경로"""
        return f"{self.job_type.category.name} > {self.job_type.name} > {self.name}"


class JobProfile(models.Model):
    """직무기술서 (Job Profile)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_role = models.OneToOneField(JobRole, on_delete=models.CASCADE, related_name='profile', verbose_name='직무')
    
    # 핵심 정보
    role_responsibility = models.TextField(verbose_name='역할과 책임')
    qualification = models.TextField(verbose_name='자격요건')
    
    # JSON 필드로 저장되는 스킬 정보
    basic_skills = models.JSONField(default=list, verbose_name='기본 기술/지식')
    applied_skills = models.JSONField(default=list, verbose_name='응용 기술/지식')
    
    # 추가 정보
    growth_path = models.TextField(blank=True, verbose_name='성장경로')
    related_certifications = models.JSONField(default=list, verbose_name='관련 자격증')
    
    # 메타 정보
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_profiles')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    
    class Meta:
        verbose_name = '직무기술서'
        verbose_name_plural = '직무기술서'
        ordering = ['job_role__job_type__category', 'job_role__job_type', 'job_role']
    
    def __str__(self):
        return f"직무기술서: {self.job_role.name}"
    
    def get_all_skills(self):
        """모든 스킬을 하나의 리스트로 반환"""
        return self.basic_skills + self.applied_skills
    
    def get_skill_count(self):
        """총 스킬 개수"""
        return len(self.basic_skills) + len(self.applied_skills)


class JobProfileHistory(models.Model):
    """직무기술서 변경 이력"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_profile = models.ForeignKey(JobProfile, on_delete=models.CASCADE, related_name='histories')
    
    # 변경 전 데이터를 JSON으로 저장
    previous_data = models.JSONField()
    
    # 변경 정보
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    change_reason = models.TextField(blank=True, verbose_name='변경 사유')
    
    class Meta:
        verbose_name = '직무기술서 변경이력'
        verbose_name_plural = '직무기술서 변경이력'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.job_profile.job_role.name} - {self.changed_at.strftime('%Y-%m-%d %H:%M')}"