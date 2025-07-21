from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'job_group', 'job_type', 'new_position', 
        'growth_level', 'department', 'manager', 'employment_status'
    ]
    
    list_filter = [
        'job_group', 'job_type', 'new_position', 'growth_level', 
        'employment_status', 'employment_type', 'department'
    ]
    
    search_fields = ['name', 'email', 'job_role']
    
    raw_id_fields = ['manager']  # 관리자 선택을 위한 검색 인터페이스
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'email', 'phone', 'hire_date')
        }),
        ('조직 정보', {
            'fields': (
                'job_group', 'job_type', 'job_role', 
                'department', 'new_position', 'growth_level', 'grade_level'
            )
        }),
        ('관계 정보', {
            'fields': ('manager',)
        }),
        ('고용 정보', {
            'fields': ('employment_type', 'employment_status')
        }),
    )
    
    ordering = ['job_group', 'job_type', 'growth_level', 'name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('manager')
