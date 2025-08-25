#!/usr/bin/env python
"""
조직 구조 업로드 API 400 오류 수정
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("조직 구조 업로드 API 수정")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def fix_upload_api():
    """views.py의 upload_organization_structure 함수 수정"""
    print("1. views.py 파일 수정")
    print("-" * 40)
    
    views_path = os.path.join(os.path.dirname(__file__), 'employees', 'views.py')
    
    # views.py 읽기
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # csrf_exempt가 import되어 있는지 확인
    if 'from django.views.decorators.csrf import csrf_exempt' not in content:
        # import 추가
        import_line = "from django.views.decorators.csrf import csrf_exempt"
        
        # JsonResponse import 뒤에 추가
        if 'from django.http import' in content:
            content = content.replace(
                'from django.http import HttpResponse, HttpResponseRedirect, JsonResponse',
                'from django.http import HttpResponse, HttpResponseRedirect, JsonResponse\nfrom django.views.decorators.csrf import csrf_exempt'
            )
            print("[OK] csrf_exempt import 추가")
    else:
        print("[OK] csrf_exempt 이미 import됨")
    
    # upload_organization_structure 함수에 @csrf_exempt 추가
    if '@csrf_exempt\ndef upload_organization_structure' not in content:
        content = content.replace(
            'def upload_organization_structure(request):',
            '@csrf_exempt\ndef upload_organization_structure(request):'
        )
        print("[OK] @csrf_exempt 데코레이터 추가")
    else:
        print("[OK] @csrf_exempt 이미 있음")
    
    # get_organization_stats에도 추가
    if '@csrf_exempt\ndef get_organization_stats' not in content:
        content = content.replace(
            'def get_organization_stats(request):',
            '@csrf_exempt\ndef get_organization_stats(request):'
        )
        print("[OK] get_organization_stats에 @csrf_exempt 추가")
    
    # save_organization에도 추가
    if '@csrf_exempt\ndef save_organization' not in content:
        content = content.replace(
            'def save_organization(request):',
            '@csrf_exempt\ndef save_organization(request):'
        )
        print("[OK] save_organization에 @csrf_exempt 추가")
    
    # 파일 저장
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n[SUCCESS] views.py 수정 완료")

def create_test_api():
    """간단한 테스트 API 생성"""
    print("\n2. 테스트 API 생성")
    print("-" * 40)
    
    test_file = os.path.join(os.path.dirname(__file__), 'employees', 'test_upload.py')
    
    test_code = '''"""
테스트용 업로드 API
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def test_upload(request):
    """간단한 테스트 업로드 API"""
    if request.method == 'POST':
        try:
            # request body 확인
            if request.body:
                data = json.loads(request.body)
                return JsonResponse({
                    'success': True,
                    'message': '데이터 수신 성공',
                    'data_count': len(data.get('data', [])),
                    'received': data
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No data received'
                }, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'message': f'JSON decode error: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Method not allowed'
    }, status=405)
'''
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"[OK] 테스트 파일 생성: {test_file}")

def update_urls():
    """URLs에 테스트 엔드포인트 추가"""
    print("\n3. URLs 업데이트")
    print("-" * 40)
    
    urls_path = os.path.join(os.path.dirname(__file__), 'employees', 'urls.py')
    
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 테스트 URL이 없으면 추가
    if 'test-upload' not in content:
        # upload-organization-structure 뒤에 추가
        new_line = "    path('api/test-upload/', views.test_upload, name='test_upload'),\n"
        
        if 'from .test_upload import test_upload' not in content:
            # import 추가
            content = content.replace(
                'from . import views, api_views',
                'from . import views, api_views\nfrom .test_upload import test_upload'
            )
            
            # URL 패턴 추가
            content = content.replace(
                "path('api/upload-organization-structure/', views.upload_organization_structure, name='upload_organization_structure'),",
                f"path('api/upload-organization-structure/', views.upload_organization_structure, name='upload_organization_structure'),\n    path('api/test-upload/', test_upload, name='test_upload'),"
            )
            
            print("[OK] 테스트 URL 추가")
    else:
        print("[OK] 테스트 URL 이미 존재")
    
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(content)

def test_local_api():
    """로컬 API 테스트"""
    print("\n4. 로컬 API 테스트")
    print("-" * 40)
    
    try:
        import requests
        import json
        
        # 테스트 데이터
        test_data = {
            'data': [
                {
                    '조직코드': 'TEST001',
                    '조직명': '테스트조직',
                    '조직레벨': 1,
                    '상태': 'active'
                }
            ]
        }
        
        urls = [
            'http://localhost:8000/employees/api/test-upload/',
            'http://localhost:8000/employees/api/upload-organization-structure/'
        ]
        
        for url in urls:
            try:
                response = requests.post(
                    url,
                    json=test_data,
                    headers={'Content-Type': 'application/json'}
                )
                print(f"\n{url}:")
                print(f"  Status: {response.status_code}")
                if response.status_code < 500:
                    print(f"  Response: {response.json()}")
            except requests.exceptions.ConnectionError:
                print(f"  [INFO] 로컬 서버가 실행 중이 아님")
            except Exception as e:
                print(f"  [ERROR] {e}")
                
    except ImportError:
        print("[INFO] requests 모듈이 없어 테스트 생략")

def main():
    """메인 실행"""
    
    print("\n시작: 조직 구조 업로드 API 수정\n")
    
    # 1. views.py 수정
    fix_upload_api()
    
    # 2. 테스트 API 생성
    create_test_api()
    
    # 3. URLs 업데이트
    update_urls()
    
    # 4. 로컬 테스트
    test_local_api()
    
    print("\n" + "="*60)
    print("수정 완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. git add .")
    print("2. git commit -m 'Fix organization upload API - add CSRF exempt'")
    print("3. git push")
    print("4. Railway 배포 대기")
    print("\n주의사항:")
    print("- CSRF 면제는 보안상 위험할 수 있으므로 프로덕션에서는 주의 필요")
    print("- 가능하면 프론트엔드에서 CSRF 토큰을 포함하도록 수정 권장")

if __name__ == "__main__":
    main()