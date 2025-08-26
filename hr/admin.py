"""
HR 관리 시스템 Admin 인터페이스
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from .models import (
    # 직급/직군 체계
    JobFamily, JobCategory, JobPosition, JobGrade,
    # 급여 관리
    SalaryGrade, BaseSalary, PerformanceBonus, Allowance,
    # 경력 관리
    CareerHistory, PromotionHistory,
    # 교육 및 자격
    Education, Certification, Training,
    # 평가 관리
    PerformanceEvaluation,
    # 복리후생
    Benefit, EmployeeBenefit,
    # 급여 계산
    MonthlySalary
)

# ========================================
# 직급/직군 체계 Admin
# ========================================

@admin.register(JobFamily)
class JobFamilyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'category_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name', 'description']
    ordering = ['code']
    
    def category_count(self, obj):
        return obj.categories.count()
    category_count.short_description = '직종 수'


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'job_family', 'is_active', 'position_count']
    list_filter = ['job_family', 'is_active']
    search_fields = ['code', 'name', 'description']
    ordering = ['job_family', 'code']
    
    def position_count(self, obj):
        return obj.positions.count()
    position_count.short_description = '직무 수'


@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'job_category', 'is_active']
    list_filter = ['job_category__job_family', 'job_category', 'is_active']
    search_fields = ['code', 'name', 'description', 'required_skills']
    ordering = ['job_category', 'code']


@admin.register(JobGrade)
class JobGradeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'level', 'min_years', 'max_years', 'is_executive', 'is_active']
    list_filter = ['is_executive', 'is_active', 'level']
    search_fields = ['code', 'name']
    ordering = ['level']


# ========================================
# 급여 관리 Admin
# ========================================

@admin.register(SalaryGrade)
class SalaryGradeAdmin(admin.ModelAdmin):
    list_display = ['grade_code', 'grade_name', 'formatted_min', 'formatted_max', 'formatted_mid', 'is_active']
    list_filter = ['is_active']
    search_fields = ['grade_code', 'grade_name']
    ordering = ['grade_code']
    
    def formatted_min(self, obj):
        return f"₩{obj.min_amount:,.0f}"
    formatted_min.short_description = '최소금액'
    
    def formatted_max(self, obj):
        return f"₩{obj.max_amount:,.0f}"
    formatted_max.short_description = '최대금액'
    
    def formatted_mid(self, obj):
        return f"₩{obj.midpoint:,.0f}"
    formatted_mid.short_description = '중간값'


@admin.register(BaseSalary)
class BaseSalaryAdmin(admin.ModelAdmin):
    list_display = ['employee_link', 'formatted_amount', 'salary_grade', 'effective_date', 'is_active']
    list_filter = ['is_active', 'salary_grade', 'effective_date']
    search_fields = ['employee__name', 'employee__email']
    date_hierarchy = 'effective_date'
    ordering = ['-effective_date']
    
    def employee_link(self, obj):
        url = reverse('admin:employees_employee_change', args=[obj.employee.pk])
        return format_html('<a href="{}">{}</a>', url, obj.employee.name)
    employee_link.short_description = '직원'
    
    def formatted_amount(self, obj):
        return f"₩{obj.base_amount:,.0f}"
    formatted_amount.short_description = '기본급'


@admin.register(PerformanceBonus)
class PerformanceBonusAdmin(admin.ModelAdmin):
    list_display = ['employee', 'bonus_type', 'formatted_amount', 'payment_date', 'is_paid']
    list_filter = ['bonus_type', 'is_paid', 'payment_date']
    search_fields = ['employee__name', 'description']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    
    def formatted_amount(self, obj):
        return f"₩{obj.bonus_amount:,.0f}"
    formatted_amount.short_description = '성과급'


@admin.register(Allowance)
class AllowanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'allowance_type', 'formatted_amount', 'effective_date', 'is_active', 'is_taxable']
    list_filter = ['allowance_type', 'is_active', 'is_taxable']
    search_fields = ['employee__name']
    date_hierarchy = 'effective_date'
    
    def formatted_amount(self, obj):
        return f"₩{obj.amount:,.0f}"
    formatted_amount.short_description = '수당금액'


# ========================================
# 경력 관리 Admin
# ========================================

@admin.register(CareerHistory)
class CareerHistoryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'company', 'position', 'department', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current', 'start_date']
    search_fields = ['employee__name', 'company', 'position']
    date_hierarchy = 'start_date'


@admin.register(PromotionHistory)
class PromotionHistoryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'from_grade', 'to_grade', 'promotion_date', 'promotion_type']
    list_filter = ['promotion_type', 'promotion_date']
    search_fields = ['employee__name']
    date_hierarchy = 'promotion_date'


# ========================================
# 교육 및 자격 Admin
# ========================================

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'degree', 'school_name', 'major', 'graduation_date', 'is_graduated']
    list_filter = ['degree', 'is_graduated']
    search_fields = ['employee__name', 'school_name', 'major']
    date_hierarchy = 'graduation_date'


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'cert_name', 'issuing_org', 'issue_date', 'is_valid', 'formatted_allowance']
    list_filter = ['is_valid', 'issuing_org']
    search_fields = ['employee__name', 'cert_name']
    date_hierarchy = 'issue_date'
    
    def formatted_allowance(self, obj):
        return f"₩{obj.cert_allowance:,.0f}"
    formatted_allowance.short_description = '자격수당'


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'training_name', 'training_type', 'start_date', 'hours', 'is_completed']
    list_filter = ['training_type', 'is_completed', 'certificate_issued']
    search_fields = ['employee__name', 'training_name', 'institution']
    date_hierarchy = 'start_date'


# ========================================
# 평가 관리 Admin
# ========================================

@admin.register(PerformanceEvaluation)
class PerformanceEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluation_type', 'evaluation_period', 'rating', 'total_score', 'is_finalized']
    list_filter = ['evaluation_type', 'rating', 'is_finalized']
    search_fields = ['employee__name']
    readonly_fields = ['created_at', 'updated_at', 'finalized_date']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('employee', 'evaluation_type', 'evaluation_period', 'evaluator')
        }),
        ('평가 점수', {
            'fields': ('job_performance_score', 'competency_score', 'attitude_score', 'total_score', 'rating')
        }),
        ('피드백', {
            'fields': ('strengths', 'improvements', 'development_plan')
        }),
        ('관리 정보', {
            'fields': ('is_finalized', 'finalized_date', 'created_at', 'updated_at')
        })
    )


# ========================================
# 복리후생 Admin
# ========================================

@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'is_active', 'employee_count']
    list_filter = ['category', 'is_active']
    search_fields = ['code', 'name', 'description']
    
    def employee_count(self, obj):
        return EmployeeBenefit.objects.filter(benefit=obj, is_active=True).count()
    employee_count.short_description = '적용 직원 수'


@admin.register(EmployeeBenefit)
class EmployeeBenefitAdmin(admin.ModelAdmin):
    list_display = ['employee', 'benefit', 'enrollment_date', 'is_active', 'formatted_usage']
    list_filter = ['benefit__category', 'is_active']
    search_fields = ['employee__name', 'benefit__name']
    date_hierarchy = 'enrollment_date'
    
    def formatted_usage(self, obj):
        return f"₩{obj.usage_amount:,.0f}"
    formatted_usage.short_description = '사용금액'


# ========================================
# 급여 계산 Admin
# ========================================

@admin.register(MonthlySalary)
class MonthlySalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'year', 'month', 'formatted_gross', 'formatted_deduction', 'formatted_net', 'is_paid']
    list_filter = ['year', 'month', 'is_paid']
    search_fields = ['employee__name']
    ordering = ['-year', '-month']
    
    def formatted_gross(self, obj):
        return f"₩{obj.gross_amount:,.0f}"
    formatted_gross.short_description = '총지급액'
    
    def formatted_deduction(self, obj):
        return f"₩{obj.total_deductions:,.0f}"
    formatted_deduction.short_description = '총공제액'
    
    def formatted_net(self, obj):
        return f"₩{obj.net_amount:,.0f}"
    formatted_net.short_description = '실지급액'
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('employee', 'year', 'month')
        }),
        ('급여 구성', {
            'fields': (
                'base_salary', 'position_allowance', 'meal_allowance',
                'transport_allowance', 'other_allowances', 'overtime_pay', 'bonus'
            )
        }),
        ('공제 항목', {
            'fields': (
                'income_tax', 'local_tax', 'national_pension',
                'health_insurance', 'employment_insurance', 'other_deductions'
            )
        }),
        ('총계', {
            'fields': ('gross_amount', 'total_deductions', 'net_amount'),
            'description': '총계는 자동으로 계산됩니다.'
        }),
        ('지급 정보', {
            'fields': ('is_paid', 'payment_date')
        })
    )
    
    readonly_fields = ['gross_amount', 'total_deductions', 'net_amount', 'created_at', 'updated_at']
