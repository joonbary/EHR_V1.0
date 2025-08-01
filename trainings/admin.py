"""
교육 관련 Django Admin 설정
"""

from django.contrib import admin
from .models import (
    TrainingCategory, TrainingCourse, TrainingEnrollment,
    TrainingRecommendation, SkillTrainingMapping
)


@admin.register(TrainingCategory)
class TrainingCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = [
        'course_code', 'title', 'category', 'skill_level',
        'duration_hours', 'course_type', 'cost', 'is_active'
    ]
    list_filter = [
        'category', 'skill_level', 'course_type',
        'is_mandatory', 'certification_eligible', 'is_active'
    ]
    search_fields = ['course_code', 'title', 'description', 'provider']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('course_code', 'title', 'category', 'description')
        }),
        ('교육 내용', {
            'fields': ('objectives', 'target_audience', 'related_skills', 'skill_level')
        }),
        ('교육 정보', {
            'fields': ('duration_hours', 'course_type', 'provider', 'cost')
        }),
        ('성장레벨 연계', {
            'fields': ('min_growth_level', 'certification_eligible', 'growth_level_impact')
        }),
        ('설정', {
            'fields': ('is_mandatory', 'is_active')
        }),
        ('시스템 정보', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(TrainingEnrollment)
class TrainingEnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'course', 'status', 'enrolled_date',
        'start_date', 'completion_date', 'attendance_rate'
    ]
    list_filter = ['status', 'enrolled_date', 'start_date']
    search_fields = ['employee__name', 'course__title']
    readonly_fields = ['id', 'enrolled_date']
    date_hierarchy = 'enrolled_date'
    
    fieldsets = (
        ('수강 정보', {
            'fields': ('employee', 'course', 'status')
        }),
        ('일정', {
            'fields': (
                'enrolled_date', 'approved_date',
                'start_date', 'end_date', 'completion_date'
            )
        }),
        ('평가 정보', {
            'fields': ('attendance_rate', 'test_score', 'satisfaction_score')
        }),
        ('추천 정보', {
            'fields': ('recommendation_reason', 'recommendation_priority')
        }),
        ('기타', {
            'fields': ('notes',)
        })
    )


@admin.register(TrainingRecommendation)
class TrainingRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'course', 'target_job', 'match_score',
        'priority', 'recommendation_type', 'is_enrolled', 'created_at'
    ]
    list_filter = ['recommendation_type', 'is_enrolled', 'created_at']
    search_fields = ['employee__name', 'course__title', 'target_job']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(SkillTrainingMapping)
class SkillTrainingMappingAdmin(admin.ModelAdmin):
    list_display = ['skill_name', 'skill_category', 'relevance_score', 'is_core_skill']
    list_filter = ['skill_category', 'is_core_skill']
    search_fields = ['skill_name']
    filter_horizontal = ['courses']