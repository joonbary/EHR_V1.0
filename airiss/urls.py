from django.urls import path
from . import views

app_name = 'airiss'

urlpatterns = [
    # 메인 대시보드
    path('', views.dashboard, name='dashboard'),
    path('debug-test/', views.dashboard, name='dashboard_debug_test'),
    
    # HR 분석
    path('analytics/', views.analytics, name='analytics'),
    
    # AI 예측
    path('predictions/', views.predictions, name='predictions'),
    
    # 인사이트
    path('insights/', views.insights, name='insights'),
    
    # HR 챗봇
    path('chatbot/', views.chatbot, name='chatbot'),
    
    # AI 모델 관리
    path('train-models/', views.train_ai_models, name='train_models'),
    path('model-status/', views.model_status, name='model_status'),
    path('change-gpt-model/', views.change_gpt_model, name='change_gpt_model'),
    
    # API endpoints
    path('api/models/', views.api_get_available_models, name='api_get_models'),
    path('api/change-model/', views.api_change_model, name='api_change_model'),
    
    # AIRISS v4 포털
    path('v4/', views.airiss_v4_portal, name='airiss_v4_portal'),
    
    # 테스트 페이지
    path('test-js/', views.test_javascript, name='test_javascript'),
    path('standalone/', views.dashboard_standalone, name='dashboard_standalone'),
    path('debug/', views.debug_page, name='debug_page'),
    path('simple/', views.simple_test, name='simple_test'),
    path('test/', views.dashboard_test, name='dashboard_test'),
]