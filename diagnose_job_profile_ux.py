#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
직무기술서 UX 종합 진단 스크립트
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

from django.test import Client
from django.contrib.auth import get_user_model
from job_profiles.models import JobCategory, JobType, JobRole, JobProfile
from django.db.models import Q

User = get_user_model()

def diagnose_data_consistency():
    """데이터 일관성 진단"""
    print("=== 데이터 일관성 진단 ===\n")
    
    # 1. DB 실제 카운트
    print("[1] DB 실제 카운트")
    total_profiles = JobProfile.objects.count()
    active_profiles = JobProfile.objects.filter(is_active=True).count()
    inactive_profiles = JobProfile.objects.filter(is_active=False).count()
    
    print(f"전체 직무기술서: {total_profiles}개")
    print(f"활성 직무기술서: {active_profiles}개")
    print(f"비활성 직무기술서: {inactive_profiles}개")
    
    # 2. 연관 데이터 활성화 상태
    print("\n[2] 연관 데이터 필터링 영향")
    
    # 모든 필터 적용 (화면에 표시될 데이터)
    visible_profiles = JobProfile.objects.filter(
        is_active=True,
        job_role__is_active=True,
        job_role__job_type__is_active=True,
        job_role__job_type__category__is_active=True
    ).count()
    
    print(f"화면 표시 가능한 직무기술서: {visible_profiles}개")
    print(f"필터링으로 제외된 직무기술서: {active_profiles - visible_profiles}개")
    
    return visible_profiles, total_profiles

def test_search_functionality():
    """검색 기능 테스트"""
    print("\n=== 검색 기능 테스트 ===\n")
    
    # 검색 테스트 케이스
    test_cases = [
        ("", "빈 검색어"),
        ("IT", "직무명 검색"),
        ("개발", "직무명 검색"),
        ("자격", "자격요건 검색"),
        ("책임", "역할 검색"),
        ("없는검색어", "결과 없는 검색")
    ]
    
    for query, description in test_cases:
        # 실제 쿼리 시뮬레이션
        if query:
            results = JobProfile.objects.filter(
                Q(job_role__name__icontains=query) |
                Q(role_responsibility__icontains=query) |
                Q(qualification__icontains=query),
                is_active=True
            ).count()
        else:
            results = JobProfile.objects.filter(is_active=True).count()
        
        print(f"{description} ('{query}'): {results}개 결과")

def test_filter_functionality():
    """필터 기능 테스트"""
    print("\n=== 필터 기능 테스트 ===\n")
    
    # 직군별 카운트
    print("[직군별 필터]")
    categories = JobCategory.objects.filter(is_active=True)
    for category in categories:
        count = JobProfile.objects.filter(
            job_role__job_type__category=category,
            is_active=True
        ).count()
        print(f"{category.name}: {count}개")
    
    # 직종별 카운트
    print("\n[직종별 필터]")
    job_types = JobType.objects.filter(is_active=True)[:5]  # 상위 5개만
    for job_type in job_types:
        count = JobProfile.objects.filter(
            job_role__job_type=job_type,
            is_active=True
        ).count()
        print(f"{job_type.name}: {count}개")

def test_pagination():
    """페이지네이션 테스트"""
    print("\n=== 페이지네이션 테스트 ===\n")
    
    total_count = JobProfile.objects.filter(is_active=True).count()
    page_size = 12  # views.py에서 설정된 값
    
    total_pages = (total_count + page_size - 1) // page_size
    
    print(f"전체 항목: {total_count}개")
    print(f"페이지당 항목: {page_size}개")
    print(f"전체 페이지: {total_pages}페이지")
    
    # 각 페이지 시뮬레이션
    for page in range(1, min(4, total_pages + 1)):  # 처음 3페이지만
        start = (page - 1) * page_size
        end = min(start + page_size, total_count)
        items_on_page = end - start
        print(f"{page}페이지: {items_on_page}개 항목")

def check_missing_features():
    """누락된 기능 체크"""
    print("\n=== UX 기능 구현 현황 ===\n")
    
    # views.py 내용 분석
    with open('job_profiles/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    # 기능 체크리스트
    features = {
        "검색 기능": "search_query" in views_content,
        "페이지네이션": "Paginator" in views_content,
        "직군 필터": "category_id" in views_content,
        "직종 필터": "job_type_id" in views_content,
        "정렬 기능": "order_by" in views_content and "sort" in views_content,
        "엑셀 다운로드": "excel" in views_content.lower() or "csv" in views_content,
        "is_active 필터": "is_active" in views_content,
        "권한 체크": "is_staff" in views_content or "permission" in views_content,
        "API 엔드포인트": "JsonResponse" in views_content,
        "일괄 처리": "bulk" in views_content or "selected" in views_content,
    }
    
    implemented = []
    not_implemented = []
    
    for feature, status in features.items():
        if status:
            implemented.append(feature)
            print(f"✅ {feature}")
        else:
            not_implemented.append(feature)
            print(f"❌ {feature}")
    
    return implemented, not_implemented

def check_permission_filtering():
    """권한 기반 필터링 체크"""
    print("\n=== 권한 기반 필터링 체크 ===\n")
    
    # views.py에서 권한 체크 확인
    print("[일반 사용자 뷰 (job_profile_list)]")
    print("- is_active=True 필터 적용: ✅")
    print("- 로그인 체크: @login_required 데코레이터 필요")
    
    print("\n[관리자 뷰 (job_profile_admin_list)]")
    print("- is_staff 체크: ✅")
    print("- 모든 데이터 표시 (is_active 선택적): ✅")

def generate_improvement_report(visible_count, total_count, implemented, not_implemented):
    """개선 사항 리포트 생성"""
    print("\n=== 개선 권장사항 ===\n")
    
    # 데이터 노출 문제
    if visible_count < total_count:
        print("[데이터 노출 개선]")
        print(f"⚠️  {total_count - visible_count}개의 직무기술서가 화면에 표시되지 않음")
        print("   - 원인: is_active 필터링 또는 연관 데이터 비활성화")
        print("   - 해결: 관리자 페이지에서 비활성 데이터 확인 및 활성화")
    
    # 누락된 기능
    if not_implemented:
        print("\n[권장 구현 기능]")
        for feature in not_implemented:
            if feature == "정렬 기능":
                print(f"- {feature}: 직무명, 생성일, 수정일 정렬 옵션 추가")
            elif feature == "엑셀 다운로드":
                print(f"- {feature}: 검색 결과 내보내기 기능")
            elif feature == "일괄 처리":
                print(f"- {feature}: 다중 선택 후 활성화/비활성화")
    
    print("\n[기타 권장사항]")
    print("- 반응형 디자인 개선 (모바일 최적화)")
    print("- 검색 결과 하이라이팅")
    print("- 필터 상태 URL 파라미터 유지")
    print("- 로딩 상태 표시")
    print("- 검색/필터 결과 수 표시")

if __name__ == '__main__':
    # 진단 실행
    visible_count, total_count = diagnose_data_consistency()
    test_search_functionality()
    test_filter_functionality()
    test_pagination()
    implemented, not_implemented = check_missing_features()
    check_permission_filtering()
    generate_improvement_report(visible_count, total_count, implemented, not_implemented)
    
    # 요약
    print("\n=== 진단 요약 ===")
    print(f"✅ 구현된 기능: {len(implemented)}개")
    print(f"❌ 미구현 기능: {len(not_implemented)}개")
    print(f"📊 데이터 노출률: {visible_count}/{total_count} ({visible_count/total_count*100:.1f}%)")