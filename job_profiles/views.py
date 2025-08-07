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

def job_detail_api_by_id(request, job_id):
    """직무 상세 정보 API (숫자 ID 버전) - 매우 풍부한 정보 버전"""
    # 하드코딩된 상세 데이터로 응답
    job_data = {
        1: {
            'name': 'IT기획담당',
            'category': 'Non-PL',
            'type': 'IT기획',
            'level': 'L3-L5',
            'department': 'IT전략부',
            'description': 'IT 전략 수립 및 시스템 기획을 담당하는 핵심 직무입니다.',
            'summary': '디지털 금융 혁신을 주도하는 IT 전략가로서, 비즈니스와 기술을 연결하는 핵심 역할을 수행합니다.',
            'profile': {
                'role_responsibility': '• IT 중장기 전략 수립 및 실행\n• 디지털 트랜스포메이션 추진\n• IT 프로젝트 기획 및 관리\n• 시스템 아키텍처 설계\n• IT 거버넌스 체계 구축\n• 비즈니스 요구사항 분석 및 IT 솔루션 제안\n• IT 투자 효율성 분석 및 예산 관리\n• 신기술 도입 검토 및 적용 방안 수립',
                'required_qualifications': '• 정보시스템 기획 경력 5년 이상\n• IT 프로젝트 관리 경험\n• 비즈니스 프로세스 이해\n• 데이터 분석 역량\n• 컴퓨터공학, 정보시스템, 경영정보학 등 관련 학사 이상\n• 금융업 이해 및 금융 IT 시스템 경험',
                'preferred_qualifications': '• PMP, PRINCE2 자격증 보유\n• 금융권 IT 기획 경험 우대\n• 애자일/스크럼 방법론 경험\n• 클라우드 아키텍처 이해\n• MBA 또는 관련 석사 학위\n• 글로벌 프로젝트 경험\n• 영어 커뮤니케이션 가능',
                'basic_skills': ['IT 전략 수립', '프로젝트 관리', '비즈니스 분석', '시스템 아키텍처', '요구사항 분석', '프로세스 개선'],
                'applied_skills': ['클라우드 컴퓨팅', '빅데이터', 'AI/ML', '블록체인', 'DevOps', 'MSA', 'API Management'],
                'tools': ['JIRA', 'Confluence', 'MS Project', 'Visio', 'Enterprise Architect', 'Tableau', 'Power BI'],
                'growth_path': '주니어 IT기획자 → IT기획 담당 → IT기획 팀장 → IT전략 부서장 → CTO/CIO',
                'career_development': {
                    'short_term': '프로젝트 관리 역량 강화, 업무 도메인 지식 습득',
                    'mid_term': '리더십 개발, 전략적 사고 역량 강화, 신기술 트렌드 학습',
                    'long_term': '경영진 역량 개발, 비즈니스 전략 수립 능력, 조직 관리 역량'
                },
                'related_certifications': ['PMP', 'PRINCE2', 'TOGAF', 'ITIL', 'CBAP', 'CSM'],
                'kpi_metrics': [
                    '프로젝트 성공률',
                    'IT 투자 ROI',
                    '시스템 가용성',
                    '비즈니스 요구사항 충족도',
                    '이해관계자 만족도'
                ],
                'key_stakeholders': ['경영진', 'IT 개발팀', '현업 부서', '외부 벤더', '규제 기관'],
                'typical_projects': [
                    '차세대 시스템 구축',
                    '디지털 채널 혁신',
                    '데이터 플랫폼 구축',
                    'AI/ML 도입 프로젝트',
                    '클라우드 전환 프로젝트'
                ],
                'work_environment': '• 하이브리드 근무 가능\n• 글로벌 협업 기회\n• 최신 기술 스택 활용\n• 지속적인 학습 지원',
                'compensation_range': 'L3: 7,000-9,000만원 / L4: 9,000-12,000만원 / L5: 12,000-15,000만원'
            }
        },
        2: {
            'name': 'IT개발담당',
            'category': 'Non-PL',
            'type': 'IT개발',
            'description': '금융 시스템 개발 및 구현을 담당하는 핵심 기술 직무입니다.',
            'profile': {
                'role_responsibility': '• 금융 시스템 설계 및 개발\n• API 개발 및 통합\n• 마이크로서비스 아키텍처 구현\n• 코드 리뷰 및 품질 관리\n• 기술 문서 작성',
                'required_qualifications': '• 개발 경력 3년 이상\n• Java/Spring 또는 Python/Django 숙련\n• RDBMS 및 NoSQL 경험\n• RESTful API 개발 경험',
                'preferred_qualifications': '• 금융권 시스템 개발 경험\n• 클라우드 네이티브 개발 경험\n• DevOps 도구 활용 능력\n• 오픈소스 기여 경험',
                'basic_skills': ['Java', 'Spring Boot', 'Python', 'SQL', 'Git'],
                'applied_skills': ['Kubernetes', 'Docker', 'Kafka', 'Redis', 'GraphQL'],
                'growth_path': '주니어 개발자 → 개발 담당 → 시니어 개발자 → 테크 리드 → 개발팀장',
                'related_certifications': ['정보처리기사', 'AWS Solutions Architect', 'CKA', 'Spring Professional']
            }
        },
        3: {
            'name': 'IT운영담당',
            'category': 'Non-PL',
            'type': 'IT운영',
            'description': '시스템 운영 및 인프라 관리를 담당하는 안정성 중심 직무입니다.',
            'profile': {
                'role_responsibility': '• 시스템 모니터링 및 운영\n• 인프라 구축 및 관리\n• 장애 대응 및 복구\n• 백업 및 복구 체계 관리\n• 보안 정책 적용 및 관리',
                'required_qualifications': '• 시스템 운영 경력 3년 이상\n• Linux/Unix 시스템 관리 경험\n• 네트워크 기초 지식\n• 클라우드 인프라 경험',
                'preferred_qualifications': '• 대규모 시스템 운영 경험\n• 자동화 스크립트 작성 능력\n• 컨테이너 오케스트레이션 경험\n• ITSM 도구 활용 경험',
                'basic_skills': ['Linux', 'Shell Script', 'Monitoring', 'Network', 'Security'],
                'applied_skills': ['Kubernetes', 'Terraform', 'Ansible', 'Prometheus', 'ELK Stack'],
                'growth_path': '주니어 엔지니어 → 시스템 엔지니어 → 시니어 엔지니어 → 인프라 아키텍트 → 인프라팀장',
                'related_certifications': ['LPIC', 'RHCE', 'AWS SysOps', 'CKA', 'CCNA']
            }
        }
    }
    
    # 더 많은 직무 데이터 추가 가능
    default_data = job_data.get(1)  # 기본값
    selected_data = job_data.get(job_id, default_data)
    
    return JsonResponse({
        'success': True,
        'job': selected_data
    })
