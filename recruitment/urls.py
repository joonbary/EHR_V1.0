from django.urls import path
from . import views

app_name = 'recruitment'

urlpatterns = [
    # 대시보드
    path('', views.recruitment_dashboard, name='dashboard'),
    
    # 채용공고
    path('postings/', views.job_posting_list, name='job_posting_list'),
    path('postings/create/', views.job_posting_create, name='job_posting_create'),
    path('postings/<uuid:pk>/', views.job_posting_detail, name='job_posting_detail'),
    path('postings/<uuid:pk>/update/', views.job_posting_update, name='job_posting_update'),
    
    # 지원자
    path('applicants/create/', views.applicant_create, name='applicant_create'),
    path('applicants/<uuid:pk>/', views.applicant_detail, name='applicant_detail'),
    
    # 지원서
    path('applications/', views.application_list, name='application_list'),
    path('applications/create/', views.application_create, name='application_create'),
    path('applications/<uuid:pk>/', views.application_detail, name='application_detail'),
    path('applications/<uuid:pk>/evaluate/', views.application_evaluate, name='application_evaluate'),
    
    # 면접
    path('applications/<uuid:application_id>/interviews/create/', 
         views.interview_schedule_create, name='interview_schedule_create'),
    path('interviews/<uuid:pk>/update/', 
         views.interview_schedule_update, name='interview_schedule_update'),
    path('interviews/<uuid:pk>/evaluate/', 
         views.interview_evaluate, name='interview_evaluate'),
]