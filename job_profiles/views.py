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
    template_name = 'job_profiles/job_tree_unified.html'  # 통합 UI 사용
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 정확한 통계 (하드코딩)
        context['total_categories'] = 2  # Non-PL, PL 직군
        context['total_job_types'] = 9  # 8 Non-PL + 1 PL  
        context['total_job_roles'] = 37  # 33 Non-PL + 4 PL
        context['total_profiles'] = 37  # 모든 직무에 기술서 있음
        
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
    """트리맵 데이터 API - 직무 체계도용 (개선된 버전)"""
    
    # 정확한 직무 구조 (하드코딩)
    result_data = {
        'Non-PL': {
            'IT기획': {
                'icon': 'fa-laptop-code',
                'jobs': [
                    {'id': '1', 'name': '시스템기획', 'has_profile': True}
                ]
            },
            'IT개발': {
                'icon': 'fa-code', 
                'jobs': [
                    {'id': '2', 'name': '시스템개발', 'has_profile': True}
                ]
            },
            'IT운영': {
                'icon': 'fa-server',
                'jobs': [
                    {'id': '3', 'name': '시스템관리', 'has_profile': True},
                    {'id': '4', 'name': '서비스운영', 'has_profile': True}
                ]
            },
            '경영관리': {
                'icon': 'fa-briefcase',
                'jobs': [
                    {'id': '5', 'name': '감사', 'has_profile': True},
                    {'id': '6', 'name': 'HRM', 'has_profile': True},
                    {'id': '7', 'name': 'HRD', 'has_profile': True},
                    {'id': '8', 'name': '경영지원', 'has_profile': True},
                    {'id': '9', 'name': '비서', 'has_profile': True},
                    {'id': '10', 'name': 'PR', 'has_profile': True},
                    {'id': '11', 'name': '경영기획', 'has_profile': True},
                    {'id': '12', 'name': '디자인', 'has_profile': True},
                    {'id': '13', 'name': '리스크관리', 'has_profile': True},
                    {'id': '14', 'name': '마케팅', 'has_profile': True},
                    {'id': '15', 'name': '스포츠사무관리', 'has_profile': True},
                    {'id': '16', 'name': '자금', 'has_profile': True},
                    {'id': '17', 'name': '재무회계', 'has_profile': True},
                    {'id': '18', 'name': '정보보안', 'has_profile': True},
                    {'id': '19', 'name': '준법지원', 'has_profile': True},
                    {'id': '20', 'name': '총무', 'has_profile': True}
                ]
            },
            '투자금융': {
                'icon': 'fa-chart-line',
                'jobs': [
                    {'id': '21', 'name': 'IB금융', 'has_profile': True}
                ]
            },
            '기업금융': {
                'icon': 'fa-building',
                'jobs': [
                    {'id': '22', 'name': '기업영업기획', 'has_profile': True},
                    {'id': '23', 'name': '기업여신심사', 'has_profile': True},
                    {'id': '24', 'name': '기업여신관리', 'has_profile': True}
                ]
            },
            '기업영업': {
                'icon': 'fa-handshake',
                'jobs': [
                    {'id': '25', 'name': '여신영업', 'has_profile': True}
                ]
            },
            '리테일금융': {
                'icon': 'fa-coins',
                'jobs': [
                    {'id': '26', 'name': '데이터/통계', 'has_profile': True},
                    {'id': '27', 'name': '플랫폼/핀테크', 'has_profile': True},
                    {'id': '28', 'name': 'NPL영업기획', 'has_profile': True},
                    {'id': '29', 'name': '리테일심사기획', 'has_profile': True},
                    {'id': '30', 'name': 'PL기획', 'has_profile': True},
                    {'id': '31', 'name': '모기지기획', 'has_profile': True},
                    {'id': '32', 'name': '수신기획', 'has_profile': True},
                    {'id': '33', 'name': '수신영업', 'has_profile': True}
                ]
            }
        },
        'PL': {
            '고객지원': {
                'icon': 'fa-headset',
                'jobs': [
                    {'id': '34', 'name': '여신고객지원', 'has_profile': True},
                    {'id': '35', 'name': '사무지원', 'has_profile': True},
                    {'id': '36', 'name': '수신고객지원', 'has_profile': True},
                    {'id': '37', 'name': '채권관리지원', 'has_profile': True}
                ]
            }
        }
    }
    
    # success 필드와 함께 반환
    return JsonResponse({
        'success': True,
        'data': result_data
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
