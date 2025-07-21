from django.contrib import admin
from .models import ReportTemplate, ReportGeneration

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'created_by', 'created_at', 'is_active']
    list_filter = ['report_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

@admin.register(ReportGeneration)
class ReportGenerationAdmin(admin.ModelAdmin):
    list_display = ['template', 'generated_by', 'generated_at', 'record_count', 'file_format']
    list_filter = ['file_format', 'generated_at', 'template']
    readonly_fields = ['generated_at']
    search_fields = ['template__name', 'generated_by__username']
