from django.core.management.base import BaseCommand
from django.db import transaction
from job_profiles.models import JobCategory, JobType, JobRole, JobProfile
import uuid


class Command(BaseCommand):
    help = 'Load simple job profiles data without employee dependency'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading job profiles data...')
        
        try:
            with transaction.atomic():
                # IT/디지털 직군
                it_category, _ = JobCategory.objects.get_or_create(
                    name='IT/디지털',
                    defaults={
                        'code': 'IT',
                        'description': 'IT 및 디지털 관련 직군',
                        'is_active': True
                    }
                )
                
                # IT기획 직종
                it_planning, _ = JobType.objects.get_or_create(
                    category=it_category,
                    name='IT기획',
                    defaults={
                        'code': 'ITP',
                        'description': 'IT 시스템 기획',
                        'is_active': True
                    }
                )
                
                # 시스템기획 직무
                sys_planning_role, _ = JobRole.objects.get_or_create(
                    job_type=it_planning,
                    name='시스템기획',
                    defaults={
                        'code': 'SYSP',
                        'description': '시스템 기획 및 설계',
                        'is_active': True
                    }
                )
                
                # IT개발 직종
                it_dev, _ = JobType.objects.get_or_create(
                    category=it_category,
                    name='IT개발',
                    defaults={
                        'code': 'ITD',
                        'description': 'IT 시스템 개발',
                        'is_active': True
                    }
                )
                
                # 시스템개발 직무
                sys_dev_role, _ = JobRole.objects.get_or_create(
                    job_type=it_dev,
                    name='시스템개발',
                    defaults={
                        'code': 'SYSD',
                        'description': '시스템 개발 및 구축',
                        'is_active': True
                    }
                )
                
                # 경영지원 직군
                mgmt_category, _ = JobCategory.objects.get_or_create(
                    name='경영지원',
                    defaults={
                        'code': 'MGMT',
                        'description': '경영 지원 관련 직군',
                        'is_active': True
                    }
                )
                
                # 경영관리 직종
                mgmt_type, _ = JobType.objects.get_or_create(
                    category=mgmt_category,
                    name='경영관리',
                    defaults={
                        'code': 'MGT',
                        'description': '경영 관리',
                        'is_active': True
                    }
                )
                
                # HRM 직무
                hrm_role, _ = JobRole.objects.get_or_create(
                    job_type=mgmt_type,
                    name='HRM',
                    defaults={
                        'code': 'HRM',
                        'description': '인사 관리',
                        'is_active': True
                    }
                )
                
                # 영업 직군
                sales_category, _ = JobCategory.objects.get_or_create(
                    name='영업',
                    defaults={
                        'code': 'SALES',
                        'description': '영업 관련 직군',
                        'is_active': True
                    }
                )
                
                # 기업영업 직종
                corp_sales, _ = JobType.objects.get_or_create(
                    category=sales_category,
                    name='기업영업',
                    defaults={
                        'code': 'CORP',
                        'description': '기업 영업',
                        'is_active': True
                    }
                )
                
                # 여신영업 직무
                loan_sales_role, _ = JobRole.objects.get_or_create(
                    job_type=corp_sales,
                    name='여신영업',
                    defaults={
                        'code': 'LOAN',
                        'description': '기업 여신 영업',
                        'is_active': True
                    }
                )
                
                # JobProfile 생성 (created_by, updated_by 없이)
                profiles = [
                    {
                        'role': sys_planning_role,
                        'data': {
                            'role_responsibility': '• 그룹 및 관계사 시스템 기획 및 구축\n• 디지털 혁신 프로젝트 기획 및 추진\n• 비즈니스 요구사항 분석 및 시스템 설계',
                            'qualification': '• 정보시스템 기획 및 설계 경험\n• 프로젝트 관리 역량\n• 비즈니스 프로세스 이해',
                            'basic_skills': ['시스템 분석', '프로젝트 관리', '요구사항 분석'],
                            'applied_skills': ['애자일 방법론', 'DevOps', '클라우드 아키텍처'],
                            'related_certifications': ['정보처리기사', 'PMP', 'CISA'],
                            'growth_path': '시스템기획 → 시니어 시스템기획 → 팀장 → 부서장'
                        }
                    },
                    {
                        'role': sys_dev_role,
                        'data': {
                            'role_responsibility': '• 그룹 및 관계사 시스템 개발 및 구축\n• 애플리케이션 설계 및 프로그래밍\n• 시스템 테스트 및 품질 관리',
                            'qualification': '• 프로그래밍 언어 숙련도\n• 데이터베이스 설계 및 관리 능력\n• 웹/모바일 개발 경험',
                            'basic_skills': ['Java/Python', 'Spring Framework', 'SQL'],
                            'applied_skills': ['MSA', 'Docker/Kubernetes', 'CI/CD'],
                            'related_certifications': ['정보처리기사', 'OCJP', 'AWS Certified'],
                            'growth_path': '시스템개발 → 시니어 개발자 → 테크리드 → CTO'
                        }
                    },
                    {
                        'role': hrm_role,
                        'data': {
                            'role_responsibility': '• 인사 정책 수립 및 운영\n• 채용 및 인재 관리\n• 성과 관리 및 보상 체계 운영',
                            'qualification': '• 인사 관리 경험\n• 노동법 및 규정 이해\n• 데이터 분석 능력',
                            'basic_skills': ['인사 관리', '채용 프로세스', '성과 관리'],
                            'applied_skills': ['HR Analytics', 'Talent Management', '조직 개발'],
                            'related_certifications': ['공인노무사', 'SHRM-CP', 'PHR'],
                            'growth_path': 'HRM → HRM 팀장 → HR 부서장 → CHRO'
                        }
                    },
                    {
                        'role': loan_sales_role,
                        'data': {
                            'role_responsibility': '• 기업 고객 여신 영업\n• 신규 고객 발굴 및 관리\n• 여신 상품 제안 및 협상',
                            'qualification': '• 기업 금융 영업 경험\n• 재무 분석 능력\n• 협상 및 설득력',
                            'basic_skills': ['여신 심사', '재무 분석', '영업 기법'],
                            'applied_skills': ['산업 분석', 'Deal Structuring', 'CRM'],
                            'related_certifications': ['여신심사역', '신용분석사', 'CFA'],
                            'growth_path': '여신영업 → 여신영업 팀장 → 지점장 → 본부장'
                        }
                    }
                ]
                
                created_count = 0
                for profile_info in profiles:
                    profile, created = JobProfile.objects.get_or_create(
                        job_role=profile_info['role'],
                        defaults=profile_info['data']
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(f"Created profile for: {profile_info['role'].name}")
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nSuccessfully loaded job profiles!\n'
                        f'Created {created_count} new profiles\n'
                        f'Total categories: {JobCategory.objects.count()}\n'
                        f'Total types: {JobType.objects.count()}\n'
                        f'Total roles: {JobRole.objects.count()}\n'
                        f'Total profiles: {JobProfile.objects.count()}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise