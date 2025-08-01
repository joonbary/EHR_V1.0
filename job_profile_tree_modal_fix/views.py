from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Prefetch, Q
import json

from job_profiles.models import JobCategory, JobType, JobRole, JobProfile


class JobTreeView(TemplateView):
    """직무 트리맵 메인 뷰 (인증 불필요)"""
    template_name = 'job_tree_unified.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 정보
        context.update({
            'total_categories': JobCategory.objects.filter(is_active=True).count(),
            'total_job_types': JobType.objects.filter(is_active=True).count(),
            'total_job_roles': JobRole.objects.filter(is_active=True).count(),
            'total_profiles': JobProfile.objects.filter(is_active=True).count(),
        })
        
        return context


def job_tree_data_api(request):
    """트리맵 데이터 API (인증 불필요)"""
    try:
        # Non-PL, PL 분류를 위한 데이터 구조
        tree_data = {
            'Non-PL': {},
            'PL': {}
        }
        
        # PL 직군 정의
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
                    try:
                        has_profile = bool(job_role.profile)
                        profile_id = str(job_role.profile.id) if has_profile else None
                    except JobProfile.DoesNotExist:
                        has_profile = False
                        profile_id = None
                    
                    job_info = {
                        'id': str(job_role.id),
                        'name': job_role.name,
                        'has_profile': has_profile,
                        'profile_id': profile_id
                    }
                    jobs.append(job_info)
                
                if jobs:
                    category_data['jobs'][job_type.name] = jobs
            
            # 데이터 추가
            if category_data['jobs']:
                tree_data[group][category.name] = category_data
        
        return JsonResponse({
            'success': True,
            'data': tree_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def job_detail_api(request, job_role_id):
    """직무 상세 정보 API (인증 불필요)"""
    try:
        job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
        
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
        try:
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
        except JobProfile.DoesNotExist:
            pass
        
        # 관련 직무 정보
        for related in related_jobs:
            try:
                has_profile = bool(related.profile)
            except JobProfile.DoesNotExist:
                has_profile = False
                
            data['related_jobs'].append({
                'id': str(related.id),
                'name': related.name,
                'has_profile': has_profile
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


def job_profile_edit(request, job_role_id):
    """직무기술서 편집 (인증 불필요)"""
    job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
    
    try:
        profile = job_role.profile
    except JobProfile.DoesNotExist:
        # 프로필이 없으면 새로 생성
        profile = JobProfile(job_role=job_role)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 데이터 업데이트
            profile.role_responsibility = data.get('role_responsibility', '')
            profile.qualification = data.get('qualification', '')
            profile.basic_skills = data.get('basic_skills', [])
            profile.applied_skills = data.get('applied_skills', [])
            profile.growth_path = data.get('growth_path', '')
            profile.related_certifications = data.get('related_certifications', [])
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': '저장되었습니다.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET 요청시 편집 페이지 렌더링
    context = {
        'job': {
            'id': str(job_role.id),
            'name': job_role.name,
            'category': job_role.job_type.category.name,
            'job_type': job_role.job_type.name,
        },
        'profile': {
            'role_responsibility': profile.role_responsibility if profile.id else '',
            'qualification': profile.qualification if profile.id else '',
            'basic_skills': profile.basic_skills if profile.id else [],
            'applied_skills': profile.applied_skills if profile.id else [],
            'growth_path': profile.growth_path if profile.id else '',
            'related_certifications': profile.related_certifications if profile.id else [],
        }
    }
    
    return render(request, 'job_profile_edit.html', context)


@csrf_exempt
def job_profile_delete_api(request, job_role_id):
    """직무기술서 삭제 API (인증 불필요)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST 메서드만 허용됩니다.'}, status=405)
    
    try:
        job_role = get_object_or_404(JobRole, id=job_role_id)
        
        # 직무기술서가 있으면 삭제
        try:
            profile = job_role.profile
            profile.delete()
            message = '직무기술서가 삭제되었습니다.'
        except JobProfile.DoesNotExist:
            message = '삭제할 직무기술서가 없습니다.'
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def job_profile_create(request):
    """직무기술서 생성 (인증 불필요)"""
    job_role_id = request.GET.get('job_role')
    
    if not job_role_id:
        return redirect('/')
    
    job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
    
    # 이미 프로필이 있으면 편집 페이지로 리다이렉트
    try:
        profile = job_role.profile
        return redirect('job_profile_edit', job_role_id=job_role_id)
    except JobProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 새 프로필 생성
            profile = JobProfile(
                job_role=job_role,
                role_responsibility=data.get('role_responsibility', ''),
                qualification=data.get('qualification', ''),
                basic_skills=data.get('basic_skills', []),
                applied_skills=data.get('applied_skills', []),
                growth_path=data.get('growth_path', ''),
                related_certifications=data.get('related_certifications', [])
            )
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': '직무기술서가 생성되었습니다.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET 요청시 생성 페이지 렌더링 (편집 템플릿 재사용)
    context = {
        'job': {
            'id': str(job_role.id),
            'name': job_role.name,
            'category': job_role.job_type.category.name,
            'job_type': job_role.job_type.name,
        },
        'profile': {
            'role_responsibility': '',
            'qualification': '',
            'basic_skills': [],
            'applied_skills': [],
            'growth_path': '',
            'related_certifications': [],
        },
        'is_create': True
    }
    
    return render(request, 'job_profile_edit.html', context)
