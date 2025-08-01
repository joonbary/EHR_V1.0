"""
월간 인력현황 API Views - 개선된 버전
"""
import pandas as pd
import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.conf import settings
import os

@require_GET
def get_monthly_workforce_data(request):
    """월간 인력현황 데이터 조회 - emp_upload.xlsx 기반"""
    try:
        # emp_upload.xlsx 파일 읽기
        file_path = os.path.join(settings.BASE_DIR, 'emp_upload.xlsx')
        
        if not os.path.exists(file_path):
            return JsonResponse({
                'error': 'emp_upload.xlsx 파일을 찾을 수 없습니다.',
                'file_path': file_path
            }, status=404)
        
        # 엑셀 파일 읽기
        df = pd.read_excel(file_path)
        
        # 회사별, 구분별, 직위별 집계
        companies = []
        
        # 회사 목록 (표시할 순서대로)
        company_order = [
            'OK홀딩스주식회사',
            'OK저축은행(서울)',
            'OK저축은행(부산/본사)',
            'OK캐피탈',
            'OK저축은행',
            'OK신용정보',
            'OK데이터시스템',
            'ON/OKIP/OKV/EX'
        ]
        
        # 회사명 정규화
        company_mapping = {
            'OK홀딩스주식회사': 'OK홀딩스',
            'OK저축은행(서울)': 'OK저축은행(서울)',
            'OK저축은행(부산/본사)': 'OK저축은행(부산)',
            'OK저축은행': 'OK저축은행',
            'OK캐피탈': 'OK캐피탈',
            'OK신용정보': 'OK신용정보',
            'OK데이터시스템': 'OK데이터시스템',
            'ON/OKIP/OKV/EX': 'OK넥스트'
        }
        
        # 데이터 행 범위 - 실제 Excel 구조에 맞게 수정
        data_rows = []
        current_category = None
        
        # Excel 파일 분석 결과에 따른 정확한 행 매핑
        # Non-PL: 4-7행 (부장, 차장, 대리, 사원)
        # PL: 9-13행 (선임, 책임, 선임 이하, 책임연구원, 연구조교)
        # 별정직: 15-17행 (별정직, 인턴무기직, 인턴/계약직 등)
        # 기타: 20-22행 (전문직, 무기직 채용중심제, 상시근로)
        
        # Non-PL 직급들 (4-7행)
        for row_idx in range(4, 8):
            col1 = df.iloc[row_idx, 1] if row_idx < len(df) else None
            if pd.notna(col1) and str(col1).strip():
                position = str(col1).strip()
                data_rows.append({
                    'category': 'Non-PL',
                    'position': position,
                    'row_idx': row_idx
                })
        
        # PL 직급들 (9-13행)
        for row_idx in range(9, 14):
            col1 = df.iloc[row_idx, 1] if row_idx < len(df) else None
            if pd.notna(col1) and str(col1).strip():
                position = str(col1).strip()
                # PL 직급 매핑
                if position in ['선임', '책임', '선임 이하', '책임연구원', '연구조교']:
                    data_rows.append({
                        'category': 'PL',
                        'position': position,
                        'row_idx': row_idx
                    })
        
        # 별정직 (15-17행)
        special_positions = {
            15: '별정직',
            16: '인턴무기직',
            17: '인턴/계약직 등'
        }
        
        for row_idx, position in special_positions.items():
            if row_idx < len(df):
                col1 = df.iloc[row_idx, 1]
                if pd.notna(col1) and str(col1).strip():
                    data_rows.append({
                        'category': '별정직',
                        'position': str(col1).strip(),
                        'row_idx': row_idx
                    })
        
        # 기타 (20-22행)
        other_positions = {
            20: '전문직',
            21: '무기직 채용중심제',
            22: '상시근로'
        }
        
        for row_idx, position in other_positions.items():
            if row_idx < len(df):
                col1 = df.iloc[row_idx, 1]
                if pd.notna(col1) and str(col1).strip():
                    data_rows.append({
                        'category': '기타',
                        'position': str(col1).strip(),
                        'row_idx': row_idx
                    })
        
        # 각 회사별 데이터 추출
        for comp in company_positions:
            company_data = {
                'name': comp['name'],
                'positions': []
            }
            
            # 각 직급별 데이터 추출
            for row_data in data_rows:
                row_idx = row_data['row_idx']
                
                # 현원, 전월, 증감, 계 데이터
                try:
                    current = int(float(df.iloc[row_idx, comp['cols'][0]])) if pd.notna(df.iloc[row_idx, comp['cols'][0]]) else 0
                    previous = int(float(df.iloc[row_idx, comp['cols'][1]])) if pd.notna(df.iloc[row_idx, comp['cols'][1]]) else 0
                    change = int(float(df.iloc[row_idx, comp['cols'][2]])) if pd.notna(df.iloc[row_idx, comp['cols'][2]]) else 0
                    total = int(float(df.iloc[row_idx, comp['cols'][3]])) if pd.notna(df.iloc[row_idx, comp['cols'][3]]) else 0
                except:
                    current = previous = change = total = 0
                
                # 데이터가 있는 경우만 추가
                if current > 0 or previous > 0 or total > 0:
                    company_data['positions'].append({
                        'type': row_data['category'],
                        'position': row_data['position'],
                        'current': current,
                        'previous': previous,
                        'change': change,
                        'total': total
                    })
            
            companies.append(company_data)
        
        # 실제 Excel 파일의 합계 행(25행) 데이터에서 전체 합계 읽기
        # 각 회사의 현원, 전월, 증감 합계
        total_current = 0
        total_previous = 0
        total_change = 0
        
        actual_totals = {}
        for comp in company_positions:
            try:
                # 합계 행(25행)의 데이터 읽기
                current_val = df.iloc[25, comp['cols'][0]]  # 현원
                previous_val = df.iloc[25, comp['cols'][1]]  # 전월
                change_val = df.iloc[25, comp['cols'][2]]  # 증감
                
                if pd.notna(current_val):
                    curr = int(float(current_val))
                    total_current += curr
                    actual_totals[comp['name']] = curr
                    
                if pd.notna(previous_val):
                    total_previous += int(float(previous_val))
                    
                if pd.notna(change_val):
                    total_change += int(float(change_val))
            except:
                pass
        
        # 제목에서 날짜 추출
        title = str(df.iloc[0, 0]) if pd.notna(df.iloc[0, 0]) else '월간 인력현황'
        
        # 해외 파견 정보 추출 (36-39행)
        overseas_info = {
            'total': 0,
            'details': []
        }
        
        for row_idx in range(36, min(40, len(df))):
            cell_val = df.iloc[row_idx, 0]
            if pd.notna(cell_val) and '해외' in str(cell_val):
                # 해외 파견 인원 찾기
                for col_idx in range(1, len(df.columns)):
                    val = df.iloc[row_idx, col_idx]
                    if pd.notna(val) and str(val).isdigit():
                        overseas_info['total'] = int(val)
                        break
            elif pd.notna(cell_val) and ('인도네시아' in str(cell_val) or '캄보디아' in str(cell_val)):
                overseas_info['details'].append(str(cell_val))
        
        return JsonResponse({
            'title': title,
            'companies': companies,
            'summary': {
                'total_current': total_current,
                'total_previous': total_previous,
                'total_change': total_change,
                'overseas': overseas_info,
                'note': '이 보고서는 부장급 및 인턴무기직 인원만 포함된 요약 보고서입니다.',
                'actual_totals': actual_totals
            },
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)