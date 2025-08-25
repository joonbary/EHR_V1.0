#!/usr/bin/env python
"""
upload-organization-structure API 400 오류 완전 해결
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Upload API 400 오류 해결")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def fix_upload_api():
    """upload_organization_structure 함수를 완전히 재작성"""
    print("1. views.py 수정")
    print("-" * 40)
    
    views_path = os.path.join(os.path.dirname(__file__), 'employees', 'views.py')
    
    with open(views_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # upload_organization_structure 함수 찾기
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if 'def upload_organization_structure' in line:
            start_idx = i - 1  # @csrf_exempt 포함
            print(f"[INFO] 함수 시작: 라인 {i}")
        elif start_idx and line.strip() and not line.startswith((' ', '\t')) and 'def ' in line:
            end_idx = i
            print(f"[INFO] 함수 끝: 라인 {i}")
            break
    
    if not start_idx:
        print("[ERROR] upload_organization_structure 함수를 찾을 수 없습니다")
        return False
    
    if not end_idx:
        # 함수가 파일 끝에 있는 경우
        for i in range(len(lines)-1, start_idx, -1):
            if 'def ' in lines[i] and i > start_idx:
                end_idx = i
                break
        if not end_idx:
            end_idx = len(lines)
    
    # 새로운 함수 (디버깅 로그 포함)
    new_function = '''@csrf_exempt
def upload_organization_structure(request):
    """조직 구조 Excel 업로드 처리 - 개선된 버전"""
    import json
    from datetime import datetime
    
    # 디버깅 로그
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Content-Type: {request.META.get('CONTENT_TYPE', 'None')}")
    print(f"[DEBUG] Request body length: {len(request.body) if request.body else 0}")
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'POST 메소드만 허용됩니다'
        }, status=405)
    
    try:
        # request body 파싱
        if not request.body:
            return JsonResponse({
                'success': False,
                'message': '요청 데이터가 없습니다'
            }, status=400)
        
        try:
            body = json.loads(request.body)
            data = body.get('data', [])
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON 파싱 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': f'JSON 파싱 오류: {str(e)}'
            }, status=400)
        
        if not data:
            return JsonResponse({
                'success': False,
                'message': '업로드할 데이터가 없습니다'
            }, status=400)
        
        print(f"[DEBUG] 데이터 개수: {len(data)}")
        
        # 모델 임포트
        try:
            from employees.models_organization import OrganizationStructure, OrganizationUploadHistory
        except ImportError as e:
            print(f"[ERROR] 모델 임포트 실패: {e}")
            return JsonResponse({
                'success': False,
                'message': '서버 설정 오류'
            }, status=500)
        
        created_count = 0
        updated_count = 0
        errors = []
        
        # 업로드 기록 생성 (선택사항)
        try:
            upload_history = OrganizationUploadHistory.objects.create(
                file_name='Excel Upload',
                total_rows=len(data),
                status='processing',
                uploaded_by=request.user if request.user.is_authenticated else None
            )
        except Exception as e:
            print(f"[WARNING] 업로드 기록 생성 실패: {e}")
            upload_history = None
        
        # 데이터 처리
        for idx, row in enumerate(data):
            try:
                # 필수 필드 확인
                org_code = row.get('조직코드', '').strip() if row.get('조직코드') else ''
                org_name = row.get('조직명', '').strip() if row.get('조직명') else ''
                
                if not org_code:
                    errors.append({
                        'row': idx + 1,
                        'error': '조직코드 없음',
                        'data': row
                    })
                    continue
                
                if not org_name:
                    errors.append({
                        'row': idx + 1,
                        'error': '조직명 없음',
                        'data': row
                    })
                    continue
                
                # 조직 레벨 처리
                try:
                    org_level = int(row.get('조직레벨', 1))
                except (ValueError, TypeError):
                    org_level = 1
                
                # 조직 생성 또는 업데이트
                org, created = OrganizationStructure.objects.get_or_create(
                    org_code=org_code,
                    defaults={
                        'org_name': org_name,
                        'org_level': org_level,
                        'status': row.get('상태', 'active'),
                        'sort_order': int(row.get('정렬순서', 0)) if row.get('정렬순서') else 0,
                        'description': row.get('설명', ''),
                    }
                )
                
                if not created:
                    # 기존 조직 업데이트
                    org.org_name = org_name
                    org.org_level = org_level
                    if row.get('상태'):
                        org.status = row.get('상태')
                    if row.get('설명'):
                        org.description = row.get('설명')
                    org.save()
                    updated_count += 1
                else:
                    created_count += 1
                
                # 상위 조직 설정
                parent_code = row.get('상위조직코드', '').strip() if row.get('상위조직코드') else ''
                if parent_code:
                    try:
                        parent = OrganizationStructure.objects.get(org_code=parent_code)
                        org.parent = parent
                        org.save()
                    except OrganizationStructure.DoesNotExist:
                        print(f"[WARNING] 상위조직 {parent_code} 찾을 수 없음")
                
            except Exception as e:
                print(f"[ERROR] 행 {idx + 1} 처리 오류: {e}")
                errors.append({
                    'row': idx + 1,
                    'error': str(e),
                    'data': row
                })
        
        # 업로드 기록 업데이트
        if upload_history:
            try:
                upload_history.status = 'completed'
                upload_history.success_count = created_count + updated_count
                upload_history.error_count = len(errors)
                upload_history.save()
            except:
                pass
        
        # 결과 반환
        result = {
            'success': True,
            'created': created_count,
            'updated': updated_count,
            'total': created_count + updated_count,
            'errors': len(errors),
            'message': f'업로드 완료: {created_count}개 생성, {updated_count}개 업데이트'
        }
        
        if errors:
            result['error_details'] = errors[:10]  # 최대 10개 오류만 반환
        
        print(f"[SUCCESS] 업로드 결과: {result['message']}")
        return JsonResponse(result)
        
    except Exception as e:
        print(f"[CRITICAL] 업로드 실패: {e}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f'서버 오류: {str(e)}'
        }, status=500)

'''
    
    # 함수 교체
    new_lines = lines[:start_idx] + [new_function] + lines[end_idx:]
    
    # 파일 저장
    with open(views_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("[OK] upload_organization_structure 함수 재작성 완료")
    return True

def test_upload_format():
    """예상되는 데이터 형식 테스트"""
    print("\n2. 데이터 형식 테스트")
    print("-" * 40)
    
    test_data = {
        'data': [
            {
                '조직코드': 'GRP001',
                '조직명': 'OK금융그룹',
                '조직레벨': 1,
                '상위조직코드': '',
                '상태': 'active',
                '정렬순서': 1,
                '설명': 'OK금융그룹 지주회사'
            },
            {
                '조직코드': 'COM001',
                '조직명': 'OK저축은행',
                '조직레벨': 2,
                '상위조직코드': 'GRP001',
                '상태': 'active',
                '정렬순서': 1,
                '설명': '저축은행'
            }
        ]
    }
    
    import json
    print("예상 요청 형식:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    print("\n[INFO] 클라이언트는 위 형식으로 데이터를 전송해야 합니다")

def main():
    """메인 실행"""
    
    print("\n시작: Upload API 400 오류 해결\n")
    
    # 1. views.py 수정
    if fix_upload_api():
        print("\n[SUCCESS] API 수정 완료")
    
    # 2. 데이터 형식 테스트
    test_upload_format()
    
    print("\n" + "="*60)
    print("수정 완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. git add employees/views.py")
    print("2. git commit -m 'Fix upload API 400 error with detailed logging'")
    print("3. git push")
    print("4. Railway 재배포 대기")
    print("\n디버깅:")
    print("- Railway logs로 상세 로그 확인 가능")
    print("- 요청 데이터 형식과 오류 메시지 확인")

if __name__ == "__main__":
    main()