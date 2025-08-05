from django.urls import path, include
from . import views
from . import views_advanced
from core.views import under_construction

app_name = 'evaluations'

urlpatterns = [
    # 메인 대시보드
    path('', views.evaluation_dashboard, name='dashboard'),
    
    # 3대 평가 관리 (기여도/전문성/영향력)
    path('contribution/', include([
        path('', views.contribution_list, name='contribution_list'),
        path('<int:employee_id>/', views.contribution_evaluation, name='contribution_evaluation'),
        path('tasks/', under_construction, name='contribution_tasks'),
        path('checkin/<int:task_id>/', views.task_checkin, name='task_checkin'),
        path('checkin/<int:task_id>/history/', views.task_checkin_history, name='task_checkin_history'),
        path('task/<int:task_id>/status/', views.task_update_status, name='task_update_status'),
        path('scoring/', under_construction, name='contribution_scoring'),
    ])),
    
    path('expertise/', include([
        path('', views.expertise_list, name='expertise_list'),
        path('<int:employee_id>/', views.expertise_evaluation, name='expertise_evaluation'),
        path('requirements/', under_construction, name='expertise_requirements'),
        path('levels/', under_construction, name='expertise_levels'),
    ])),
    
    path('impact/', include([
        path('', views.impact_list, name='impact_list'),
        path('<int:employee_id>/', views.impact_evaluation, name='impact_evaluation'),
        path('values/', under_construction, name='impact_values'),
        path('leadership/', under_construction, name='impact_leadership'),
    ])),
    
    # 종합평가 관리
    path('comprehensive/', include([
        path('', views.comprehensive_list, name='comprehensive_list'),
        path('<int:employee_id>/', views.comprehensive_evaluation, name='comprehensive_evaluation'),
        path('primary/', under_construction, name='comprehensive_primary'),
        path('final/', under_construction, name='comprehensive_final'),
    ])),
    
    # Calibration 관리
    path('calibration/', include([
        path('', views.calibration_list, name='calibration_list'),
        path('create/', views.create_calibration_session, name='create_calibration_session'),
        path('session/<int:session_id>/', views.calibration_session, name='calibration_session'),
        path('dashboard/<int:period_id>/', views_advanced.CalibrationDashboardView.as_view(), name='calibration_dashboard'),
    ])),
    
    # 성장레벨 관리
    path('growth-level/', include([
        path('', under_construction, name='growth_dashboard'),
        path('<int:employee_id>/', views.growth_level_dashboard, name='growth_level_dashboard'),
        path('standards/', under_construction, name='growth_standards'),
        path('certification/', under_construction, name='growth_certification'),
        path('history/', under_construction, name='growth_history'),
    ])),
    
    # 피평가자 화면 (본인평가)
    path('my/', include([
        path('', views.my_evaluations_dashboard, name='my_evaluations'),
        path('goals/', views.my_goals, name='my_goals'),
        path('goals/create/', views.create_goal, name='create_goal'),
        path('goals/<int:task_id>/update/', views.update_goal, name='update_goal'),
        path('results/', views.my_evaluation_results, name='my_results'),
    ])),
    
    # 평가자 화면 
    path('evaluator/', include([
        path('', views.evaluator_dashboard, name='evaluator_dashboard'),
        path('evaluate/<int:employee_id>/', views.evaluate_employee, name='evaluate_employee'),
    ])),
    
    # 인사담당자 화면
    path('hr-admin/', include([
        path('', views.hr_admin_dashboard, name='hr_admin_dashboard'),
        path('period-management/', views.period_management, name='period_management'),
        path('statistics/', views.evaluation_statistics, name='evaluation_statistics'),
    ])),
    
    # 분석 및 리포트
    path('analytics/', include([
        path('', views.analytics_dashboard, name='analytics_dashboard'),
        path('api/', views_advanced.evaluation_analytics_api, name='evaluation_analytics'),
        path('trends/<int:employee_id>/', views_advanced.PerformanceTrendView.as_view(), name='performance_trend'),
        path('insights/', views_advanced.EvaluationInsightsView.as_view(), name='evaluation_insights'),
        path('reports/', under_construction, name='evaluation_reports'),
    ])),
    
    # API 및 유틸리티
    path('api/', include([
        path('calculate-score/', views.calculate_score_ajax, name='calculate_score_ajax'),
        path('process/<int:period_id>/', views_advanced.ProcessEvaluationView.as_view(), name='process_evaluation'),
    ])),
] 