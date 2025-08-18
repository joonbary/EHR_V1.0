#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
직무기술서 데이터 분석 스크립트
"""

import os
import sys
import django

# 한글 출력 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from job_profiles.models import JobCategory, JobType, JobRole, JobProfile
from django.db.models import Count, Q

def analyze_job_profile_data():
    print("=== 직무기술서 데이터 분석 ===\n")
    
    # 1. 전체 카운트
    print("[1] 전체 데이터 수")
    print(f"직군(JobCategory): {JobCategory.objects.count()}개")
    print(f"직종(JobType): {JobType.objects.count()}개")
    print(f"직무(JobRole): {JobRole.objects.count()}개")
    print(f"직무기술서(JobProfile): {JobProfile.objects.count()}개\n")
    
    # 2. is_active 상태별 분석
    print("[2] is_active 상태별 분석")
    for model, name in [(JobCategory, '직군'), (JobType, '직종'), (JobRole, '직무'), (JobProfile, '직무기술서')]:
        active_count = model.objects.filter(is_active=True).count()
        inactive_count = model.objects.filter(is_active=False).count()
        print(f"{name}:")
        print(f"  - 활성화: {active_count}개")
        print(f"  - 비활성화: {inactive_count}개")
        print(f"  - 총계: {active_count + inactive_count}개")
    
    # 3. 직무기술서 상세 분석
    print("\n[3] 직무기술서 상세 분석")
    
    # 활성화된 직무기술서
    active_profiles = JobProfile.objects.filter(is_active=True)
    print(f"활성화된 직무기술서: {active_profiles.count()}개")
    
    # 비활성화된 직무기술서
    inactive_profiles = JobProfile.objects.filter(is_active=False)
    print(f"비활성화된 직무기술서: {inactive_profiles.count()}개")
    
    # 연결된 직무의 is_active 상태 확인
    print("\n[4] 연관 데이터 활성화 상태 확인")
    
    # 비활성화된 직무와 연결된 직무기술서
    profiles_with_inactive_role = JobProfile.objects.filter(
        is_active=True,
        job_role__is_active=False
    ).count()
    print(f"활성화된 직무기술서 중 비활성화된 직무와 연결된 것: {profiles_with_inactive_role}개")
    
    # 비활성화된 직종과 연결된 직무기술서
    profiles_with_inactive_type = JobProfile.objects.filter(
        is_active=True,
        job_role__job_type__is_active=False
    ).count()
    print(f"활성화된 직무기술서 중 비활성화된 직종과 연결된 것: {profiles_with_inactive_type}개")
    
    # 비활성화된 직군과 연결된 직무기술서
    profiles_with_inactive_category = JobProfile.objects.filter(
        is_active=True,
        job_role__job_type__category__is_active=False
    ).count()
    print(f"활성화된 직무기술서 중 비활성화된 직군과 연결된 것: {profiles_with_inactive_category}개")
    
    # 5. 실제 화면에 표시될 직무기술서 수
    print("\n[5] 화면 표시 예상 수")
    
    # 일반 사용자 화면 (ESS)
    ess_visible_count = JobProfile.objects.filter(
        is_active=True,
        job_role__is_active=True,
        job_role__job_type__is_active=True,
        job_role__job_type__category__is_active=True
    ).count()
    print(f"일반 사용자(ESS) 화면에 표시될 직무기술서: {ess_visible_count}개")
    
    # 관리자 화면
    admin_visible_count = JobProfile.objects.count()
    print(f"관리자 화면에 표시될 직무기술서: {admin_visible_count}개")
    
    # 6. 샘플 데이터 출력
    print("\n[6] 비활성화된 데이터 샘플")
    inactive_samples = JobProfile.objects.filter(is_active=False)[:5]
    for profile in inactive_samples:
        print(f"  - {profile.job_role.name} (ID: {profile.id})")
    
    # 7. soft delete 필드 확인
    print("\n[7] Soft Delete 관련 필드 확인")
    print("JobProfile 모델 필드:")
    for field in JobProfile._meta.get_fields():
        if 'delete' in field.name.lower() or 'remove' in field.name.lower():
            print(f"  - {field.name}: {field.get_internal_type()}")
    
    # deleted_at 필드가 있는지 확인
    if hasattr(JobProfile, 'deleted_at'):
        deleted_count = JobProfile.objects.filter(deleted_at__isnull=False).count()
        print(f"삭제된(deleted_at이 설정된) 직무기술서: {deleted_count}개")
    else:
        print("deleted_at 필드 없음 - soft delete는 is_active로 관리됨")

if __name__ == '__main__':
    analyze_job_profile_data()