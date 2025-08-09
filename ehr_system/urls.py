from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from .views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 인증 URL - 제거됨
    
    # 메인 대시보드
    path('', DashboardView.as_view(), name='home'),
    path('dashboard/', include('dashboard.urls')),  # 대시보드 하위 메뉴
    
    # 앱별 URL
    path('core/', include('core.urls')),
    path('job-profiles/', include('job_profiles.urls')),
    path('employees/', include('employees.urls')),
    path('evaluations/', include('evaluations.urls')),
    path('compensation/', include('compensation.urls')),
    path('promotions/', include('promotions.urls')),
    path('selfservice/', include('selfservice.urls')),
    
    # 경영진 대시보드
    path('leader-kpi-dashboard/', TemplateView.as_view(template_name='dashboards/leader_kpi_dashboard.html'), name='leader_kpi_dashboard'),
    path('workforce-comp-dashboard/', TemplateView.as_view(template_name='dashboards/workforce_comp_dashboard.html'), name='workforce_comp_dashboard'),
    path('skillmap-dashboard/', TemplateView.as_view(template_name='skillmap/dashboard.html'), name='skillmap_dashboard'),
    
    # AI 도구
    path('ai-chatbot/', TemplateView.as_view(template_name='ai/chatbot.html'), name='ai_chatbot'),
    path('leader-ai-assistant/', TemplateView.as_view(template_name='ai/leader_assistant.html'), name='leader_ai_assistant'),
    
    # 채용관리
    path('recruitment/', include('recruitment.urls')),
    
    # 교육훈련 및 자격증
    path('trainings/', include('trainings.urls')),
    path('certifications/', include('certifications.urls')),
    
    # AIRISS (AI 기반 HR 지원)
    path('airiss/', include('airiss.urls')),
    
    # AI 인사이트 대시보드
    path('ai-insights/', include('ai_insights.urls')),
    
    # AI 이직 위험도 분석
    path('ai-predictions/', include('ai_predictions.urls')),
    
    # AI 면접관
    path('ai-interviewer/', include('ai_interviewer.urls')),
    
    # AI 팀 조합 최적화
    path('ai-team-optimizer/', include('ai_team_optimizer.urls')),
    
    # AI Quick Win 메뉴들
    path('ai/', include('ai_quickwin.urls')),  # AI Quick Win 통합 대시보드
    path('ai-coaching/', include('ai_coaching.urls')),
    path('ai-team-optimizer/', include('ai_team_optimizer.urls')),
    path('ai-insights/', include('ai_insights.urls')),
    path('ai-predictions/', include('ai_predictions.urls')),
    path('ai-interviewer/', include('ai_interviewer.urls')),
    
    # 조직관리
    path('organization/', include('organization.urls')),
    
    # 보고서
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)