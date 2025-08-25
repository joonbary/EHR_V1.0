from django.contrib import admin
from .models import Employee

# 인재 관리 Admin 등록
try:
    from .admin_talent import *
except ImportError:
    pass  # 마이그레이션 전에는 무시

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'no', 'name', 'company', 'final_department', 'current_position', 
        'employment_status', 'age', 'gender', 'hire_date'
    ]
    
    list_filter = [
        'company', 'employment_status', 'gender', 'job_series', 
        'current_position', 'headquarters1', 'final_department',
        'job_group', 'job_type', 'growth_level'
    ]
    
    search_fields = [
        'name', 'dummy_name', 'email', 'dummy_email', 
        'no', 'final_department', 'job_tag_name'
    ]
    
    raw_id_fields = ['manager']  # 관리자 선택을 위한 검색 인터페이스
    
    fieldsets = (
        ('기본 정보', {
            'fields': (
                'no', 'name', 'email', 'phone', 'gender', 'age', 'birth_date',
                'education', 'marital_status'
            )
        }),
        ('익명화 데이터', {
            'fields': (
                'dummy_name', 'dummy_chinese_name', 'dummy_email', 'dummy_mobile',
                'dummy_ssn', 'dummy_registered_address', 'dummy_residence_address'
            ),
            'classes': ('collapse',),
        }),
        ('회사/조직 정보', {
            'fields': (
                'company', 'headquarters1', 'headquarters2',
                'department1', 'department2', 'department3', 'department4',
                'final_department'
            )
        }),
        ('직급/직책 정보', {
            'fields': (
                'previous_position', 'current_position', 'job_series', 'title',
                'responsibility', 'promotion_level', 'salary_grade',
                'job_family', 'job_field', 'classification', 'detailed_classification'
            )
        }),
        ('입사/근무 정보', {
            'fields': (
                'hire_date', 'group_join_date', 'career_join_date', 'new_join_date',
                'promotion_accumulated_years', 'diversity_years', 'current_headcount'
            )
        }),
        ('평가/태그 정보', {
            'fields': (
                'final_evaluation', 'job_tag_name', 'rank_tag_name', 'category'
            )
        }),
        ('기존 신인사제도 필드', {
            'fields': (
                'job_group', 'job_type', 'job_role', 'department', 'position',
                'new_position', 'growth_level', 'grade_level',
                'employment_type', 'employment_status'
            ),
            'classes': ('collapse',),
        }),
        ('관계/기타 정보', {
            'fields': (
                'manager', 'address', 'emergency_contact', 'emergency_phone',
                'profile_image', 'user'
            ),
            'classes': ('collapse',),
        }),
    )
    
    ordering = ['company', 'headquarters1', 'final_department', 'current_position', 'name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('manager')
