from django.core.management.base import BaseCommand
from django.db import transaction
from job_profiles.models import JobCategory, JobType, JobRole, JobProfile
from employees.models import Employee
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Load OK Financial Group job profiles data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting job profiles data loading...'))
        
        # OK금융그룹 직무 데이터
        job_data = {
            'IT/디지털': {
                'IT기획': ['시스템기획'],
                'IT개발': ['시스템개발'],
                'IT운영': ['시스템관리', '서비스운영']
            },
            '경영지원': {
                '경영관리': ['감사', 'HRM', 'HRD', '경영지원', '비서', 'PR', '경영기획',
                           '디자인', '리스크관리', '마케팅', '스포츠사무관리', '자금',
                           '재무회계', '정보보안', '준법지원', '총무']
            },
            '금융': {
                '투자금융': ['IB금융'],
                '기업금융': ['기업영업기획', '기업여신심사', '기업여신관리'],
                '리테일금융': ['데이터/통계', '플랫폼/핀테크', 'NPL영업기획', '리테일심사기획',
                             'PL기획', '모기지기획', '수신기획', '수신영업']
            },
            '영업': {
                '기업영업': ['여신영업']
            },
            'PL': {
                '고객지원': ['여신고객지원', '사무지원', '수신고객지원', '채권관리지원']
            }
        }

        # 직무기술서 상세 데이터
        job_profiles_data = {
            '시스템기획': {
                'role_responsibility': '• 그룹 및 관계사 시스템 기획 및 구축\n• 디지털 혁신 프로젝트 기획 및 추진\n• 비즈니스 요구사항 분석 및 시스템 설계\n• IT 프로젝트 관리 및 성과 측정',
                'qualification': '• 정보시스템 기획 및 설계 경험\n• 프로젝트 관리 역량\n• 비즈니스 프로세스 이해\n• 커뮤니케이션 및 협업 능력',
                'basic_skills': ['시스템 분석 및 설계', '프로젝트 관리', '요구사항 분석', '문서화 능력'],
                'applied_skills': ['애자일 방법론', 'DevOps', '클라우드 아키텍처', 'AI/ML 이해'],
                'related_certifications': ['정보처리기사', 'PMP', 'CISA', 'ITIL']
            },
            '시스템개발': {
                'role_responsibility': '• 그룹 및 관계사 시스템 개발 및 구축\n• 애플리케이션 설계 및 프로그래밍\n• 시스템 테스트 및 품질 관리\n• 기술 문서 작성 및 유지보수',
                'qualification': '• 프로그래밍 언어 숙련도\n• 데이터베이스 설계 및 관리 능력\n• 웹/모바일 개발 경험\n• 문제 해결 능력',
                'basic_skills': ['Java/Python/JavaScript', 'Spring Framework', 'SQL', 'Git'],
                'applied_skills': ['MSA', 'Docker/Kubernetes', 'CI/CD', 'React/Vue.js'],
                'related_certifications': ['정보처리기사', 'OCJP', 'AWS Certified', 'CKA']
            },
            '시스템관리': {
                'role_responsibility': '• IT 인프라 운영 및 관리\n• 서버/네트워크/DB 관리\n• 시스템 모니터링 및 장애 대응\n• 보안 정책 수립 및 이행',
                'qualification': '• 시스템/네트워크 운영 경험\n• 트러블슈팅 능력\n• 보안 관련 지식\n• 24/7 운영 대응 능력',
                'basic_skills': ['Linux/Windows Server', '네트워크 관리', 'DB 관리', '모니터링 도구'],
                'applied_skills': ['클라우드 플랫폼', '자동화 스크립트', '컨테이너 기술', 'IaC'],
                'related_certifications': ['리눅스마스터', 'CCNA', 'OCP', 'AWS SysOps']
            },
            '서비스운영': {
                'role_responsibility': '• 디지털 서비스 운영 관리\n• 서비스 품질 모니터링 및 개선\n• 고객 요구사항 분석 및 대응\n• 운영 프로세스 최적화',
                'qualification': '• 서비스 운영 경험\n• 데이터 분석 능력\n• 고객 중심 사고\n• 프로세스 개선 역량',
                'basic_skills': ['서비스 운영 관리', '데이터 분석', 'ITSM', '품질 관리'],
                'applied_skills': ['애자일 운영', 'SRE', 'APM 도구', '자동화'],
                'related_certifications': ['ITIL', 'ITSM', 'SRE', 'Agile']
            },
            'HRM': {
                'role_responsibility': '• 인사 정책 수립 및 운영\n• 채용 및 인재 관리\n• 성과 관리 및 보상 체계 운영\n• 조직 문화 개선 활동',
                'qualification': '• 인사 관리 경험\n• 노동법 및 규정 이해\n• 데이터 분석 능력\n• 커뮤니케이션 스킬',
                'basic_skills': ['인사 관리', '채용 프로세스', '성과 관리', '보상 설계'],
                'applied_skills': ['HR Analytics', 'Talent Management', '조직 개발', 'Change Management'],
                'related_certifications': ['공인노무사', 'SHRM-CP', 'PHR', 'HR Analytics']
            },
            'HRD': {
                'role_responsibility': '• 교육 체계 수립 및 운영\n• 리더십 및 직무 교육 프로그램 개발\n• 조직 역량 진단 및 개발\n• 경력 개발 지원',
                'qualification': '• 교육 기획 및 운영 경험\n• 교수 설계 능력\n• 디지털 러닝 이해\n• 퍼실리테이션 스킬',
                'basic_skills': ['교육 기획', '교수 설계', '강의 스킬', '평가 설계'],
                'applied_skills': ['e-Learning', 'Microlearning', 'AI 교육', '조직 개발'],
                'related_certifications': ['HRD 자격증', 'ATD', 'CPLP', '평생교육사']
            },
            '여신영업': {
                'role_responsibility': '• 기업 고객 여신 영업\n• 신규 고객 발굴 및 관리\n• 여신 상품 제안 및 협상\n• 리스크 관리 및 사후 관리',
                'qualification': '• 기업 금융 영업 경험\n• 재무 분석 능력\n• 협상 및 설득력\n• 리스크 관리 이해',
                'basic_skills': ['여신 심사', '재무 분석', '영업 기법', '고객 관리'],
                'applied_skills': ['산업 분석', 'Deal Structuring', '디지털 영업', 'CRM'],
                'related_certifications': ['여신심사역', '신용분석사', 'CFA', 'FRM']
            }
        }

        try:
            with transaction.atomic():
                # 시스템 사용자 생성 또는 가져오기
                system_user, _ = Employee.objects.get_or_create(
                    email='system@okfg.com',
                    defaults={
                        'name': 'System',
                        'department': 'IT',
                        'position': 'System'
                    }
                )

                created_count = 0
                
                # 직군별 처리
                for category_name, job_types in job_data.items():
                    # JobCategory 생성
                    category, _ = JobCategory.objects.get_or_create(
                        name=category_name,
                        defaults={
                            'code': category_name[:3].upper(),
                            'description': f'{category_name} 직군',
                            'is_active': True
                        }
                    )
                    
                    # 직종별 처리
                    for type_name, roles in job_types.items():
                        # JobType 생성
                        job_type, _ = JobType.objects.get_or_create(
                            category=category,
                            name=type_name,
                            defaults={
                                'code': type_name[:4].upper(),
                                'description': f'{type_name} 직종',
                                'is_active': True
                            }
                        )
                        
                        # 직무별 처리
                        for role_name in roles:
                            # JobRole 생성
                            job_role, _ = JobRole.objects.get_or_create(
                                job_type=job_type,
                                name=role_name,
                                defaults={
                                    'code': role_name[:5].upper().replace('/', ''),
                                    'description': f'{role_name} 직무',
                                    'is_active': True
                                }
                            )
                            
                            # JobProfile 생성 (상세 데이터가 있는 경우)
                            if role_name in job_profiles_data:
                                profile_data = job_profiles_data[role_name]
                                
                                job_profile, created = JobProfile.objects.get_or_create(
                                    job_role=job_role,
                                    defaults={
                                        'role_responsibility': profile_data['role_responsibility'],
                                        'qualification': profile_data['qualification'],
                                        'basic_skills': profile_data['basic_skills'],
                                        'applied_skills': profile_data['applied_skills'],
                                        'related_certifications': profile_data['related_certifications'],
                                        'growth_path': f'{role_name} → 시니어 {role_name} → 팀장 → 부서장',
                                        'created_by': system_user,
                                        'updated_by': system_user
                                    }
                                )
                                
                                if created:
                                    created_count += 1
                                    self.stdout.write(f'Created profile: {category_name} > {type_name} > {role_name}')
                            else:
                                # 기본 프로필 생성
                                job_profile, created = JobProfile.objects.get_or_create(
                                    job_role=job_role,
                                    defaults={
                                        'role_responsibility': f'{role_name} 관련 업무 수행',
                                        'qualification': f'{role_name} 관련 경험 및 역량',
                                        'basic_skills': [f'{role_name} 기본 역량'],
                                        'applied_skills': [f'{role_name} 응용 역량'],
                                        'related_certifications': ['관련 자격증'],
                                        'growth_path': f'{role_name} → 시니어 {role_name} → 팀장 → 부서장',
                                        'created_by': system_user,
                                        'updated_by': system_user
                                    }
                                )
                                
                                if created:
                                    created_count += 1
                                    self.stdout.write(f'Created basic profile: {category_name} > {type_name} > {role_name}')

                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nSuccessfully loaded job profiles data!\n'
                        f'Total profiles created: {created_count}\n'
                        f'Total categories: {JobCategory.objects.count()}\n'
                        f'Total types: {JobType.objects.count()}\n'
                        f'Total roles: {JobRole.objects.count()}\n'
                        f'Total profiles: {JobProfile.objects.count()}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading job profiles: {str(e)}')
            )
            raise