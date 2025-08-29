from django.urls import path, include
from . import views, api_views
from .test_upload import test_upload
try:
    from . import api_talent
except ImportError:
    api_talent = None
from django.views.generic import TemplateView
from core.views import under_construction
from .views_test import test_database
from . import views_debug
from . import views_system_debug
from . import views_deployment_debug
from . import views_template_debug
from . import views_simple_debug

app_name = 'employees'

urlpatterns = [
    path('', TemplateView.as_view(template_name='employees/employee_management_revolutionary.html'), name='employee_management'),
    path('list/', views.EmployeeListView.as_view(), name='employee_list'),
    path('create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('bulk-upload/', views.BulkUploadView.as_view(), name='employee_bulk_upload'),
    path('download-template/', views.download_template, name='employee_download_template'),
    path('org-chart/', views.organization_chart, name='organization_chart'),
    path('advanced-org-chart/', views.advanced_organization_chart, name='advanced_organization_chart'),
    path('hierarchy/', views.hierarchy_organization_view, name='hierarchy_organization'),
    path('api/organization-data/', views.organization_data_api, name='organization_data_api'),
    path('api/hierarchy-data/', views.hierarchy_organization_api, name='hierarchy_organization_api'),
    
    # Advanced Org Chart APIs
    path('api/org/root', views.org_tree_api, name='org_tree_api'),
    path('api/org/node/<str:node_id>/', views.org_tree_api, name='org_node_api'),
    path('api/org/search', views.org_search_api, name='org_search_api'),
    
    # Organization Input
    path('organization/input/', views.organization_input_view, name='organization_input'),
    path('api/save-employee/', views.save_employee_api, name='save_employee'),
    path('api/bulk-upload/', views.bulk_upload_api, name='bulk_upload'),
    path('api/get-managers/', views.get_managers_api, name='get_managers'),
    
    # Organization Structure Management
    path('organization/structure/', views.organization_structure_view, name='organization_structure'),
    path('organization/upload/', views.organization_structure_upload_view, name='organization_structure_upload'),
    path('api/upload-organization-structure/', views.upload_organization_structure, name='upload_organization_structure'),
    path('api/test-upload/', test_upload, name='test_upload'),
    path('api/organization-tree/', views.get_organization_tree, name='get_organization_tree'),
    path('api/organization-stats/', views.get_organization_stats, name='get_organization_stats'),
    path('api/delete-organization-data/', views.delete_organization_data, name='delete_organization_data'),
    path('api/save-organization/', views.save_organization, name='save_organization'),
    path('download/org-sample/', views.download_org_sample, name='download_org_sample'),
    
    # Debug endpoints
    path('debug/count/', views_debug.debug_employee_count, name='debug-count'),
    path('debug/list/', views_debug.debug_employee_list, name='debug-list'),
    path('debug/context/', views_debug.debug_template_context, name='debug-context'),
    
    # REST API endpoints
    path('api/test/', test_database, name='test-database'),  # 테스트 엔드포인트
    path('api/employees/', api_views.EmployeeListCreateAPIView.as_view(), name='employee-list-create'),
    path('api/employees/<int:pk>/', api_views.EmployeeDetailAPIView.as_view(), name='employee-detail'),
    path('api/employees/<int:pk>/retire/', api_views.employee_retire_view, name='employee-retire'),
    
    path('<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    
    # 미구현 기능
    path('attendance/', under_construction, name='attendance_management'),
    
    # HR Dashboard
    path('hr/dashboard/', views.hr_dashboard_view, name='hr_dashboard'),
    path('hr/outsourced/', views.outsourced_dashboard_view, name='outsourced_dashboard'),
    path('hr/monthly/', views.monthly_workforce_view, name='monthly_workforce'),
    path('hr/full/', views.full_workforce_view, name='full_workforce'),
    path('hr/overseas/', views.overseas_workforce_view, name='overseas_workforce'),
    
    # HR Dashboard API
    path('hr/api/', include('employees.urls_hr')),
    
    # Talent Management API (AIRISS Integration)
    
    # System debug views (Railway troubleshooting)
    path('system/debug/', views_system_debug.system_debug_info, name='system_debug_info'),
    path('system/force-load/', views_system_debug.force_load_employees, name='force_load_employees'),
    
    # Deployment debug
    path('deployment/debug/', views_deployment_debug.deployment_debug, name='deployment_debug'),
    
    # Template debug
    path('template/debug/', views_template_debug.template_debug, name='template_debug'),
    path('advanced-org-chart-test/', views_template_debug.render_advanced_org_chart, name='advanced_org_chart_test'),
    path('simple/debug/', views_simple_debug.simple_debug, name='simple_debug'),
]

# 인재 관리 API URL 추가
if api_talent:
    from . import api_talent_improved
    urlpatterns += [
        path('api/talent/pool/', api_talent_improved.talent_pool_api_improved, name='talent_pool_api'),
        path('api/talent/detail/<int:employee_id>/', api_talent_improved.talent_detail_api_improved, name='talent_detail_api'),
        path('api/talent/test/', api_talent_improved.talent_pool_api_improved, name='test_talent_db'),
    ] 