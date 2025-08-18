from django.contrib import admin
from .models import (
    AIAnalysisType, AIAnalysisResult, HRChatbotConversation,
    AIInsight, AIModelConfig
)


@admin.register(AIAnalysisType)
class AIAnalysisTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type_code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'type_code', 'description']
    ordering = ['name']


@admin.register(AIAnalysisResult)
class AIAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['get_analysis_display', 'get_target', 'score', 'confidence', 'analyzed_at', 'is_valid']
    list_filter = ['analysis_type', 'analyzed_at', 'confidence']
    search_fields = ['employee__name', 'department', 'insights']
    raw_id_fields = ['employee', 'created_by']
    readonly_fields = ['analyzed_at', 'is_valid']
    ordering = ['-analyzed_at']
    
    def get_analysis_display(self, obj):
        return obj.analysis_type.name
    get_analysis_display.short_description = '분석 유형'
    
    def get_target(self, obj):
        if obj.employee:
            return f"{obj.employee.name} ({obj.employee.department})"
        elif obj.department:
            return f"{obj.department} 부서"
        return "전사"
    get_target.short_description = '분석 대상'


@admin.register(HRChatbotConversation)
class HRChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'employee', 'is_active', 'started_at', 'last_message_at', 'satisfaction_score']
    list_filter = ['is_active', 'started_at', 'satisfaction_score']
    search_fields = ['user__username', 'employee__name', 'feedback']
    raw_id_fields = ['user', 'employee']
    readonly_fields = ['started_at', 'last_message_at']
    ordering = ['-last_message_at']


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'priority', 'generated_at', 'views_count', 'is_archived']
    list_filter = ['category', 'priority', 'is_archived', 'generated_at']
    search_fields = ['title', 'description', 'impact_analysis']
    filter_horizontal = ['target_employees']
    readonly_fields = ['generated_at', 'views_count']
    ordering = ['-generated_at']
    
    actions = ['archive_insights', 'unarchive_insights']
    
    def archive_insights(self, request, queryset):
        updated = queryset.update(is_archived=True)
        self.message_user(request, f"{updated}개의 인사이트가 보관되었습니다.")
    archive_insights.short_description = "선택한 인사이트 보관"
    
    def unarchive_insights(self, request, queryset):
        updated = queryset.update(is_archived=False)
        self.message_user(request, f"{updated}개의 인사이트가 활성화되었습니다.")
    unarchive_insights.short_description = "선택한 인사이트 활성화"


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'analysis_type', 'version', 'accuracy', 'is_active', 'last_trained']
    list_filter = ['analysis_type', 'is_active', 'last_trained']
    search_fields = ['model_name', 'version']
    raw_id_fields = ['analysis_type']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['model_name']
