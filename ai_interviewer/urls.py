"""
AI Interviewer URL Configuration
"""
from django.urls import path
from . import views

app_name = 'ai_interviewer'

urlpatterns = [
    # 메인 대시보드
    path('', views.InterviewDashboard.as_view(), name='interview_dashboard'),
    
    # 면접 세션 관리
    path('sessions/', views.InterviewSessionListView.as_view(), name='session_list'),
    path('session/<uuid:session_id>/', views.InterviewSessionDetailView.as_view(), name='session_detail'),
    path('live/<uuid:session_id>/', views.LiveInterviewView.as_view(), name='live_interview'),
    
    # 템플릿 관리
    path('templates/', views.InterviewTemplateListView.as_view(), name='template_list'),
    
    # API 엔드포인트
    path('api/create-session/', views.api_create_session, name='api_create_session'),
    path('api/start/<uuid:session_id>/', views.api_start_interview, name='api_start_interview'),
    path('api/submit/<uuid:session_id>/', views.api_submit_response, name='api_submit_response'),
    path('api/status/<uuid:session_id>/', views.api_session_status, name='api_session_status'),
    path('api/pause/<uuid:session_id>/', views.api_pause_interview, name='api_pause_interview'),
    path('api/resume/<uuid:session_id>/', views.api_resume_interview, name='api_resume_interview'),
    path('api/statistics/', views.api_interview_statistics, name='api_interview_statistics'),
    path('api/insights/<uuid:session_id>/', views.api_candidate_insights, name='api_candidate_insights'),
    path('api/generate-templates/', views.api_generate_templates, name='api_generate_templates'),
]