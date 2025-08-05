from django.contrib import admin
from .models import (
    JobPosting, Applicant, Application, 
    InterviewSchedule, RecruitmentStage, ApplicationHistory
)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'position', 'employment_type', 'status', 'closing_date', 'created_at']
    list_filter = ['status', 'employment_type', 'department', 'created_at']
    search_fields = ['title', 'description', 'requirements']
    date_hierarchy = 'created_at'
    readonly_fields = ['id', 'created_at', 'updated_at', 'posted_date']
    
    fieldsets = [
        ('기본 정보', {
            'fields': ['title', 'position', 'department', 'employment_type', 'status']
        }),
        ('채용 상세', {
            'fields': ['description', 'requirements', 'preferred_qualifications']
        }),
        ('자격 요건', {
            'fields': ['min_experience_years', 'max_experience_years']
        }),
        ('채용 조건', {
            'fields': ['vacancies', 'location', 'salary_range_min', 'salary_range_max']
        }),
        ('일정', {
            'fields': ['posted_date', 'closing_date']
        }),
        ('시스템 정보', {
            'fields': ['id', 'created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    date_hierarchy = 'created_at'
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = [
        ('기본 정보', {
            'fields': ['first_name', 'last_name', 'email', 'phone']
        }),
        ('추가 정보', {
            'fields': ['gender', 'birth_date', 'address']
        }),
        ('프로필 링크', {
            'fields': ['linkedin_url', 'portfolio_url']
        }),
        ('지원 서류', {
            'fields': ['resume_file', 'cover_letter']
        }),
        ('시스템 정보', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(RecruitmentStage)
class RecruitmentStageAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'is_active']
    list_filter = ['is_active']
    ordering = ['order']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job_posting', 'current_stage', 'status', 'applied_date', 'assigned_to']
    list_filter = ['status', 'current_stage', 'applied_date', 'job_posting__department']
    search_fields = ['applicant__first_name', 'applicant__last_name', 'applicant__email', 'job_posting__title']
    date_hierarchy = 'applied_date'
    readonly_fields = ['id', 'applied_date', 'created_at', 'updated_at']
    raw_id_fields = ['applicant', 'job_posting']
    
    fieldsets = [
        ('지원 정보', {
            'fields': ['job_posting', 'applicant', 'applied_date']
        }),
        ('진행 상태', {
            'fields': ['current_stage', 'status', 'assigned_to']
        }),
        ('평가', {
            'fields': ['technical_score', 'cultural_fit_score', 'overall_rating']
        }),
        ('메모', {
            'fields': ['notes', 'rejection_reason']
        }),
        ('시스템 정보', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ['application', 'interview_type', 'scheduled_date', 'status', 'created_by']
    list_filter = ['status', 'interview_type', 'scheduled_date']
    search_fields = ['application__applicant__first_name', 'application__applicant__last_name', 'location']
    date_hierarchy = 'scheduled_date'
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['application']
    filter_horizontal = ['interviewers']
    
    fieldsets = [
        ('면접 정보', {
            'fields': ['application', 'interview_type', 'status']
        }),
        ('일정', {
            'fields': ['scheduled_date', 'duration_minutes', 'location', 'meeting_link']
        }),
        ('면접관', {
            'fields': ['interviewers']
        }),
        ('평가', {
            'fields': ['interview_notes', 'technical_assessment', 'cultural_assessment', 'recommendation']
        }),
        ('시스템 정보', {
            'fields': ['id', 'created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(ApplicationHistory)
class ApplicationHistoryAdmin(admin.ModelAdmin):
    list_display = ['application', 'stage', 'status', 'changed_by', 'changed_at']
    list_filter = ['status', 'changed_at']
    search_fields = ['application__applicant__first_name', 'application__applicant__last_name', 'notes']
    date_hierarchy = 'changed_at'
    readonly_fields = ['changed_at']
    raw_id_fields = ['application']
