from django.urls import path
from . import views

app_name = 'ai_insights'

urlpatterns = [
    path('', views.executive_dashboard, name='dashboard'),
    path('api/metrics/', views.get_metrics, name='get_metrics'),
]