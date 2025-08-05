from django.urls import path
from . import views

app_name = "airiss"

urlpatterns = [
    path("executive/", views.executive_dashboard, name="executive_dashboard"),
    path("employees/", views.employee_analysis_all, name="employee_analysis_all"),
    path("employee/<int:employee_id>/analysis/", views.employee_analysis_detail, name="employee_analysis_detail"),
    path("msa_integration/", views.msa_integration, name="msa_integration"),
]
