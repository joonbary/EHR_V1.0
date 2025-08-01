# job_profiles/urls.py에 추가할 URL 패턴

from .views import JobProfileTreeMapView, job_tree_map_data_api, job_detail_modal_api

urlpatterns += [
    # 트리맵 뷰
    path('tree-map/', JobProfileTreeMapView.as_view(), name='tree_map'),
    
    # 트리맵 API
    path('api/tree-map-data/', job_tree_map_data_api, name='tree_map_data_api'),
    path('api/job-detail-modal/<uuid:job_role_id>/', job_detail_modal_api, name='job_detail_modal_api'),
]