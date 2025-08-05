from django.db import models
from django.contrib.auth.models import User, Group, Permission
from employees.models import Employee
from django.contrib.contenttypes.models import ContentType

class HRRole(models.Model):
    """HR 시스템 역할"""
    ROLE_CHOICES = [
        ('HR_ADMIN', 'HR 관리자'),
        ('HR_MANAGER', 'HR 매니저'),
        ('DEPT_HEAD', '부서장'),
        ('TEAM_LEADER', '팀장'),
        ('EMPLOYEE', '일반 직원'),
        ('EXECUTIVE', '임원'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField()
    permissions = models.ManyToManyField(Permission, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'HR 역할'
        verbose_name_plural = 'HR 역할'
    
    def __str__(self):
        return self.get_name_display()

class EmployeeRole(models.Model):
    """직원별 역할 할당"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    role = models.ForeignKey(HRRole, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['employee', 'role']
        verbose_name = '직원 역할'
        verbose_name_plural = '직원 역할'
    
    def __str__(self):
        return f"{self.employee.name} - {self.role.get_name_display()}"

class DataAccessRule(models.Model):
    """데이터 접근 규칙"""
    ACCESS_LEVEL_CHOICES = [
        ('SELF', '본인 데이터만'),
        ('TEAM', '팀 데이터'),
        ('DEPT', '부서 데이터'),
        ('COMPANY', '전사 데이터'),
    ]
    
    role = models.ForeignKey(HRRole, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES)
    can_view = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['role', 'model_name']
        verbose_name = '데이터 접근 규칙'
        verbose_name_plural = '데이터 접근 규칙'
    
    def __str__(self):
        return f"{self.role.get_name_display()} - {self.model_name} ({self.get_access_level_display()})"

class AuditLog(models.Model):
    """감사 로그"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField(null=True)
    object_repr = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    changes = models.JSONField(null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = '감사 로그'
        verbose_name_plural = '감사 로그'
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
