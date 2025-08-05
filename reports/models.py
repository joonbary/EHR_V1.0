from django.db import models
from django.contrib.auth.models import User
import json

class ReportTemplate(models.Model):
    """리포트 템플릿"""
    REPORT_TYPES = [
        ('EMPLOYEE_LIST', '직원 명부'),
        ('EVALUATION_SUMMARY', '평가 결과 요약'),
        ('COMPENSATION_ANALYSIS', '보상 분석'),
        ('PROMOTION_CANDIDATES', '승진 대상자'),
        ('DEPARTMENT_STATISTICS', '부서별 통계'),
        ('ANNUAL_HR_REPORT', '연간 HR 리포트'),
    ]
    
    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField()
    parameters = models.JSONField(default=dict)  # 필터 조건 등
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class ReportGeneration(models.Model):
    """리포트 생성 이력"""
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to='reports/', null=True, blank=True)
    parameters_used = models.JSONField()
    record_count = models.IntegerField()
    file_format = models.CharField(max_length=10)  # excel, pdf, csv
    
    def __str__(self):
        return f"{self.template.name} - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"
