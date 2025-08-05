from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter
from .models import (
    Role, Permission, RolePermission, UserRole,
    AccessLog, SecurityPolicy, AuditTrail
)


class ActiveRoleFilter(SimpleListFilter):
    title = '활성화 상태'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('1', '활성화'),
            ('0', '비활성화'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_active=True)
        if self.value() == '0':
            return queryset.filter(is_active=False)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'role_type', 'level', 'parent', 'is_active', 
        'is_system', 'max_assignees', 'user_count'
    ]
    list_filter = [
        'role_type', 'is_active', 'is_system', 'level', 
        ActiveRoleFilter, 'created_at'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'user_count']
    raw_id_fields = ['parent', 'created_by']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('id', 'name', 'description', 'role_type')
        }),
        ('계층 구조', {
            'fields': ('parent', 'level', 'inherit_permissions')
        }),
        ('제한 및 상태', {
            'fields': ('max_assignees', 'is_active', 'is_system')
        }),
        ('생성 정보', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_count(self, obj):
        count = obj.user_roles.filter(is_active=True).count()
        return format_html('<span style="color: #2563eb;">{}</span>', count)
    user_count.short_description = '할당된 사용자 수'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent', 'created_by')
    
    actions = ['activate_roles', 'deactivate_roles']
    
    def activate_roles(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count}개 역할이 활성화되었습니다.")
    activate_roles.short_description = "역할 활성화"
    
    def deactivate_roles(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count}개 역할이 비활성화되었습니다.")
    deactivate_roles.short_description = "역할 비활성화"


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'codename', 'permission_type', 'resource_type', 
        'level', 'is_active', 'is_system'
    ]
    list_filter = [
        'permission_type', 'resource_type', 'level', 'is_active', 
        'is_system', 'created_at'
    ]
    search_fields = ['name', 'codename', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('id', 'name', 'codename', 'description')
        }),
        ('권한 분류', {
            'fields': ('permission_type', 'resource_type', 'level')
        }),
        ('상태', {
            'fields': ('is_active', 'is_system')
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_permissions', 'deactivate_permissions']
    
    def activate_permissions(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count}개 권한이 활성화되었습니다.")
    activate_permissions.short_description = "권한 활성화"
    
    def deactivate_permissions(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count}개 권한이 비활성화되었습니다.")
    deactivate_permissions.short_description = "권한 비활성화"


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = [
        'role', 'permission', 'is_granted', 'is_denied', 
        'granted_by', 'granted_at'
    ]
    list_filter = [
        'is_granted', 'is_denied', 'granted_at', 'role__role_type',
        'permission__permission_type', 'permission__resource_type'
    ]
    search_fields = [
        'role__name', 'permission__name', 'permission__codename'
    ]
    raw_id_fields = ['role', 'permission', 'granted_by']
    readonly_fields = ['granted_at']
    
    fieldsets = (
        ('권한 매핑', {
            'fields': ('role', 'permission')
        }),
        ('권한 상태', {
            'fields': ('is_granted', 'is_denied')
        }),
        ('조건부 권한', {
            'fields': ('conditions',)
        }),
        ('메타데이터', {
            'fields': ('granted_by', 'granted_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'role', 'permission', 'granted_by'
        )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'role', 'scope_type', 'scope_value', 
        'is_active', 'is_primary', 'start_date', 'end_date'
    ]
    list_filter = [
        'scope_type', 'is_active', 'is_primary', 'start_date', 
        'end_date', 'role__role_type'
    ]
    search_fields = [
        'user__name', 'role__name', 'scope_value', 'assigned_reason'
    ]
    raw_id_fields = ['user', 'role', 'assigned_by']
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_expired']
    
    fieldsets = (
        ('기본 할당', {
            'fields': ('id', 'user', 'role')
        }),
        ('적용 범위', {
            'fields': ('scope_type', 'scope_value')
        }),
        ('기간 설정', {
            'fields': ('start_date', 'end_date', 'is_expired')
        }),
        ('상태', {
            'fields': ('is_active', 'is_primary')
        }),
        ('할당 정보', {
            'fields': ('assigned_by', 'assigned_reason')
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def is_expired(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: #dc2626;">만료됨</span>')
        return format_html('<span style="color: #059669;">유효함</span>')
    is_expired.short_description = '만료 상태'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'role', 'assigned_by'
        )
    
    date_hierarchy = 'start_date'
    
    actions = ['activate_user_roles', 'deactivate_user_roles']
    
    def activate_user_roles(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count}개 사용자 역할이 활성화되었습니다.")
    activate_user_roles.short_description = "사용자 역할 활성화"
    
    def deactivate_user_roles(self, request, queryset):
        for user_role in queryset:
            user_role.deactivate("관리자에 의한 일괄 비활성화")
        self.message_user(request, f"{queryset.count()}개 사용자 역할이 비활성화되었습니다.")
    deactivate_user_roles.short_description = "사용자 역할 비활성화"


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'action', 'resource_type', 'is_successful', 
        'used_role', 'ip_address', 'created_at'
    ]
    list_filter = [
        'action', 'resource_type', 'is_successful', 'created_at'
    ]
    search_fields = [
        'user__name', 'resource_type', 'resource_id', 
        'error_message', 'ip_address'
    ]
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['user', 'used_role', 'used_permission']
    
    fieldsets = (
        ('접근 정보', {
            'fields': ('id', 'user', 'action', 'resource_type', 'resource_id')
        }),
        ('결과', {
            'fields': ('is_successful', 'error_message')
        }),
        ('권한 정보', {
            'fields': ('used_role', 'used_permission')
        }),
        ('요청 정보', {
            'fields': ('ip_address', 'user_agent', 'request_path', 'request_method', 'session_key'),
            'classes': ('collapse',)
        }),
        ('메타데이터', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'used_role', 'used_permission'
        )
    
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False  # 접근 로그는 직접 생성하지 않음
    
    def has_change_permission(self, request, obj=None):
        return False  # 접근 로그는 수정하지 않음


@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'policy_type', 'is_active', 'is_enforced', 
        'applies_to_all', 'effective_date', 'expiry_date'
    ]
    list_filter = [
        'policy_type', 'is_active', 'is_enforced', 
        'applies_to_all', 'effective_date'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['created_by']
    filter_horizontal = ['target_roles']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('id', 'name', 'description', 'policy_type')
        }),
        ('정책 설정', {
            'fields': ('settings',)
        }),
        ('적용 범위', {
            'fields': ('applies_to_all', 'target_roles', 'target_departments')
        }),
        ('상태 및 기간', {
            'fields': ('is_active', 'is_enforced', 'effective_date', 'expiry_date')
        }),
        ('메타데이터', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')
    
    actions = ['activate_policies', 'deactivate_policies']
    
    def activate_policies(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count}개 정책이 활성화되었습니다.")
    activate_policies.short_description = "정책 활성화"
    
    def deactivate_policies(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count}개 정책이 비활성화되었습니다.")
    deactivate_policies.short_description = "정책 비활성화"


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'audit_type', 'action', 'target_user', 
        'risk_level', 'ip_address', 'created_at'
    ]
    list_filter = [
        'audit_type', 'risk_level', 'created_at'
    ]
    search_fields = [
        'user__name', 'target_user__name', 'action', 
        'description', 'ip_address'
    ]
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['user', 'target_user']
    
    fieldsets = (
        ('감사 정보', {
            'fields': ('id', 'audit_type', 'action', 'description')
        }),
        ('관련 사용자', {
            'fields': ('user', 'target_user')
        }),
        ('변경 내용', {
            'fields': ('old_value', 'new_value')
        }),
        ('위험도 및 요청 정보', {
            'fields': ('risk_level', 'ip_address', 'user_agent')
        }),
        ('메타데이터', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'target_user'
        )
    
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False  # 감사 추적은 직접 생성하지 않음
    
    def has_change_permission(self, request, obj=None):
        return False  # 감사 추적은 수정하지 않음
