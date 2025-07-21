from django.contrib import admin
from .models import (
    SalaryTable, CompetencyPayTable, PositionAllowance,
    PerformanceIncentiveRate, EmployeeCompensation
)


@admin.register(SalaryTable)
class SalaryTableAdmin(admin.ModelAdmin):
    list_display = ['growth_level', 'base_salary', 'formatted_salary']
    list_filter = ['growth_level']
    search_fields = ['growth_level']
    ordering = ['growth_level']
    
    def formatted_salary(self, obj):
        return f"{obj.base_salary:,}원"
    formatted_salary.short_description = '기본급'


@admin.register(CompetencyPayTable)
class CompetencyPayTableAdmin(admin.ModelAdmin):
    list_display = ['growth_level', 'job_type', 'competency_pay', 'formatted_pay']
    list_filter = ['growth_level', 'job_type']
    search_fields = ['growth_level', 'job_type']
    ordering = ['growth_level', 'job_type']
    
    def formatted_pay(self, obj):
        return f"{obj.competency_pay:,}원"
    formatted_pay.short_description = '역량급'


@admin.register(PositionAllowance)
class PositionAllowanceAdmin(admin.ModelAdmin):
    list_display = ['position', 'allowance_amount', 'formatted_allowance']
    search_fields = ['position']
    ordering = ['allowance_amount']
    
    def formatted_allowance(self, obj):
        return f"{obj.allowance_amount:,}원"
    formatted_allowance.short_description = '직책급'


@admin.register(PerformanceIncentiveRate)
class PerformanceIncentiveRateAdmin(admin.ModelAdmin):
    list_display = ['evaluation_grade', 'incentive_rate', 'formatted_rate']
    search_fields = ['evaluation_grade']
    ordering = ['-incentive_rate']
    
    def formatted_rate(self, obj):
        return f"{obj.incentive_rate}%"
    formatted_rate.short_description = '지급률'


@admin.register(EmployeeCompensation)
class EmployeeCompensationAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'year', 'month', 'formatted_base_salary',
        'formatted_total_compensation', 'evaluation_grade'
    ]
    list_filter = ['year', 'month', 'employee__job_type']
    search_fields = ['employee__name', 'employee__email']
    readonly_fields = [
        'fixed_overtime', 'total_compensation', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('기본정보', {
            'fields': ('employee', 'year', 'month', 'evaluation')
        }),
        ('급여 구성', {
            'fields': ('base_salary', 'fixed_overtime', 'competency_pay', 'position_allowance')
        }),
        ('성과급', {
            'fields': ('pi_amount',)
        }),
        ('총 보상', {
            'fields': ('total_compensation',)
        }),
        ('시스템정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_base_salary(self, obj):
        return f"{obj.base_salary:,}원"
    formatted_base_salary.short_description = '기본급'
    
    def formatted_total_compensation(self, obj):
        return f"{obj.total_compensation:,}원"
    formatted_total_compensation.short_description = '총 보상'
    
    def evaluation_grade(self, obj):
        if obj.evaluation and obj.evaluation.manager_grade:
            return obj.evaluation.manager_grade
        return '-'
    evaluation_grade.short_description = '평가등급'
