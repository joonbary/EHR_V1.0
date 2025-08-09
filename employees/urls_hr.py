"""
HR Dashboard URL Configuration
"""

from django.urls import path, include
from . import api_views_hr, api_views_outsourced, api_views_monthly, api_views_full_workforce, api_views_monthly_download_simple, api_views_overseas

app_name = 'hr_api'

urlpatterns = [
    # 파일 업로드
    path('upload/', api_views_hr.upload_hr_file, name='upload_file'),
    path('task/<str:task_id>/status/', api_views_hr.get_task_status, name='task_status'),
    
    # 직원 관리
    path('employees/', api_views_hr.get_employees, name='employees'),
    path('contractors/', api_views_hr.get_contractors, name='contractors'),
    
    # 대시보드
    path('dashboard/summary/', api_views_hr.get_dashboard_summary, name='dashboard_summary'),
    path('dashboard/trend/', api_views_hr.get_monthly_trend, name='monthly_trend'),
    
    # 외주인력 현황관리
    path('outsourced/upload/', api_views_outsourced.upload_outsourced_file, name='upload_outsourced'),
    path('outsourced/current/', api_views_outsourced.get_outsourced_current, name='outsourced_current'),
    path('outsourced/trend/', api_views_outsourced.get_outsourced_trend, name='outsourced_trend'),
    path('outsourced/diff/', api_views_outsourced.get_outsourced_diff, name='outsourced_diff'),
    
    # 주간 인력현황 관리
    path('workforce/', include('employees.urls_workforce')),
    
    # 월간 인력현황
    path('monthly-workforce/', api_views_monthly.get_monthly_workforce_data, name='monthly_workforce_data'),
    path('monthly-workforce/upload/', api_views_monthly.upload_monthly_workforce_file, name='upload_monthly_workforce'),
    path('monthly-workforce/download/', api_views_monthly_download_simple.download_monthly_workforce_excel, name='download_monthly_workforce'),
    
    # 전체 인력현황 (emp_upload.xlsx 기반)
    path('full-workforce/', api_views_full_workforce.get_full_workforce_data, name='full_workforce_data'),
    
    # 해외 인력현황
    path('overseas/upload/', api_views_overseas.upload_overseas_file, name='upload_overseas'),
    path('overseas/current/', api_views_overseas.get_overseas_current, name='overseas_current'),
    path('overseas/months/', api_views_overseas.get_overseas_months, name='overseas_months'),
]