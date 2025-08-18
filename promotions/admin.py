from django.contrib import admin
from .models import (
    PromotionRequirement, PromotionRequest, JobTransfer, OrganizationChart
)
from datetime import date


@admin.register(PromotionRequirement)
class PromotionRequirementAdmin(admin.ModelAdmin):
    list_display = ['from_level', 'to_level', 'min_years_required', 
                   'consecutive_a_grades', 'min_performance_score']
    list_filter = ['from_level', 'to_level']
    search_fields = ['from_level', 'to_level']
    ordering = ['from_level', 'to_level']


@admin.register(PromotionRequest)
class PromotionRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'current_level', 'target_level', 'status', 
                   'years_of_service', 'consecutive_a_grades', 'created_at']
    list_filter = ['status', 'current_level', 'target_level', 'created_at']
    search_fields = ['employee__name', 'employee__employee_id']
    readonly_fields = ['years_of_service', 'consecutive_a_grades', 'average_performance_score',
                      'years_requirement_met', 'grades_requirement_met', 'performance_requirement_met']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('employee', 'current_level', 'target_level', 'status')
        }),
        ('평가 결과', {
            'fields': ('evaluation_results', 'years_of_service', 'consecutive_a_grades', 
                      'average_performance_score')
        }),
        ('요건 충족 여부', {
            'fields': ('years_requirement_met', 'grades_requirement_met', 'performance_requirement_met')
        }),
        ('부서장 추천', {
            'fields': ('department_recommendation', 'department_recommender', 
                      'department_recommendation_date', 'department_comments')
        }),
        ('HR위원회 심사', {
            'fields': ('hr_committee_decision', 'hr_committee_date', 'hr_comments')
        }),
        ('최종 결정', {
            'fields': ('final_decision', 'final_decision_date', 'final_decision_by')
        }),
        ('기타', {
            'fields': ('employee_comments', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['calculate_requirements', 'approve_promotion', 'reject_promotion']
    
    def calculate_requirements(self, request, queryset):
        for promotion in queryset:
            promotion.calculate_requirements()
        self.message_user(request, f"{queryset.count()}개 승진 요청의 요건을 계산했습니다.")
    calculate_requirements.short_description = "승진 요건 계산"
    
    def approve_promotion(self, request, queryset):
        for promotion in queryset:
            promotion.status = 'APPROVED'
            promotion.final_decision = 'APPROVED'
            promotion.final_decision_date = date.today()
            promotion.save()
        self.message_user(request, f"{queryset.count()}개 승진 요청을 승인했습니다.")
    approve_promotion.short_description = "승진 승인"
    
    def reject_promotion(self, request, queryset):
        for promotion in queryset:
            promotion.status = 'REJECTED'
            promotion.final_decision = 'REJECTED'
            promotion.final_decision_date = date.today()
            promotion.save()
        self.message_user(request, f"{queryset.count()}개 승진 요청을 반려했습니다.")
    reject_promotion.short_description = "승진 반려"


@admin.register(JobTransfer)
class JobTransferAdmin(admin.ModelAdmin):
    list_display = ['employee', 'from_department', 'to_department', 'transfer_type', 
                   'effective_date', 'status']
    list_filter = ['transfer_type', 'status', 'effective_date']
    search_fields = ['employee__name', 'from_department', 'to_department']
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        ('직원 정보', {
            'fields': ('employee', 'transfer_type')
        }),
        ('이동 정보', {
            'fields': ('from_department', 'to_department', 'from_position', 'to_position')
        }),
        ('일정', {
            'fields': ('effective_date', 'announcement_date')
        }),
        ('승인', {
            'fields': ('status', 'approved_by', 'approval_date')
        }),
        ('사유', {
            'fields': ('reason', 'additional_notes')
        }),
    )
    
    actions = ['approve_transfer', 'execute_transfer']
    
    def approve_transfer(self, request, queryset):
        for transfer in queryset:
            transfer.status = 'APPROVED'
            transfer.approved_by = request.user.employee if hasattr(request.user, 'employee') else None
            transfer.approval_date = date.today()
            transfer.save()
        self.message_user(request, f"{queryset.count()}개 인사이동을 승인했습니다.")
    approve_transfer.short_description = "이동 승인"
    
    def execute_transfer(self, request, queryset):
        executed_count = 0
        for transfer in queryset:
            if transfer.execute_transfer():
                executed_count += 1
        self.message_user(request, f"{executed_count}개 인사이동을 실행했습니다.")
    execute_transfer.short_description = "이동 실행"


@admin.register(OrganizationChart)
class OrganizationChartAdmin(admin.ModelAdmin):
    list_display = ['department', 'parent_department', 'department_head', 
                   'employee_count', 'display_order', 'is_active']
    list_filter = ['is_active', 'parent_department']
    search_fields = ['department']
    ordering = ['display_order', 'department']
    
    actions = ['update_employee_counts']
    
    def update_employee_counts(self, request, queryset):
        for org in queryset:
            org.update_employee_count()
        self.message_user(request, f"{queryset.count()}개 부서의 직원 수를 업데이트했습니다.")
    update_employee_counts.short_description = "직원 수 업데이트"
