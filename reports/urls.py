from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportDashboardView.as_view(), name='dashboard'),
    path('employee-list/', views.EmployeeListReportView.as_view(), name='employee_list_report'),
    path('evaluation-summary/', views.EvaluationSummaryReportView.as_view(), name='evaluation_summary_report'),
    path('compensation-analysis/', views.CompensationAnalysisReportView.as_view(), name='compensation_analysis_report'),
    path('promotion-candidates/', views.PromotionCandidatesReportView.as_view(), name='promotion_candidates_report'),
    path('department-statistics/', views.DepartmentStatisticsReportView.as_view(), name='department_statistics_report'),
    # 이직 위험도 리포트
    path('generate/turnover/', views.TurnoverRiskReportView.as_view(), name='turnover_risk_report'),
] 