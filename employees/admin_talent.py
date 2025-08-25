"""
인재 관리 Admin 설정
"""

from django.contrib import admin
from django.utils.html import format_html
from .models_talent import (
    TalentCategory, TalentPool, PromotionCandidate, 
    RetentionRisk, TalentDevelopment
)


@admin.register(TalentCategory)
class TalentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_code', 'is_active', 'created_at']
    list_filter = ['category_code', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TalentPool)
class TalentPoolAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'category_display', 'ai_score_display', 
                    'confidence_display', 'status_badge', 'is_valid_display']
    list_filter = ['category', 'status', 'added_at']
    search_fields = ['employee__name', 'employee__email', 'notes']
    readonly_fields = ['added_at', 'updated_at', 'added_by', 'updated_by']
    autocomplete_fields = ['employee', 'ai_analysis_result']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('employee', 'category', 'status')
        }),
        ('AI 분석 결과', {
            'fields': ('ai_analysis_result', 'ai_score', 'confidence_level')
        }),
        ('평가 상세', {
            'fields': ('strengths', 'development_areas', 'recommendations', 'notes')
        }),
        ('유효성', {
            'fields': ('review_date', 'valid_until')
        }),
        ('메타데이터', {
            'fields': ('added_by', 'added_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = '직원명'
    employee_name.admin_order_field = 'employee__name'
    
    def category_display(self, obj):
        return obj.category.get_category_code_display()
    category_display.short_description = '카테고리'
    
    def ai_score_display(self, obj):
        color = 'green' if obj.ai_score >= 80 else 'orange' if obj.ai_score >= 60 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}</span>',
            color, obj.ai_score
        )
    ai_score_display.short_description = 'AI 점수'
    
    def confidence_display(self, obj):
        percentage = obj.confidence_level * 100
        return f"{percentage:.1f}%"
    confidence_display.short_description = '신뢰도'
    
    def status_badge(self, obj):
        colors = {
            'ACTIVE': 'green',
            'MONITORING': 'orange',
            'PENDING': 'blue',
            'EXCLUDED': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = '상태'
    
    def is_valid_display(self, obj):
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ 유효</span>')
        return format_html('<span style="color: red;">✗ 만료</span>')
    is_valid_display.short_description = '유효성'


@admin.register(PromotionCandidate)
class PromotionCandidateAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'current_position', 'target_position', 
                    'readiness_badge', 'ai_score_display', 'expected_date']
    list_filter = ['readiness_level', 'is_active', 'target_position']
    search_fields = ['employee__name', 'review_notes']
    date_hierarchy = 'expected_promotion_date'
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('employee', 'talent_pool', 'current_position', 'target_position')
        }),
        ('승진 준비도', {
            'fields': ('readiness_level', 'expected_promotion_date')
        }),
        ('평가 점수', {
            'fields': ('performance_score', 'potential_score', 'ai_recommendation_score')
        }),
        ('개발 계획', {
            'fields': ('development_plan', 'completed_requirements', 'pending_requirements')
        }),
        ('검토', {
            'fields': ('is_active', 'review_notes', 'reviewed_by', 'reviewed_at')
        }),
    )
    
    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = '직원명'
    
    def readiness_badge(self, obj):
        colors = {
            'READY': 'green',
            'NEAR_READY': 'blue',
            'DEVELOPING': 'orange',
            'NOT_READY': 'red'
        }
        color = colors.get(obj.readiness_level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_readiness_level_display()
        )
    readiness_badge.short_description = '준비도'
    
    def ai_score_display(self, obj):
        return format_html(
            '<span style="font-weight: bold;">{:.1f}</span>',
            obj.ai_recommendation_score
        )
    ai_score_display.short_description = 'AI 추천점수'
    
    def expected_date(self, obj):
        if obj.expected_promotion_date:
            return obj.expected_promotion_date.strftime('%Y-%m-%d')
        return '-'
    expected_date.short_description = '예상 승진일'


@admin.register(RetentionRisk)
class RetentionRiskAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'risk_level_badge', 'risk_score_display', 
                    'action_status_badge', 'assigned_to', 'identified_date']
    list_filter = ['risk_level', 'action_status', 'is_retained']
    search_fields = ['employee__name', 'retention_strategy', 'outcome']
    date_hierarchy = 'identified_date'
    
    fieldsets = (
        ('직원 정보', {
            'fields': ('employee', 'talent_pool')
        }),
        ('위험도 평가', {
            'fields': ('risk_level', 'risk_score', 'risk_factors')
        }),
        ('대응 계획', {
            'fields': ('retention_strategy', 'action_items', 'action_status', 'assigned_to')
        }),
        ('결과', {
            'fields': ('intervention_date', 'outcome', 'is_retained')
        }),
    )
    
    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = '직원명'
    
    def risk_level_badge(self, obj):
        colors = {
            'CRITICAL': 'red',
            'HIGH': 'orange',
            'MEDIUM': 'yellow',
            'LOW': 'green'
        }
        color = colors.get(obj.risk_level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_risk_level_display()
        )
    risk_level_badge.short_description = '위험 수준'
    
    def risk_score_display(self, obj):
        color = 'red' if obj.risk_score >= 70 else 'orange' if obj.risk_score >= 40 else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, obj.risk_score
        )
    risk_score_display.short_description = '위험 점수'
    
    def action_status_badge(self, obj):
        colors = {
            'PENDING': 'gray',
            'IN_PROGRESS': 'blue',
            'COMPLETED': 'green',
            'FAILED': 'red'
        }
        color = colors.get(obj.action_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_action_status_display()
        )
    action_status_badge.short_description = '조치 상태'


@admin.register(TalentDevelopment)
class TalentDevelopmentAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'development_goal', 'progress_bar', 
                    'priority_badge', 'start_date', 'end_date', 'is_active']
    list_filter = ['priority', 'is_active', 'start_date']
    search_fields = ['employee__name', 'development_goal', 'current_state', 'target_state']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('employee', 'talent_pool', 'development_goal')
        }),
        ('개발 계획', {
            'fields': ('current_state', 'target_state', 'priority')
        }),
        ('활동', {
            'fields': ('activities', 'timeline', 'resources_needed')
        }),
        ('진행 상황', {
            'fields': ('progress_percentage', 'milestones', 'completed_activities')
        }),
        ('일정', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('메타데이터', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = '직원명'
    
    def progress_bar(self, obj):
        color = 'green' if obj.progress_percentage >= 75 else 'blue' if obj.progress_percentage >= 50 else 'orange' if obj.progress_percentage >= 25 else 'red'
        return format_html(
            '<div style="width: 100px; height: 20px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; height: 100%; background-color: {}; border-radius: 3px; text-align: center; color: white;">{:.0f}%</div>'
            '</div>',
            obj.progress_percentage, color, obj.progress_percentage
        )
    progress_bar.short_description = '진행률'
    
    def priority_badge(self, obj):
        colors = {
            'URGENT': 'red',
            'HIGH': 'orange',
            'MEDIUM': 'blue',
            'LOW': 'gray'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = '우선순위'