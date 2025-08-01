#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OK금융그룹 37개 직무기술서를 실제 Django DB에 저장
"""

import os
import sys
import django
import json
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from job_profiles.models import JobCategory, JobType, JobRole, JobProfile

def create_categories_and_types():
    """필요한 직군/직종 생성"""
    
    # OK금융그룹 직군/직종 구조
    structure = {
        'IT/디지털': {
            'IT기획': ['시스템기획'],
            'IT개발': ['시스템개발'],
            'IT운영': ['시스템관리', '서비스운영']
        },
        '경영지원': {
            '경영관리': [
                '감사', '인사관리', '인재개발', '경영지원', '비서', '홍보',
                '경영기획', '디자인', '리스크관리', '마케팅', '스포츠사무관리',
                '자금', '재무회계', '정보보안', '준법지원', '총무'
            ]
        },
        '금융': {
            '투자금융': ['투자금융'],
            '기업금융': ['기업영업기획', '기업여신심사', '기업여신관리'],
            '리테일금융': [
                '데이터분석', '디지털플랫폼', 'NPL사업기획', '리테일심사기획',
                '개인신용대출기획', '모기지기획', '예금기획', '예금영업'
            ]
        },
        '영업': {
            '기업영업': ['기업여신영업']
        },
        '고객서비스': {
            '고객지원': ['대출고객지원', '업무지원', '예금고객지원', '채권관리']
        }
    }
    
    categories = {}
    job_types = {}
    job_roles = {}
    
    for category_name, types in structure.items():
        # 직군 생성
        category, created = JobCategory.objects.get_or_create(
            name=category_name,
            defaults={
                'code': category_name[:3],
                'description': f'{category_name} 관련 업무'
            }
        )
        categories[category_name] = category
        if created:
            print(f"직군 생성: {category_name}")
        
        for job_type_name, roles in types.items():
            # 직종 생성
            job_type, created = JobType.objects.get_or_create(
                category=category,
                name=job_type_name,
                defaults={
                    'code': f"{category.code}{len(job_types)+1:02d}",
                    'description': f'{job_type_name} 관련 업무'
                }
            )
            job_types[job_type_name] = job_type
            if created:
                print(f"직종 생성: {category_name} > {job_type_name}")
            
            for role_name in roles:
                # 직무 생성
                job_role, created = JobRole.objects.get_or_create(
                    job_type=job_type,
                    name=role_name,
                    defaults={
                        'code': f"{job_type.code}{len(job_roles)+1:03d}",
                        'description': f'{role_name} 업무'
                    }
                )
                job_roles[role_name] = job_role
                if created:
                    print(f"직무 생성: {category_name} > {job_type_name} > {role_name}")
    
    return categories, job_types, job_roles


def import_job_profiles():
    """JSON에서 직무기술서 가져와 DB에 저장"""
    
    json_path = r"C:/Users/apro/OneDrive/Desktop/설명회자료/job_profile_complete/json/ok_job_profiles_complete.json"
    
    # 1. 직군/직종/직무 구조 생성
    print("1. 직군/직종/직무 구조 생성 중...")
    categories, job_types, job_roles = create_categories_and_types()
    
    # 2. JSON 파일 로드
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        jobs = data.get('jobs', [])
        print(f"2. JSON에서 {len(jobs)}개 직무 데이터 로드 완료")
        
    except FileNotFoundError:
        print(f"JSON 파일을 찾을 수 없습니다: {json_path}")
        return create_sample_profiles()
    
    # 3. 직무기술서 생성
    print("3. 직무기술서 생성 중...")
    
    # 직무명 표준화 매핑
    job_name_mapping = {
        'HRM': '인사관리',
        'HRD': '인재개발',
        'PR': '홍보',
        'IB금융': '투자금융',
        '여신영업': '기업여신영업',
        '데이터/통계': '데이터분석',
        '플랫폼/핀테크': '디지털플랫폼',
        'NPL영업기획': 'NPL사업기획',
        'PL기획': '개인신용대출기획',
        '모기지사업': '모기지기획',
        '수신기획': '예금기획',
        '수신영업': '예금영업',
        '여신고객지원': '대출고객지원',
        '사무지원': '업무지원',
        '수신고객지원': '예금고객지원',
        '채권관리지원': '채권관리'
    }
    
    success_count = 0
    for job_data in jobs:
        try:
            original_name = job_data.get('job_title', '').strip()
            if not original_name:
                continue
            
            # 직무명 표준화
            job_name = job_name_mapping.get(original_name, original_name)
            
            # JobRole 찾기
            job_role = job_roles.get(job_name)
            if not job_role:
                print(f"직무를 찾을 수 없음: {job_name} (원본: {original_name})")
                continue
            
            # 이미 직무기술서가 있는지 확인
            if JobProfile.objects.filter(job_role=job_role).exists():
                print(f"이미 존재하는 직무기술서: {job_name}")
                continue
            
            # 책임과 역할 정리
            responsibilities = job_data.get('responsibilities', [])
            role_responsibility = '\n'.join(responsibilities) if responsibilities else f'{job_name} 관련 업무 수행'
            
            # 자격요건 정리
            basic_skills = job_data.get('basic_skills', [])
            applied_skills = job_data.get('advanced_skills', [])
            
            qualification = f"기본 요구사항: {job_name} 관련 업무 경험"
            if basic_skills or applied_skills:
                qualification += f"\n추가 요구사항: 관련 분야 전문 지식"
            
            # JobProfile 생성
            job_profile = JobProfile.objects.create(
                job_role=job_role,
                role_responsibility=role_responsibility,
                qualification=qualification,
                basic_skills=basic_skills if isinstance(basic_skills, list) else [],
                applied_skills=applied_skills if isinstance(applied_skills, list) else [],
                is_active=True
            )
            
            success_count += 1
            print(f"직무기술서 생성: {job_name}")
            
        except Exception as e:
            print(f"오류 발생 ({original_name}): {str(e)}")
    
    print(f"\n직무기술서 생성 완료: {success_count}개")
    return success_count


def create_sample_profiles():
    """샘플 직무기술서 생성"""
    
    print("샘플 직무기술서 생성 중...")
    
    # 간단한 구조로 샘플 생성
    samples = [
        {
            'category': 'IT/디지털',
            'job_type': 'IT기획',
            'job_role': '시스템기획',
            'role_responsibility': 'IT 시스템 중장기 로드맵 수립\nIT 환경 분석 및 전략 수립\nIT 프로젝트 기획 및 관리',
            'qualification': 'IT 관련 학과 졸업\n시스템 분석 및 설계 경험\n프로젝트 관리 경험',
            'basic_skills': ['시스템 분석', '프로젝트 관리', 'IT 전략'],
            'applied_skills': ['디지털 트랜스포메이션', '신기술 도입']
        },
        {
            'category': 'IT/디지털',
            'job_type': 'IT개발',
            'job_role': '시스템개발',
            'role_responsibility': '시스템 설계 및 개발\n코딩 및 테스팅\n시스템 배포 및 유지보수',
            'qualification': '컴퓨터공학 관련 전공\n프로그래밍 언어 숙련\n개발 프로젝트 경험',
            'basic_skills': ['Java', 'Python', 'Database'],
            'applied_skills': ['클라우드', 'DevOps', '마이크로서비스']
        },
        {
            'category': '경영지원',
            'job_type': '경영관리',
            'job_role': '인사관리',
            'role_responsibility': '인사제도 설계 및 운영\n채용 및 교육 관리\n평가 및 보상 관리',
            'qualification': '인사 관련 업무 경험\nHR 시스템 활용 능력\n노무 관련 법규 지식',
            'basic_skills': ['채용관리', '교육기획', '평가제도'],
            'applied_skills': ['조직개발', 'HR Analytics', '노무관리']
        }
    ]
    
    success_count = 0
    
    for sample in samples:
        try:
            # 직군 생성
            category, _ = JobCategory.objects.get_or_create(
                name=sample['category'],
                defaults={'code': sample['category'][:3], 'description': f"{sample['category']} 관련 업무"}
            )
            
            # 직종 생성
            job_type, _ = JobType.objects.get_or_create(
                category=category,
                name=sample['job_type'],
                defaults={'code': f"{category.code}01", 'description': f"{sample['job_type']} 관련 업무"}
            )
            
            # 직무 생성
            job_role, _ = JobRole.objects.get_or_create(
                job_type=job_type,
                name=sample['job_role'],
                defaults={'code': f"{job_type.code}001", 'description': f"{sample['job_role']} 업무"}
            )
            
            # 직무기술서 생성 (중복 확인)
            if not JobProfile.objects.filter(job_role=job_role).exists():
                JobProfile.objects.create(
                    job_role=job_role,
                    role_responsibility=sample['role_responsibility'],
                    qualification=sample['qualification'],
                    basic_skills=sample['basic_skills'],
                    applied_skills=sample['applied_skills'],
                    is_active=True
                )
                success_count += 1
                print(f"샘플 생성: {sample['job_role']}")
            
        except Exception as e:
            print(f"샘플 생성 오류 ({sample['job_role']}): {str(e)}")
    
    return success_count


def main():
    """메인 실행 함수"""
    print("OK금융그룹 직무기술서 DB 저장 시작")
    print("="*50)
    
    # 기존 데이터 확인
    existing_profiles = JobProfile.objects.count()
    existing_roles = JobRole.objects.count()
    
    print(f"기존 직무: {existing_roles}개")
    print(f"기존 직무기술서: {existing_profiles}개")
    
    # 데이터 가져오기
    imported_count = import_job_profiles()
    
    # 결과 확인
    total_profiles = JobProfile.objects.count()
    total_roles = JobRole.objects.count()
    
    print(f"\n작업 완료!")
    print(f"총 직무: {total_roles}개")
    print(f"총 직무기술서: {total_profiles}개")
    print(f"새로 생성된 직무기술서: {imported_count}개")
    
    if total_profiles > 0:
        print(f"\n직무기술서 확인 URL:")
        print(f"  - 관리자: http://localhost:8000/admin/job_profiles/jobprofile/")
        print(f"  - 사용자: http://localhost:8000/job_profiles/")
        
        # 첫 번째 직무기술서 정보 출력
        first_profile = JobProfile.objects.first()
        if first_profile:
            print(f"\n첫 번째 직무기술서 예시:")
            print(f"  {first_profile.job_role.full_path}")
    else:
        print(f"\n직무기술서가 생성되지 않았습니다.")


if __name__ == '__main__':
    main()