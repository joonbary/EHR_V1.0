"""
월간 인력현황 API Views - 원본 템플릿 구조 100% 준수
행: 구분/직급별, 열: 회사/직책별
"""
import pandas as pd
import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from collections import defaultdict
from django.db.models import Sum, Max
from .models_hr import OutsourcedStaff

@require_GET
def get_monthly_workforce_data(request):
    """월간 인력현황 데이터 조회 - 템플릿 구조 완전 준수"""
    try:
        # Employee 모델에서 데이터 가져오기
        from .models import Employee
        
        # 모든 직원 데이터를 DataFrame으로 변환 (재직중인 직원만)
        employees = Employee.objects.filter(employment_status='재직').values(
            'name', 'company', 'department', 'position', 
            'title', 'employment_type', 'hire_date'
        )
        
        if not employees:
            # 데이터가 없으면 emp_upload.xlsx 파일 시도
            file_path = os.path.join(settings.BASE_DIR, 'emp_upload.xlsx')
            
            if not os.path.exists(file_path):
                # 샘플 데이터 생성
                df = pd.DataFrame({
                    '회사': ['OK홀딩스'] * 10 + ['OK저축은행(본사)'] * 15 + ['OK캐피탈'] * 8,
                    '직책': ['부장'] * 5 + ['본사팀장'] * 8 + ['팀원'] * 20,
                    '직급': ['부장'] * 5 + ['차장'] * 8 + ['대리'] * 10 + ['사원'] * 10,
                    '구분': ['Non-PL'] * 20 + ['PL'] * 13,
                    '고용형태': ['정규직'] * 30 + ['계약직'] * 3
                })
            else:
                # 엑셀 파일 읽기
                df = pd.read_excel(file_path, engine='openpyxl')
        else:
            # Employee 데이터를 DataFrame으로 변환
            df = pd.DataFrame(list(employees))
            
            # 컬럼명 매핑
            column_mapping = {
                'company': '회사',
                'title': '직책',  # title 필드로 변경
                'position': '직급',
                'employment_type': '고용형태'
            }
            df = df.rename(columns=column_mapping)
            
            # 구분 필드 추가 (정규직/계약직 기반)
            df['구분'] = df['고용형태'].apply(lambda x: 'Non-PL' if x in ['REGULAR', '정규직'] else 'PL')
        
        # 디버그: 데이터 구조 확인
        print("=== 데이터 구조 확인 ===")
        print("총 행수:", len(df))
        print("컬럼:", list(df.columns))
        if '직책' in df.columns:
            print("\n직책 분포:")
            print(df['직책'].value_counts().head(10))
            
            # 부장급 직책 확인
            print("\n부장급 데이터:")
            부장_데이터 = df[df['직책'] == '부장']
            print(f"부장 인원: {len(부장_데이터)}명")
            if len(부장_데이터) > 0:
                print("회사별 부장 분포:")
                print(부장_데이터['회사'].value_counts())
            
            본사팀장_데이터 = df[df['직책'] == '본사팀장']
            print(f"\n본사팀장 인원: {len(본사팀장_데이터)}명")
            if len(본사팀장_데이터) > 0:
                print("회사별 본사팀장 분포:")
                print(본사팀장_데이터['회사'].value_counts())
        print("===================")
        
        # 템플릿 정확한 회사 순서 및 직책 구조
        companies_structure = [
            {'name': 'OK홀딩스', 'positions': ['부장', '본사팀장', '팀원', '계']},
            {'name': 'OK저축은행(본사)', 'positions': ['부장', '본사팀장', '팀원', '계']},
            {'name': 'OK저축은행(센터/지점)', 'positions': ['부장', '센터장/지점장', '부지점장/팀장', '팀원', '계']},
            {'name': 'OK넥스트(OT, OKIP, OKV, EX)', 'positions': ['부장', '본사팀장', '팀원', '계']},
            {'name': 'OK캐피탈', 'positions': ['부장', '본사팀장', '지점장/팀장', '팀원', '계']},
            {'name': 'OK신용정보(OFI 포함)', 'positions': ['부장', '본사팀장', '지점장/팀장', '팀원', '계']},
            {'name': 'OK데이터시스템', 'positions': ['부장', '본사팀장', '팀원', '계']},
        ]
        
        # 템플릿 정확한 행 구조 (구분/직급별)
        rows_structure = [
            {'category': 'Non-PL', 'position': '부장'},
            {'category': 'Non-PL', 'position': '차장'},
            {'category': 'Non-PL', 'position': '대리'},
            {'category': 'Non-PL', 'position': '사원'},
            {'category': 'Non-PL', 'position': '계'},
            {'category': 'PL', 'position': '프로'},
            {'category': 'PL', 'position': '책임'},
            {'category': 'PL', 'position': '선임 이하'},
            {'category': 'PL', 'position': '관리전문직'},
            {'category': 'PL', 'position': '계'},
            {'category': '정규직', 'position': '계'},
            {'category': '계약직', 'position': '별정직'},
            {'category': '계약직', 'position': '전문계약직'},
            {'category': '계약직', 'position': '인턴/계약직 등'},
            {'category': '계약직', 'position': '계'},
            {'category': '직원', 'position': '계'},
            {'category': '기타', 'position': '도급'},
            {'category': '기타', 'position': '위임직 채권추심인'},
            {'category': '기타', 'position': '외주인력'},
            {'category': '기타', 'position': '계'},
            {'category': '총계', 'position': ''},
        ]
        
        # 회사명 매핑 (emp_upload.xlsx -> 템플릿)
        company_mapping = {
            'ON/OKIP/OKV/EX': 'OK넥스트(OT, OKIP, OKV, EX)',
            '오케이데이터시스템': 'OK데이터시스템',
            '오케이신용정보': 'OK신용정보(OFI 포함)',
            '오케이에프앤아이': 'OK신용정보(OFI 포함)',
            '오케이저축은행(본사)': 'OK저축은행(본사)',
            '오케이저축은행(센터/지점)': 'OK저축은행(센터/지점)',
            '오케이캐피탈': 'OK캐피탈',
            '오케이홀딩스대부': 'OK홀딩스'
        }
        
        # 직급 매핑 (emp_upload.xlsx -> 템플릿)
        position_mapping = {
            '부장(N)': '부장',
            '차장(N)': '차장',
            '대리(N)': '대리', 
            '사원(N)': '사원',
            '프로': '프로',
            '책임': '책임',
            '선임이하': '선임 이하',
            '관리전문직': '관리전문직',
            '별정직': '별정직',
            '전문계약직': '전문계약직',
            '인턴/계약직 등': '인턴/계약직 등',
            '도급': '도급',
            '위임직 채권추심인': '위임직 채권추심인',
            '개인사업자': '외주인력',
            '파견사원': '외주인력'
        }
        
        # 구분 매핑 (emp_upload.xlsx -> 템플릿)
        category_mapping = {
            'Non-PL': 'Non-PL',
            'PL': 'PL', 
            '계약직': '계약직',
            '기타': '기타'
        }
        
        # 데이터 집계 (3차원: [회사][구분/직급][직책])
        data_matrix = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        for _, row in df.iterrows():
            company = row['회사']
            category = row['구분']
            position = row['직급']
            
            # 회사명 매핑
            if company in company_mapping:
                company = company_mapping[company]
            else:
                continue
                
            # 구분 매핑
            if category in category_mapping:
                category = category_mapping[category]
            else:
                continue
                
            # 직급 매핑
            if position in position_mapping:
                position = position_mapping[position]
            else:
                continue
                
            # 직책 데이터 활용
            job_position = row.get('직책', '팀원')  # 직책이 없으면 기본값 '팀원'
            
            # 직책 매핑 (실제 데이터의 직책을 템플릿 직책으로 매핑)
            job_position_mapping = {
                '부장': '부장',
                '본사팀장': '본사팀장',
                '센터장/지점장': '센터장/지점장',
                '본사팀장/센터장': '본사팀장',
                '센터장': '본사팀장',
                '부지점장/팀장': '부지점장/팀장',
                '지점장/팀장': '지점장/팀장',
                '팀원': '팀원'
            }
            
            # 매핑된 직책 사용 (매핑이 없으면 기본값 '팀원')
            job_position = job_position_mapping.get(job_position, '팀원')
            
            # 데이터 집계
            category_position_key = f"{category}|{position}"
            data_matrix[company][category_position_key][job_position] += 1
        
        # 외주인력 데이터 추가
        selected_month = request.GET.get('month')
        if selected_month:
            # 특정 월의 외주인력 데이터
            try:
                year, month_num = selected_month.split('-')
                start_date = datetime(int(year), int(month_num), 1).date()
                
                # 다음 달 1일 계산
                if int(month_num) == 12:
                    end_date = datetime(int(year) + 1, 1, 1).date()
                else:
                    end_date = datetime(int(year), int(month_num) + 1, 1).date()
                
                latest_date = OutsourcedStaff.objects.filter(
                    report_date__gte=start_date,
                    report_date__lt=end_date
                ).aggregate(latest=Max('report_date'))['latest']
            except ValueError:
                latest_date = None
        else:
            # 최신 외주인력 데이터
            latest_date = OutsourcedStaff.objects.aggregate(
                latest=Max('report_date')
            )['latest']
        
        if latest_date:
            # 회사별 외주인력 집계
            outsourced_data = OutsourcedStaff.objects.filter(
                report_date=latest_date
            ).values('company_name').annotate(
                total_headcount=Sum('headcount')
            )
            
            # 외주인력 데이터를 data_matrix에 추가
            for item in outsourced_data:
                company_name = item['company_name']
                headcount = item['total_headcount'] or 0
                
                # 회사명 매핑
                mapped_company = company_mapping.get(company_name, company_name)
                
                # 기타-외주인력 카테고리에 추가 (팀원 직책)
                if headcount > 0:
                    category_position_key = "기타|외주인력"
                    data_matrix[mapped_company][category_position_key]["팀원"] += headcount
        
        # 템플릿 구조로 결과 데이터 생성
        table_data = []
        
        for row_info in rows_structure:
            row_category = row_info['category']
            row_position = row_info['position']
            
            if row_position == '계' or row_category == '총계':  # 소계/합계 행
                row_data = {
                    'category': row_category,
                    'position': row_position,
                    'is_total': True,
                    'companies': []
                }
                
                # 각 회사별 합계 계산
                for company_info in companies_structure:
                    company_name = company_info['name']
                    company_data = {'name': company_name, 'positions': []}
                    
                    for job_pos in company_info['positions']:
                        total = 0
                        
                        if row_category == 'Non-PL' and row_position == '계':
                            for pos in ['부장', '차장', '대리', '사원']:
                                key = f"Non-PL|{pos}"
                                if job_pos == '계':
                                    total += sum(data_matrix[company_name][key].values())
                                else:
                                    total += data_matrix[company_name][key].get(job_pos, 0)
                        elif row_category == 'PL' and row_position == '계':
                            for pos in ['프로', '책임', '선임 이하', '관리전문직']:
                                key = f"PL|{pos}"
                                if job_pos == '계':
                                    total += sum(data_matrix[company_name][key].values())
                                else:
                                    total += data_matrix[company_name][key].get(job_pos, 0)
                        elif row_category == '계약직' and row_position == '계':
                            for pos in ['별정직', '전문계약직', '인턴/계약직 등']:
                                key = f"계약직|{pos}"
                                if job_pos == '계':
                                    total += sum(data_matrix[company_name][key].values())
                                else:
                                    total += data_matrix[company_name][key].get(job_pos, 0)
                        elif row_category == '기타' and row_position == '계':
                            for pos in ['도급', '위임직 채권추심인', '외주인력']:
                                key = f"기타|{pos}"
                                if job_pos == '계':
                                    total += sum(data_matrix[company_name][key].values())
                                else:
                                    total += data_matrix[company_name][key].get(job_pos, 0)
                        elif row_category == '정규직' and row_position == '계':
                            # Non-PL + PL 합계
                            for cat in ['Non-PL', 'PL']:
                                for key in data_matrix[company_name]:
                                    if key.startswith(f"{cat}|"):
                                        if job_pos == '계':
                                            total += sum(data_matrix[company_name][key].values())
                                        else:
                                            total += data_matrix[company_name][key].get(job_pos, 0)
                        elif row_category == '직원' and row_position == '계':
                            # 정규직 + 계약직 합계
                            for cat in ['Non-PL', 'PL', '계약직']:
                                for key in data_matrix[company_name]:
                                    if key.startswith(f"{cat}|"):
                                        if job_pos == '계':
                                            total += sum(data_matrix[company_name][key].values())
                                        else:
                                            total += data_matrix[company_name][key].get(job_pos, 0)
                        elif row_category == '총계':
                            # 모든 직원 합계
                            for key in data_matrix[company_name]:
                                if job_pos == '계':
                                    total += sum(data_matrix[company_name][key].values())
                                else:
                                    total += data_matrix[company_name][key].get(job_pos, 0)
                        
                        company_data['positions'].append({
                            'position': job_pos,
                            'count': total
                        })
                    
                    row_data['companies'].append(company_data)
                    
            else:  # 일반 데이터 행
                category_position_key = f"{row_category}|{row_position}"
                
                row_data = {
                    'category': row_category,
                    'position': row_position,
                    'is_total': False,
                    'companies': []
                }
                
                # 각 회사별 데이터
                for company_info in companies_structure:
                    company_name = company_info['name']
                    company_data = {'name': company_name, 'positions': []}
                    
                    for job_pos in company_info['positions']:
                        if job_pos == '계':
                            # 해당 회사/구분/직급의 모든 직책 합계
                            total = sum(data_matrix[company_name][category_position_key].values())
                            company_data['positions'].append({
                                'position': job_pos,
                                'count': total
                            })
                        else:
                            # 개별 직책 데이터
                            count = data_matrix[company_name][category_position_key][job_pos]
                            company_data['positions'].append({
                                'position': job_pos,
                                'count': count
                            })
                    
                    row_data['companies'].append(company_data)
            
            table_data.append(row_data)
        
        return JsonResponse({
            'title': '월간 인력현황',
            'companies_header': companies_structure,
            'table_data': table_data,
            'summary': {
                'total_current': len(df),
                'total_previous': len(df),
                'total_change': 0,
                'by_category': df['구분'].value_counts().to_dict()
            },
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
@csrf_exempt
def upload_monthly_workforce_file(request):
    """월간 인력현황 엑셀 파일 업로드"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': '파일이 없습니다.'}, status=400)
        
        uploaded_file = request.FILES['file']
        
        # 파일 확장자 확인
        if not uploaded_file.name.endswith(('.xlsx', '.xls')):
            return JsonResponse({'error': 'Excel 파일만 업로드 가능합니다.'}, status=400)
        
        # 임시 파일로 저장
        temp_path = os.path.join(settings.BASE_DIR, 'temp_upload.xlsx')
        with open(temp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # 파일 읽기 및 검증
        try:
            df = pd.read_excel(temp_path, engine='openpyxl')
            
            # 필수 컬럼 확인
            required_columns = ['구분', '회사', '직급']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                os.remove(temp_path)
                return JsonResponse({
                    'error': f'필수 컬럼이 없습니다: {", ".join(missing_columns)}'
                }, status=400)
            
            # 업로드 성공 시 emp_upload.xlsx 대체
            file_path = os.path.join(settings.BASE_DIR, 'emp_upload.xlsx')
            
            # 기존 파일이 있으면 백업
            if os.path.exists(file_path):
                backup_path = os.path.join(settings.BASE_DIR, f'emp_upload_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
                os.rename(file_path, backup_path)
            
            # 새 파일로 대체
            os.rename(temp_path, file_path)
            
            return JsonResponse({
                'success': True,
                'message': '파일이 성공적으로 업로드되었습니다.',
                'filename': uploaded_file.name,
                'rows': len(df),
                'columns': list(df.columns)
            })
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return JsonResponse({
                'error': f'파일 읽기 오류: {str(e)}'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)