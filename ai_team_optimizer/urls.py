"""
AI Team Optimizer URLs - AI 팀 조합 최적화 URL 패턴
"""
from django.urls import path
from django.http import HttpResponse
from . import views

app_name = 'ai_team_optimizer'

# 테스트 뷰
def test_view(request):
    return HttpResponse("AI Team Optimizer is working!")

urlpatterns = [
    # 테스트 URL
    path('test/', test_view, name='test'),
    
    # 대시보드
    path('', views.TeamOptimizerDashboardView.as_view(), name='dashboard'),
    
    # 프로젝트 관리
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/<int:project_id>/', views.ProjectDetailView.as_view(), name='project_detail'),
    
    # 팀 구성 관리  
    path('compositions/<int:composition_id>/', views.TeamCompositionDetailView.as_view(), name='composition_detail'),
    
    # API 엔드포인트
    path('api/optimize/<int:project_id>/', views.OptimizeTeamView.as_view(), name='optimize_team'),
    path('api/skill-match/<int:project_id>/', views.SkillMatchView.as_view(), name='skill_match'),
    path('api/approve/<int:composition_id>/', views.ApproveCompositionView.as_view(), name='approve_composition'),
    path('api/employees/availability/', views.EmployeeAvailabilityView.as_view(), name='employee_availability'),
    path('api/projects/<int:project_id>/skills/', views.ProjectSkillAnalysisView.as_view(), name='project_skill_analysis'),
    
    # 분석 대시보드
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('templates/', views.TeamTemplatesView.as_view(), name='templates'),
]