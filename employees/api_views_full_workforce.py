"""
전체 인력현황 API Views - emp_upload.xlsx 기반
"""
import pandas as pd
import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.conf import settings
import os

@require_GET
def get_full_workforce_data(request):
    """전체 인력현황 데이터 조회 (emp_upload.xlsx 기반)"""
    try:
        # 파일 경로
        file_path = os.path.join(settings.BASE_DIR, 'emp_upload.xlsx')
        
        if not os.path.exists(file_path):
            return JsonResponse({
                'error': 'emp_upload.xlsx 파일을 찾을 수 없습니다.',
                'file_path': file_path
            }, status=404)
        
        # 엑셀 파일 읽기
        df = pd.read_excel(file_path)
        
        # 회사별, 직급구분별, 직위별로 집계
        companies_data = []
        
        # 회사 목록 추출
        companies = df['회사'].unique()
        
        for company in companies:
            company_df = df[df['회사'] == company]
            positions = []
            
            # 직급구분별로 집계
            for category in ['Non-PL', 'PL', '별정직', '기타']:
                category_df = company_df[company_df['직급구분'] == category]
                
                # 직위별로 집계
                position_counts = category_df['직위'].value_counts()
                
                for position, count in position_counts.items():
                    positions.append({
                        'type': category,
                        'position': position,
                        'current': int(count),
                        'previous': int(count),  # 이전 달 데이터가 없으므로 같은 값 사용
                        'change': 0,
                        'total': int(count)
                    })
            
            # 회사 데이터 추가
            companies_data.append({
                'name': company,
                'positions': positions
            })
        
        # 전체 합계 계산
        total_current = len(df)
        
        # 직급구분별 합계
        category_summary = {
            'Non-PL': len(df[df['직급구분'] == 'Non-PL']),
            'PL': len(df[df['직급구분'] == 'PL']),
            '별정직': len(df[df['직급구분'] == '별정직']),
            '기타': len(df[df['직급구분'] == '기타'])
        }
        
        return JsonResponse({
            'title': '전체 인력현황 (emp_upload.xlsx 기반)',
            'companies': companies_data,
            'summary': {
                'total_current': total_current,
                'total_previous': total_current,
                'total_change': 0,
                'category_summary': category_summary,
                'note': '이 데이터는 emp_upload.xlsx 파일의 전체 인력 데이터입니다.'
            },
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)