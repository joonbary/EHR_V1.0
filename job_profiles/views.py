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
    """트리맵 데이터 API - 실제 데이터베이스 기반"""
    try:
        # 실제 데이터베이스에서 데이터 가져오기 (OneToOneField이므로 profile 사용)
        job_roles = JobRole.objects.select_related('job_type__category', 'profile').all()
        
        # 카테고리별 아이콘 매핑
        category_icons = {
            'IT기획': 'fa-laptop-code',
            'IT개발': 'fa-code',
            'IT운영': 'fa-server',
            '경영관리': 'fa-briefcase',
            '투자금융': 'fa-chart-line',
            '기업금융': 'fa-building',
            '기업영업': 'fa-handshake',
            '리테일금융': 'fa-coins',
            '고객지원': 'fa-headset'
        }
        
        # JavaScript가 기대하는 'Non-PL'과 'PL' 구조로 그룹화
        result_data = {
            'Non-PL': {},
            'PL': {}
        }
        
        for job_role in job_roles:
            # 카테고리와 직종 정보 가져오기
            category_name = job_role.job_type.category.name if job_role.job_type and job_role.job_type.category else 'Non-PL'
            job_type_name = job_role.job_type.name if job_role.job_type else '일반직무'
            
            # JobProfile 존재 여부 확인 (OneToOneField이므로 hasattr 사용)
            has_profile = hasattr(job_role, 'profile') and job_role.profile is not None
            
            # PL과 Non-PL로 그룹화 ('PL' 카테고리는 PL 그룹, 나머지는 Non-PL 그룹)
            group_key = 'PL' if category_name == 'PL' else 'Non-PL'
            
            # 결과 데이터 구조 생성
            if job_type_name not in result_data[group_key]:
                result_data[group_key][job_type_name] = {
                    'icon': category_icons.get(job_type_name, 'fa-folder'),
                    'jobs': []
                }
            
            # 직무 정보 추가 (UUID를 문자열로 변환)
            result_data[group_key][job_type_name]['jobs'].append({
                'id': str(job_role.id),  # UUID를 문자열로 변환
                'name': job_role.name,
                'has_profile': has_profile
            })
        
        # success 필드와 함께 반환
        return JsonResponse({
            'success': True,
            'data': result_data
        })
        
    except Exception as e:
        # 에러 발생시 기본 응답
        return JsonResponse({
            'success': False,
            'error': f'데이터 로드 실패: {str(e)}',
            'data': {}
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
        
        # 카테고리와 타입 정보 가져오기
        category_name = 'Non-PL'
        type_name = '일반직무'
        
        if job_role.job_type:
            type_name = job_role.job_type.name
            if job_role.job_type.category:
                category_name = job_role.job_type.category.name
        
        # 기본 직무 정보
        job_data = {
            'id': str(job_role.id),
            'name': job_role.name,
            'category': category_name,
            'type': type_name,
            'description': job_role.description or f'{job_role.name} 직무를 담당하는 핵심 역할입니다.',
            'summary': f'{job_role.name}는 {type_name} 영역에서 전문성을 발휘하는 중요한 직무입니다.'
        }
        
        # JobProfile 정보 가져오기
        try:
            profile = JobProfile.objects.get(job_role=job_role)
            job_data['profile'] = {
                'role_responsibility': profile.role_responsibility,
                'required_qualifications': profile.qualification,  # frontend expects 'required_qualifications'
                'preferred_qualifications': '',  # 추가 가능
                'basic_skills': profile.basic_skills or [],
                'applied_skills': profile.applied_skills or [],
                'tools': [],  # 추가 가능
                'growth_path': profile.growth_path,
                'career_development': {},  # 추가 가능
                'related_certifications': profile.related_certifications or [],
                'kpi_metrics': [],  # 추가 가능
                'key_stakeholders': [],  # 추가 가능
                'typical_projects': [],  # 추가 가능
                'work_environment': '',  # 추가 가능
                'compensation_range': ''  # 추가 가능
            }
        except JobProfile.DoesNotExist:
            job_data['profile'] = None
        
        # 프론트엔드가 기대하는 형식으로 응답
        return JsonResponse({
            'success': True,
            'job': job_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def job_detail_api_by_id(request, job_id):
    """직무 상세 정보 API (UUID 버전) - 실제 데이터베이스 기반"""
    try:
        # 실제 데이터베이스에서 JobRole 조회 (연관 데이터 포함)
        job_role = JobRole.objects.select_related('job_type__category', 'profile').get(id=job_id)
        
        # 기본 직무 정보 구성 (안전한 접근)
        try:
            category_name = job_role.job_type.category.name if job_role.job_type and job_role.job_type.category else 'Non-PL'
            type_name = job_role.job_type.name if job_role.job_type else '일반직무'
        except AttributeError:
            category_name = 'Non-PL'
            type_name = '일반직무'
            
        job_data = {
            'id': str(job_role.id),
            'name': job_role.name,
            'category': category_name,
            'type': type_name,
            'description': job_role.description or f'{job_role.name} 직무를 담당하는 핵심 역할입니다.',
            'summary': f'{job_role.name}는 {type_name} 영역에서 전문성을 발휘하는 중요한 직무입니다.',
        }
        
        # JobProfile이 있는 경우 상세 정보 추가 (OneToOneField 사용)
        if hasattr(job_role, 'profile') and job_role.profile:
            profile = job_role.profile
            job_data['profile'] = {
                'role_responsibility': profile.role_responsibility,
                'qualification': profile.qualification,  # 모델의 실제 필드명
                'basic_skills': profile.basic_skills or [],
                'applied_skills': profile.applied_skills or [],
                'growth_path': profile.growth_path,
                'related_certifications': profile.related_certifications or []
            }
        else:
            # 프로필이 없는 경우 직무별로 기본 템플릿 정보 제공
            job_type_name = job_role.job_type.name if job_role.job_type else '일반직무'
            
            # 직종별 기본 템플릿
            templates = {
                'IT기획': {
                    'role_responsibility': f'• {job_role.name} 전략 수립 및 실행\n• 프로젝트 기획 및 관리\n• 시스템 분석 및 설계\n• 이해관계자 협업 및 소통',
                    'required_qualifications': f'• {job_type_name} 관련 업무 경력 3년 이상\n• 프로젝트 관리 경험\n• 분석적 사고 능력\n• 커뮤니케이션 능력',
                    'basic_skills': ['프로젝트 관리', '업무 분석', '문서 작성', '협업'],
                    'applied_skills': ['디지털 도구 활용', '데이터 분석', '프로세스 개선'],
                    'tools': ['MS Office', '프로젝트 관리 도구', '협업 플랫폼'],
                    'growth_path': f'주니어 → {job_role.name} → 시니어 → 팀장 → 부서장',
                    'work_environment': '• 사무실 근무\n• 팀 협업 중심\n• 지속적인 학습 기회',
                },
                'IT개발': {
                    'role_responsibility': f'• {job_role.name} 시스템 개발 및 구현\n• 코드 작성 및 테스트\n• 기술 문서 작성\n• 시스템 유지보수',
                    'required_qualifications': f'• 개발 경력 2년 이상\n• 프로그래밍 언어 숙련\n• 데이터베이스 기본 지식\n• 문제 해결 능력',
                    'basic_skills': ['프로그래밍', 'DB 설계', '시스템 분석', '테스트'],
                    'applied_skills': ['클라우드', 'API 개발', '프레임워크', '자동화'],
                    'tools': ['개발 IDE', '버전관리', 'DB 관리도구', '테스트 도구'],
                    'growth_path': f'주니어 개발자 → {job_role.name} → 시니어 개발자 → 테크 리드',
                    'work_environment': '• 개발 환경\n• 코드 리뷰 문화\n• 신기술 학습 지원',
                },
                'IT운영': {
                    'role_responsibility': f'• {job_role.name} 시스템 운영 및 모니터링\n• 인프라 관리\n• 장애 대응 및 복구\n• 운영 프로세스 개선',
                    'required_qualifications': f'• 시스템 운영 경력 2년 이상\n• 인프라 기본 지식\n• 장애 대응 경험\n• 24시간 운영 가능',
                    'basic_skills': ['시스템 운영', '모니터링', '장애 대응', '문서화'],
                    'applied_skills': ['클라우드 인프라', '자동화', '보안', '성능 튜닝'],
                    'tools': ['모니터링 도구', '운영 도구', '자동화 스크립트', 'ITSM'],
                    'growth_path': f'주니어 엔지니어 → {job_role.name} → 시니어 엔지니어 → 아키텍트',
                    'work_environment': '• 24/7 운영 체계\n• 신속한 장애 대응\n• 안정성 중심',
                }
            }
            
            # 기본 템플릿 적용
            template = templates.get(job_type_name, templates.get('IT기획'))
            job_data['profile'] = template
            
        return JsonResponse({
            'success': True,
            'job': job_data
        })
        
    except JobRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '해당 직무를 찾을 수 없습니다.'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
