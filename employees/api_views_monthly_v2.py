"""
월간 인력현황 API Views - emp_upload.xlsx 기반
"""
import pandas as pd
import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.conf import settings
import os
from collections import defaultdict

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
        
        # 회사명 정규화
        company_mapping = {
            'OK홀딩스주식회사': 'OK홀딩스',
            'OK저축은행(서울)': 'OK저축은행(서울)',
            'OK저축은행(부산/본사)': 'OK저축은행(부산)',
            'OK캐피탈': 'OK캐피탈',
            'OK신용정보': 'OK신용정보',
            'OK데이터시스템': 'OK데이터시스템',
            'ON/OKIP/OKV/EX': 'OK넥스트'
        }
        
        # 직위 매핑 (월간인력현황 형식에 맞게)
        position_mapping = {
            # Non-PL
            '부장': '부장',
            '부장(N)': '부장',
            '차장': '차장',
            '차장(N)': '차장',
            '과장': '대리',  # 과장을 대리로 매핑
            '과장(N)': '대리',
            '대리': '대리',
            '대리(N)': '대리',
            '주임': '사원',
            '사원': '사원',
            # PL
            '수석': '선임',
            '책임': '책임',
            '선임': '선임',
            '전임': '선임 이하',
            '원': '선임 이하',
            # 별정직
            '고문': '별정직',
            '자문': '별정직',
            '임원': '별정직',
            # 기타
            '계약직': '기타',
            '파견직': '기타',
            '인턴': '기타'
        }
        
        # 구분별 직위 분류
        position_categories = {
            'Non-PL': ['부장', '차장', '대리', '사원'],
            'PL': ['선임', '책임', '선임 이하', '책임연구원', '연구조교'],
            '별정직': ['별정직', '인턴무기직', '인턴/계약직 등'],
            '기타': ['전문직', '무기직 채용중심제', '상시근로', '기타']
        }
        
        # 회사별, 구분별, 직위별 집계
        company_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        for _, row in df.iterrows():
            company = row['회사']
            category = row['구분']
            position = row['직위']
            
            # 회사명 정규화
            if company in company_mapping:
                company = company_mapping[company]
            else:
                continue  # 매핑되지 않은 회사는 제외
            
            # 직위 정규화
            if position in position_mapping:
                position = position_mapping[position]
            
            company_data[company][category][position] += 1
        
        # 결과 데이터 구성
        companies = []
        company_order = ['OK홀딩스', 'OK저축은행(서울)', 'OK저축은행(부산)', 'OK넥스트', 
                        'OK캐피탈', 'OK신용정보', 'OK데이터시스템']
        
        for company_name in company_order:
            company_positions = []
            
            # 각 카테고리별로 데이터 수집
            for category, positions in position_categories.items():
                for position in positions:
                    current_count = company_data[company_name][category][position]
                    
                    if current_count > 0 or position in ['부장', '차장', '대리', '사원']:  # 주요 직급은 0이어도 표시
                        company_positions.append({
                            'type': category,
                            'position': position,
                            'current': current_count,
                            'previous': current_count,  # 이전 달 데이터가 없으므로 현재와 동일
                            'change': 0,  # 변동 없음
                            'total': current_count
                        })
            
            companies.append({
                'name': company_name,
                'positions': company_positions
            })
        
        # 전체 합계 계산
        total_current = len(df)
        total_by_category = df['구분'].value_counts().to_dict()
        
        return JsonResponse({
            'title': '월간 인력현황',
            'companies': companies,
            'summary': {
                'total_current': total_current,
                'total_previous': total_current,  # 이전 달 데이터 없음
                'total_change': 0,
                'by_category': total_by_category,
                'note': 'emp_upload.xlsx 파일 기반 현재 인력 현황입니다.'
            },
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)