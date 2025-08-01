"""
HR Excel Auto Parser
OK금융그룹 인력현황 엑셀 파일 자동 분류 및 파싱
"""

import pandas as pd
import re
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HRExcelAutoParser:
    """엑셀 파일 자동 분류 및 파싱"""
    
    def __init__(self):
        # 국내 회사 리스트
        self.domestic_companies = ['OK홀딩스', 'OK저축은행', 'OK캐피탈', 'OK투자증권']
        
        # 해외 회사 리스트
        self.overseas_companies = {
            'OK Bank (인니)': '인도네시아',
            'OK Asset (인니)': '인도네시아',
            'PPCBank (캄보디아)': '캄보디아',
            '천진법인': '중국'
        }
        
        # 직급 매핑
        self.job_levels = [
            '사원', '대리', '과장', '차장', '부장', '부장대우',
            '부부장', '팀장', '실장', '본부장', '상무', '전무', '부사장', '사장'
        ]
        
        # 계열사 리스트 (외주인력 현황용)
        self.all_companies = self.domestic_companies + list(self.overseas_companies.keys())
    
    def identify_file_type(self, file_path: str) -> str:
        """파일명과 내용으로 파일 타입 자동 식별"""
        file_name = os.path.basename(file_path).lower()
        
        # 파일명으로 1차 판단
        if '해외' in file_name:
            return 'overseas'
        elif '외주' in file_name:
            return 'contractor'
        
        # 파일 내용으로 판단
        try:
            # 첫 번째 시트의 처음 10행 읽기
            df = pd.read_excel(file_path, nrows=10)
            content = ' '.join(df.astype(str).values.flatten())
            
            # 해외 회사명 확인
            for company in self.overseas_companies.keys():
                if company in content:
                    return 'overseas'
            
            # 외주 관련 키워드 확인
            if '외주' in content or '프로젝트' in content or '업체명' in content:
                return 'contractor'
            
            # 나머지는 국내로 분류
            return 'domestic'
            
        except Exception as e:
            logger.warning(f"파일 내용 확인 실패: {e}")
            return 'domestic'  # 기본값
    
    def parse_domestic_hr(self, file_path: str) -> Dict[str, List[Dict]]:
        """국내 인력현황 파싱"""
        result = {
            'employees': [],
            'new_hires': [],
            'resignations': [],
            'summary': {}
        }
        
        try:
            xls = pd.ExcelFile(file_path)
            
            # 인력현황 시트 파싱
            if '인력현황' in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name='인력현황', header=None)
                
                # 회사별 컬럼 위치 찾기
                company_columns = {}
                for col in range(df.shape[1]):
                    for row in range(min(5, df.shape[0])):
                        cell = df.iloc[row, col]
                        if pd.notna(cell) and str(cell) in self.domestic_companies:
                            company_columns[col] = str(cell)
                            break
                
                # 직급별 데이터 추출
                job_level_data = {}
                for row in range(5, df.shape[0]):
                    job_level = df.iloc[row, 1] if df.shape[1] > 1 else None
                    if pd.isna(job_level) or str(job_level) in ['계', '합계', 'PL', 'Non-PL']:
                        continue
                    
                    if str(job_level) in self.job_levels:
                        for col, company in company_columns.items():
                            count = df.iloc[row, col]
                            if pd.notna(count) and int(count) > 0:
                                # 집계 데이터로 저장
                                if company not in job_level_data:
                                    job_level_data[company] = {}
                                job_level_data[company][str(job_level)] = int(count)
                
                result['summary'] = job_level_data
            
            # 입사자 시트 파싱
            if '입사자' in xls.sheet_names:
                df_hire = pd.read_excel(xls, sheet_name='입사자')
                
                # 컬럼명 정규화
                df_hire.columns = [col.strip() for col in df_hire.columns]
                
                for _, row in df_hire.iterrows():
                    if pd.notna(row.get('성명', row.get('이름'))):
                        result['new_hires'].append({
                            'name': str(row.get('성명', row.get('이름'))),
                            'employee_no': str(row.get('사번', '')),
                            'company': str(row.get('회사', '')),
                            'department': str(row.get('부서', '')),
                            'position': str(row.get('직책', '')),
                            'job_level': str(row.get('직급', '')),
                            'hire_date': pd.to_datetime(row.get('입사일')).strftime('%Y-%m-%d') if pd.notna(row.get('입사일')) else None,
                            'location_type': 'domestic',
                            'status': 'new_hire'
                        })
            
            # 퇴사자 시트 파싱
            if '퇴사자' in xls.sheet_names:
                df_resign = pd.read_excel(xls, sheet_name='퇴사자')
                
                # 컬럼명 정규화
                df_resign.columns = [col.strip() for col in df_resign.columns]
                
                for _, row in df_resign.iterrows():
                    if pd.notna(row.get('성명', row.get('이름'))):
                        result['resignations'].append({
                            'name': str(row.get('성명', row.get('이름'))),
                            'employee_no': str(row.get('사번', '')),
                            'company': str(row.get('회사', '')),
                            'department': str(row.get('부서', '')),
                            'resignation_date': pd.to_datetime(row.get('퇴사일')).strftime('%Y-%m-%d') if pd.notna(row.get('퇴사일')) else None,
                            'location_type': 'domestic',
                            'status': 'resigned'
                        })
                        
        except Exception as e:
            logger.error(f"국내 인력현황 파싱 오류: {e}")
            raise
        
        return result
    
    def parse_overseas_hr(self, file_path: str) -> List[Dict]:
        """해외 인력현황 파싱"""
        employees = []
        
        try:
            df = pd.read_excel(file_path, sheet_name='월간양식', header=None)
            
            # 해외 법인별 데이터 영역 찾기
            company_ranges = self._find_overseas_company_ranges(df)
            
            for company, (start_row, end_row, start_col, end_col) in company_ranges.items():
                country = self.overseas_companies.get(company, '')
                
                # 직급/직위별 인원 추출
                for row in range(start_row + 2, end_row):  # 헤더 제외
                    position = df.iloc[row, start_col]
                    if pd.isna(position) or str(position) in ['계', '합계', 'Total']:
                        continue
                    
                    # 각 컬럼(직급)별 인원 수 확인
                    for col in range(start_col + 1, end_col):
                        job_level = df.iloc[start_row + 1, col] if start_row + 1 < df.shape[0] else None
                        count = df.iloc[row, col]
                        
                        if pd.notna(count) and int(count) > 0:
                            # 집계 데이터 생성
                            for i in range(int(count)):
                                employees.append({
                                    'company': company,
                                    'position': str(position),
                                    'job_level': str(job_level) if pd.notna(job_level) else '',
                                    'location_type': 'overseas',
                                    'country': country,
                                    'branch': company,
                                    'status': 'active'
                                })
                                
        except Exception as e:
            logger.error(f"해외 인력현황 파싱 오류: {e}")
            raise
        
        return employees
    
    def parse_contractor(self, file_path: str) -> List[Dict]:
        """외주 현황 파싱"""
        contractors = []
        
        try:
            # 헤더가 없는 상태로 읽기
            df_raw = pd.read_excel(file_path, header=None)
            
            # 헤더 행 찾기 - 외주 파일은 일반적으로 10행이 헤더
            header_row = 10
            
            # 헤더가 올바른지 확인
            if len(df_raw) > header_row:
                row = df_raw.iloc[header_row]
                row_str = ' '.join([str(val) for val in row if pd.notna(val)])
                if '담당' not in row_str and '업체' not in row_str:
                    # 헤더 자동 탐색
                    for idx in range(min(20, len(df_raw))):
                        row = df_raw.iloc[idx]
                        row_str = ' '.join([str(val) for val in row if pd.notna(val)])
                        if '담당' in row_str and '업체' in row_str:
                            header_row = idx
                            break
            
            # 헤더를 설정하여 다시 읽기
            df = pd.read_excel(file_path, header=header_row)
            logger.info(f"외주 파일 읽기 완료. 헤더 행: {header_row}, 데이터 행: {len(df)}, 컬럼: {list(df.columns)}")
            
            # 컬럼명 정규화
            df.columns = [col.strip() if isinstance(col, str) else str(col) for col in df.columns]
            
            # 데이터 추출 - 병합된 셀 구조 처리
            current_company = None
            for idx, row in df.iterrows():
                # 담당 회사 업데이트 (병합된 셀의 경우 첫 번째 행에만 값이 있음)
                if pd.notna(row.get('담당')):
                    company_value = str(row.get('담당'))
                    if company_value == '담당':  # 헤더 행은 건너뛰기
                        continue
                    current_company = company_value
                
                # Unnamed: 1 컬럼에 외주 인력 이름이 있는 경우만 처리
                name_value = row.get('Unnamed: 1')
                if pd.notna(name_value) and str(name_value) not in ['nan', '담당', '소계']:
                    contractor_name = str(name_value)
                    
                    contractor = {
                        'contractor_name': contractor_name,
                        'vendor_company': str(row.get('업체', '')) if pd.notna(row.get('업체')) else '',
                        'project_name': str(row.get('프로젝트', '')) if pd.notna(row.get('프로젝트')) else '',
                        'department': str(row.get('투입부서', '')) if pd.notna(row.get('투입부서')) else '',
                        'role': str(row.get('역할', '')) if pd.notna(row.get('역할')) else '',
                        'company': current_company if current_company else 'Unknown',  # 담당 회사 추가
                        'status': 'active'
                    }
                    
                    # 기간 처리
                    if pd.notna(row.get('기간')):
                        period = str(row.get('기간'))
                        contractor['period'] = period
                    
                    # 인원 수 처리 (정수로 변환)
                    if pd.notna(row.get('인원')):
                        try:
                            contractor['count'] = int(float(row.get('인원')))
                        except:
                            contractor['count'] = 1
                    
                    contractors.append(contractor)
                    logger.debug(f"외주 인력 추가: {contractor}")
            
            logger.info(f"외주 인력 파싱 완료: {len(contractors)}명")
                    
        except Exception as e:
            logger.error(f"외주 현황 파싱 오류: {e}")
            raise
        
        return contractors
    
    def _find_overseas_company_ranges(self, df: pd.DataFrame) -> Dict[str, Tuple[int, int, int, int]]:
        """해외 법인별 데이터 영역 찾기"""
        company_ranges = {}
        
        # 전체 데이터프레임에서 회사명 찾기
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                cell = df.iloc[row, col]
                if pd.notna(cell):
                    cell_str = str(cell)
                    for company in self.overseas_companies.keys():
                        if company in cell_str:
                            # 해당 회사의 데이터 영역 찾기
                            start_row = row
                            start_col = col
                            
                            # 종료 지점 찾기 (다음 회사 또는 끝)
                            end_row = row + 20  # 기본값
                            end_col = col + 10  # 기본값
                            
                            # 실제 데이터 영역 찾기
                            for r in range(row + 1, min(row + 30, df.shape[0])):
                                next_cell = df.iloc[r, col]
                                if pd.notna(next_cell) and any(c in str(next_cell) for c in self.overseas_companies.keys()):
                                    end_row = r
                                    break
                            
                            company_ranges[company] = (start_row, end_row, start_col, end_col)
                            break
        
        return company_ranges
    
    def _extract_country(self, company_name: str) -> str:
        """회사명에서 국가 추출"""
        return self.overseas_companies.get(company_name, '')
    
    def parse_outsourced_staff(self, file_path: str) -> List[Dict]:
        """외주인력 현황 파싱 (OK금융그룹 양식)"""
        staff_list = []
        
        try:
            logger.info(f"외주인력 파일 파싱 시작: {file_path}")
            # 헤더 없이 읽기
            df_raw = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
            logger.info(f"Excel 파일 읽기 완료: {len(df_raw)}행 x {len(df_raw.columns)}열")
            
            # 현재 담당 회사
            current_company = None
            
            # 기준일 추출 (파일명에서 또는 현재 날짜)
            report_date = datetime.now().date()
            import re
            date_match = re.search(r'(\d{6})', file_path)
            if date_match:
                date_str = date_match.group(1)
                # YYMMDD 또는 YYDDMM 형식 처리
                year_part = int(date_str[:2])
                mid_part = int(date_str[2:4])
                last_part = int(date_str[4:6])
                
                # 연도는 2000년대로 가정
                year = 2000 + year_part
                
                # 월과 일 구분 - 중간 부분이 12보다 크면 일이 먼저 온 것으로 판단
                if mid_part > 12:  # YYDDMM 형식
                    day = mid_part
                    month = last_part
                else:  # YYMMDD 형식
                    month = mid_part
                    day = last_part
                
                # 유효성 검증
                if 1 <= month <= 12 and 1 <= day <= 31:
                    try:
                        report_date = datetime(year, month, day).date()
                    except ValueError:
                        # 잘못된 날짜인 경우 현재 날짜 사용
                        logger.warning(f"잘못된 날짜 형식: {date_str}")
                        report_date = datetime.now().date()
                else:
                    logger.warning(f"날짜 범위 초과: year={year}, month={month}, day={day}")
                    report_date = datetime.now().date()
            
            # 현재 섹션 추적 변수
            current_section = 'resident'  # 기본값은 상주
            
            # 카운터 변수 추가
            resident_count = 0
            non_resident_count = 0
            project_count = 0
            
            # 실제 데이터 시작 행 찾기 (요약 부분 제외)
            data_start_row = 11
            for i in range(len(df_raw)):
                row = df_raw.iloc[i]
                # "담당"이라는 헤더가 있는 행 찾기
                if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() == '담당':
                    data_start_row = i + 1
                    logger.info(f"데이터 시작 행: {data_start_row}")
                    break
            
            # 데이터 처리
            for i in range(data_start_row, len(df_raw)):
                row = df_raw.iloc[i]
                
                # 디버깅용 로그 추가
                row_data = [str(row.iloc[j]) if pd.notna(row.iloc[j]) else 'NaN' for j in range(min(6, len(row)))]
                logger.debug(f"행 {i}: {row_data}")
                
                # 0번 열: 담당 회사 (병합된 셀)
                if pd.notna(row.iloc[0]):
                    company_value = str(row.iloc[0]).strip()
                    logger.debug(f"회사 감지: '{company_value}'")
                    # 회사명 매핑
                    if 'OKDS' in company_value:
                        current_company = 'OK데이터시스템'
                        current_section = 'resident'  # 새 회사 시작시 상주로 리셋
                    elif 'OKIP' in company_value:
                        current_company = 'OK정보보호'
                        current_section = 'resident'
                    elif 'OC' in company_value or 'OK캐피탈' in company_value:
                        current_company = 'OK캐피탈'
                        current_section = 'resident'
                    elif 'OKS' in company_value or 'OK저축' in company_value:
                        current_company = 'OK저축은행'
                        current_section = 'resident'
                    elif 'OK' in company_value and ('홀딩스' in company_value or 'HD' in company_value):
                        current_company = 'OK홀딩스'
                        current_section = 'resident'
                    elif company_value == 'OK':  # OK만 있는 경우 OK홀딩스로 처리
                        current_company = 'OK홀딩스'
                        current_section = 'resident'
                    elif '합계' in company_value or '총' in company_value or '명 철수' in company_value:
                        current_company = None  # 합계 행은 무시
                        continue
                    else:
                        current_company = company_value
                        current_section = 'resident'
                    logger.debug(f"회사 설정: {current_company}, 초기 섹션: {current_section}")
                
                # 1번 열 체크로 섹션 변경 감지
                col1_value = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                
                # 섹션 변경 처리
                if '소계' in col1_value:
                    logger.debug(f"소계 행 스킵: '{col1_value}'")
                    # 소계 이후는 다른 구분이 올 수 있음
                    continue
                elif '비상주' in col1_value:  # == 대신 in 사용
                    current_section = 'non_resident'
                    logger.debug(f"비상주 섹션 시작: '{col1_value}'")
                    # 비상주 헤더 행은 데이터가 아니므로 continue
                    if pd.isna(row.iloc[2]):
                        continue
                elif '프로젝트' in col1_value:  # == 대신 in 사용 (프로젝트(3개) 같은 경우 처리)
                    current_section = 'project'
                    logger.debug(f"프로젝트 섹션 시작: '{col1_value}'")
                    # 프로젝트 헤더 행은 데이터가 아니므로 continue
                    if pd.isna(row.iloc[2]):
                        continue
                elif '상주' in col1_value:  # == 대신 in 사용
                    current_section = 'resident'
                    logger.debug(f"상주 섹션 시작: '{col1_value}'")
                    # 상주 헤더 행은 데이터가 아니므로 continue
                    if pd.isna(row.iloc[2]):
                        continue
                
                # 2번 열: 인원
                if pd.notna(row.iloc[2]) and current_company:
                    try:
                        headcount = int(float(row.iloc[2]))
                        logger.debug(f"인원 추출: {headcount}")
                    except:
                        logger.debug(f"인원 추출 실패: {row.iloc[2]}")
                        continue
                    
                    # 3번 열: 내용/프로젝트명
                    project_name = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ''
                    
                    # 4번 열: 업체
                    vendor = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ''
                    
                    logger.debug(f"프로젝트명: '{project_name}', 업체: '{vendor}', 섹션: '{current_section}'")
                    
                    # 데이터가 유효한 경우만 추가
                    if project_name and headcount > 0:
                        # 특수문자 정리
                        project_name = project_name.replace('\xa0', ' ').strip()
                        if vendor:
                            vendor = vendor.replace('\xa0', ' ').strip()
                            
                        staff = {
                            'company_name': current_company,
                            'project_name': f"{project_name} ({vendor})" if vendor else project_name,
                            'staff_type': current_section,  # 현재 섹션 사용
                            'headcount': headcount,
                            'report_date': report_date
                        }
                        
                        staff_list.append(staff)
                        
                        # 카운터 업데이트
                        if current_section == 'resident':
                            resident_count += headcount
                        elif current_section == 'non_resident':
                            non_resident_count += headcount
                        elif current_section == 'project':
                            project_count += headcount
                        
                        logger.info(f"[{current_section}] 외주인력 추가: {current_company} - {project_name} - {headcount}명")
                    else:
                        logger.debug(f"데이터 무효 (스킵): project_name='{project_name}', headcount={headcount}")
            
            logger.info(f"외주인력 파싱 완료: {len(staff_list)}개 항목 (상주: {resident_count}명, 비상주: {non_resident_count}명, 프로젝트: {project_count}명)")
                        
        except Exception as e:
            logger.error(f"외주인력 현황 파싱 오류: {e}")
            raise
        
        return staff_list
    
    def _parse_boolean(self, value) -> bool:
        """불린 값 파싱"""
        if pd.isna(value):
            return True
        
        value_str = str(value).upper().strip()
        return value_str in ['Y', 'YES', 'TRUE', '상주', 'O', '1']
    
    def parse_excel_file(self, file_path: str, file_type: Optional[str] = None) -> Dict:
        """엑셀 파일 파싱 (자동 분류 포함)"""
        # 파일 타입 자동 식별
        if not file_type:
            file_type = self.identify_file_type(file_path)
        
        logger.info(f"파일 타입: {file_type}")
        
        # 파일 타입별 파싱
        if file_type == 'domestic':
            return self.parse_domestic_hr(file_path)
        elif file_type == 'overseas':
            employees = self.parse_overseas_hr(file_path)
            return {'employees': employees}
        elif file_type == 'contractor':
            contractors = self.parse_contractor(file_path)
            return {'contractors': contractors}
        elif file_type == 'outsourced_staff':
            staff = self.parse_outsourced_staff(file_path)
            return {'outsourced_staff': staff}
        else:
            raise ValueError(f"지원하지 않는 파일 타입: {file_type}")
    
    def parse_overseas_workforce(self, file_path):
        """해외 인력현황 파일 파싱"""
        logger.info(f"Parsing overseas workforce file: {file_path}")
        
        try:
            # 엑셀 파일 읽기 (header=None으로 전체를 읽음)
            df = pd.read_excel(file_path, sheet_name=0, header=None)
            
            # 기준일 찾기 (X3 셀 - 인덱스 [2, 23])
            report_date = None
            
            # X3 셀 확인
            if df.shape[0] > 2 and df.shape[1] > 23:
                val = df.iloc[2, 23]  # X3 셀
                if pd.notna(val):
                    if isinstance(val, pd.Timestamp):
                        report_date = val.date()
                    elif isinstance(val, datetime):
                        report_date = val.date()
            
            # 기준일을 못 찾았으면 전체 검색
            if not report_date:
                for i in range(min(5, df.shape[0])):
                    for j in range(df.shape[1]):
                        val = df.iloc[i, j]
                        if pd.notna(val) and isinstance(val, (pd.Timestamp, datetime)):
                            report_date = val.date() if hasattr(val, 'date') else val
                            logger.info(f"기준일을 [{i},{j}]에서 발견: {report_date}")
                            break
                    if report_date:
                        break
            
            if not report_date:
                # 파일명에서 날짜 추출 시도 (employee_global_250801.xlsx)
                filename = os.path.basename(file_path)
                date_match = re.search(r'(\d{2})(\d{2})(\d{2})', filename)
                if date_match:
                    yy, mm, dd = date_match.groups()
                    # 2000년대로 가정
                    year = 2000 + int(yy)
                    report_date = datetime(year, int(mm), int(dd)).date()
                    logger.info(f"파일명에서 기준일 추출: {report_date}")
                else:
                    raise ValueError("기준일을 찾을 수 없습니다.")
            
            logger.info(f"기준일: {report_date}")
            
            # 법인별 데이터 파싱 - 엑셀 형식 그대로 저장
            results = []
            
            # OK Bank (인니) - 전체 데이터 구조
            ok_bank_data = {
                'corporation': 'OK Bank (인니)',
                'report_date': report_date,
                'position_data': {},  # 직책별 데이터
                'rank_data': {},      # 직급별 데이터
                'executive_count': 0,
                'general_manager_count': 0,
                'deputy_manager_count': 0,
                'manager_count': 0,
                'assistant_manager_count': 0,
                'staff_count': 0,
                'ceo_count': 0,
                'division_head_count': 0,
                'department_head_count': 0,
                'branch_manager_count': 0,
                'team_leader_count': 0,
                'total_count': 0
            }
            
            # OK Asset (인니) - 열 9-15
            ok_asset_data = {
                'corporation': 'OK Asset (인니)',
                'report_date': report_date,
                'executive_count': 0,
                'general_manager_count': 0,
                'deputy_manager_count': 0,
                'manager_count': 0,
                'assistant_manager_count': 0,
                'staff_count': 0,
                'cbo_count': 0,
                'total_count': 0
            }
            
            # PPCBank (캄보디아) - 열 17-24
            ppcbank_data = {
                'corporation': 'PPCBank (캄보디아)',
                'report_date': report_date,
                'executive_count': 0,
                'general_manager_count': 0,
                'deputy_manager_count': 0,
                'manager_count': 0,
                'assistant_manager_count': 0,
                'staff_count': 0,
                'evp_count': 0,
                'svp_count': 0,
                'vp_count': 0,
                'total_count': 0
            }
            
            # 천진법인 (중국) - 열 26-28
            tianjin_data = {
                'corporation': '천진법인 (중국)',
                'report_date': report_date,
                'executive_count': 0,
                'general_manager_count': 0,
                'deputy_manager_count': 0,
                'manager_count': 0,
                'assistant_manager_count': 0,
                'staff_count': 0,
                'total_count': 0
            }
            
            # 직급별 데이터 추출 (실제 행 인덱스는 5-10, 엑셀 행 번호는 6-11)
            position_mapping = {
                5: 'executive_count',       # 이사 (엑셀 행6)
                6: 'general_manager_count', # 부장급 (엑셀 행7) 
                7: 'deputy_manager_count',  # 차장 (엑셀 행8)
                8: 'manager_count',         # 과장 (엑셀 행9)
                9: 'assistant_manager_count', # 대리 (엑셀 행10)
                10: 'staff_count',          # 사원 (엑셀 행11)
            }
            
            # 각 행에서 데이터 추출
            for row_idx, position_field in position_mapping.items():
                if row_idx < df.shape[0]:
                    # OK Bank (인니) - H열 (인덱스 7)
                    if 7 < df.shape[1]:
                        val = df.iloc[row_idx, 7]  # H열 (계)
                        if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                            ok_bank_data[position_field] = int(float(val))
                    
                    # OK Asset (인니) - P열 (인덱스 15)
                    if 15 < df.shape[1]:
                        val = df.iloc[row_idx, 15]  # P열 (계)
                        if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                            ok_asset_data[position_field] = int(float(val))
                    
                    # PPCBank (캄보디아) - Y열 (인덱스 24) 
                    if 24 < df.shape[1]:
                        val = df.iloc[row_idx, 24]  # Y열 (계)
                        if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                            ppcbank_data[position_field] = int(float(val))
                    
                    # 천진법인 (중국) - AC열 (인덱스 28)
                    if 28 < df.shape[1]:
                        val = df.iloc[row_idx, 28]  # AC열 (인원)
                        if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                            tianjin_data[position_field] = int(float(val))
            
            # 직책별 데이터 추출 (OK Bank)
            # 이사급 - 대표이사 (엑셀 행6, C열 = 인덱스 [5, 2])
            if 5 < df.shape[0] and 2 < df.shape[1]:
                val = df.iloc[5, 2]  # C6
                if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                    ok_bank_data['ceo_count'] = int(float(val))
            
            # 부장급 - 본부장 (엑셀 행7, D열 = 인덱스 [6, 3])
            if 6 < df.shape[0] and 3 < df.shape[1]:
                val = df.iloc[6, 3]  # D7
                if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                    ok_bank_data['division_head_count'] = int(float(val))
            
            # 차장 직책들 (엑셀 행8)
            # 부서장 (E8 = 인덱스 [7, 4])
            if 7 < df.shape[0] and 4 < df.shape[1]:
                val = df.iloc[7, 4]  # E8
                if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                    ok_bank_data['department_head_count'] = int(float(val))
            
            # 지점장 (F8 = 인덱스 [7, 5])
            if 7 < df.shape[0] and 5 < df.shape[1]:
                val = df.iloc[7, 5]  # F8
                if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                    ok_bank_data['branch_manager_count'] = int(float(val))
            
            # 팀장 (G8 = 인덱스 [7, 6])
            if 7 < df.shape[0] and 6 < df.shape[1]:
                val = df.iloc[7, 6]  # G8
                if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                    ok_bank_data['team_leader_count'] = int(float(val))
            
            # OK Asset 직책별 데이터
            # 이사급 - 최고사업책임자 (엑셀 행6, L열 = 인덱스 [5, 11])
            if 5 < df.shape[0] and 11 < df.shape[1]:
                val = df.iloc[5, 11]  # L6
                if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                    ok_asset_data['cbo_count'] = int(float(val))
            
            # PPCBank 직책별 데이터
            # 이사급 - 부문장 (엑셀 행6, U열 = 인덱스 [5, 20])
            if 5 < df.shape[0] and 20 < df.shape[1]:
                val = df.iloc[5, 20]  # U6
                if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                    ppcbank_data['evp_count'] = int(float(val))
            
            # 부장급 - 수석부사장 (엑셀 행7, V열 = 인덱스 [6, 21])
            if 6 < df.shape[0] and 21 < df.shape[1]:
                val = df.iloc[6, 21]  # V7
                if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                    ppcbank_data['svp_count'] = int(float(val))
            
            # 차장 - 상무이사 (엑셀 행8, W열 = 인덱스 [7, 22])
            if 7 < df.shape[0] and 22 < df.shape[1]:
                val = df.iloc[7, 22]  # W8
                if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                    ppcbank_data['vp_count'] = int(float(val))
            
            # 합계 계산
            for data in [ok_bank_data, ok_asset_data, ppcbank_data, tianjin_data]:
                data['total_count'] = (
                    data['executive_count'] + 
                    data['general_manager_count'] + 
                    data['deputy_manager_count'] + 
                    data['manager_count'] + 
                    data['assistant_manager_count'] + 
                    data['staff_count']
                )
            
            # 결과 리스트에 추가
            results.extend([ok_bank_data, ok_asset_data, ppcbank_data, tianjin_data])
            
            logger.info(f"Parsed {len(results)} corporations")
            return results
            
        except Exception as e:
            logger.error(f"Error parsing overseas workforce file: {e}")
            raise