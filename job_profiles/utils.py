"""
Job Profiles Utilities - Common functions for job profile operations
"""
from typing import Dict, Any, Optional
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class JobProfileService:
    """Service class for job profile operations"""
    
    DEFAULT_TEMPLATES = {
        'IT기획': {
            'role_responsibility': '• {job_name} 전략 수립 및 실행\n• 프로젝트 기획 및 관리\n• 시스템 분석 및 설계\n• 이해관계자 협업 및 소통',
            'required_qualifications': '• {job_type} 관련 업무 경력 3년 이상\n• 프로젝트 관리 경험\n• 분석적 사고 능력\n• 커뮤니케이션 능력',
            'basic_skills': ['프로젝트 관리', '업무 분석', '문서 작성', '협업'],
            'applied_skills': ['디지털 도구 활용', '데이터 분석', '프로세스 개선'],
            'tools': ['MS Office', '프로젝트 관리 도구', '협업 플랫폼'],
            'growth_path': '주니어 → {job_name} → 시니어 → 팀장 → 부서장',
            'work_environment': '• 사무실 근무\n• 팀 협업 중심\n• 지속적인 학습 기회',
        },
        'IT개발': {
            'role_responsibility': '• {job_name} 시스템 개발 및 구현\n• 코드 작성 및 테스트\n• 기술 문서 작성\n• 시스템 유지보수',
            'required_qualifications': '• 개발 경력 2년 이상\n• 프로그래밍 언어 숙련\n• 데이터베이스 기본 지식\n• 문제 해결 능력',
            'basic_skills': ['프로그래밍', 'DB 설계', '시스템 분석', '테스트'],
            'applied_skills': ['클라우드', 'API 개발', '프레임워크', '자동화'],
            'tools': ['개발 IDE', '버전관리', 'DB 관리도구', '테스트 도구'],
            'growth_path': '주니어 개발자 → {job_name} → 시니어 개발자 → 테크 리드',
            'work_environment': '• 개발 환경\n• 코드 리뷰 문화\n• 신기술 학습 지원',
        },
        'IT운영': {
            'role_responsibility': '• {job_name} 시스템 운영 및 모니터링\n• 인프라 관리\n• 장애 대응 및 복구\n• 운영 프로세스 개선',
            'required_qualifications': '• 시스템 운영 경력 2년 이상\n• 인프라 기본 지식\n• 장애 대응 경험\n• 24시간 운영 가능',
            'basic_skills': ['시스템 운영', '모니터링', '장애 대응', '문서화'],
            'applied_skills': ['클라우드 인프라', '자동화', '보안', '성능 튜닝'],
            'tools': ['모니터링 도구', '운영 도구', '자동화 스크립트', 'ITSM'],
            'growth_path': '주니어 엔지니어 → {job_name} → 시니어 엔지니어 → 아키텍트',
            'work_environment': '• 24/7 운영 체계\n• 신속한 장애 대응\n• 안정성 중심',
        }
    }
    
    CATEGORY_ICONS = {
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
    
    @classmethod
    def get_job_role_data(cls, job_role, include_profile: bool = True) -> Dict[str, Any]:
        """
        Get formatted job role data
        
        Args:
            job_role: JobRole instance
            include_profile: Whether to include profile data
            
        Returns:
            Dictionary with job role information
        """
        try:
            # Safe attribute access
            category_name = 'Non-PL'
            type_name = '일반직무'
            
            if hasattr(job_role, 'job_type') and job_role.job_type:
                type_name = job_role.job_type.name
                if hasattr(job_role.job_type, 'category') and job_role.job_type.category:
                    category_name = job_role.job_type.category.name
            
            # Build base job data
            job_data = {
                'id': str(job_role.id),
                'name': job_role.name,
                'category': category_name,
                'type': type_name,
                'description': job_role.description or f'{job_role.name} 직무를 담당하는 핵심 역할입니다.',
                'summary': f'{job_role.name}는 {type_name} 영역에서 전문성을 발휘하는 중요한 직무입니다.'
            }
            
            # Add profile data if requested
            if include_profile:
                job_data['profile'] = cls.get_job_profile_data(job_role)
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error getting job role data: {e}")
            raise
    
    @classmethod
    def get_job_profile_data(cls, job_role) -> Optional[Dict[str, Any]]:
        """
        Get job profile data for a job role
        
        Args:
            job_role: JobRole instance
            
        Returns:
            Dictionary with profile data or None
        """
        # Check if profile exists (OneToOneField)
        if hasattr(job_role, 'profile') and job_role.profile:
            profile = job_role.profile
            return {
                'role_responsibility': profile.role_responsibility,
                'qualification': profile.qualification,
                'required_qualifications': profile.qualification,  # Alias for frontend
                'basic_skills': profile.basic_skills or [],
                'applied_skills': profile.applied_skills or [],
                'growth_path': profile.growth_path,
                'related_certifications': profile.related_certifications or [],
                'tools': [],  # Can be extended
                'career_development': {},  # Can be extended
                'kpi_metrics': [],  # Can be extended
                'key_stakeholders': [],  # Can be extended
                'typical_projects': [],  # Can be extended
                'work_environment': '',  # Can be extended
                'compensation_range': ''  # Can be extended
            }
        else:
            # Return template if no profile exists
            return cls.get_template_profile(job_role)
    
    @classmethod
    def get_template_profile(cls, job_role) -> Dict[str, Any]:
        """
        Get template profile for job role without profile
        
        Args:
            job_role: JobRole instance
            
        Returns:
            Dictionary with template profile data
        """
        job_type_name = '일반직무'
        if hasattr(job_role, 'job_type') and job_role.job_type:
            job_type_name = job_role.job_type.name
        
        # Get template or use IT기획 as default
        template = cls.DEFAULT_TEMPLATES.get(job_type_name, cls.DEFAULT_TEMPLATES['IT기획'])
        
        # Format template with job role name
        formatted_template = {}
        for key, value in template.items():
            if isinstance(value, str):
                formatted_template[key] = value.format(
                    job_name=job_role.name,
                    job_type=job_type_name
                )
            else:
                formatted_template[key] = value
        
        # Add additional fields for frontend compatibility
        formatted_template['qualification'] = formatted_template.get('required_qualifications', '')
        
        return formatted_template
    
    @classmethod
    def format_job_for_treemap(cls, job_role) -> Dict[str, Any]:
        """
        Format job role for treemap display
        
        Args:
            job_role: JobRole instance
            
        Returns:
            Dictionary with treemap-compatible format
        """
        return {
            'id': str(job_role.id),
            'name': job_role.name,
            'has_profile': hasattr(job_role, 'profile') and job_role.profile is not None
        }
    
    @classmethod
    def get_category_icon(cls, category_name: str) -> str:
        """
        Get icon for category
        
        Args:
            category_name: Category name
            
        Returns:
            Icon class string
        """
        return cls.CATEGORY_ICONS.get(category_name, 'fa-folder')
    
    @classmethod
    def create_api_response(
        cls,
        success: bool,
        data: Any = None,
        error: str = None,
        status: int = 200
    ) -> JsonResponse:
        """
        Create standardized API response
        
        Args:
            success: Success status
            data: Response data
            error: Error message
            status: HTTP status code
            
        Returns:
            JsonResponse object
        """
        response = {'success': success}
        
        if data is not None:
            response['data'] = data
        elif success:  # If success but no data, provide job key for compatibility
            response['job'] = data
            
        if error:
            response['error'] = error
        
        return JsonResponse(response, status=status)