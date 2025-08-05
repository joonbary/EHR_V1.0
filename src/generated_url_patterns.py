
# === 신규 추가 URL 패턴 ===

# 1. 통합 테스트 시스템
path('testing/', include([
    path('', testing_views.test_dashboard, name='test_dashboard'),
    path('run-scenario/<str:scenario>/', testing_views.run_scenario_test, name='run_scenario_test'),
    path('ai-quality/', testing_views.ai_quality_test, name='ai_quality_test'),
    path('performance/', testing_views.performance_test, name='performance_test'),
    path('security/', testing_views.security_test, name='security_test'),
    path('api/results/', testing_views.test_results_api, name='test_results_api'),
])),

# 2. 직무 매칭 시스템
path('matching/', include([
    path('', matching_views.matching_dashboard, name='matching_dashboard'),
    path('job-search/', matching_views.job_search, name='job_search'),
    path('talent-pool/', matching_views.talent_pool, name='talent_pool'),
    path('recommendations/', matching_views.recommendations, name='matching_recommendations'),
    path('api/match/', matching_views.matching_api, name='matching_api'),
    path('api/recommend/', matching_views.recommend_api, name='recommend_api'),
])),

# 3. 자격증 관리 시스템
path('certifications/', include([
    path('', certification_views.certification_dashboard, name='certification_dashboard'),
    path('my-certifications/', certification_views.my_certifications, name='my_certifications'),
    path('growth-level/', certification_views.growth_level, name='growth_level'),
    path('verification/', certification_views.verification, name='certification_verification'),
    path('api/growth-status/', certification_views.growth_status_api, name='growth_status_api'),
])),

# 4. ESS 확장 기능
path('ess-plus/', include([
    path('', ess_views.ess_plus_dashboard, name='ess_plus_dashboard'),
    path('growth-path/', ess_views.growth_path, name='growth_path'),
    path('training-recommendations/', ess_views.training_recommendations, name='training_recommendations'),
    path('career-planning/', ess_views.career_planning, name='career_planning'),
    path('mentoring/', ess_views.mentoring_match, name='mentoring_match'),
])),

# 5. 고급 분석 도구
path('analytics/', include([
    path('', analytics_views.analytics_dashboard, name='analytics_dashboard'),
    path('strategy-report/', analytics_views.strategy_report, name='strategy_report'),
    path('promotion-analysis/', analytics_views.promotion_analysis, name='promotion_analysis'),
    path('talent-risk/', analytics_views.talent_risk_analysis, name='talent_risk_analysis'),
    path('api/generate-report/', analytics_views.generate_report_api, name='generate_report_api'),
])),
