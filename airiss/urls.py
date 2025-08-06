from django.urls import path
from . import views

app_name = "airiss"

urlpatterns = [
    # 메인 기능
    path("executive/", views.executive_dashboard, name="executive_dashboard"),
    path("employee-analysis/all/", views.employee_analysis_all, name="employee_analysis_all"),
    path("employee/<int:employee_id>/analysis/", views.employee_analysis_detail, name="employee_analysis_detail"),
    path("msa-integration/", views.msa_integration, name="msa_integration"),
    
    # AI 분석 결과 조회
    path("analysis-results/", views.analysis_results, name="analysis_results"),
    
    # 파일 업로드
    path("file-upload/", views.file_upload, name="file_upload"),
    path("api/upload-proxy/", views.airiss_upload_proxy, name="upload_proxy"),
    
    # 더미 URL들 - base_modern.html 호환성을 위해
    path("", views.dashboard, name="dashboard"),
    path("analytics/", views.analytics, name="analytics"),
    path("predictions/", views.predictions, name="predictions"),
    path("insights/", views.insights, name="insights"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("airiss-v4-portal/", views.airiss_v4_portal, name="airiss_v4_portal"),
]
