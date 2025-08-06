from django.urls import path
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # 새로운 직무체계도 뷰 (기본)
    path('', views.JobHierarchyView.as_view(), name='hierarchy'),
    
    # 기존 트리맵 뷰 (옵션)
    path('treemap/', views.JobTreeMapView.as_view(), name='treemap'),
    
    # API 엔드포인트
    path('api/tree-map-data/', views.job_tree_map_data_api, name='tree_map_data'),
    path('api/job-detail-modal/<uuid:job_role_id>/', views.job_detail_modal_api, name='job_detail_modal'),
    path('api/job-detail/<uuid:job_role_id>/', views.job_detail_api, name='job_detail_api'),
    
    # 편집
    path('edit/<uuid:job_role_id>/', views.job_profile_edit_view, name='edit'),
]