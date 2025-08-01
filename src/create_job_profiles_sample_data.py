import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from job_profiles.models import JobCategory, JobType, JobRole, JobProfile
from django.contrib.auth.models import User

# 관리자 계정 찾기
admin_user = User.objects.filter(is_superuser=True).first()

# 1. 직군(Category) 생성
categories = [
    {'code': 'MGMT', 'name': '경영지원', 'description': '경영/기획/인사/재무 등 경영지원 업무'},
    {'code': 'IT', 'name': 'IT/디지털', 'description': 'IT 기획, 개발, 운영 관련 업무'},
    {'code': 'SALES', 'name': '영업/마케팅', 'description': '영업, 마케팅, 고객관리 업무'},
]

created_categories = {}
for cat_data in categories:
    cat, created = JobCategory.objects.get_or_create(
        code=cat_data['code'],
        defaults={'name': cat_data['name'], 'description': cat_data['description']}
    )
    created_categories[cat_data['code']] = cat
    if created:
        print(f"Created category: {cat.name}")

# 2. 직종(Type) 생성
job_types_data = {
    'MGMT': [
        {'code': 'HR', 'name': '인사', 'description': '인사 관련 업무'},
        {'code': 'FIN', 'name': '재무', 'description': '재무/회계 관련 업무'},
        {'code': 'STRAT', 'name': '전략기획', 'description': '경영전략 및 기획 업무'},
    ],
    'IT': [
        {'code': 'PLAN', 'name': 'IT기획', 'description': 'IT 전략 및 기획 업무'},
        {'code': 'DEV', 'name': '시스템개발', 'description': '시스템 개발 및 구축 업무'},
        {'code': 'INFRA', 'name': 'IT인프라', 'description': 'IT 인프라 운영 및 관리'},
    ],
    'SALES': [
        {'code': 'B2B', 'name': '기업영업', 'description': 'B2B 영업 업무'},
        {'code': 'B2C', 'name': '개인영업', 'description': 'B2C 영업 업무'},
        {'code': 'MKT', 'name': '마케팅', 'description': '마케팅 전략 및 실행'},
    ]
}

created_types = {}
for cat_code, types in job_types_data.items():
    for type_data in types:
        job_type, created = JobType.objects.get_or_create(
            code=type_data['code'],
            defaults={
                'category': created_categories[cat_code],
                'name': type_data['name'],
                'description': type_data['description']
            }
        )
        created_types[type_data['code']] = job_type
        if created:
            print(f"Created job type: {job_type.name}")

# 3. 직무(Role) 및 직무기술서(Profile) 생성
job_profiles_data = [
    {
        'role': {
            'code': 'HR_MGR',
            'name': 'HRM',
            'job_type': 'HR',
            'description': '인적자원관리 전문가'
        },
        'profile': {
            'role_responsibility': '''• 인사 전략 수립 및 실행
• 채용, 교육, 평가, 보상 등 HR 전 영역 관리
• 조직문화 개선 및 직원 만족도 향상 프로그램 운영
• 노사관계 관리 및 노동법규 준수
• HR 시스템 및 프로세스 개선
• 인사 관련 정책 및 규정 수립/개정''',
            'qualification': '''• 학사 이상 (인사, 경영, 심리학 등 관련 전공 우대)
• HR 업무 경력 5년 이상
• 노동법 및 인사 관련 법규에 대한 이해
• 데이터 분석 및 HR Analytics 역량
• 커뮤니케이션 및 대인관계 능력 우수
• 영어 비즈니스 회화 가능자 우대''',
            'basic_skills': [
                '채용 프로세스 설계 및 운영',
                '교육체계 수립 및 운영',
                '성과평가 제도 설계',
                '보상체계 설계 및 운영',
                '노동법 및 관련 법규 지식',
                'HR 정보시스템 활용',
                '조직진단 및 분석',
                '커뮤니케이션 스킬'
            ],
            'applied_skills': [
                'HR Analytics 및 데이터 분석',
                '조직개발(OD) 방법론',
                'Talent Management',
                '리더십 개발 프로그램 설계',
                'Change Management',
                '글로벌 HR 관리',
                'Employer Branding',
                'HR Tech 트렌드 이해'
            ],
            'growth_path': '''Junior HR → HR Specialist → HR Manager → HR Team Leader → HR Director → CHRO''',
            'related_certifications': [
                '공인노무사',
                'PHR/SPHR (미국 HR 자격증)',
                'SHRM-CP/SHRM-SCP',
                '경영지도사(인적자원관리)',
                '산업카운슬러'
            ]
        }
    },
    {
        'role': {
            'code': 'IT_PLN',
            'name': 'IT기획',
            'job_type': 'PLAN',
            'description': 'IT 전략 및 기획 전문가'
        },
        'profile': {
            'role_responsibility': '''• IT 중장기 전략 및 로드맵 수립
• 디지털 트랜스포메이션 추진
• IT 프로젝트 기획 및 관리
• IT 예산 수립 및 관리
• IT 거버넌스 체계 구축 및 운영
• 신기술 도입 검토 및 적용 방안 수립
• IT 투자 효과 분석 및 성과 관리''',
            'qualification': '''• 학사 이상 (컴퓨터공학, 정보시스템, 경영학 등)
• IT 기획 또는 컨설팅 경력 5년 이상
• IT 프로젝트 관리 경험
• 비즈니스 프로세스에 대한 이해
• 최신 IT 트렌드에 대한 지식
• 분석적 사고 및 문제해결 능력
• 프레젠테이션 및 커뮤니케이션 능력''',
            'basic_skills': [
                'IT 전략 수립 방법론',
                '프로젝트 관리 (PMP, Agile)',
                '비즈니스 프로세스 분석',
                'IT 아키텍처 이해',
                '예산 수립 및 관리',
                'ROI 분석',
                '문서 작성 능력',
                '이해관계자 관리'
            ],
            'applied_skills': [
                'Digital Transformation 전략',
                'EA(Enterprise Architecture)',
                'IT Governance Framework',
                'Cloud Migration 전략',
                'Data Strategy',
                'AI/ML 도입 전략',
                'IT Service Management',
                'Vendor Management'
            ],
            'growth_path': '''IT Planner → Senior IT Planner → IT Planning Manager → IT Strategy Team Leader → CTO/CIO''',
            'related_certifications': [
                'PMP (Project Management Professional)',
                'ITIL Foundation',
                'TOGAF',
                'CBAP (Certified Business Analysis Professional)',
                'CSM (Certified Scrum Master)',
                'Cloud 관련 자격증 (AWS, Azure, GCP)'
            ]
        }
    },
    {
        'role': {
            'code': 'SYS_DEV',
            'name': '시스템개발',
            'job_type': 'DEV',
            'description': '시스템 개발 전문가'
        },
        'profile': {
            'role_responsibility': '''• 업무 요구사항 분석 및 시스템 설계
• 애플리케이션 개발 및 테스트
• 시스템 통합 및 배포
• 기존 시스템 유지보수 및 개선
• 개발 표준 및 가이드라인 수립
• 코드 리뷰 및 품질 관리
• 기술 문서 작성 및 관리''',
            'qualification': '''• 학사 이상 (컴퓨터공학, 소프트웨어공학 등)
• 개발 경력 3년 이상
• 주요 프로그래밍 언어 숙련도
• 데이터베이스 및 SQL 활용 능력
• 웹/모바일 개발 경험
• 문제 해결 능력 및 분석적 사고
• 팀워크 및 커뮤니케이션 능력''',
            'basic_skills': [
                'Java, Python, JavaScript 등 프로그래밍',
                'Spring, Django, React 등 프레임워크',
                'RDBMS (Oracle, MySQL, PostgreSQL)',
                'RESTful API 설계 및 개발',
                'Git 버전 관리',
                'Unit Testing',
                'Debugging 및 Troubleshooting',
                'Agile/Scrum 개발 방법론'
            ],
            'applied_skills': [
                'Microservices Architecture',
                'Container (Docker, Kubernetes)',
                'CI/CD Pipeline',
                'Cloud Native Development',
                'NoSQL Database',
                'Message Queue (Kafka, RabbitMQ)',
                'DevOps 실무',
                'Performance Tuning'
            ],
            'growth_path': '''Junior Developer → Developer → Senior Developer → Tech Lead → Development Manager → CTO''',
            'related_certifications': [
                '정보처리기사',
                'OCP (Oracle Certified Professional)',
                'AWS Certified Developer',
                'CKA (Certified Kubernetes Administrator)',
                'Spring Professional Certification',
                'Python Institute Certifications'
            ]
        }
    }
]

# 직무 및 직무기술서 생성
for data in job_profiles_data:
    role_data = data['role']
    profile_data = data['profile']
    
    # 직무 생성
    job_role, created = JobRole.objects.get_or_create(
        code=role_data['code'],
        defaults={
            'name': role_data['name'],
            'job_type': created_types[role_data['job_type']],
            'description': role_data['description']
        }
    )
    
    if created:
        print(f"Created job role: {job_role.name}")
        
        # 직무기술서 생성
        job_profile = JobProfile.objects.create(
            job_role=job_role,
            role_responsibility=profile_data['role_responsibility'],
            qualification=profile_data['qualification'],
            basic_skills=profile_data['basic_skills'],
            applied_skills=profile_data['applied_skills'],
            growth_path=profile_data['growth_path'],
            related_certifications=profile_data['related_certifications'],
            created_by=admin_user,
            updated_by=admin_user
        )
        print(f"Created job profile for: {job_role.name}")

print("\n샘플 데이터 생성 완료!")
print(f"직군: {JobCategory.objects.count()}개")
print(f"직종: {JobType.objects.count()}개")
print(f"직무: {JobRole.objects.count()}개")
print(f"직무기술서: {JobProfile.objects.count()}개")