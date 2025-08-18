from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import HRRole, EmployeeRole, AuditLog
from .mixins import HRPermissionMixin

class RoleManagementView(HRPermissionMixin, ListView):
    """역할 관리"""
    model = HRRole
    template_name = 'permissions/role_management.html'
    model_name = 'HRRole'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_roles'] = EmployeeRole.objects.select_related(
            'employee', 'role'
        ).filter(is_active=True)
        return context

class AssignRoleView(HRPermissionMixin, CreateView):
    """역할 할당"""
    model = EmployeeRole
    fields = ['employee', 'role']
    template_name = 'permissions/assign_role.html'
    model_name = 'EmployeeRole'
    success_url = reverse_lazy('permissions:role_management')
    
    def form_valid(self, form):
        form.instance.assigned_by = self.request.user
        messages.success(self.request, '역할이 성공적으로 할당되었습니다.')
        return super().form_valid(form)

class RevokeRoleView(HRPermissionMixin, DeleteView):
    """역할 해제"""
    model = EmployeeRole
    model_name = 'EmployeeRole'
    
    def delete(self, request, *args, **kwargs):
        role = self.get_object()
        role.is_active = False
        role.save()
        return JsonResponse({'status': 'success'})

class AuditLogView(HRPermissionMixin, ListView):
    """감사 로그 조회"""
    model = AuditLog
    template_name = 'permissions/audit_log.html'
    paginate_by = 50
    model_name = 'AuditLog'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 필터링
        user = self.request.GET.get('user')
        action = self.request.GET.get('action')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if user:
            queryset = queryset.filter(user__username__icontains=user)
        if action:
            queryset = queryset.filter(action=action)
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actions'] = AuditLog.objects.values_list('action', flat=True).distinct()
        return context

class PermissionDashboardView(HRPermissionMixin, ListView):
    """권한 대시보드"""
    model = EmployeeRole
    template_name = 'permissions/dashboard.html'
    model_name = 'EmployeeRole'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 역할별 통계
        context['role_stats'] = {}
        for role in HRRole.objects.all():
            context['role_stats'][role.name] = EmployeeRole.objects.filter(
                role=role, is_active=True
            ).count()
        
        # 최근 감사 로그
        context['recent_logs'] = AuditLog.objects.select_related('user')[:10]
        
        # 부서별 권한 현황
        context['dept_permissions'] = EmployeeRole.objects.select_related(
            'employee', 'role'
        ).filter(is_active=True)
        
        return context
