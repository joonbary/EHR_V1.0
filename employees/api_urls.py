from django.urls import path
from .api_views import (
    EmployeeListCreateAPIView,
    EmployeeDetailAPIView,
    employee_retire_view,
    employee_statistics_view,
    employee_managers_view,
    employee_organization_tree_view,
)

app_name = 'employees_api'

urlpatterns = [
    # 직원 CRUD API
    path('', EmployeeListCreateAPIView.as_view(), name='employee-list-create'),
    path('<int:pk>/', EmployeeDetailAPIView.as_view(), name='employee-detail'),
    path('<int:pk>/retire/', employee_retire_view, name='employee-retire'),
    
    # 직원 관련 정보 API
    path('statistics/', employee_statistics_view, name='employee-statistics'),
    path('managers/', employee_managers_view, name='employee-managers'),
    path('organization-tree/', employee_organization_tree_view, name='employee-organization-tree'),
]