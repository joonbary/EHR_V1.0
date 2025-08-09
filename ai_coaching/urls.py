"""
AI Coaching URLs - AI 실시간 코칭 어시스턴트 URL 설정
"""
from django.urls import path
from django.http import HttpResponse
from . import views

app_name = 'ai_coaching'

# 테스트 뷰
def test_view(request):
    return HttpResponse("AI Coaching is working!")

urlpatterns = [
    # 테스트 URL
    path('test/', test_view, name='test'),
    
    # 대시보드
    path('', views.CoachingDashboardView.as_view(), name='dashboard'),
    
    # 세션 관리
    path('start/', views.StartCoachingView.as_view(), name='start_session'),
    path('session/<uuid:session_id>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('session/<uuid:session_id>/message/', views.SendMessageView.as_view(), name='send_message'),
    path('session/<uuid:session_id>/end/', views.EndSessionView.as_view(), name='end_session'),
    
    # 목표 관리
    path('session/<uuid:session_id>/goal/', views.CreateGoalView.as_view(), name='create_goal'),
    path('goals/', views.GoalsListView.as_view(), name='goals_list'),
    
    # 액션 아이템
    path('session/<uuid:session_id>/action-item/', views.CreateActionItemView.as_view(), name='create_action_item'),
    
    # 피드백
    path('session/<uuid:session_id>/feedback/', views.SubmitFeedbackView.as_view(), name='submit_feedback'),
    
    # 기록 및 분석
    path('history/', views.SessionHistoryView.as_view(), name='session_history'),
]