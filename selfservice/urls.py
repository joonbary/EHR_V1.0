from django.urls import path
from . import views
from .views import CompensationStatementView, ProfileUpdateView, CustomPasswordChangeView
from core.views import under_construction

app_name = 'selfservice'

urlpatterns = [
    path('', views.my_dashboard, name='dashboard'),
    path('profile/', ProfileUpdateView.as_view(), name='profile_update'),
    path('password/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('evaluations/', views.evaluation_history, name='evaluation_history'),
    path('compensation/', CompensationStatementView.as_view(), name='compensation_statement'),
    path('compensation/<int:year>/<int:month>/', CompensationStatementView.as_view(), name='compensation_statement_detail'),
    path('career/', views.career_path, name='career_path'),
    
    # 미구현 기능
    path('my-evaluation/', under_construction, name='my_evaluation'),
    path('my-compensation/', under_construction, name='my_compensation'),
] 