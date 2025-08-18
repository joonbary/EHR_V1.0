"""
Django Admin Configuration for Enhanced Organization Models
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from .models_enhanced import OrgUnit, OrgScenario, OrgSnapshot, OrgChangeLog


@admin.register(OrgUnit)
class OrgUnitAdmin(admin.ModelAdmin):
    """조직 단위 관리"""
    list_display = [
        'id', 'company_badge', 'name', 'function',
        'reports_to_link', 'leader_info', 'headcount_badge',
        'subordinates_count'
    ]
    list_filter = ['company', 'function', 'created_at']
    search_fields = ['id', 'name', 'leader_name', 'function']
    raw_id_fields = ['reports_to', 'created_by']
    readonly_fields = ['created_at', 'updated_at', 'get_tree_view', 'get_total_headcount']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('id', 'company', 'name', 'function')
        }),
        ('조직 구조', {
            'fields': ('reports_to', 'get_tree_view')
        }),
        ('리더 정보', {
            'fields': ('leader_title', 'leader_rank', 'leader_name', 'leader_age')
        }),
        ('인원 구성', {
            'fields': ('headcount', 'members', 'get_total_headcount')
        }),
        ('메타데이터', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def company_badge(self, obj):
        colors = {
            'OK저축은행': '#4169E1',
            'OK캐피탈': '#FF6347',
            'OK금융그룹': '#22C55E',
        }
        color = colors.get(obj.company, '#888')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.company
        )
    company_badge.short_description = '회사'
    
    def reports_to_link(self, obj):
        if obj.reports_to:
            return format_html(
                '<a href="/admin/organization/orgunit/{}/change/">{}</a>',
                obj.reports_to.id, obj.reports_to.name
            )
        return '-'
    reports_to_link.short_description = '상위 조직'
    
    def leader_info(self, obj):
        if obj.leader_name:
            return format_html(
                '<strong>{}</strong><br/>{} · {}',
                obj.leader_name, obj.leader_title, obj.leader_rank
            )
        return '-'
    leader_info.short_description = '리더'
    
    def headcount_badge(self, obj):
        return format_html(
            '<span style="background-color: #f0f0f0; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            obj.headcount
        )
    headcount_badge.short_description = '인원'
    
    def subordinates_count(self, obj):
        count = obj.subordinates.count()
        if count > 0:
            return format_html(
                '<span style="color: #4CAF50; font-weight: bold;">{}</span>',
                count
            )
        return '0'
    subordinates_count.short_description = '하위 조직'
    
    def get_tree_view(self, obj):
        """조직 트리 뷰"""
        tree = []
        current = obj
        while current.reports_to:
            tree.insert(0, current.reports_to.name)
            current = current.reports_to
        tree.append(f'<strong>{obj.name}</strong>')
        
        subordinates = obj.get_all_subordinates()
        if subordinates:
            tree.append(f'└─ {len(subordinates)}개 하위 조직')
        
        return format_html(' > '.join(tree))
    get_tree_view.short_description = '조직 계층'
    
    def get_total_headcount(self, obj):
        """총 인원수 (하위 조직 포함)"""
        return obj.get_total_headcount()
    get_total_headcount.short_description = '총 인원수'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('reports_to', 'created_by')


@admin.register(OrgScenario)
class OrgScenarioAdmin(admin.ModelAdmin):
    """조직 시나리오 관리"""
    list_display = [
        'name', 'author', 'is_active_badge',
        'units_count', 'created_at'
    ]
    list_filter = ['is_active', 'created_at', 'author']
    search_fields = ['name', 'description', 'tags']
    readonly_fields = ['scenario_id', 'created_at', 'updated_at', 'preview_scenario']
    raw_id_fields = ['author']
    
    fieldsets = (
        ('시나리오 정보', {
            'fields': ('name', 'description', 'tags', 'is_active')
        }),
        ('시나리오 데이터', {
            'fields': ('payload', 'preview_scenario')
        }),
        ('메타데이터', {
            'fields': ('scenario_id', 'author', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; '
                'padding: 3px 8px; border-radius: 3px;">활성</span>'
            )
        return format_html(
            '<span style="background-color: #ccc; color: white; '
            'padding: 3px 8px; border-radius: 3px;">비활성</span>'
        )
    is_active_badge.short_description = '상태'
    
    def units_count(self, obj):
        return len(obj.payload)
    units_count.short_description = '조직 수'
    
    def preview_scenario(self, obj):
        """시나리오 미리보기"""
        if not obj.payload:
            return '데이터 없음'
        
        preview = []
        for unit in obj.payload[:5]:  # Show first 5 units
            preview.append(f"• {unit.get('company', '')} - {unit.get('name', '')}")
        
        if len(obj.payload) > 5:
            preview.append(f"... 외 {len(obj.payload) - 5}개")
        
        return format_html('<br>'.join(preview))
    preview_scenario.short_description = '시나리오 미리보기'
    
    actions = ['apply_scenario', 'deactivate_scenario']
    
    def apply_scenario(self, request, queryset):
        """시나리오 적용"""
        for scenario in queryset:
            try:
                scenario.apply_scenario()
                self.message_user(request, f'시나리오 "{scenario.name}"가 적용되었습니다.')
            except Exception as e:
                self.message_user(request, f'오류: {str(e)}', level='ERROR')
    apply_scenario.short_description = '선택한 시나리오 적용'
    
    def deactivate_scenario(self, request, queryset):
        """시나리오 비활성화"""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()}개 시나리오가 비활성화되었습니다.')
    deactivate_scenario.short_description = '선택한 시나리오 비활성화'


@admin.register(OrgSnapshot)
class OrgSnapshotAdmin(admin.ModelAdmin):
    """조직 스냅샷 관리"""
    list_display = [
        'name', 'snapshot_type_badge', 'units_count',
        'created_by', 'created_at'
    ]
    list_filter = ['snapshot_type', 'created_at', 'created_by']
    search_fields = ['name', 'snapshot_id']
    readonly_fields = ['snapshot_id', 'created_at', 'preview_data']
    raw_id_fields = ['scenario', 'created_by']
    
    def snapshot_type_badge(self, obj):
        colors = {
            'CURRENT': '#2196F3',
            'WHATIF': '#FF9800',
            'BACKUP': '#9C27B0',
            'COMPARISON': '#4CAF50',
        }
        color = colors.get(obj.snapshot_type, '#888')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_snapshot_type_display()
        )
    snapshot_type_badge.short_description = '유형'
    
    def units_count(self, obj):
        return len(obj.data)
    units_count.short_description = '조직 수'
    
    def preview_data(self, obj):
        """데이터 미리보기"""
        if not obj.data:
            return '데이터 없음'
        
        preview = []
        for unit in obj.data[:5]:
            preview.append(f"• {unit.get('company', '')} - {unit.get('name', '')}")
        
        if len(obj.data) > 5:
            preview.append(f"... 외 {len(obj.data) - 5}개")
        
        return format_html('<br>'.join(preview))
    preview_data.short_description = '데이터 미리보기'


@admin.register(OrgChangeLog)
class OrgChangeLogAdmin(admin.ModelAdmin):
    """조직 변경 로그"""
    list_display = [
        'action_badge', 'org_unit_id', 'user',
        'ip_address', 'created_at'
    ]
    list_filter = ['action', 'created_at', 'user']
    search_fields = ['org_unit_id', 'user__username', 'ip_address']
    readonly_fields = ['created_at', 'formatted_changes']
    
    def action_badge(self, obj):
        colors = {
            'CREATE': '#4CAF50',
            'UPDATE': '#2196F3',
            'DELETE': '#F44336',
            'REORG': '#FF9800',
            'IMPORT': '#9C27B0',
            'EXPORT': '#00BCD4',
            'WHATIF': '#FFC107',
            'SCENARIO': '#795548',
        }
        color = colors.get(obj.action, '#888')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_action_display()
        )
    action_badge.short_description = '액션'
    
    def formatted_changes(self, obj):
        """변경 내역 포맷팅"""
        import json
        try:
            formatted = json.dumps(obj.changes, indent=2, ensure_ascii=False)
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', formatted)
        except:
            return str(obj.changes)
    formatted_changes.short_description = '변경 내역'
    
    def has_add_permission(self, request):
        # Prevent manual creation of logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent modification of logs
        return False