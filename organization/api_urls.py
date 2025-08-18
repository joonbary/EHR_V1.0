"""
Organization API URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    OrgUnitViewSet, OrgScenarioViewSet, 
    WhatIfAnalysisViewSet, ExcelIOViewSet
)

# Create router
router = DefaultRouter()
router.register(r'units', OrgUnitViewSet, basename='orgunit')
router.register(r'scenarios', OrgScenarioViewSet, basename='orgscenario')

# Custom ViewSets
whatif_list = {
    'post': 'reassign'
}

excel_list = {
    'post': 'import_excel',
    'get': 'export_excel'
}

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # What-if Analysis
    path('whatif/reassign/', 
         WhatIfAnalysisViewSet.as_view({'post': 'reassign'}), 
         name='whatif-reassign'),
    
    # Excel IO
    path('io/import/', 
         ExcelIOViewSet.as_view({'post': 'import_excel'}), 
         name='excel-import'),
    path('io/export/', 
         ExcelIOViewSet.as_view({'get': 'export_excel'}), 
         name='excel-export'),
]