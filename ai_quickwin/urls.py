"""
AI Quick Win URL 설정
"""
from django.urls import path
from .views import (
    AIQuickWinDashboardView,
    AIQuickWinAPIView,
    ai_chatbot_view,
    ai_leader_assistant_view,
    EmployeeSyncAPIView,
    InterviewToCoachingAPIView,
    ComprehensiveReportAPIView,
    ModuleIntegrationStatusAPIView,
    batch_sync_employees
)

app_name = 'ai_quickwin'

urlpatterns = [
    # 메인 대시보드
    path('', AIQuickWinDashboardView.as_view(), name='dashboard'),
    path('dashboard/', AIQuickWinDashboardView.as_view(), name='main_dashboard'),
    
    # API 엔드포인트
    path('api/stats/', AIQuickWinAPIView.as_view(), name='api_stats'),
    
    # 오케스트레이터 API 엔드포인트
    path('api/sync/employee/<int:employee_id>/', EmployeeSyncAPIView.as_view(), name='api_sync_employee'),
    path('api/sync/batch/', batch_sync_employees, name='api_sync_batch'),
    path('api/interview-to-coaching/', InterviewToCoachingAPIView.as_view(), name='api_interview_to_coaching'),
    path('api/report/<int:employee_id>/', ComprehensiveReportAPIView.as_view(), name='api_comprehensive_report'),
    path('api/integration-status/', ModuleIntegrationStatusAPIView.as_view(), name='api_integration_status'),
    
    # 개별 AI 기능
    path('chatbot/', ai_chatbot_view, name='chatbot'),
    path('leader-assistant/', ai_leader_assistant_view, name='leader_assistant'),
]