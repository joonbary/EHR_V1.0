from django.contrib import admin
from .models import (
    EvaluationPeriod, Task, ContributionEvaluation,
    ExpertiseEvaluation, ImpactEvaluation, ComprehensiveEvaluation
)


@admin.register(EvaluationPeriod)
class EvaluationPeriodAdmin(admin.ModelAdmin):
    list_display = ['year', 'period_type', 'start_date', 'end_date', 'is_active', 'status']
    list_filter = ['year', 'period_type', 'is_active', 'status']
    search_fields = ['year']
    ordering = ['-year', 'period_type']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['employee', 'title', 'weight', 'target_value', 'actual_value', 'achievement_rate', 'status']
    list_filter = ['evaluation_period', 'status', 'contribution_method']
    search_fields = ['employee__name', 'title']
    readonly_fields = ['achievement_rate', 'created_at', 'updated_at']
    
    fieldsets = (
        ('기본정보', {
            'fields': ('employee', 'evaluation_period', 'title', 'description')
        }),
        ('과제설정', {
            'fields': ('weight', 'contribution_method')
        }),
        ('목표/실적', {
            'fields': ('target_value', 'target_unit', 'actual_value', 'achievement_rate', 'status')
        }),
        ('시스템정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContributionEvaluation)
class ContributionEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluation_period', 'total_achievement_rate', 'contribution_score', 'is_achieved']
    list_filter = ['evaluation_period', 'is_achieved']
    search_fields = ['employee__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ExpertiseEvaluation)
class ExpertiseEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluation_period', 'required_level', 'total_score', 'is_achieved']
    list_filter = ['evaluation_period', 'is_achieved', 'required_level']
    search_fields = ['employee__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ImpactEvaluation)
class ImpactEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluation_period', 'total_score', 'is_achieved']
    list_filter = ['evaluation_period', 'is_achieved']
    search_fields = ['employee__name']
    readonly_fields = ['created_at', 'updated_at']


# Inline 클래스들
class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ['title', 'weight', 'target_value', 'actual_value', 'achievement_rate']
    readonly_fields = ['achievement_rate']


class ContributionInline(admin.StackedInline):
    model = ContributionEvaluation
    extra = 0
    max_num = 1


class ExpertiseInline(admin.StackedInline):
    model = ExpertiseEvaluation
    extra = 0
    max_num = 1


class ImpactInline(admin.StackedInline):
    model = ImpactEvaluation
    extra = 0
    max_num = 1


@admin.register(ComprehensiveEvaluation)
class ComprehensiveEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluation_period', 'manager_grade', 'final_grade', 'status', 'achievement_summary']
    list_filter = ['evaluation_period', 'status', 'manager_grade', 'final_grade']
    search_fields = ['employee__name', 'employee__email']
    readonly_fields = ['created_at', 'updated_at', 'achievement_summary']
    
    fieldsets = (
        ('기본정보', {
            'fields': ('employee', 'evaluation_period', 'status')
        }),
        ('평가연결', {
            'fields': ('contribution_evaluation', 'expertise_evaluation', 'impact_evaluation')
        }),
        ('달성여부', {
            'fields': ('contribution_achieved', 'expertise_achieved', 'impact_achieved', 'achievement_summary')
        }),
        ('1차평가', {
            'fields': ('manager', 'manager_grade', 'manager_comments', 'manager_evaluated_date')
        }),
        ('최종평가', {
            'fields': ('final_grade', 'calibration_comments')
        }),
        ('시스템정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def achievement_summary(self, obj):
        """달성 요약"""
        achieved = []
        if obj.contribution_achieved:
            achieved.append('기여도')
        if obj.expertise_achieved:
            achieved.append('전문성')
        if obj.impact_achieved:
            achieved.append('영향력')
        
        count = len(achieved)
        if count == 0:
            return '미달성'
        return f"{', '.join(achieved)} ({count}/3)"
    
    achievement_summary.short_description = '달성 요약'
