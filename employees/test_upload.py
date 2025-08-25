"""
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
