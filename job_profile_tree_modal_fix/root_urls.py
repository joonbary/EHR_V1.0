from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from job_profiles.views import JobTreeView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 루트 경로를 직무 트리맵으로 설정
    path('', JobTreeView.as_view(), name='home'),
    
    # 앱별 URL
    path('', include('job_profiles.urls')),
    
    # 기타 앱들 (필요시 추가)
    # path('employees/', include('employees.urls')),
    # path('evaluations/', include('evaluations.urls')),
]

# 정적 파일 및 미디어 파일 서빙 (개발 환경)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
