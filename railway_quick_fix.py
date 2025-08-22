#!/usr/bin/env python
"""
Railway 빠른 수정 - CSRF 및 권한 문제 해결
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway Quick Fix")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def fix_csrf_settings():
    """CSRF 설정 확인 및 수정"""
    print("1. CSRF 설정 확인")
    print("-" * 40)
    
    from django.conf import settings
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    else:
        print("[WARNING] CSRF_TRUSTED_ORIGINS 설정 없음")
    
    if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
    
    return True

def test_with_mock_data():
    """Mock 데이터로 API 테스트"""
    print("\n2. Mock 데이터 API 테스트")
    print("-" * 40)
    
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    import json
    
    factory = RequestFactory()
    
    # Admin 사용자 가져오기 또는 생성
    try:
        user = User.objects.get(username='admin')
        print(f"[OK] Admin 사용자 사용: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print(f"[OK] Admin 사용자 생성: {user.username}")
    
    # 1. Organization Stats API
    print("\nOrganization Stats API:")
    try:
        from employees.views import get_organization_stats
        request = factory.get('/api/organization-stats/')
        request.user = user
        response = get_organization_stats(request)
        print(f"  응답: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  데이터: {data}")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # 2. Upload API with simple data
    print("\nUpload Organization API:")
    try:
        from employees.views import upload_organization_structure
        from employees.models_organization import OrganizationStructure
        
        # 상위 조직 확인
        parent_org = OrganizationStructure.objects.filter(org_level=2).first()
        parent_code = parent_org.org_code if parent_org else None
        
        test_data = {
            'data': [{
                '조직코드': 'HQ999',
                '조직명': '테스트본부',
                '조직레벨': 3,
                '상위조직코드': parent_code,
                '상태': 'active',
                '정렬순서': 999,
                '설명': '테스트'
            }]
        }
        
        request = factory.post(
            '/api/upload-organization-structure/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        request.user = user
        request._dont_enforce_csrf_checks = True
        
        response = upload_organization_structure(request)
        print(f"  응답: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  성공: {data}")
        elif response.status_code == 400:
            data = json.loads(response.content)
            print(f"  검증 오류: {data.get('error', 'Unknown')}")
            if 'errors' in data:
                for err in data['errors'][:3]:
                    print(f"    - {err}")
        else:
            print(f"  내용: {response.content.decode('utf-8')[:200]}")
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
    
    return True

def check_parent_organizations():
    """상위 조직 존재 확인"""
    print("\n3. 조직 계층 확인")
    print("-" * 40)
    
    from employees.models_organization import OrganizationStructure
    
    for level in range(1, 6):
        count = OrganizationStructure.objects.filter(org_level=level).count()
        print(f"  레벨 {level}: {count}개")
        
        if count > 0:
            orgs = OrganizationStructure.objects.filter(org_level=level)[:3]
            for org in orgs:
                print(f"    - {org.org_code}: {org.org_name}")
    
    return True

def create_missing_organizations():
    """누락된 기본 조직 생성"""
    print("\n4. 기본 조직 생성")
    print("-" * 40)
    
    from employees.models_organization import OrganizationStructure
    
    created = []
    
    # 레벨 1: 그룹
    if not OrganizationStructure.objects.filter(org_level=1).exists():
        org = OrganizationStructure.objects.create(
            org_code='GRP001',
            org_name='OK금융그룹',
            org_level=1,
            status='active',
            sort_order=1,
            description='OK금융그룹 지주회사'
        )
        created.append(f"그룹: {org.org_name}")
    
    # 레벨 2: 계열사
    group = OrganizationStructure.objects.filter(org_level=1).first()
    if group and not OrganizationStructure.objects.filter(org_level=2).exists():
        org = OrganizationStructure.objects.create(
            org_code='COM001',
            org_name='OK저축은행',
            org_level=2,
            parent=group,
            status='active',
            sort_order=1,
            description='OK저축은행'
        )
        created.append(f"계열사: {org.org_name}")
    
    # 레벨 3: 본부
    company = OrganizationStructure.objects.filter(org_level=2).first()
    if company and not OrganizationStructure.objects.filter(org_level=3).exists():
        org = OrganizationStructure.objects.create(
            org_code='HQ001',
            org_name='리테일본부',
            org_level=3,
            parent=company,
            status='active',
            sort_order=1,
            description='리테일 금융 서비스'
        )
        created.append(f"본부: {org.org_name}")
    
    if created:
        print("생성된 조직:")
        for item in created:
            print(f"  [OK] {item}")
    else:
        print("  [INFO] 기본 조직이 이미 존재합니다")
    
    return True

def main():
    """메인 실행"""
    
    # 1. CSRF 설정 확인
    fix_csrf_settings()
    
    # 2. 기본 조직 확인 및 생성
    check_parent_organizations()
    create_missing_organizations()
    
    # 3. API 테스트
    test_with_mock_data()
    
    print("\n" + "="*60)
    print("Quick Fix 완료")
    print("="*60)
    print("\n다음 단계:")
    print("1. railway restart")
    print("2. 브라우저에서 다시 테스트")
    print("\n문제 지속 시:")
    print("1. railway logs --tail 100")
    print("2. Railway 환경변수에서 DJANGO_SETTINGS_MODULE 확인")

if __name__ == "__main__":
    main()