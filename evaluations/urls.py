from django.urls import path
from . import views

app_name = 'evaluations'

urlpatterns = [
    path('', views.evaluation_dashboard, name='dashboard'),
    path('contribution/<int:employee_id>/', views.contribution_evaluation, name='contribution_evaluation'),
    path('expertise/<int:employee_id>/', views.expertise_evaluation, name='expertise_evaluation'),
    path('impact/<int:employee_id>/', views.impact_evaluation, name='impact_evaluation'),
    path('calculate-score/', views.calculate_score_ajax, name='calculate_score_ajax'),
] 