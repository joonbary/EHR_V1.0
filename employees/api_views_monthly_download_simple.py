"""
월간 인력현황 Excel 다운로드 API - 간소화 버전
"""
import pandas as pd
import json
from datetime import datetime
from django.http import HttpResponse
import io
from .api_views_monthly import get_monthly_workforce_data

def download_monthly_workforce_excel(request):
    """월간 인력현황을 Excel 파일로 다운로드 - 간소화 버전"""
    try:
        # 월간 인력현황 데이터 가져오기
        workforce_response = get_monthly_workforce_data(request)
        workforce_data = json.loads(workforce_response.content)
        
        # 데이터 준비
        table_data = workforce_data.get('table_data', [])
        companies_header = workforce_data.get('companies_header', [])
        
        # 간단한 테이블 데이터 생성
        rows = []
        for row in table_data:
            row_data = {
                '구분': row['category'],
                '직급': row['position']
            }
            
            # 각 회사별 데이터 추가
            for company in row['companies']:
                company_name = company['name']
                for pos_data in company['positions']:
                    col_name = f"{company_name}_{pos_data['position']}"
                    row_data[col_name] = pos_data['count']
            
            rows.append(row_data)
        
        # DataFrame 생성
        df = pd.DataFrame(rows)
        
        # Excel 파일 생성
        output = io.BytesIO()
        df.to_excel(output, index=False, sheet_name='월간인력현황')
        output.seek(0)
        
        # HTTP 응답 생성
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="monthly_workforce_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        
        return response
        
    except Exception as e:
        import traceback
        error_msg = f"Excel 다운로드 오류: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return HttpResponse(error_msg, status=500, content_type='text/plain')