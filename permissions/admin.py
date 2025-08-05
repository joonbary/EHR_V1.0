from django.contrib import admin
from .models import HRRole, EmployeeRole, DataAccessRule, AuditLog

@admin.register(HRRole)
class HRRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    list_filter = ['name']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']

@admin.register(EmployeeRole)
class EmployeeRoleAdmin(admin.ModelAdmin):
    list_display = ['employee', 'role', 'assigned_by', 'assigned_at', 'is_active']
    list_filter = ['role', 'is_active', 'assigned_at']
    search_fields = ['employee__name', 'employee__email']
    date_hierarchy = 'assigned_at'

@admin.register(DataAccessRule)
class DataAccessRuleAdmin(admin.ModelAdmin):
    list_display = ['role', 'model_name', 'access_level', 'can_view', 'can_edit', 'can_delete', 'can_approve']
    list_filter = ['role', 'access_level', 'can_view', 'can_edit', 'can_delete', 'can_approve']
    search_fields = ['role__name', 'model_name']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'timestamp', 'ip_address']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'model_name', 'object_repr']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_repr', 'timestamp', 'ip_address', 'user_agent', 'changes']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
