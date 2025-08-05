"""
주간 인력현황 관리 URL Configuration
"""

from django.urls import path
from . import api_views_workforce

app_name = 'workforce_api'

urlpatterns = [
    # 파일 업로드
    path('upload/snapshot/', api_views_workforce.upload_workforce_snapshot, name='upload_snapshot'),
    path('upload/join-leave/', api_views_workforce.upload_join_leave, name='upload_join_leave'),
    
    # 데이터 조회
    path('summary/', api_views_workforce.get_workforce_summary, name='summary'),
    path('trend/', api_views_workforce.get_workforce_trend, name='trend'),
    path('changes/', api_views_workforce.get_workforce_changes, name='changes'),
]