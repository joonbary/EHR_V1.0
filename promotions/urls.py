from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('', views.promotion_dashboard, name='dashboard'),
    path('requests/', views.promotion_request_list, name='request_list'),
    path('requests/<int:request_id>/', views.promotion_request_detail, name='request_detail'),
    path('requests/create/<int:employee_id>/', views.create_promotion_request, name='create_request'),
    path('transfers/', views.job_transfer_list, name='transfer_list'),
    path('transfers/create/', views.create_job_transfer, name='create_transfer'),
    path('organization/', views.organization_chart, name='organization_chart'),
    path('analytics/', views.promotion_analytics, name='analytics'),
] 