from django.urls import path
from . import views, api_views

app_name = 'compensation'

urlpatterns = [
    # 웹 페이지 URLs
    path('', views.compensation_dashboard, name='dashboard'),
    path('dashboard/', views.compensation_dashboard, name='dashboard_alt'),
    path('calculator/', views.compensation_calculator, name='calculator'),
    path('reports/', views.compensation_reports, name='reports'),
    path('settings/', views.compensation_settings, name='settings'),
    
    # 기존 API URLs
    path('api/summary/', views.api_compensation_summary, name='api_summary'),
    path('api/grade-distribution/', views.api_grade_distribution, name='api_grade_distribution'),
    path('api/level-comparison/', views.api_level_comparison, name='api_level_comparison'),
    path('api/job-type-analysis/', views.api_job_type_analysis, name='api_job_type_analysis'),
    
    # 새로운 API URLs (작업지시서 기반)
    path('api/employee/<int:employee_id>/statement/', api_views.get_compensation_statement, name='api_statement'),
    path('api/kpi/mix-ratio/', api_views.get_compensation_mix_ratio, name='api_mix_ratio'),
    path('api/kpi/variance-alerts/', api_views.get_variance_alerts, name='api_variance_alerts'),
    path('api/snapshot/run/', api_views.run_compensation_snapshot, name='api_snapshot_run'),
    path('api/positions/allowance/', api_views.get_position_allowance, name='api_position_allowance'),
    path('api/employees/<int:employee_id>/position/assign/', api_views.assign_employee_position, name='api_position_assign'),
    path('api/dashboard-new/', api_views.get_compensation_dashboard, name='api_dashboard_new'),
    path('api/real-data/', api_views.get_real_compensation_data, name='api_real_data'),
] 