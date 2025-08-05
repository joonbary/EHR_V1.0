#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
직무기술서 UX 기능 테스트 스크립트
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# 한글 출력 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from job_profiles.models import JobCategory, JobType, JobRole, JobProfile

User = get_user_model()

def test_job_profile_ux():
    print("=== 직무기술서 UX 기능 테스트 ===\n")
    
    # 테스트 클라이언트 생성
    client = Client()
    
    # 1. 비로그인 상태 접근 테스트
    print("[1] 비로그인 상태 접근 테스트")
    response = client.get('/job-profiles/')
    print(f"상태 코드: {response.status_code}")
    if response.status_code == 302:
        print("로그인 페이지로 리다이렉트 (정상)")
    else:
        print("비정상 - 로그인 체크 필요")
    
    # 테스트 사용자 로그인
    try:
        user = User.objects.get(username='admin')
        client.force_login(user)
        print("\n로그인 성공 (admin)\n")
    except User.DoesNotExist:
        print("\n❌ admin 사용자가 없습니다.\n")
        return
    
    # 2. 기본 목록 페이지 테스트
    print("[2] 기본 목록 페이지 테스트")
    response = client.get('/job-profiles/')
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        context = response.context
        
        # 페이지네이션 확인
        if 'page_obj' in context:
            page_obj = context['page_obj']
            print(f"페이지네이션 활성화: Yes")
            print(f"전체 항목 수: {page_obj.paginator.count}")
            print(f"페이지당 항목 수: {page_obj.paginator.per_page}")
            print(f"현재 페이지: {page_obj.number}")
            print(f"전체 페이지 수: {page_obj.paginator.num_pages}")
            print(f"현재 페이지 항목 수: {len(page_obj)}")
        
        # 필터 옵션 확인
        if 'categories' in context:
            print(f"\n직군 필터 옵션: {context['categories'].count()}개")
        
        # 검색 기능 확인
        content = response.content.decode('utf-8')
        if '<input type="text" name="q"' in content:
            print("검색 입력 필드: 있음")
        else:
            print("검색 입력 필드: 없음")
    
    # 3. 검색 기능 테스트
    print("\n[3] 검색 기능 테스트")
    test_queries = ['IT', '개발', '관리', 'test']
    
    for query in test_queries:
        response = client.get('/job-profiles/', {'q': query})
        if response.status_code == 200:
            page_obj = response.context.get('page_obj')
            if page_obj:
                print(f"검색어 '{query}': {page_obj.paginator.count}개 결과")
    
    # 4. 필터 기능 테스트
    print("\n[4] 필터 기능 테스트")
    
    # 첫 번째 카테고리로 필터
    first_category = JobCategory.objects.first()
    if first_category:
        response = client.get('/job-profiles/', {'category': str(first_category.id)})
        if response.status_code == 200:
            page_obj = response.context.get('page_obj')
            if page_obj:
                print(f"직군 '{first_category.name}' 필터: {page_obj.paginator.count}개 결과")
    
    # 5. 페이지네이션 테스트
    print("\n[5] 페이지네이션 테스트")
    
    # 2페이지 접근
    response = client.get('/job-profiles/', {'page': '2'})
    print(f"2페이지 접근: {response.status_code}")
    
    # 잘못된 페이지 번호
    response = client.get('/job-profiles/', {'page': '999'})
    print(f"잘못된 페이지(999) 접근: {response.status_code}")
    
    # 6. 정렬 기능 확인
    print("\n[6] 정렬 기능 확인")
    content = response.content.decode('utf-8')
    
    sort_options = ['name', 'created_at', 'updated_at']
    sort_found = False
    for option in sort_options:
        if f'sort={option}' in content or f'order={option}' in content:
            sort_found = True
            print(f"정렬 옵션 '{option}' 발견")
    
    if not sort_found:
        print("정렬 기능 없음 (미구현)")
    
    # 7. 관리자 페이지 접근
    print("\n[7] 관리자 페이지 비교")
    
    # 일반 사용자 페이지
    response = client.get('/job-profiles/')
    if response.status_code == 200:
        user_count = response.context.get('page_obj').paginator.count if 'page_obj' in response.context else 0
        print(f"일반 사용자 페이지: {user_count}개 표시")
    
    # 관리자 페이지
    response = client.get('/job-profiles/admin/')
    if response.status_code == 200:
        admin_count = response.context.get('total_count', 0)
        print(f"관리자 페이지: {admin_count}개 표시")
        
        # is_active 필터 확인
        content = response.content.decode('utf-8')
        if 'name="is_active"' in content:
            print("is_active 필터: 있음")
        else:
            print("is_active 필터: 없음")
    
    # 8. API 엔드포인트 확인
    print("\n[8] API 엔드포인트 확인")
    
    # API URL 시도
    api_urls = [
        '/api/job-profiles/',
        '/api/v1/job-profiles/',
        '/job-profiles/api/list/',
    ]
    
    for url in api_urls:
        response = client.get(url)
        print(f"{url}: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  JSON 응답: {len(data.get('results', data))}개 항목")
            except:
                print("  JSON 파싱 실패")

def check_missing_features():
    print("\n\n=== 누락된 UX 기능 체크리스트 ===")
    
    features = {
        "검색 기능": True,  # 구현됨
        "페이지네이션": True,  # 구현됨
        "직군/직종 필터": True,  # 구현됨
        "정렬 기능": False,  # 미구현
        "엑셀 다운로드": False,  # 미구현
        "일괄 작업": False,  # 미구현
        "즐겨찾기": False,  # 미구현
        "최근 본 항목": False,  # 미구현
        "상세 검색": False,  # 미구현
        "모바일 반응형": None,  # 확인 필요
    }
    
    for feature, status in features.items():
        if status is True:
            print(f"✅ {feature}: 구현됨")
        elif status is False:
            print(f"❌ {feature}: 미구현")
        else:
            print(f"❓ {feature}: 확인 필요")

if __name__ == '__main__':
    test_job_profile_ux()
    check_missing_features()