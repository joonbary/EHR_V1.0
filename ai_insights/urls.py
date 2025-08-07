"""
AI Insights URL Configuration
"""
from django.urls import path
from . import views

app_name = 'ai_insights'

urlpatterns = [
    # 메인 대시보드
    path('', views.AIExecutiveDashboard.as_view(), name='executive_dashboard'),
    
    # API 엔드포인트
    path('api/insights/daily/', views.api_daily_insights, name='api_daily_insights'),
    path('api/actions/', views.api_action_items, name='api_action_items'),
]