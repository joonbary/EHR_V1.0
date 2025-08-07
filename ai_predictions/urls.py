"""
AI Predictions URL Configuration
"""
from django.urls import path
from . import views

app_name = 'ai_predictions'

urlpatterns = [
    # 메인 대시보드
    path('', views.TurnoverRiskDashboard.as_view(), name='turnover_dashboard'),
    
    # 개별 직원 상세
    path('employee/<int:employee_id>/', views.EmployeeRiskDetailView.as_view(), name='employee_risk_detail'),
    
    # 유지 계획
    path('retention-plans/', views.RetentionPlanListView.as_view(), name='retention_plans'),
    
    # API 엔드포인트
    path('api/analyze/<int:employee_id>/', views.api_analyze_employee_risk, name='api_analyze_employee'),
    path('api/high-risk/', views.api_high_risk_employees, name='api_high_risk_employees'),
    path('api/batch-analyze/', views.api_batch_analyze, name='api_batch_analyze'),
    path('api/statistics/', views.api_risk_statistics, name='api_risk_statistics'),
    path('api/alert/<int:alert_id>/acknowledge/', views.api_acknowledge_alert, name='api_acknowledge_alert'),
]