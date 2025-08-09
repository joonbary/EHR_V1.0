"""
AI Quick Win URL 설정
"""
from django.urls import path
from .views import (
    AIQuickWinDashboardView,
    AIQuickWinAPIView,
    ai_chatbot_view,
    ai_leader_assistant_view
)

app_name = 'ai_quickwin'

urlpatterns = [
    # 메인 대시보드
    path('', AIQuickWinDashboardView.as_view(), name='dashboard'),
    path('dashboard/', AIQuickWinDashboardView.as_view(), name='main_dashboard'),
    
    # API 엔드포인트
    path('api/stats/', AIQuickWinAPIView.as_view(), name='api_stats'),
    
    # 개별 AI 기능
    path('chatbot/', ai_chatbot_view, name='chatbot'),
    path('leader-assistant/', ai_leader_assistant_view, name='leader_assistant'),
]