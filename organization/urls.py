from django.urls import path, include
from . import views

app_name = 'organization'

urlpatterns = [
    # 대시보드
    path('', views.organization_dashboard, name='dashboard'),
    
    # 부서 관리
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<uuid:department_id>/', views.department_detail, name='department_detail'),
    
    # 직위 관리
    path('positions/', views.position_list, name='position_list'),
    path('positions/<int:position_id>/', views.position_detail, name='position_detail'),
    
    # 조직도
    path('chart/', views.organization_chart, name='organization_chart'),
    
    # 인사이동
    path('transfers/', views.transfer_list, name='transfer_list'),
    path('transfers/create/', views.transfer_create, name='transfer_create'),
    path('transfers/<int:transfer_id>/', views.transfer_detail, name='transfer_detail'),
    path('transfers/<int:transfer_id>/approve/', views.transfer_approve, name='transfer_approve'),
    
    # 팀 배치
    path('assignments/', views.team_assignment_list, name='team_assignment_list'),
    
    # Enhanced Organization API
    path('api/org/', include('organization.api_urls')),
    
    # Legacy API
    path('api/departments/<uuid:department_id>/employees/', views.api_department_employees, name='api_department_employees'),
    path('api/organization-tree/', views.api_organization_tree, name='api_organization_tree'),
]