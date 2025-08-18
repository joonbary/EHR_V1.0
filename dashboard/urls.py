from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('executive/', views.executive_dashboard, name='executive'),
    path('hr/', views.hr_dashboard, name='hr_analytics'),
    path('workforce/', views.workforce_overview, name='workforce'),
    path('performance/', views.performance_analytics, name='performance'),
    path('compensation/', views.compensation_analytics, name='compensation'),
]