from django.urls import path
from django.http import JsonResponse
from . import views

app_name = 'job_profiles'

def health_check(request):
    """Health check endpoint"""
    try:
        from .models import JobCategory, JobType, JobRole, JobProfile
        categories = JobCategory.objects.count()
        types = JobType.objects.count()
        roles = JobRole.objects.count()
        profiles = JobProfile.objects.count()
        
        # 실제 데이터 샘플
        sample_categories = list(JobCategory.objects.values('name')[:5])
        
        return JsonResponse({
            'status': 'ok', 
            'counts': {
                'categories': categories,
                'types': types,
                'roles': roles,
                'profiles': profiles
            },
            'sample_categories': sample_categories
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),
    
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