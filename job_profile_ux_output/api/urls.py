
from django.urls import path
from . import job_tree_api

urlpatterns = [
    path('api/job-tree/', job_tree_api.job_tree_api, name='job_tree_api'),
    path('api/job-profiles/<uuid:job_role_id>/', job_tree_api.job_profile_detail_api, name='job_profile_detail'),
    path('api/job-search/', job_tree_api.job_search_api, name='job_search'),
    path('api/job-statistics/', job_tree_api.job_statistics_api, name='job_statistics'),
]
