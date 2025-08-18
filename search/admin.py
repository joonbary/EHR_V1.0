from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    SearchIndex, SearchQuery, PopularSearch, 
    SearchSuggestion, SavedSearch
)


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'search_type', 'priority', 'search_count', 
        'is_public', 'department_restricted', 'last_searched'
    ]
    list_filter = [
        'search_type', 'is_public', 'priority', 
        'department_restricted', 'created_at'
    ]
    search_fields = ['title', 'content', 'keywords']
    readonly_fields = ['id', 'search_count', 'last_searched', 'created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('id', 'search_type', 'title', 'content', 'keywords')
        }),
        ('연결 정보', {
            'fields': ('content_type', 'object_id', 'url', 'image_url')
        }),
        ('접근 권한', {
            'fields': ('is_public', 'department_restricted', 'position_restricted')
        }),
        ('통계 및 우선순위', {
            'fields': ('priority', 'search_count', 'last_searched')
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content_type')
    
    actions = ['rebuild_search_index', 'reset_search_counts']
    
    def rebuild_search_index(self, request, queryset):
        from .services import SearchIndexManager
        SearchIndexManager.rebuild_all_indexes()
        self.message_user(request, "검색 인덱스가 재구축되었습니다.")
    rebuild_search_index.short_description = "검색 인덱스 재구축"
    
    def reset_search_counts(self, request, queryset):
        queryset.update(search_count=0, last_searched=None)
        self.message_user(request, f"{queryset.count()}개 항목의 검색 횟수가 초기화되었습니다.")
    reset_search_counts.short_description = "검색 횟수 초기화"


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'query', 'search_type', 'results_count', 
        'execution_time', 'created_at'
    ]
    list_filter = [
        'search_type', 'results_count', 'created_at'
    ]
    search_fields = ['query', 'query_normalized', 'user__name']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('검색 정보', {
            'fields': ('id', 'user', 'query', 'query_normalized', 'search_type')
        }),
        ('검색 결과', {
            'fields': ('results_count', 'selected_result_id', 'execution_time')
        }),
        ('요청 정보', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('메타데이터', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    date_hierarchy = 'created_at'


@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = [
        'query', 'search_count', 'trend_score', 
        'daily_count', 'weekly_count', 'monthly_count', 'last_searched'
    ]
    list_filter = ['created_at', 'last_searched']
    search_fields = ['query']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('검색어 정보', {
            'fields': ('query',)
        }),
        ('통계', {
            'fields': ('search_count', 'daily_count', 'weekly_count', 'monthly_count')
        }),
        ('트렌드', {
            'fields': ('trend_score', 'last_searched')
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['recalculate_trend_scores', 'reset_period_counts']
    
    def recalculate_trend_scores(self, request, queryset):
        for item in queryset:
            item.calculate_trend_score()
            item.save()
        self.message_user(request, f"{queryset.count()}개 항목의 트렌드 스코어가 재계산되었습니다.")
    recalculate_trend_scores.short_description = "트렌드 스코어 재계산"
    
    def reset_period_counts(self, request, queryset):
        queryset.update(daily_count=0, weekly_count=0, monthly_count=0)
        self.message_user(request, f"{queryset.count()}개 항목의 기간별 카운트가 초기화되었습니다.")
    reset_period_counts.short_description = "기간별 카운트 초기화"


@admin.register(SearchSuggestion)
class SearchSuggestionAdmin(admin.ModelAdmin):
    list_display = [
        'display_text', 'query', 'suggestion_type', 
        'priority', 'usage_count', 'is_active'
    ]
    list_filter = ['suggestion_type', 'is_active', 'priority']
    search_fields = ['query', 'display_text']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('제안 정보', {
            'fields': ('query', 'display_text', 'suggestion_type')
        }),
        ('설정', {
            'fields': ('priority', 'is_active')
        }),
        ('통계', {
            'fields': ('usage_count',)
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_suggestions', 'deactivate_suggestions']
    
    def activate_suggestions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()}개 제안이 활성화되었습니다.")
    activate_suggestions.short_description = "제안 활성화"
    
    def deactivate_suggestions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()}개 제안이 비활성화되었습니다.")
    deactivate_suggestions.short_description = "제안 비활성화"


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'name', 'query', 'search_type', 
        'enable_alerts', 'usage_count', 'last_used'
    ]
    list_filter = [
        'search_type', 'enable_alerts', 'alert_frequency', 'created_at'
    ]
    search_fields = ['name', 'query', 'user__name']
    readonly_fields = ['id', 'usage_count', 'last_used', 'created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('id', 'user', 'name', 'query', 'search_type')
        }),
        ('알림 설정', {
            'fields': ('enable_alerts', 'alert_frequency', 'last_alert_sent')
        }),
        ('사용 통계', {
            'fields': ('usage_count', 'last_used')
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['execute_saved_searches']
    
    def execute_saved_searches(self, request, queryset):
        """저장된 검색 실행 (테스트용)"""
        for saved_search in queryset:
            result = saved_search.execute_search()
            self.message_user(
                request, 
                f"'{saved_search.name}' 검색 실행 완료 - {result['total_count']}개 결과"
            )
    execute_saved_searches.short_description = "저장된 검색 실행"
