#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
직무기술서 UX 고도화 테스트 스크립트
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
from job_profiles.models import JobProfile

User = get_user_model()

def test_improved_features():
    print("=== 직무기술서 UX 개선 기능 테스트 ===\n")
    
    client = Client()
    
    # 로그인
    try:
        user = User.objects.get(username='admin')
        client.force_login(user)
        print("✅ 로그인 성공\n")
    except:
        print("❌ admin 사용자가 없습니다.\n")
        return
    
    # 1. 정렬 테스트
    print("[1] 정렬 기능 테스트")
    sort_tests = [
        ('name', 'asc', '직무명 오름차순'),
        ('name', 'desc', '직무명 내림차순'),
        ('created_at', 'desc', '생성일 최신순'),
        ('updated_at', 'desc', '수정일 최신순')
    ]
    
    for sort_by, order, desc in sort_tests:
        response = client.get('/job-profiles/', {
            'sort': sort_by,
            'order': order
        })
        print(f"  - {desc}: {response.status_code}")
    
    # 2. 다운로드 테스트
    print("\n[2] 다운로드 기능 테스트")
    
    # Excel 다운로드
    response = client.get('/job-profiles/download/', {'format': 'excel'})
    print(f"  - Excel 다운로드: {response.status_code}")
    if response.status_code == 200:
        print(f"    Content-Type: {response['Content-Type']}")
        print(f"    파일명: {response['Content-Disposition']}")
    
    # CSV 다운로드
    response = client.get('/job-profiles/download/', {'format': 'csv'})
    print(f"  - CSV 다운로드: {response.status_code}")
    
    # 3. 북마크 테스트
    print("\n[3] 북마크 기능 테스트")
    
    profile = JobProfile.objects.first()
    if profile:
        response = client.post(f'/job-profiles/bookmark/{profile.id}/')
        print(f"  - 북마크 토글: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    성공: {data.get('success')}")
            print(f"    북마크 상태: {data.get('bookmarked')}")
    
    # 4. 검색 카운트 테스트
    print("\n[4] 검색 결과 수 표시 테스트")
    
    response = client.get('/job-profiles/', {'q': 'IT'})
    if response.status_code == 200:
        context = response.context
        print(f"  - 검색어 'IT' 결과: {context.get('total_count')}건")
    
    # 5. 일괄 작업 테스트 (관리자)
    print("\n[5] 일괄 작업 테스트")
    
    profiles = JobProfile.objects.all()[:2]
    if profiles:
        profile_ids = [str(p.id) for p in profiles]
        
        response = client.post('/job-profiles/admin/bulk/update/', 
            json.dumps({
                'profile_ids': profile_ids,
                'action': 'deactivate'
            }),
            content_type='application/json'
        )
        print(f"  - 일괄 비활성화: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"    성공: {data.get('success')}")
            print(f"    메시지: {data.get('message')}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == '__main__':
    import json
    test_improved_features()
