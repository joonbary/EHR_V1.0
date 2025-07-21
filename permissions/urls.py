from django.urls import path
from . import views

app_name = 'permissions'

urlpatterns = [
    path('', views.PermissionDashboardView.as_view(), name='dashboard'),
    path('roles/', views.RoleManagementView.as_view(), name='role_management'),
    path('assign/', views.AssignRoleView.as_view(), name='assign_role'),
    path('revoke/<int:pk>/', views.RevokeRoleView.as_view(), name='revoke_role'),
    path('audit/', views.AuditLogView.as_view(), name='audit_log'),
] 