from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from .models import EmployeeRole, DataAccessRule, AuditLog
from django.shortcuts import get_object_or_404

class HRPermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    """HR 권한 체크 Mixin"""
    required_permission = None
    model_name = None
    
    def test_func(self):
        if not hasattr(self.request.user, 'employee'):
            return False
            
        employee = self.request.user.employee
        roles = EmployeeRole.objects.filter(
            employee=employee, 
            is_active=True
        ).values_list('role__name', flat=True)
        
        # HR 관리자는 모든 권한
        if 'HR_ADMIN' in roles:
            return True
            
        # 모델별 접근 권한 체크
        if self.model_name:
            access_rules = DataAccessRule.objects.filter(
                role__name__in=roles,
                model_name=self.model_name
            )
            
            for rule in access_rules:
                if self.check_access_level(rule):
                    self.log_access()
                    return True
                    
        return False
    
    def check_access_level(self, rule):
        """데이터 접근 레벨 체크"""
        if rule.access_level == 'SELF':
            # 본인 데이터만 접근 가능
            return self.is_own_data()
        elif rule.access_level == 'TEAM':
            # 같은 팀 데이터 접근 가능
            return self.is_team_data()
        elif rule.access_level == 'DEPT':
            # 같은 부서 데이터 접근 가능
            return self.is_dept_data()
        elif rule.access_level == 'COMPANY':
            # 전사 데이터 접근 가능
            return True
            
        return False
    
    def is_own_data(self):
        """본인 데이터인지 확인"""
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            return hasattr(obj, 'employee') and obj.employee == self.request.user.employee
        return True
    
    def is_team_data(self):
        """팀 데이터인지 확인"""
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            if hasattr(obj, 'employee'):
                return obj.employee.manager == self.request.user.employee
        return True
    
    def is_dept_data(self):
        """부서 데이터인지 확인"""
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            if hasattr(obj, 'employee'):
                return obj.employee.department == self.request.user.employee.department
        return True
    
    def log_access(self):
        """접근 로그 기록"""
        AuditLog.objects.create(
            user=self.request.user,
            action=self.request.method,
            model_name=self.model_name or 'Unknown',
            object_id=self.kwargs.get('pk'),
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def get_client_ip(self):
        """클라이언트 IP 주소 가져오기"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class EmployeeSelfOnlyMixin(HRPermissionMixin):
    """본인 데이터만 접근 가능"""
    def test_func(self):
        if not hasattr(self.request.user, 'employee'):
            return False
        obj = self.get_object()
        return hasattr(obj, 'employee') and obj.employee == self.request.user.employee

class TeamLeaderMixin(HRPermissionMixin):
    """팀장 권한 체크"""
    def test_func(self):
        if not hasattr(self.request.user, 'employee'):
            return False
        employee = self.request.user.employee
        return employee.position in ['팀장', '부서장', '본부장', '사장']

class DepartmentHeadMixin(HRPermissionMixin):
    """부서장 권한 체크"""
    def test_func(self):
        if not hasattr(self.request.user, 'employee'):
            return False
        employee = self.request.user.employee
        return employee.position in ['부서장', '본부장', '사장'] 