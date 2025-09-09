"""
URL configuration for ehr_evaluation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls')),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('api/', include('users.urls')),
    path('api/evaluations/', include('evaluations.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    # 각 앱의 URL 패턴 추가
    path('employees/', include('employees.urls')),
    path('compensation/', include('compensation.urls')),
    path('organization/', include('organization.urls')),
    path('airiss/', include('airiss.urls')),
    path('ai-quickwin/', include('ai_quickwin.urls')),
    path('ai-coaching/', include('ai_coaching.urls')),
    path('ai-insights/', include('ai_insights.urls')),
    path('ai-predictions/', include('ai_predictions.urls')),
    path('ai-interviewer/', include('ai_interviewer.urls')),
    path('ai-team-optimizer/', include('ai_team_optimizer.urls')),
    path('job-profiles/', include('job_profiles.urls')),
    path('evaluations/', include('evaluations.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
