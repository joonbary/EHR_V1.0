"""
HR 관리 시스템 URL 설정
"""

from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # 대시보드
    path('', views.hr_dashboard, name='dashboard'),
    
    # 직급/직군 관리
    path('job-structure/', views.job_structure, name='job_structure'),
    
    # 급여 관리
    path('salary/', views.salary_management, name='salary_management'),
    path('salary/<int:employee_id>/', views.employee_salary_detail, name='employee_salary_detail'),
    
    # 교육/자격증
    path('education/', views.education_management, name='education_management'),
    
    # 평가 관리
    path('evaluation/', views.evaluation_list, name='evaluation_list'),
    
    # 복리후생
    path('benefits/', views.benefits_management, name='benefits_management'),
]