"""
성장레벨 인증 샘플 데이터 생성
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from certifications.models import GrowthLevelRequirement, JobLevelRequirement
from job_profiles.models import JobProfile
from trainings.models import TrainingCategory, TrainingCourse, SkillTrainingMapping


def create_growth_level_requirements():
    """성장레벨별 기본 요건 생성"""
    
    levels = [
        {
            'level': 'Lv.1',
            'level_name': '신입',
            'min_evaluation_grade': 'C',
            'consecutive_evaluations': 1,
            'required_courses': [],
            'required_course_categories': {},
            'min_training_hours': 0,
            'required_skills': [],
            'skill_proficiency_level': 'BASIC',
            'min_years_in_level': 0,
            'min_total_years': 0,
            'description': '신입 직원 기본 레벨'
        },
        {
            'level': 'Lv.2',
            'level_name': '일반',
            'min_evaluation_grade': 'B',
            'consecutive_evaluations': 1,
            'required_courses': ['신입사원교육'],
            'required_course_categories': {'공통역량': 1},
            'min_training_hours': 40,
            'required_skills': ['업무기초', '팀워크'],
            'skill_proficiency_level': 'INTERMEDIATE',
            'min_years_in_level': 1,
            'min_total_years': 1,
            'description': '기본 업무 수행 가능 레벨'
        },
        {
            'level': 'Lv.3',
            'level_name': '전문가',
            'min_evaluation_grade': 'B+',
            'consecutive_evaluations': 2,
            'required_courses': ['성과관리전략', '리더십기초'],
            'required_course_categories': {'리더십': 1, '직무역량': 2},
            'min_training_hours': 80,
            'required_skills': ['성과관리', '전략수립', '조직운영'],
            'skill_proficiency_level': 'ADVANCED',
            'min_years_in_level': 2,
            'min_total_years': 3,
            'description': '전문성을 갖춘 핵심 인재 레벨'
        },
        {
            'level': 'Lv.4',
            'level_name': '리더',
            'min_evaluation_grade': 'A',
            'consecutive_evaluations': 2,
            'required_courses': ['리더십고급', '전략경영'],
            'required_course_categories': {'리더십': 2, '전략': 1},
            'min_training_hours': 120,
            'required_skills': ['리더십', '전략수립', '조직운영', '성과관리'],
            'skill_proficiency_level': 'ADVANCED',
            'min_years_in_level': 2,
            'min_total_years': 5,
            'description': '조직을 이끄는 리더 레벨'
        },
        {
            'level': 'Lv.5',
            'level_name': '임원',
            'min_evaluation_grade': 'A+',
            'consecutive_evaluations': 3,
            'required_courses': ['임원리더십', '경영전략'],
            'required_course_categories': {'임원역량': 2, '경영': 2},
            'min_training_hours': 160,
            'required_skills': ['경영전략', '조직운영', '리더십', '의사결정'],
            'skill_proficiency_level': 'EXPERT',
            'min_years_in_level': 3,
            'min_total_years': 10,
            'description': '최고 경영진 레벨'
        }
    ]
    
    for level_data in levels:
        GrowthLevelRequirement.objects.get_or_create(
            level=level_data['level'],
            defaults=level_data
        )
    
    print(f"Created {len(levels)} growth level requirements")


def create_training_categories():
    """교육 카테고리 생성"""
    categories = [
        {'name': '공통역량', 'description': '모든 직원이 갖추어야 할 기본 역량'},
        {'name': '리더십', 'description': '리더십 개발 및 조직 관리 역량'},
        {'name': '직무역량', 'description': '직무별 전문 역량'},
        {'name': '전략', 'description': '전략 수립 및 실행 역량'},
        {'name': '임원역량', 'description': '임원급 필수 역량'},
        {'name': '경영', 'description': '경영 전반에 대한 이해와 실행'},
    ]
    
    for cat in categories:
        TrainingCategory.objects.get_or_create(
            name=cat['name'],
            defaults=cat
        )
    
    print(f"Created {len(categories)} training categories")


def create_sample_courses():
    """샘플 교육과정 생성"""
    
    # 카테고리 조회
    categories = {cat.name: cat for cat in TrainingCategory.objects.all()}
    
    courses = [
        # 공통역량
        {
            'course_code': 'COM-001',
            'title': '신입사원교육',
            'category': categories.get('공통역량'),
            'description': '신입사원을 위한 기본 교육',
            'objectives': ['회사 이해', '기본 업무 스킬', '조직 문화 적응'],
            'related_skills': ['업무기초', '팀워크', '커뮤니케이션'],
            'skill_level': 'BASIC',
            'duration_hours': 40,
            'course_type': 'OFFLINE',
            'is_mandatory': True,
            'certification_eligible': True,
            'growth_level_impact': {'Lv.2': 0.3}
        },
        
        # 리더십
        {
            'course_code': 'LDR-001',
            'title': '리더십기초',
            'category': categories.get('리더십'),
            'description': '예비 리더를 위한 기초 리더십 교육',
            'objectives': ['리더십 이론', '팀 관리', '동기부여'],
            'related_skills': ['리더십', '팀관리', '커뮤니케이션'],
            'skill_level': 'INTERMEDIATE',
            'duration_hours': 24,
            'course_type': 'BLENDED',
            'certification_eligible': True,
            'growth_level_impact': {'Lv.3': 0.2}
        },
        {
            'course_code': 'LDR-002',
            'title': '리더십고급',
            'category': categories.get('리더십'),
            'description': '중간관리자를 위한 고급 리더십 교육',
            'objectives': ['전략적 리더십', '변화관리', '성과관리'],
            'related_skills': ['리더십', '전략수립', '성과관리', '조직운영'],
            'skill_level': 'ADVANCED',
            'duration_hours': 32,
            'course_type': 'OFFLINE',
            'certification_eligible': True,
            'growth_level_impact': {'Lv.4': 0.2}
        },
        
        # 직무역량
        {
            'course_code': 'JOB-001',
            'title': '성과관리전략',
            'category': categories.get('직무역량'),
            'description': '효과적인 성과관리 전략 수립',
            'objectives': ['성과지표 설정', 'KPI 관리', '평가 피드백'],
            'related_skills': ['성과관리', '데이터분석', '커뮤니케이션'],
            'skill_level': 'INTERMEDIATE',
            'duration_hours': 16,
            'course_type': 'ONLINE',
            'certification_eligible': True,
            'growth_level_impact': {'Lv.3': 0.2}
        },
        {
            'course_code': 'JOB-002',
            'title': '조직운영실무',
            'category': categories.get('직무역량'),
            'description': '조직 운영의 실무적 접근',
            'objectives': ['조직 설계', '프로세스 개선', '인력 관리'],
            'related_skills': ['조직운영', '프로세스관리', '인사관리'],
            'skill_level': 'ADVANCED',
            'duration_hours': 24,
            'course_type': 'BLENDED',
            'growth_level_impact': {'Lv.3': 0.15, 'Lv.4': 0.1}
        },
        
        # 전략
        {
            'course_code': 'STR-001',
            'title': '전략경영',
            'category': categories.get('전략'),
            'description': '경영 전략 수립과 실행',
            'objectives': ['전략 프레임워크', '시장 분석', '전략 실행'],
            'related_skills': ['전략수립', '시장분석', '의사결정'],
            'skill_level': 'ADVANCED',
            'duration_hours': 40,
            'course_type': 'OFFLINE',
            'certification_eligible': True,
            'growth_level_impact': {'Lv.4': 0.2}
        },
        
        # 임원역량
        {
            'course_code': 'EXE-001',
            'title': '임원리더십',
            'category': categories.get('임원역량'),
            'description': '임원급 리더십 역량 개발',
            'objectives': ['비전 수립', '조직 문화', '대외 관계'],
            'related_skills': ['경영전략', '리더십', '의사결정', '비전수립'],
            'skill_level': 'EXPERT',
            'duration_hours': 48,
            'course_type': 'OFFLINE',
            'certification_eligible': True,
            'growth_level_impact': {'Lv.5': 0.25}
        },
        {
            'course_code': 'EXE-002',
            'title': '경영전략',
            'category': categories.get('경영'),
            'description': '최고경영진을 위한 경영전략',
            'objectives': ['글로벌 경영', 'M&A 전략', '혁신 경영'],
            'related_skills': ['경영전략', '글로벌비즈니스', 'M&A', '혁신'],
            'skill_level': 'EXPERT',
            'duration_hours': 60,
            'course_type': 'OFFLINE',
            'certification_eligible': True,
            'growth_level_impact': {'Lv.5': 0.3}
        }
    ]
    
    for course_data in courses:
        TrainingCourse.objects.get_or_create(
            course_code=course_data['course_code'],
            defaults=course_data
        )
    
    print(f"Created {len(courses)} training courses")


def create_skill_mappings():
    """스킬-교육 매핑 생성"""
    
    # 스킬별 관련 교육 매핑
    skill_mappings = [
        {
            'skill_name': '리더십',
            'skill_category': '공통',
            'course_codes': ['LDR-001', 'LDR-002', 'EXE-001'],
            'relevance_score': 1.0,
            'is_core_skill': True
        },
        {
            'skill_name': '성과관리',
            'skill_category': '관리',
            'course_codes': ['JOB-001', 'LDR-002'],
            'relevance_score': 0.9,
            'is_core_skill': True
        },
        {
            'skill_name': '전략수립',
            'skill_category': '전략',
            'course_codes': ['STR-001', 'LDR-002', 'EXE-002'],
            'relevance_score': 1.0,
            'is_core_skill': True
        },
        {
            'skill_name': '조직운영',
            'skill_category': '관리',
            'course_codes': ['JOB-002', 'LDR-002'],
            'relevance_score': 0.9,
            'is_core_skill': True
        },
        {
            'skill_name': '경영전략',
            'skill_category': '경영',
            'course_codes': ['EXE-001', 'EXE-002', 'STR-001'],
            'relevance_score': 1.0,
            'is_core_skill': True
        }
    ]
    
    for mapping_data in skill_mappings:
        # 스킬 매핑 생성
        skill_mapping, created = SkillTrainingMapping.objects.get_or_create(
            skill_name=mapping_data['skill_name'],
            defaults={
                'skill_category': mapping_data['skill_category'],
                'relevance_score': mapping_data['relevance_score'],
                'is_core_skill': mapping_data['is_core_skill']
            }
        )
        
        # 관련 교육과정 연결
        if created:
            courses = TrainingCourse.objects.filter(
                course_code__in=mapping_data['course_codes']
            )
            skill_mapping.courses.set(courses)
    
    print(f"Created {len(skill_mappings)} skill mappings")


def create_job_level_requirements():
    """직무별 레벨 요건 생성"""
    
    # 몇 가지 대표 직무에 대한 요건 생성
    job_requirements = [
        {
            'job_name': '팀장',
            'required_level': 'Lv.3',
            'job_specific_courses': ['조직운영실무'],
            'job_specific_skills': ['팀관리', '프로젝트관리'],
            'override_eval_grade': ''  # 기본값 사용
        },
        {
            'job_name': '본부장',
            'required_level': 'Lv.4',
            'job_specific_courses': ['전략경영'],
            'job_specific_skills': ['사업전략', '조직관리'],
            'override_eval_grade': 'A'
        },
        {
            'job_name': '임원',
            'required_level': 'Lv.5',
            'job_specific_courses': ['임원리더십', '경영전략'],
            'job_specific_skills': ['경영판단', '비전수립'],
            'override_eval_grade': 'A+'
        }
    ]
    
    for req_data in job_requirements:
        # 해당 이름을 포함하는 직무 찾기
        job_profiles = JobProfile.objects.filter(
            job_role__name__icontains=req_data['job_name']
        )
        
        for job_profile in job_profiles[:3]:  # 각 타입별로 최대 3개만
            JobLevelRequirement.objects.get_or_create(
                job_profile=job_profile,
                required_growth_level=req_data['required_level'],
                defaults={
                    'job_specific_courses': req_data['job_specific_courses'],
                    'job_specific_skills': req_data['job_specific_skills'],
                    'override_eval_grade': req_data['override_eval_grade']
                }
            )
    
    print(f"Created job level requirements")


if __name__ == '__main__':
    print("Creating certification sample data...")
    
    # 1. 성장레벨 요건 생성
    create_growth_level_requirements()
    
    # 2. 교육 카테고리 생성
    create_training_categories()
    
    # 3. 샘플 교육과정 생성
    create_sample_courses()
    
    # 4. 스킬-교육 매핑 생성
    create_skill_mappings()
    
    # 5. 직무별 레벨 요건 생성
    create_job_level_requirements()
    
    print("Certification sample data created successfully!")