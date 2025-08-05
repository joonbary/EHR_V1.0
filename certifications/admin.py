"""
성장레벨 인증 Django Admin 설정
"""

from django.contrib import admin
from .models import (
    GrowthLevelRequirement, JobLevelRequirement,
    GrowthLevelCertification, CertificationCheckLog
)


@admin.register(GrowthLevelRequirement)
class GrowthLevelRequirementAdmin(admin.ModelAdmin):
    list_display = [
        'level', 'level_name', 'min_evaluation_grade',
        'consecutive_evaluations', 'min_training_hours',
        'min_years_in_level', 'is_active'
    ]
    list_filter = ['level', 'is_active']
    search_fields = ['level', 'level_name']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('level', 'level_name', 'description')
        }),
        ('평가 요건', {
            'fields': ('min_evaluation_grade', 'consecutive_evaluations')
        }),
        ('교육 요건', {
            'fields': (
                'required_courses', 'required_course_categories',
                'min_training_hours'
            )
        }),
        ('스킬 요건', {
            'fields': ('required_skills', 'skill_proficiency_level')
        }),
        ('경력 요건', {
            'fields': ('min_years_in_level', 'min_total_years')
        }),
        ('추가 설정', {
            'fields': ('additional_requirements', 'is_active')
        })
    )


@admin.register(JobLevelRequirement)
class JobLevelRequirementAdmin(admin.ModelAdmin):
    list_display = [
        'job_profile', 'required_growth_level',
        'override_eval_grade', 'is_active'
    ]
    list_filter = ['required_growth_level', 'is_active']
    search_fields = ['job_profile__job_role__name']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('job_profile', 'required_growth_level')
        }),
        ('직무별 추가 요건', {
            'fields': (
                'job_specific_courses', 'job_specific_skills',
                'override_eval_grade'
            )
        }),
        ('설정', {
            'fields': ('is_active',)
        })
    )


@admin.register(GrowthLevelCertification)
class GrowthLevelCertificationAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'growth_level', 'status',
        'applied_date', 'certified_date'
    ]
    list_filter = ['status', 'growth_level', 'applied_date']
    search_fields = ['employee__name', 'growth_level']
    readonly_fields = [
        'id', 'applied_date', 'certification_snapshot'
    ]
    date_hierarchy = 'applied_date'
    
    fieldsets = (
        ('신청 정보', {
            'fields': ('employee', 'growth_level', 'status')
        }),
        ('일자', {
            'fields': ('applied_date', 'certified_date', 'expiry_date')
        }),
        ('체크 결과', {
            'fields': (
                'evaluation_check', 'training_check',
                'skill_check', 'experience_check'
            )
        }),
        ('상세 정보', {
            'fields': (
                'missing_requirements', 'certification_snapshot'
            ),
            'classes': ('collapse',)
        }),
        ('검토', {
            'fields': ('reviewed_by', 'review_notes')
        })
    )


@admin.register(CertificationCheckLog)
class CertificationCheckLogAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'target_level', 'target_job',
        'check_result', 'checked_at'
    ]
    list_filter = ['check_result', 'checked_at', 'target_level']
    search_fields = ['employee__name', 'target_job']
    readonly_fields = ['id', 'checked_at', 'result_details']
    date_hierarchy = 'checked_at'