from django.urls import path
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # 직무체계도 트리맵 뷰
    path('', views.JobTreeMapView.as_view(), name='list'),
    
    # API 엔드포인트
    path('api/tree-map-data/', views.job_tree_map_data_api, name='tree_map_data'),
    path('api/job-detail-modal/<uuid:job_role_id>/', views.job_detail_modal_api, name='job_detail_modal'),
    
    # 편집
    path('edit/<uuid:job_role_id>/', views.job_profile_edit_view, name='edit'),
]