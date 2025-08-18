from django.urls import path
from . import views_improved as views

app_name = 'job_profiles_improved'

urlpatterns = [
    # 개선된 통합 직무 체계도 뷰
    path('', views.ImprovedJobTreeUnifiedView.as_view(), name='tree_unified'),
    
    # API 엔드포인트
    path('api/tree-data/', views.improved_job_tree_data_api, name='tree_data_api'),
    path('api/job-detail/<str:job_id>/', views.improved_job_detail_api, name='job_detail_api'),
]