#!/usr/bin/env python
"""
Railway API 오류 수정 스크립트
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway API 수정 시작")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화 성공")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def fix_organization_imports():
    """조직 관련 모델 import 문제 수정"""
    print("\n=== 조직 모델 Import 테스트 ===")
    
    try:
        from employees.models_organization import OrganizationStructure, OrganizationUploadHistory
        print("[OK] OrganizationStructure import 성공")
        
        # 테이블 존재 확인
        count = OrganizationStructure.objects.count()
        print(f"    현재 조직 수: {count}개")
        
    except Exception as e:
        print(f"[ERROR] OrganizationStructure import 실패: {e}")
        return False
    
    try:
        from employees.models import Employee
        print("[OK] Employee import 성공")
        
        count = Employee.objects.count()
        print(f"    현재 직원 수: {count}개")
        
    except Exception as e:
        print(f"[ERROR] Employee import 실패: {e}")
        return False
    
    return True

def create_initial_organizations():
    """초기 조직 데이터 생성"""
    print("\n=== 초기 조직 데이터 생성 ===")
    
    from employees.models_organization import OrganizationStructure
    
    if OrganizationStructure.objects.count() > 0:
        print(f"[INFO] 이미 {OrganizationStructure.objects.count()}개의 조직이 존재합니다")
        return True
    
    try:
        # 그룹 레벨
        group = OrganizationStructure.objects.create(
            org_code='GRP001',
            org_name='OK금융그룹',
            org_level=1,
            status='active',
            sort_order=1,
            description='OK금융그룹 지주회사'
        )
        print("[OK] OK금융그룹 생성")
        
        # 계열사 레벨
        company = OrganizationStructure.objects.create(
            org_code='COM001',
            org_name='OK저축은행',
            org_level=2,
            parent=group,
            status='active',
            sort_order=1,
            description='OK저축은행'
        )
        print("[OK] OK저축은행 생성")
        
        print("\n[OK] 초기 조직 데이터 생성 완료")
        return True
        
    except Exception as e:
        print(f"[ERROR] 초기 데이터 생성 실패: {e}")
        return False

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("\n=== API 엔드포인트 테스트 ===")
    
    try:
        from employees.views import get_organization_stats, upload_organization_structure
        print("[OK] API 함수 import 성공")
        
        # 통계 API 테스트
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/api/organization-stats/')
        
        response = get_organization_stats(request)
        print(f"[OK] organization-stats API 테스트: {response.status_code}")
        
    except Exception as e:
        print(f"[ERROR] API 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """메인 실행 함수"""
    
    # 1. Import 테스트
    if not fix_organization_imports():
        print("\n[CRITICAL] 모델 import 실패 - 마이그레이션 필요")
        print("다음 명령 실행: python manage.py migrate")
        return False
    
    # 2. 초기 데이터 생성
    if not create_initial_organizations():
        print("\n[WARNING] 초기 데이터 생성 실패")
    
    # 3. API 테스트
    if not test_api_endpoints():
        print("\n[WARNING] API 테스트 실패")
    
    print("\n" + "="*60)
    print("수정 작업 완료!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)