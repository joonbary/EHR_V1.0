from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Department, Position, OrganizationChart, 
    DepartmentHistory, EmployeeTransfer, TeamAssignment
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department_type', 'parent', 'manager', 'is_active', 'employee_count']
    list_filter = ['department_type', 'is_active', 'level']
    search_fields = ['code', 'name', 'name_en', 'manager__name']
    raw_id_fields = ['parent', 'manager', 'created_by']
    ordering = ['level', 'code']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('code', 'name', 'name_en', 'department_type')
        }),
        ('조직 구조', {
            'fields': ('parent', 'level', 'manager')
        }),
        ('부서 정보', {
            'fields': ('description', 'location', 'phone', 'email')
        }),
        ('상태', {
            'fields': ('is_active', 'established_date', 'closed_date')
        }),
        ('메타데이터', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'employee_count']
    
    def employee_count(self, obj):
        return obj.get_employee_count()
    employee_count.short_description = '직원 수'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('parent', 'manager')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'position_type', 'rank', 'growth_level_range', 'is_manager', 'is_active']
    list_filter = ['position_type', 'is_manager', 'can_approve', 'can_evaluate', 'is_active']
    search_fields = ['code', 'name', 'name_en']
    ordering = ['rank', 'code']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('code', 'name', 'name_en', 'position_type')
        }),
        ('직급 정보', {
            'fields': ('rank', 'growth_level_min', 'growth_level_max')
        }),
        ('권한', {
            'fields': ('is_manager', 'can_approve', 'can_evaluate')
        }),
        ('설명', {
            'fields': ('description', 'responsibilities', 'requirements'),
            'classes': ('collapse',)
        }),
        ('상태', {
            'fields': ('is_active',)
        }),
    )
    
    def growth_level_range(self, obj):
        return f"Lv.{obj.growth_level_min} - Lv.{obj.growth_level_max}"
    growth_level_range.short_description = '성장레벨 범위'


@admin.register(OrganizationChart)
class OrganizationChartAdmin(admin.ModelAdmin):
    list_display = ['version', 'name', 'effective_date', 'is_active', 'approval_status']
    list_filter = ['is_active', 'effective_date']
    search_fields = ['version', 'name']
    date_hierarchy = 'effective_date'
    raw_id_fields = ['approved_by', 'created_by']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('version', 'name', 'description')
        }),
        ('시행 정보', {
            'fields': ('effective_date', 'end_date', 'is_active')
        }),
        ('승인 정보', {
            'fields': ('approved_by', 'approved_date')
        }),
        ('메타데이터', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']
    
    def approval_status(self, obj):
        if obj.approved_date:
            return format_html('<span style="color: green;">승인완료</span>')
        return format_html('<span style="color: orange;">미승인</span>')
    approval_status.short_description = '승인 상태'
    
    actions = ['activate_organization_chart']
    
    def activate_organization_chart(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "하나의 조직도만 선택해주세요.", level='error')
            return
        
        org_chart = queryset.first()
        org_chart.activate()
        self.message_user(request, f"{org_chart.name}이(가) 활성화되었습니다.")
    activate_organization_chart.short_description = "선택한 조직도 활성화"


@admin.register(DepartmentHistory)
class DepartmentHistoryAdmin(admin.ModelAdmin):
    list_display = ['department', 'change_type', 'changed_date', 'organization_chart', 'changed_by']
    list_filter = ['change_type', 'changed_date']
    search_fields = ['department__name', 'old_name', 'new_name', 'reason']
    date_hierarchy = 'changed_date'
    raw_id_fields = ['department', 'organization_chart', 'old_parent', 'new_parent', 'changed_by']
    
    fieldsets = (
        ('부서 정보', {
            'fields': ('department', 'organization_chart')
        }),
        ('변경 내용', {
            'fields': ('change_type', 'old_name', 'new_name', 'old_parent', 'new_parent')
        }),
        ('변경 사유', {
            'fields': ('reason', 'changed_date', 'changed_by')
        }),
    )
    readonly_fields = ['created_at']


@admin.register(EmployeeTransfer)
class EmployeeTransferAdmin(admin.ModelAdmin):
    list_display = ['employee', 'transfer_type', 'transfer_date', 'department_change', 'position_change', 'approval_status']
    list_filter = ['transfer_type', 'transfer_date', 'approved_date']
    search_fields = ['employee__name', 'reason', 'remarks']
    date_hierarchy = 'transfer_date'
    raw_id_fields = ['employee', 'old_department', 'new_department', 'approved_by', 'created_by']
    
    fieldsets = (
        ('직원 정보', {
            'fields': ('employee', 'transfer_type', 'transfer_date')
        }),
        ('이전 정보', {
            'fields': ('old_department', 'old_position', 'old_growth_level')
        }),
        ('새 정보', {
            'fields': ('new_department', 'new_position', 'new_growth_level')
        }),
        ('상세 정보', {
            'fields': ('reason', 'remarks')
        }),
        ('승인 정보', {
            'fields': ('approved_by', 'approved_date')
        }),
        ('메타데이터', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']
    
    def department_change(self, obj):
        if obj.old_department and obj.new_department:
            return f"{obj.old_department.name} → {obj.new_department.name}"
        return "-"
    department_change.short_description = '부서 변경'
    
    def position_change(self, obj):
        if obj.old_position != obj.new_position:
            return f"{obj.old_position} → {obj.new_position}"
        return obj.new_position
    position_change.short_description = '직위 변경'
    
    def approval_status(self, obj):
        if obj.approved_date:
            return format_html('<span style="color: green;">승인완료</span>')
        return format_html('<span style="color: orange;">승인대기</span>')
    approval_status.short_description = '승인 상태'
    
    actions = ['approve_transfers']
    
    def approve_transfers(self, request, queryset):
        approved_count = 0
        for transfer in queryset.filter(approved_date__isnull=True):
            transfer.approved_by = request.user
            transfer.approved_date = timezone.now()
            transfer.save()
            transfer.execute_transfer()
            approved_count += 1
        
        self.message_user(request, f"{approved_count}건의 인사이동이 승인되었습니다.")
    approve_transfers.short_description = "선택한 인사이동 승인"


@admin.register(TeamAssignment)
class TeamAssignmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'department', 'role', 'is_primary', 'assignment_ratio', 'period_display', 'is_active']
    list_filter = ['is_primary', 'start_date', 'end_date']
    search_fields = ['employee__name', 'department__name', 'role']
    date_hierarchy = 'start_date'
    raw_id_fields = ['employee', 'department', 'created_by']
    
    fieldsets = (
        ('배치 정보', {
            'fields': ('employee', 'department', 'role')
        }),
        ('업무 비중', {
            'fields': ('is_primary', 'assignment_ratio')
        }),
        ('기간', {
            'fields': ('start_date', 'end_date')
        }),
        ('메타데이터', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'is_active']
    
    def period_display(self, obj):
        if obj.end_date:
            return f"{obj.start_date} ~ {obj.end_date}"
        return f"{obj.start_date} ~ 현재"
    period_display.short_description = '배치 기간'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('employee', 'department')