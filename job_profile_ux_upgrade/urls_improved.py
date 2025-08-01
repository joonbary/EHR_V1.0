from django.urls import path
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # ESS용 (일반 직원 조회)
    path('', views.job_profile_list, name='list'),
    path('<uuid:profile_id>/', views.job_profile_detail, name='detail'),
    path('hierarchy/', views.job_hierarchy_navigation, name='hierarchy'),
    
    # 다운로드 (신규)
    path('download/', views.job_profile_download, name='download'),
    
    # 북마크 (신규)
    path('bookmark/<uuid:profile_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    
    # 관리자용
    path('admin/', views.job_profile_admin_list, name='admin_list'),
    path('admin/create/', views.job_profile_create, name='create'),
    path('admin/<uuid:profile_id>/', views.job_profile_admin_detail, name='admin_detail'),
    path('admin/<uuid:profile_id>/update/', views.job_profile_update, name='update'),
    path('admin/<uuid:profile_id>/delete/', views.job_profile_delete, name='delete'),
    
    # 일괄 작업 (신규)
    path('admin/bulk/update/', views.bulk_update_status, name='bulk_update'),
    
    # API 엔드포인트
    path('api/job-types/<uuid:category_id>/', views.get_job_types, name='get_job_types'),
    path('api/job-roles/<uuid:job_type_id>/', views.get_job_roles, name='get_job_roles'),
]
