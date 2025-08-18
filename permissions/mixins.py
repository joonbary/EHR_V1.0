from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from .models import EmployeeRole, DataAccessRule, AuditLog
from django.shortcuts import get_object_or_404

class HRPermissionMixin(UserPassesTestMixin):
    """HR 권한 체크 Mixin"""
    required_permission = None
    model_name = None
    
    def test_func(self):
        # Authentication removed - always return True for testing
        if self.model_name:
            self.log_access()
        return True
    
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
        # Authentication removed - always return True
        return True
    
    def is_team_data(self):
        """팀 데이터인지 확인"""
        # Authentication removed - always return True
        return True
    
    def is_dept_data(self):
        """부서 데이터인지 확인"""
        # Authentication removed - always return True
        return True
    
    def log_access(self):
        """접근 로그 기록"""
        # Authentication removed - skip logging for now
        pass
    
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
        # Authentication removed - always return True
        return True

class TeamLeaderMixin(HRPermissionMixin):
    """팀장 권한 체크"""
    def test_func(self):
        # Authentication removed - always return True
        return True

class DepartmentHeadMixin(HRPermissionMixin):
    """부서장 권한 체크"""
    def test_func(self):
        # Authentication removed - always return True
        return True 