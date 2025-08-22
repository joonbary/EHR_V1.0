#!/usr/bin/env python
"""
Railway API 500 오류 최종 수정
"""

import os
import sys
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway API 500 오류 수정")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection

def verify_table_columns():
    """테이블 컬럼 확인 및 수정"""
    print("1. 테이블 컬럼 확인")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 현재 컬럼 확인
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees_organizationstructure'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        print(f"현재 컬럼 ({len(columns)}개):")
        for col in column_names:
            print(f"  - {col}")
        
        # 필수 컬럼 확인 및 추가
        required_columns = {
            'group_name': 'VARCHAR(100)',
            'company_name': 'VARCHAR(100)',
            'headquarters_name': 'VARCHAR(100)',
            'department_name': 'VARCHAR(100)',
            'team_name': 'VARCHAR(100)',
            'establishment_date': 'DATE',
            'leader_id': 'INTEGER',
            'created_by_id': 'INTEGER'
        }
        
        print("\n누락된 컬럼 추가:")
        for col_name, col_type in required_columns.items():
            if col_name not in column_names:
                try:
                    if col_type == 'INTEGER':
                        cursor.execute(f"""
                            ALTER TABLE employees_organizationstructure 
                            ADD COLUMN IF NOT EXISTS {col_name} {col_type};
                        """)
                    else:
                        cursor.execute(f"""
                            ALTER TABLE employees_organizationstructure 
                            ADD COLUMN IF NOT EXISTS {col_name} {col_type};
                        """)
                    print(f"  [OK] {col_name} 추가")
                except Exception as e:
                    print(f"  [INFO] {col_name}: {str(e)[:50]}")

def test_model_import():
    """모델 import 테스트"""
    print("\n2. 모델 Import 테스트")
    print("-" * 40)
    
    try:
        from employees.models_organization import OrganizationStructure
        
        # 데이터 조회 테스트
        count = OrganizationStructure.objects.count()
        print(f"[OK] OrganizationStructure 모델 로드 성공")
        print(f"  현재 조직 수: {count}개")
        
        # 첫 번째 레코드 조회
        if count > 0:
            org = OrganizationStructure.objects.first()
            print(f"  첫 번째 조직: {org.org_name} (코드: {org.org_code})")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 모델 import 실패: {e}")
        traceback.print_exc()
        return False

def test_api_direct():
    """API 직접 테스트"""
    print("\n3. API 직접 테스트")
    print("-" * 40)
    
    try:
        from employees.views import get_organization_stats
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        
        factory = RequestFactory()
        request = factory.get('/api/organization-stats/')
        
        # Mock user
        try:
            user = User.objects.first()
            if user:
                request.user = user
        except:
            pass
        
        # API 호출
        print("get_organization_stats 호출...")
        response = get_organization_stats(request)
        
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            import json
            data = json.loads(response.content)
            print("[SUCCESS] API 정상 작동!")
            print(f"  - 전체 조직: {data.get('total_orgs', 0)}")
            print(f"  - 활성 조직: {data.get('active_orgs', 0)}")
            print(f"  - 전체 직원: {data.get('total_employees', 0)}")
            return True
        else:
            print(f"[ERROR] API 오류")
            print(f"응답 내용: {response.content.decode('utf-8')}")
            return False
            
    except Exception as e:
        print(f"[ERROR] API 테스트 실패:")
        print(str(e))
        traceback.print_exc()
        return False

def fix_api_import():
    """API views.py 수정"""
    print("\n4. API Import 수정")
    print("-" * 40)
    
    try:
        # views.py 파일 경로
        views_path = os.path.join(os.path.dirname(__file__), 'employees', 'views.py')
        
        # 파일이 존재하는지 확인
        if not os.path.exists(views_path):
            print(f"[ERROR] views.py 파일을 찾을 수 없습니다: {views_path}")
            return False
        
        print(f"[INFO] views.py 파일 확인: {views_path}")
        
        # views.py에 필요한 import가 있는지 확인
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 상단에 import 추가 확인
        if 'from .models_organization import OrganizationStructure' not in content[:2000]:
            print("[WARNING] models_organization import가 파일 상단에 없습니다")
            print("[ACTION] 수동으로 views.py 파일 상단에 다음 라인 추가 필요:")
            print("  from .models_organization import OrganizationStructure, OrganizationUploadHistory")
        else:
            print("[OK] models_organization import 확인됨")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] views.py 확인 실패: {e}")
        return False

def update_full_paths():
    """full_path 업데이트"""
    print("\n5. 조직 경로 업데이트")
    print("-" * 40)
    
    try:
        from employees.models_organization import OrganizationStructure
        
        orgs = OrganizationStructure.objects.all()
        for org in orgs:
            if not org.full_path:
                # 전체 경로 생성
                path_parts = []
                current = org
                while current:
                    path_parts.insert(0, current.org_name)
                    current = current.parent
                
                org.full_path = ' > '.join(path_parts)
                
                # 레벨별 이름 설정
                if org.org_level == 1:
                    org.group_name = org.org_name
                elif org.org_level == 2:
                    org.company_name = org.org_name
                    if org.parent:
                        org.group_name = org.parent.org_name
                elif org.org_level == 3:
                    org.headquarters_name = org.org_name
                    if org.parent and org.parent.parent:
                        org.company_name = org.parent.org_name
                        org.group_name = org.parent.parent.org_name
                
                org.save()
                print(f"  [UPDATE] {org.org_name}: {org.full_path}")
        
        print("[OK] 경로 업데이트 완료")
        return True
        
    except Exception as e:
        print(f"[WARNING] 경로 업데이트 실패: {e}")
        return False

def main():
    """메인 실행"""
    
    print("\n시작: API 500 오류 수정 프로세스\n")
    
    # 1. 테이블 컬럼 확인
    verify_table_columns()
    
    # 2. 모델 테스트
    model_ok = test_model_import()
    
    # 3. 경로 업데이트
    if model_ok:
        update_full_paths()
    
    # 4. API 테스트
    api_ok = test_api_direct()
    
    # 5. views.py 확인
    fix_api_import()
    
    print("\n" + "="*60)
    if api_ok:
        print("✅ 성공! API가 정상 작동합니다.")
        print("="*60)
        print("\n다음 단계:")
        print("1. railway restart")
        print("2. 브라우저에서 조직 구조 업로드 테스트")
    else:
        print("⚠️ API 오류가 지속됩니다.")
        print("="*60)
        print("\n추가 확인 필요:")
        print("1. railway logs --tail 100")
        print("2. views.py 파일 상단 import 확인")
        print("3. railway run python manage.py shell 에서 직접 테스트")

if __name__ == "__main__":
    main()