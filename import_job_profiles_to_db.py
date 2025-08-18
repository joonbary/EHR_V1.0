#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
추출된 직무기술서 데이터를 Django 데이터베이스에 실제 저장
"""

import os
import sys
import django
import json
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from job_profiles.models import JobProfile

def import_job_profiles_from_json():
    """JSON 파일에서 직무 프로필을 DB로 가져오기"""
    
    json_path = r"C:/Users/apro/OneDrive/Desktop/설명회자료/job_profile_complete/json/ok_job_profiles_complete.json"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        jobs = data.get('jobs', [])
        
        print(f"총 {len(jobs)}개 직무 프로필 가져오기 시작...")
        
        # 기존 데이터 확인
        existing_count = JobProfile.objects.count()
        print(f"기존 DB 직무 프로필: {existing_count}개")
        
        success_count = 0
        error_count = 0
        
        for job_data in jobs:
            try:
                # 직무명이 이미 존재하는지 확인
                job_title = job_data.get('job_title', '').strip()
                if not job_title:
                    print(f"⚠️  직무명이 없는 데이터 건너뜀: {job_data}")
                    continue
                
                # 중복 확인
                if JobProfile.objects.filter(job_title=job_title).exists():
                    print(f"이미 존재하는 직무: {job_title}")
                    continue
                
                # 카테고리 매핑
                category_mapping = {
                    'Non-PL': '정규직',
                    'PL': '파트타임'
                }
                
                # 직종 카테고리 매핑
                job_type_mapping = {
                    'IT기획': 'IT/디지털',
                    'IT개발': 'IT/디지털', 
                    'IT운영': 'IT/디지털',
                    '경영관리': '경영지원',
                    '투자금융': '금융',
                    '기업금융': '금융',
                    '기업영업': '영업',
                    '리테일금융': '금융',
                    '고객지원': '고객서비스'
                }
                
                # JobProfile 객체 생성
                job_profile = JobProfile(
                    job_title=job_title,
                    job_type=job_data.get('job_type', '기타'),
                    job_category=job_type_mapping.get(job_data.get('job_type', ''), '기타'),
                    description='\n'.join(job_data.get('responsibilities', [])),
                    requirements=f"필수역량:\n" + '\n'.join(job_data.get('basic_skills', [])) + 
                               f"\n\n우대역량:\n" + '\n'.join(job_data.get('advanced_skills', [])),
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                job_profile.save()
                success_count += 1
                print(f"저장 완료: {job_title}")
                
            except Exception as e:
                error_count += 1
                print(f"❌ 저장 실패 ({job_data.get('job_title', 'Unknown')}): {str(e)}")
        
        print(f"\n가져오기 완료!")
        print(f"성공: {success_count}개")
        print(f"실패: {error_count}개")
        print(f"총 DB 직무 프로필: {JobProfile.objects.count()}개")
        
        return success_count
        
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {json_path}")
        return 0
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return 0


def create_sample_job_profiles():
    """샘플 직무 프로필 생성 (JSON 파일이 없는 경우)"""
    
    sample_jobs = [
        {
            'job_title': '시스템기획',
            'job_type': 'IT기획',
            'job_category': 'IT/디지털',
            'description': 'IT 시스템 중장기 로드맵 수립, IT 환경분석, IT 프로젝트 기획, IT 신기술 서베이, IT 프로젝트 지원',
            'requirements': '필수역량: IT 전략기획, 프로젝트 관리, 시스템 분석\n우대역량: 디지털 트랜스포메이션, 신기술 트렌드 분석'
        },
        {
            'job_title': '시스템개발',
            'job_type': 'IT개발',
            'job_category': 'IT/디지털',
            'description': '시스템 설계 및 개발, 코딩, 테스팅, 배포, 유지보수',
            'requirements': '필수역량: 프로그래밍 언어, 데이터베이스, 시스템 아키텍처\n우대역량: 클라우드, DevOps, 마이크로서비스'
        },
        {
            'job_title': '인사관리',
            'job_type': '경영관리',
            'job_category': '경영지원',
            'description': '인사제도 운영, 채용, 교육, 평가, 보상 관리',
            'requirements': '필수역량: 인사법규, 채용관리, 교육기획\n우대역량: HR 시스템, 조직개발, 노무관리'
        }
    ]
    
    print("샘플 직무 프로필 생성 중...")
    
    success_count = 0
    for job_data in sample_jobs:
        try:
            # 중복 확인
            if JobProfile.objects.filter(job_title=job_data['job_title']).exists():
                print(f"이미 존재하는 직무: {job_data['job_title']}")
                continue
            
            job_profile = JobProfile(**job_data)
            job_profile.save()
            success_count += 1
            print(f"샘플 생성: {job_data['job_title']}")
            
        except Exception as e:
            print(f"❌ 샘플 생성 실패 ({job_data['job_title']}): {str(e)}")
    
    return success_count


def main():
    """메인 실행 함수"""
    print("직무기술서 데이터베이스 가져오기 시작")
    print("="*50)
    
    # 1. JSON 파일에서 가져오기 시도
    imported_count = import_job_profiles_from_json()
    
    # 2. JSON 파일이 없거나 실패한 경우 샘플 데이터 생성
    if imported_count == 0:
        print("\nJSON 파일을 찾을 수 없어 샘플 데이터를 생성합니다...")
        sample_count = create_sample_job_profiles()
        imported_count = sample_count
    
    # 3. 결과 확인
    total_count = JobProfile.objects.count()
    print(f"\n작업 완료!")
    print(f"현재 DB 총 직무 프로필: {total_count}개")
    
    if total_count > 0:
        print(f"\n이제 다음 URL에서 직무기술서를 확인할 수 있습니다:")
        print(f"   http://localhost:8000/job_profiles/")
        print(f"   http://localhost:8000/admin/job_profiles/jobprofile/")
    else:
        print(f"\n직무 프로필이 없습니다. job_profiles/models.py 모델을 확인해주세요.")


if __name__ == '__main__':
    main()