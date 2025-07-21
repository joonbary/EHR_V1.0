"""
URL configuration for ehr_system project.

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
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.admin.sites import site
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, user_passes_test
from employees.models import Employee
from compensation.models import EmployeeCompensation
from django.db.models import Count, Avg
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Django 관리자 사이트 설정
admin.site.site_header = "OK금융그룹 eHR 시스템 관리자"
admin.site.site_title = "OK금융그룹 eHR"
admin.site.index_title = "사이트 관리"

def home(request):
    # 대시보드 데이터 수집
    context = {
        'total_employees': Employee.objects.count(),
        'total_departments': Employee.objects.values('department').distinct().count(),
        'completed_evaluations': 0,  # 평가 모델이 있다면 실제 데이터로 변경
        'avg_salary': EmployeeCompensation.objects.aggregate(Avg('total_compensation'))['total_compensation__avg'] or 0,
        'recent_employees': Employee.objects.order_by('-hire_date')[:5],
        'department_stats': Employee.objects.values('department').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
    }
    
    # 부서별 비율 계산
    total = context['total_employees']
    if total > 0:
        for dept in context['department_stats']:
            dept['percentage'] = (dept['count'] / total) * 100
    
    return render(request, 'dashboard.html', context)

@method_decorator(staff_member_required, name='dispatch')
class CustomAdminDashboardView(TemplateView):
    template_name = 'admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Django 관리자 앱 리스트 가져오기
        app_list = site.get_app_list(self.request)
        
        # 각 모델의 실제 카운트 계산
        for app in app_list:
            for model in app['models']:
                try:
                    # 모델 클래스 가져오기
                    model_admin = site._registry.get(model['model'])
                    if model_admin:
                        # 실제 데이터베이스 카운트 계산
                        model['count'] = model_admin.model.objects.count()
                    else:
                        model['count'] = 0
                except Exception as e:
                    print(f"모델 카운트 계산 오류: {model['name']} - {e}")
                    model['count'] = 0
        
        context['app_list'] = app_list
        context['title'] = '사이트 관리'
        
        return context

# Django 기본 관리자를 커스텀 대시보드로 리다이렉트
def admin_redirect(request):
    return redirect('admin_dashboard')

# API 엔드포인트들 (AJAX 요청용)
@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def api_model_data(request, app_label, model_name):
    """모델 데이터를 JSON으로 반환하는 API"""
    try:
        # Django 모델 동적 로드
        from django.apps import apps
        model = apps.get_model(app_label, model_name)
        
        # 페이지네이션
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        start = (page - 1) * per_page
        end = start + per_page
        
        # 데이터 조회
        objects = model.objects.all()[start:end]
        total_count = model.objects.count()
        
        # 직렬화
        data = []
        for obj in objects:
            data.append({
                'id': obj.id,
                'str': str(obj),
                # 필요한 필드들 추가
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'pages': (total_count + per_page - 1) // per_page
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def api_create_object(request, app_label, model_name):
    """새 객체 생성 API"""
    if request.method == 'POST':
        try:
            from django.apps import apps
            model = apps.get_model(app_label, model_name)
            
            data = json.loads(request.body)
            # 데이터 검증 및 생성 로직
            obj = model.objects.create(**data)
            
            return JsonResponse({
                'success': True,
                'id': obj.id,
                'message': '객체가 성공적으로 생성되었습니다.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

urlpatterns = [
    path('', home, name='home'),
    
    # Django 기본 관리자를 커스텀 대시보드로 리다이렉트
    path('admin/', admin_redirect, name='admin_redirect'),
    path('admin/dashboard/', CustomAdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Django 기본 관리자 (백업용)
    path('django-admin/', admin.site.urls),
    
    # API 엔드포인트들
    path('api/model/<str:app_label>/<str:model_name>/', api_model_data, name='api_model_data'),
    path('api/create/<str:app_label>/<str:model_name>/', api_create_object, name='api_create_object'),
    
    # Django 인증 URL 추가
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='login.html',
        success_url='/'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # 기존 앱 URL들
    path('employees/', include('employees.urls')),
    path('evaluations/', include('evaluations.urls')),
    path('compensation/', include('compensation.urls')),
    path('promotions/', include('promotions.urls')),
    path('permissions/', include('permissions.urls')),
    path('selfservice/', include('selfservice.urls')),
    path('reports/', include('reports.urls')),
]
