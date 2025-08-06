from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Prefetch
import json

# Conditional import to prevent import errors
try:
    from .models import JobCategory, JobType, JobRole, JobProfile
except ImportError:
    JobCategory = None
    JobType = None
    JobRole = None
    JobProfile = None


class JobHierarchyView(TemplateView):
    """새로운 직무체계도 계층 뷰"""
    template_name = 'job_profiles/simple_hierarchy.html'  # 임시로 간단한 템플릿 사용
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            
            context['total_categories'] = JobCategory.objects.count()
            context['total_job_types'] = JobType.objects.count()
            context['total_job_roles'] = JobRole.objects.count()
            context['total_profiles'] = JobProfile.objects.count()
            
        except Exception as e:
            print(f"Job 모델 통계 오류: {e}")
            context['total_categories'] = 0
            context['total_job_types'] = 0
            context['total_job_roles'] = 0
            context['total_profiles'] = 0
        
        return context


class JobTreeMapView(TemplateView):
    """직무체계도 트리맵 뷰"""
    template_name = 'job_profiles/job_treemap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 데이터 - 모델이 있으면 사용, 없으면 0
        try:
            
            context['total_categories'] = JobCategory.objects.count()
            context['total_job_types'] = JobType.objects.count()
            context['total_job_roles'] = JobRole.objects.count()
            context['total_profiles'] = JobProfile.objects.count()
            
        except Exception as e:
            print(f"Job 모델 통계 오류: {e}")
            context['total_categories'] = 0
            context['total_job_types'] = 0
            context['total_job_roles'] = 0
            context['total_profiles'] = 0
        
        return context


def job_tree_map_data_api(request):
    """트리맵 데이터 API"""
    try:
        # 카테고리별 데이터 구성 (수정됨 - 고객서비스 제거)
        non_pl_categories = ['IT/디지털', '경영지원', '금융', '영업']
        print(f"DEBUG: non_pl_categories = {non_pl_categories}")  # 디버그 로그
        icon_map = {
            'IT/디지털': 'laptop',
            '경영지원': 'briefcase',
            '금융': 'dollar-sign',
            '영업': 'users',
            '고객서비스': 'headphones',
            'PL': 'user-shield'
        }
        
        tree_data = {'Non-PL': {}, 'PL': {}}
        
        # 모든 카테고리 조회
        categories = JobCategory.objects.all()
        
        for category in categories:
            category_data = {
                'name': category.name,
                'icon': icon_map.get(category.name, 'folder'),
                'jobs': {}
            }
            
            # 카테고리별 직종과 직무 조회
            job_types = JobType.objects.filter(category=category)
            
            for job_type in job_types:
                jobs = []
                job_roles = JobRole.objects.filter(job_type=job_type)
                
                for job_role in job_roles:
                    # 프로필 존재 여부 확인
                    try:
                        has_profile = JobProfile.objects.filter(job_role=job_role).exists()
                    except:
                        has_profile = False
                    
                    jobs.append({
                        'id': str(job_role.id),
                        'name': job_role.name,
                        'has_profile': has_profile
                    })
                
                if jobs:
                    category_data['jobs'][job_type.name] = jobs
            
            # Non-PL 또는 PL로 분류
            if category.name in non_pl_categories:
                tree_data['Non-PL'][category.name] = category_data
            else:
                tree_data['PL'][category.name] = category_data
        
        return JsonResponse({
            'success': True,
            'data': tree_data
        })
        
    except Exception as e:
        print(f"API 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': {'Non-PL': {}, 'PL': {}}
        })


def job_detail_modal_api(request, job_role_id):
    """직무 상세 정보 API"""
    try:
            
        job_role = get_object_or_404(JobRole, id=job_role_id)
        
        data = {
            'job': {
                'id': str(job_role.id),
                'name': job_role.name,
                'category': job_role.job_type.category.name,
                'job_type': job_role.job_type.name,
                'description': '',
                'full_path': f"{job_role.job_type.category.name} > {job_role.job_type.name} > {job_role.name}"
            }
        }
        
        # 프로필 정보 확인
        try:
            profile = JobProfile.objects.get(job_role=job_role)
            data['profile'] = {
                'id': str(profile.id),
                'role_responsibility': getattr(profile, 'role_responsibility', ''),
                'qualification': getattr(profile, 'qualification', ''),
                'basic_skills': getattr(profile, 'basic_skills', []),
                'applied_skills': getattr(profile, 'applied_skills', []),
                'growth_path': getattr(profile, 'growth_path', ''),
                'related_certifications': getattr(profile, 'related_certifications', [])
            }
        except JobProfile.DoesNotExist:
            data['profile'] = None
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=404)


def job_profile_edit_view(request, job_role_id):
    """직무기술서 편집 뷰"""
    
    job_role = get_object_or_404(JobRole, id=job_role_id)
    
    if request.method == 'GET':
        try:
            profile = JobProfile.objects.get(job_role=job_role)
        except JobProfile.DoesNotExist:
            profile = None
        
        context = {
            'job': job_role,
            'profile': profile
        }
        return render(request, 'job_profiles/job_profile_edit.html', context)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            profile, created = JobProfile.objects.update_or_create(
                job_role=job_role,
                defaults=data
            )
            
            return JsonResponse({
                'success': True,
                'message': '저장되었습니다.',
                'profile_id': str(profile.id)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


def job_detail_api(request, job_role_id):
    """직무 상세 정보 API (새로운 UI용)"""
    try:
            
        job_role = get_object_or_404(JobRole, id=job_role_id)
        
        # JobProfile 정보 가져오기
        try:
            profile = JobProfile.objects.get(job_role=job_role)
            profile_data = {
                'role_responsibility': profile.role_responsibility,
                'qualification': profile.qualification,
                'basic_skills': profile.basic_skills,
                'applied_skills': profile.applied_skills,
                'related_certifications': profile.related_certifications,
                'growth_path': profile.growth_path,
            }
        except JobProfile.DoesNotExist:
            profile_data = None
        
        # 응답 데이터 구성
        data = {
            'success': True,
            'job_role': {
                'id': str(job_role.id),
                'name': job_role.name,
                'code': job_role.code,
                'description': job_role.description,
                'job_type': {
                    'name': job_role.job_type.name if job_role.job_type else None,
                    'category': {
                        'name': job_role.job_type.category.name if job_role.job_type and job_role.job_type.category else None
                    }
                } if job_role.job_type else None
            },
            'profile': profile_data
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
