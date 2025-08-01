
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
import json

@require_http_methods(["GET"])
@cache_page(60 * 5)  # 5분 캐시
def skillmap_data_api(request):
    '''스킬맵 데이터 API with 페이지네이션'''
    
    try:
        # 페이지 파라미터
        page = request.GET.get('page', 1)
        per_page = int(request.GET.get('per_page', 20))
        
        # 최대 페이지당 항목 수 제한
        per_page = min(per_page, 100)
        
        # 쿼리 최적화
        queryset = (Employee.objects
                   .select_related('job_profile', 'department')
                   .prefetch_related('skills')
                   .filter(employment_status='재직')
                   .order_by('department', 'name'))
        
        # 페이지네이션
        paginator = Paginator(queryset, per_page)
        
        try:
            employees = paginator.page(page)
        except PageNotAnInteger:
            employees = paginator.page(1)
        except EmptyPage:
            return JsonResponse({
                'results': [],
                'has_next': False,
                'has_previous': False,
                'total_pages': paginator.num_pages,
                'current_page': page,
                'total_count': 0
            })
        
        # 데이터 직렬화
        results = []
        for employee in employees:
            results.append({
                'id': str(employee.id),
                'name': employee.name,
                'department': employee.department,
                'job_title': employee.job_title,
                'skills': [
                    {
                        'skill_name': skill.skill_name,
                        'proficiency_level': skill.proficiency_level,
                        'skill_category': skill.skill_category
                    }
                    for skill in employee.skills.all()
                ]
            })
        
        return JsonResponse({
            'results': results,
            'has_next': employees.has_next(),
            'has_previous': employees.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': employees.number,
            'total_count': paginator.count
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'results': []
        }, status=500)


class SkillmapDashboardView(LoginRequiredMixin, TemplateView):
    '''스킬맵 대시보드 뷰 with 최적화'''
    
    template_name = 'dashboards/skillmap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 초기 데이터만 로드 (첫 페이지)
        initial_employees = (Employee.objects
                           .select_related('job_profile', 'department')
                           .prefetch_related('skills')
                           .filter(employment_status='재직')
                           .order_by('department', 'name')[:20])
        
        # 요약 통계만 계산
        context['stats'] = {
            'total_employees': Employee.objects.filter(employment_status='재직').count(),
            'departments': Employee.objects.values('department').distinct().count(),
            'total_skills': Skill.objects.count(),
        }
        
        # 초기 데이터
        context['initial_data'] = [
            {
                'id': str(emp.id),
                'name': emp.name,
                'department': emp.department,
                'skills_count': emp.skills.count()
            }
            for emp in initial_employees
        ]
        
        return context
