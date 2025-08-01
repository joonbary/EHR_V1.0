"""
성장레벨 인증 URL 패턴
"""

from django.urls import path
from .certification_api import (
    GrowthLevelCertificationCheckAPI,
    MyGrowthLevelStatusAPI,
    GrowthLevelCertificationApplyAPI,
    GrowthLevelProgressAPI
)

app_name = 'certifications'

urlpatterns = [
    # API 엔드포인트
    path('api/growth-level-certification-check/', 
         GrowthLevelCertificationCheckAPI.as_view(), 
         name='growth_level_certification_check'),
    
    path('api/my-growth-level-status/', 
         MyGrowthLevelStatusAPI.as_view(), 
         name='my_growth_level_status'),
    
    path('api/growth-level-certification-apply/', 
         GrowthLevelCertificationApplyAPI.as_view(), 
         name='growth_level_certification_apply'),
    
    path('api/growth-level-progress/', 
         GrowthLevelProgressAPI.as_view(), 
         name='growth_level_progress'),
]