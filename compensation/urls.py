from django.urls import path
from . import views

app_name = 'compensation'

urlpatterns = [
    path('dashboard/', views.compensation_dashboard, name='dashboard'),
    path('api/summary/', views.api_compensation_summary, name='api_summary'),
    path('api/grade-distribution/', views.api_grade_distribution, name='api_grade_distribution'),
    path('api/level-comparison/', views.api_level_comparison, name='api_level_comparison'),
    path('api/job-type-analysis/', views.api_job_type_analysis, name='api_job_type_analysis'),
] 