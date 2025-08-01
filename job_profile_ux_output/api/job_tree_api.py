
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from job_profiles.models import JobCategory, JobType, JobRole, JobProfile
import json


@require_http_methods(["GET"])
def job_tree_api(request):
    """직무 체계도 트리 데이터 API"""
    
    try:
        # 직군별 색상 매핑
        category_colors = {
            'IT/디지털': '#3B82F6',
            '경영지원': '#10B981', 
            '금융': '#F59E0B',
            '영업': '#EF4444',
            '고객서비스': '#8B5CF6'
        }
        
        # 직무별 아이콘 매핑
        job_icons = {
            '시스템기획': 'fas fa-project-diagram',
            '시스템개발': 'fas fa-code',
            '시스템관리': 'fas fa-server',
            '서비스운영': 'fas fa-cogs',
            '감사': 'fas fa-search',
            '인사관리': 'fas fa-users',
            '인재개발': 'fas fa-graduation-cap',
            # ... 더 많은 아이콘 매핑
        }
        
        # 전체 구조 쿼리
        categories = JobCategory.objects.filter(is_active=True).prefetch_related(
            Prefetch('job_types', queryset=JobType.objects.filter(is_active=True).prefetch_related(
                Prefetch('job_roles', queryset=JobRole.objects.filter(is_active=True))
            ))
        )
        
        # 루트 노드 생성
        total_jobs = JobRole.objects.filter(is_active=True).count()
        
        root_node = {
            'id': 'root',
            'name': 'OK금융그룹 직무체계',
            'type': 'root',
            'level': 0,
            'parent_id': None,
            'children': [],
            'metadata': {
                'total_categories': categories.count(),
                'total_jobs': total_jobs
            },
            'color': '#1F2937',
            'icon': 'fas fa-sitemap',
            'description': '전체 직무 체계도',
            'job_count': total_jobs
        }
        
        # 직군 노드 생성
        for category in categories:
            category_job_count = JobRole.objects.filter(
                job_type__category=category,
                is_active=True
            ).count()
            
            category_color = category_colors.get(category.name, '#6B7280')
            
            category_node = {
                'id': f'category_{category.id}',
                'name': category.name,
                'type': 'category',
                'level': 1,
                'parent_id': 'root',
                'children': [],
                'metadata': {
                    'job_types_count': category.job_types.filter(is_active=True).count(),
                    'total_jobs': category_job_count
                },
                'color': category_color,
                'icon': 'fas fa-layer-group',
                'description': category.description or f'{category.name} 관련 업무',
                'job_count': category_job_count
            }
            
            # 직종 노드 생성
            for job_type in category.job_types.filter(is_active=True):
                job_type_job_count = job_type.job_roles.filter(is_active=True).count()
                
                job_type_node = {
                    'id': f'type_{job_type.id}',
                    'name': job_type.name,
                    'type': 'job_type',
                    'level': 2,
                    'parent_id': f'category_{category.id}',
                    'children': [],
                    'metadata': {
                        'category': category.name,
                        'jobs_count': job_type_job_count
                    },
                    'color': category_color,
                    'icon': 'fas fa-folder',
                    'description': job_type.description or f'{job_type.name} 직종',
                    'job_count': job_type_job_count
                }
                
                # 직무 노드 생성
                for job_role in job_type.job_roles.filter(is_active=True):
                    has_profile = hasattr(job_role, 'profile') and job_role.profile.is_active
                    
                    job_role_node = {
                        'id': f'role_{job_role.id}',
                        'name': job_role.name,
                        'type': 'job_role',
                        'level': 3,
                        'parent_id': f'type_{job_type.id}',
                        'children': [],
                        'metadata': {
                            'category': category.name,
                            'job_type': job_type.name,
                            'has_profile': has_profile,
                            'job_role_id': str(job_role.id)
                        },
                        'color': f'{category_color}40',  # 투명도 적용
                        'icon': job_icons.get(job_role.name, 'fas fa-user-cog'),
                        'description': job_role.description or f'{job_role.name} 직무',
                        'job_count': 1
                    }
                    job_type_node['children'].append(job_role_node)
                
                category_node['children'].append(job_type_node)
            
            root_node['children'].append(category_node)
        
        return JsonResponse({
            'success': True,
            'data': root_node,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def job_profile_detail_api(request, job_role_id):
    """직무 상세 정보 API"""
    
    try:
        job_role = JobRole.objects.select_related(
            'job_type__category'
        ).get(id=job_role_id, is_active=True)
        
        # 직무기술서 조회
        job_profile = None
        if hasattr(job_role, 'profile'):
            job_profile = job_role.profile
        
        # 관련 직무 찾기 (같은 직종 내 다른 직무들)
        related_jobs = JobRole.objects.filter(
            job_type=job_role.job_type,
            is_active=True
        ).exclude(id=job_role_id)[:5]
        
        # 응답 데이터 구성
        response_data = {
            'id': str(job_role.id),
            'name': job_role.name,
            'code': job_role.code,
            'description': job_role.description,
            'job_type': {
                'id': str(job_role.job_type.id),
                'name': job_role.job_type.name,
                'code': job_role.job_type.code
            },
            'category': {
                'id': str(job_role.job_type.category.id),
                'name': job_role.job_type.category.name,
                'code': job_role.job_type.category.code
            },
            'full_path': job_role.full_path,
            'has_profile': job_profile is not None,
            'profile': None,
            'related_jobs': []
        }
        
        # 직무기술서 정보 추가
        if job_profile:
            response_data['profile'] = {
                'role_responsibility': job_profile.role_responsibility,
                'qualification': job_profile.qualification,
                'basic_skills': job_profile.basic_skills,
                'applied_skills': job_profile.applied_skills,
                'growth_path': job_profile.growth_path,
                'related_certifications': job_profile.related_certifications,
                'created_at': job_profile.created_at.isoformat(),
                'updated_at': job_profile.updated_at.isoformat()
            }
        
        # 관련 직무 정보 추가
        for related_job in related_jobs:
            response_data['related_jobs'].append({
                'id': str(related_job.id),
                'name': related_job.name,
                'description': related_job.description,
                'has_profile': hasattr(related_job, 'profile')
            })
        
        return JsonResponse({
            'success': True,
            'data': response_data
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


@require_http_methods(["GET"])
def job_search_api(request):
    """직무 검색 API"""
    
    try:
        query = request.GET.get('q', '').strip()
        category_filter = request.GET.get('category', '')
        job_type_filter = request.GET.get('job_type', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # 기본 쿼리셋
        queryset = JobRole.objects.select_related(
            'job_type__category'
        ).filter(is_active=True)
        
        # 검색어 필터
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(job_type__name__icontains=query) |
                Q(job_type__category__name__icontains=query)
            )
        
        # 카테고리 필터
        if category_filter:
            queryset = queryset.filter(job_type__category__name=category_filter)
        
        # 직종 필터
        if job_type_filter:
            queryset = queryset.filter(job_type__name=job_type_filter)
        
        # 페이지네이션
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # 결과 구성
        results = []
        for job_role in page_obj:
            results.append({
                'id': str(job_role.id),
                'name': job_role.name,
                'description': job_role.description,
                'job_type': job_role.job_type.name,
                'category': job_role.job_type.category.name,
                'full_path': job_role.full_path,
                'has_profile': hasattr(job_role, 'profile')
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'results': results,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def job_statistics_api(request):
    """직무 통계 API"""
    
    try:
        # 전체 통계
        total_categories = JobCategory.objects.filter(is_active=True).count()
        total_job_types = JobType.objects.filter(is_active=True).count()
        total_job_roles = JobRole.objects.filter(is_active=True).count()
        total_profiles = JobProfile.objects.filter(is_active=True).count()
        
        # 직군별 통계
        category_stats = []
        categories = JobCategory.objects.filter(is_active=True).annotate(
            job_type_count=Count('job_types', filter=Q(job_types__is_active=True)),
            job_role_count=Count('job_types__job_roles', filter=Q(
                job_types__is_active=True,
                job_types__job_roles__is_active=True
            ))
        )
        
        for category in categories:
            category_stats.append({
                'name': category.name,
                'job_type_count': category.job_type_count,
                'job_role_count': category.job_role_count,
                'description': category.description
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'summary': {
                    'total_categories': total_categories,
                    'total_job_types': total_job_types,
                    'total_job_roles': total_job_roles,
                    'total_profiles': total_profiles,
                    'profile_completion_rate': round(
                        (total_profiles / total_job_roles * 100) if total_job_roles > 0 else 0, 1
                    )
                },
                'category_breakdown': category_stats
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
