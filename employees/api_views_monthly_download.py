"""
월간 인력현황 Excel 다운로드 API
"""
import pandas as pd
import json
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import io

@require_POST
def download_monthly_workforce_excel(request):
    """월간 인력현황을 Excel 파일로 다운로드"""
    try:
        # POST 데이터 파싱
        data = json.loads(request.body)
        headers = data.get('headers', [])
        table_data = data.get('data', [])
        title = data.get('title', '월간 인력현황')
        
        # Excel 파일 생성
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # 제목 추가
            title_df = pd.DataFrame([[title]], columns=[''])
            title_df.to_excel(writer, sheet_name='인력현황', index=False, header=False, startrow=0)
            
            # 날짜 추가
            date_df = pd.DataFrame([[f'생성일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}']], columns=[''])
            date_df.to_excel(writer, sheet_name='인력현황', index=False, header=False, startrow=2)
            
            # 데이터 준비
            # 헤더 정리 (colspan 처리된 데이터를 실제 헤더로 변환)
            if len(headers) >= 2:
                # 첫 번째 헤더 행과 두 번째 헤더 행을 결합
                final_headers = []
                main_headers = headers[0]
                sub_headers = headers[1] if len(headers) > 1 else []
                
                # 구분, 직급은 그대로
                final_headers.extend(['구분', '직급'])
                
                # 회사별 헤더 생성
                companies = [h for h in main_headers[2:] if h and h != '구분' and h != '직급']
                for company in companies:
                    if company:
                        final_headers.extend([f'{company}_현원', f'{company}_전월', f'{company}_증감', f'{company}_계'])
            else:
                final_headers = ['구분', '직급']
            
            # 데이터 정리
            processed_data = []
            for row in table_data:
                if len(row) >= 2:  # 최소한 구분과 직급이 있어야 함
                    processed_row = []
                    # 구분과 직급
                    processed_row.extend(row[:2])
                    
                    # 나머지 데이터 (회사별 현원, 전월, 증감, 계)
                    for i in range(2, len(row), 4):
                        if i + 3 < len(row):
                            processed_row.extend(row[i:i+4])
                    
                    processed_data.append(processed_row)
            
            # DataFrame 생성
            df = pd.DataFrame(processed_data, columns=final_headers[:len(processed_data[0])] if processed_data else final_headers)
            
            # Excel 파일에 쓰기
            df.to_excel(writer, sheet_name='인력현황', index=False, startrow=5)
            
            # 워크북과 워크시트 가져오기
            workbook = writer.book
            worksheet = writer.sheets['인력현황']
            
            # 스타일 설정
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'center',
                'align': 'center',
                'border': 1,
                'bg_color': '#D7E4BD'
            })
            
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center'
            })
            
            # 제목 스타일 적용
            worksheet.merge_range('A1:H1', title, title_format)
            
            # 컬럼 너비 설정
            worksheet.set_column('A:B', 15)
            worksheet.set_column('C:Z', 12)
            
        # 파일 포인터를 처음으로 이동
        output.seek(0)
        
        # HTTP 응답 생성
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="monthly_workforce_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        
        return response
        
    except Exception as e:
        return HttpResponse(str(e), status=500)