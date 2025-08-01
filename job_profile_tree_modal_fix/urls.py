from django.urls import path
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # 메인 트리맵 (루트 경로)
    path('', views.JobTreeView.as_view(), name='tree'),
    
    # API 엔드포인트
    path('api/job-tree-data/', views.job_tree_data_api, name='tree_data_api'),
    path('api/job-detail/<uuid:job_role_id>/', views.job_detail_api, name='job_detail_api'),
    path('api/job-profiles/<uuid:job_role_id>/delete/', views.job_profile_delete_api, name='delete_api'),
    
    # 편집/생성 페이지
    path('job-profiles/<uuid:job_role_id>/edit/', views.job_profile_edit, name='edit'),
    path('job-profiles/create/', views.job_profile_create, name='create'),
]
