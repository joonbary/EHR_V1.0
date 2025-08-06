from django.views.generic import TemplateView
from django.db.models import Count, Q
from datetime import datetime, timedelta


class DashboardView(TemplateView):
    """메인 대시보드 뷰"""
    template_name = 'simple_dashboard.html'  # 안정적인 독립 템플릿 사용
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Employee 모델 임포트를 여기서 수행
        try:
            from employees.models import Employee
            
            # employment_status='active'인 직원만 카운트
            active_employees = Employee.objects.filter(
                employment_status='active'
            ).count()
            
            # 부서 수 (중복 제거)
            departments = Employee.objects.filter(
                employment_status='active'
            ).values('department').distinct().count()
            
            # 최근 30일 신규 입사자
            today = datetime.now().date()
            month_ago = today - timedelta(days=30)
            recent_hires = Employee.objects.filter(
                hire_date__gte=month_ago,
                employment_status='active'
            ).count()
            
        except Exception as e:
            print(f"Employee 통계 오류: {e}")
            active_employees = 0
            departments = 0
            recent_hires = 0
        
        # JobRole, JobProfile 통계
        try:
            from job_profiles.models import JobRole, JobProfile
            
            total_job_roles = JobRole.objects.count()
            completed_profiles = JobProfile.objects.count()
            
        except Exception as e:
            print(f"Job 통계 오류: {e}")
            total_job_roles = 0
            completed_profiles = 0
        
        # 컨텍스트에 통계 추가
        context['stats'] = {
            'total_employees': active_employees,
            'total_departments': departments,
            'total_job_roles': total_job_roles,
            'completed_profiles': completed_profiles,
            'recent_hires': recent_hires,
            'pending_evaluations': 0
        }
        
        return context
