from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q
from job_profiles.models import JobCategory, JobType, JobRole, JobProfile

class JobProfileTreeMapView(LoginRequiredMixin, TemplateView):
    '''직무 트리맵 뷰'''
    template_name = 'job_profiles/job_tree_map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 정보
        context.update({
            'total_categories': JobCategory.objects.filter(is_active=True).count(),
            'total_job_types': JobType.objects.filter(is_active=True).count(),
            'total_job_roles': JobRole.objects.filter(is_active=True).count(),
            'total_profiles': JobProfile.objects.filter(is_active=True).count(),
            'page_title': 'OK금융그룹 직무 체계도',
            'page_description': '직군-직종-직무 3단계 트리맵 시각화'
        })
        
        return context


from django.contrib.auth.decorators import login_required

@login_required
def job_tree_map_data_api(request):
    '''트리맵 데이터 API'''
    try:
        # Non-PL, PL 분류를 위한 데이터 구조
        tree_data = {
            'Non-PL': {},
            'PL': {}
        }
        
        # PL 직군 정의 (고객서비스)
        pl_categories = ['고객서비스']
        
        # 모든 카테고리 조회
        categories = JobCategory.objects.filter(is_active=True).prefetch_related(
            Prefetch(
                'job_types',
                queryset=JobType.objects.filter(is_active=True).prefetch_related(
                    Prefetch(
                        'job_roles',
                        queryset=JobRole.objects.filter(is_active=True).select_related('profile')
                    )
                )
            )
        )
        
        # 색상 및 아이콘 매핑
        category_meta = {
            'IT/디지털': {'color': '#3B82F6', 'icon': 'laptop'},
            '경영지원': {'color': '#8B5CF6', 'icon': 'briefcase'},
            '금융': {'color': '#10B981', 'icon': 'dollar-sign'},
            '영업': {'color': '#F59E0B', 'icon': 'users'},
            '고객서비스': {'color': '#EF4444', 'icon': 'headphones'}
        }
        
        for category in categories:
            # PL/Non-PL 분류
            group = 'PL' if category.name in pl_categories else 'Non-PL'
            
            # 카테고리 데이터 구조
            category_data = {
                'id': str(category.id),
                'name': category.name,
                'color': category_meta.get(category.name, {}).get('color', '#6B7280'),
                'icon': category_meta.get(category.name, {}).get('icon', 'folder'),
                'jobs': {}
            }
            
            # 직종별 직무 정리
            for job_type in category.job_types.all():
                jobs = []
                for job_role in job_type.job_roles.all():
                    job_info = {
                        'id': str(job_role.id),
                        'name': job_role.name,
                        'has_profile': hasattr(job_role, 'profile') and job_role.profile is not None,
                        'profile_id': str(job_role.profile.id) if hasattr(job_role, 'profile') and job_role.profile else None
                    }
                    jobs.append(job_info)
                
                if jobs:
                    category_data['jobs'][job_type.name] = jobs
            
            # 데이터 추가
            if category_data['jobs']:
                tree_data[group][category.name] = category_data
        
        # 통계 정보 추가
        statistics = {
            'Non-PL': {
                'categories': len(tree_data['Non-PL']),
                'job_types': sum(len(cat['jobs']) for cat in tree_data['Non-PL'].values()),
                'jobs': sum(len(jobs) for cat in tree_data['Non-PL'].values() for jobs in cat['jobs'].values())
            },
            'PL': {
                'categories': len(tree_data['PL']),
                'job_types': sum(len(cat['jobs']) for cat in tree_data['PL'].values()),
                'jobs': sum(len(jobs) for cat in tree_data['PL'].values() for jobs in cat['jobs'].values())
            }
        }
        
        return JsonResponse({
            'success': True,
            'data': tree_data,
            'statistics': statistics
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def job_detail_modal_api(request, job_role_id):
    '''직무 상세 정보 모달 API'''
    try:
        job_role = JobRole.objects.select_related(
            'job_type__category',
            'profile'
        ).get(id=job_role_id, is_active=True)
        
        # 관련 직무 조회
        related_jobs = JobRole.objects.filter(
            job_type=job_role.job_type,
            is_active=True
        ).exclude(id=job_role.id).select_related('profile')[:5]
        
        # 응답 데이터 구성
        data = {
            'job': {
                'id': str(job_role.id),
                'name': job_role.name,
                'description': job_role.description,
                'full_path': job_role.full_path,
                'category': job_role.job_type.category.name,
                'job_type': job_role.job_type.name,
            },
            'profile': None,
            'related_jobs': []
        }
        
        # 직무기술서 정보
        if hasattr(job_role, 'profile') and job_role.profile:
            profile = job_role.profile
            data['profile'] = {
                'id': str(profile.id),
                'role_responsibility': profile.role_responsibility,
                'qualification': profile.qualification,
                'basic_skills': profile.basic_skills,
                'applied_skills': profile.applied_skills,
                'growth_path': profile.growth_path,
                'related_certifications': profile.related_certifications
            }
        
        # 관련 직무 정보
        for related in related_jobs:
            data['related_jobs'].append({
                'id': str(related.id),
                'name': related.name,
                'has_profile': hasattr(related, 'profile') and related.profile is not None
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except JobRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '직무를 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)