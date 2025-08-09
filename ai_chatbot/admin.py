from django.contrib import admin
from .models import ChatSession, ChatMessage, AIPromptTemplate, QuickAction, AIConfiguration


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'created_at', 'updated_at', 'is_active', 'get_message_count']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'employee__name', 'context']
    date_hierarchy = 'created_at'
    
    def get_message_count(self, obj):
        return obj.get_message_count()
    get_message_count.short_description = '메시지 수'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['get_session_title', 'role', 'get_content_preview', 'created_at', 'tokens_used', 'model_used']
    list_filter = ['role', 'model_used', 'created_at']
    search_fields = ['content', 'session__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['id', 'created_at']
    
    def get_session_title(self, obj):
        return obj.session.title
    get_session_title.short_description = '세션'
    
    def get_content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    get_content_preview.short_description = '내용'


@admin.register(AIPromptTemplate)
class AIPromptTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'usage_count', 'success_rate', 'updated_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description', 'prompt_template']
    readonly_fields = ['created_at', 'updated_at', 'usage_count', 'success_rate']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('프롬프트', {
            'fields': ('prompt_template',)
        }),
        ('통계', {
            'fields': ('usage_count', 'success_rate', 'created_at', 'updated_at')
        }),
    )


@admin.register(QuickAction)
class QuickActionAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'icon', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'prompt']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'title']


@admin.register(AIConfiguration)
class AIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['key', 'get_value_preview', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['key', 'description']
    readonly_fields = ['updated_at']
    
    def get_value_preview(self, obj):
        # API 키 등 민감한 정보는 마스킹
        if 'KEY' in obj.key or 'SECRET' in obj.key:
            return '***HIDDEN***'
        return obj.value[:100] + '...' if len(obj.value) > 100 else obj.value
    get_value_preview.short_description = '값'