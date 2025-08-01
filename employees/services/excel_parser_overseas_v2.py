"""
해외 인력현황 Excel 파서 V2 - 정확한 엑셀 구조 반영
대구분(종합직/계약직/파견) - 소구분(직급) X 직책 매트릭스
"""

import pandas as pd
import re
import os
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class OverseasWorkforceParserV2:
    """해외 인력현황 엑셀 파서 - 정확한 표 구조 반영"""
    
    def parse_file(self, file_path):
        """엑셀 파일을 파싱하여 원본 형식 그대로 반환"""
        logger.info(f"Parsing overseas workforce file (V2): {file_path}")
        
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(file_path, sheet_name=0, header=None)
            logger.info(f"Excel shape: {df.shape}")
            
            # 엑셀 파일 구조 디버깅
            logger.info("Excel file first 10 rows and columns:")
            for i in range(min(10, df.shape[0])):
                row_data = []
                for j in range(min(10, df.shape[1])):
                    val = df.iloc[i, j]
                    if pd.notna(val):
                        row_data.append(f"[{i},{j}]: {val}")
                if row_data:
                    logger.info(f"Row {i}: {', '.join(row_data)}")
            
            # 기준일 찾기 (X3 셀 = [2, 23])
            report_date = self._extract_report_date(df, file_path)
            logger.info(f"Report date found: {report_date}")
            
            # 각 법인별 데이터 파싱
            corporations = []
            
            # 1. OK Bank (인니) 파싱
            logger.info("Attempting to parse OK Bank...")
            ok_bank = self._parse_ok_bank_v2(df, report_date)
            if ok_bank:
                logger.info("OK Bank parsed successfully")
                corporations.append(ok_bank)
            else:
                logger.warning("OK Bank parsing failed")
            
            # 2. OK Asset (인니) 파싱
            logger.info("Attempting to parse OK Asset...")
            ok_asset = self._parse_ok_asset_v2(df, report_date)
            if ok_asset:
                logger.info("OK Asset parsed successfully")
                corporations.append(ok_asset)
            else:
                logger.warning("OK Asset parsing failed")
            
            # 3. PPCBank (캄보디아) 파싱
            logger.info("Attempting to parse PPCBank...")
            ppcbank = self._parse_ppcbank_v2(df, report_date)
            if ppcbank:
                logger.info("PPCBank parsed successfully")
                corporations.append(ppcbank)
            else:
                logger.warning("PPCBank parsing failed")
            
            # 4. 천진법인 (중국) 파싱
            logger.info("Attempting to parse Tianjin...")
            tianjin = self._parse_tianjin_v2(df, report_date)
            if tianjin:
                logger.info("Tianjin parsed successfully")
                corporations.append(tianjin)
            else:
                logger.warning("Tianjin parsing failed")
            
            logger.info(f"Total corporations parsed: {len(corporations)}")
            return corporations
            
        except Exception as e:
            logger.error(f"Error parsing overseas workforce file: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def _extract_report_date(self, df, file_path):
        """기준일 추출"""
        report_date = None
        
        # X3 셀 확인
        if df.shape[0] > 2 and df.shape[1] > 23:
            val = df.iloc[2, 23]  # X3
            if pd.notna(val):
                if isinstance(val, (pd.Timestamp, datetime)):
                    report_date = val.date() if hasattr(val, 'date') else val
                    logger.info(f"기준일 발견: {report_date}")
        
        if not report_date:
            # 파일명에서 추출
            filename = os.path.basename(file_path)
            date_match = re.search(r'(\d{2})(\d{2})(\d{2})', filename)
            if date_match:
                yy, mm, dd = date_match.groups()
                year = 2000 + int(yy)
                report_date = datetime(year, int(mm), int(dd)).date()
                logger.info(f"파일명에서 기준일 추출: {report_date}")
        
        if not report_date:
            raise ValueError("기준일을 찾을 수 없습니다.")
        
        return report_date
    
    def _parse_ok_bank_v2(self, df, report_date):
        """OK Bank (인니) 데이터 파싱 - 정확한 구조"""
        logger.info(f"Parsing OK Bank data, df shape: {df.shape}")
        try:
            data = {
                'corporation': 'OK Bank (인니)',
                'report_date': report_date.strftime('%Y-%m-%d') if hasattr(report_date, 'strftime') else str(report_date),
                'structure': {
                    'headers': {
                        'positions': ['대표이사', '본부장', '부서장', '지점장/Br.Mg', '팀장/T.leader/Staff'],
                        'categories': {
                            '종합직': {
                                '직급': ['이사', '부장', '차장', '과장', '대리', '계장', '사원'],
                                'data': {}
                            },
                            '계약직': {
                                '직급': ['일반', '수습'],
                                'data': {}
                            },
                            '파견(도급)': {
                                '직급': ['GA', 'Retail'],
                                'data': {}
                            }
                        }
                    }
                },
                'totals': {},
                'summary': {}
            }
            
            # 종합직 데이터 (행 6-12, 열 C-H)
            positions = ['대표이사', '본부장', '부서장', '지점장/Br.Mg', '팀장/T.leader/Staff', '계']
            col_indices = [2, 3, 4, 5, 6, 7]  # C-H 열
            
            logger.info(f"OK Bank positions: {positions}")
            logger.info(f"OK Bank col_indices: {col_indices}")
            
            # 종합직 데이터
            ranks = ['이사', '부장', '차장', '과장', '대리', '계장', '사원']
            row_indices = [5, 6, 7, 8, 9, 10, 11]  # 행 6-12
            
            logger.info(f"OK Bank ranks: {ranks}")
            logger.info(f"OK Bank row_indices: {row_indices}")
            
            for i, rank in enumerate(ranks):
                if row_indices[i] < df.shape[0]:
                    rank_data = {}
                    for j, pos in enumerate(positions):
                        if col_indices[j] < df.shape[1]:
                            val = self._safe_int(df.iloc[row_indices[i], col_indices[j]])
                            rank_data[pos] = val
                            logger.debug(f"OK Bank [{rank}][{pos}] at [{row_indices[i]},{col_indices[j]}] = {val}")
                    data['structure']['headers']['categories']['종합직']['data'][rank] = rank_data
                    logger.info(f"OK Bank {rank} data: {rank_data}")
            
            # 종합직 소계 (행 14)
            if 13 < df.shape[0]:
                subtotal_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[13, col_indices[j]])
                        subtotal_data[pos] = val
                data['structure']['headers']['categories']['종합직']['소계'] = subtotal_data
            
            # 계약직 데이터 (행 15-16)
            contract_ranks = ['일반', '수습']
            contract_rows = [14, 15]  # 행 15-16
            
            for i, rank in enumerate(contract_ranks):
                if contract_rows[i] < df.shape[0]:
                    rank_data = {}
                    for j, pos in enumerate(positions):
                        if col_indices[j] < df.shape[1]:
                            val = self._safe_int(df.iloc[contract_rows[i], col_indices[j]])
                            rank_data[pos] = val
                    data['structure']['headers']['categories']['계약직']['data'][rank] = rank_data
            
            # 계약직 소계 (행 17)
            if 16 < df.shape[0]:
                subtotal_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[16, col_indices[j]])
                        subtotal_data[pos] = val
                data['structure']['headers']['categories']['계약직']['소계'] = subtotal_data
            
            # 총계 (행 18)
            if 17 < df.shape[0]:
                total_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[17, col_indices[j]])
                        total_data[pos] = val
                data['totals']['총계'] = total_data
            
            # 파견(도급) 데이터 (행 19-20)
            dispatch_ranks = ['GA', 'Retail']
            dispatch_rows = [18, 19]  # 행 19-20
            
            for i, rank in enumerate(dispatch_ranks):
                if dispatch_rows[i] < df.shape[0]:
                    rank_data = {}
                    for j, pos in enumerate(positions):
                        if col_indices[j] < df.shape[1]:
                            val = self._safe_int(df.iloc[dispatch_rows[i], col_indices[j]])
                            rank_data[pos] = val
                    data['structure']['headers']['categories']['파견(도급)']['data'][rank] = rank_data
            
            # 파견 소계 (행 21)
            if 20 < df.shape[0]:
                subtotal_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[20, col_indices[j]])
                        subtotal_data[pos] = val
                data['structure']['headers']['categories']['파견(도급)']['소계'] = subtotal_data
            
            # 전월비증감 (파견제외) - 행 22
            if 21 < df.shape[0]:
                change_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[21, col_indices[j]])
                        change_data[pos] = val
                data['totals']['전월비증감(파견제외)'] = change_data
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing OK Bank data: {e}")
            return None
    
    def _parse_ok_asset_v2(self, df, report_date):
        """OK Asset (인니) 데이터 파싱 - 정확한 구조"""
        try:
            data = {
                'corporation': 'OK Asset (인니)',
                'report_date': report_date.strftime('%Y-%m-%d') if hasattr(report_date, 'strftime') else str(report_date),
                'structure': {
                    'headers': {
                        'positions': ['최고사업책임자', '본부장/Div Head', '팀장/Team Head', '직원/Staff'],
                        'categories': {
                            '종합직': {
                                '직급': ['이사', '부장', '차장', '과장', '대리', '계장', '사원'],
                                'data': {}
                            },
                            '계약직': {
                                '직급': ['일반', '수습'],
                                'data': {}
                            },
                            '파견(도급)': {
                                '직급': ['GA', 'Retail'],
                                'data': {}
                            }
                        }
                    }
                },
                'totals': {},
                'summary': {}
            }
            
            # OK Asset 데이터는 J-P 열 (인덱스 9-15)
            positions = ['최고사업책임자', '본부장/Div Head', '팀장/Team Head', '직원/Staff', '계']
            col_indices = [11, 12, 13, 14, 15]  # L-P 열
            
            # 종합직 데이터
            ranks = ['이사', '부장', '차장', '과장', '대리', '계장', '사원']
            row_indices = [5, 6, 7, 8, 9, 10, 11]  # 행 6-12
            
            for i, rank in enumerate(ranks):
                if row_indices[i] < df.shape[0]:
                    rank_data = {}
                    for j, pos in enumerate(positions):
                        if col_indices[j] < df.shape[1]:
                            val = self._safe_int(df.iloc[row_indices[i], col_indices[j]])
                            rank_data[pos] = val
                    data['structure']['headers']['categories']['종합직']['data'][rank] = rank_data
            
            # 종합직 소계 (행 14)
            if 13 < df.shape[0]:
                subtotal_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[13, col_indices[j]])
                        subtotal_data[pos] = val
                data['structure']['headers']['categories']['종합직']['소계'] = subtotal_data
            
            # 계약직 데이터 (행 15-16)
            contract_ranks = ['일반', '수습']
            contract_rows = [14, 15]  # 행 15-16
            
            for i, rank in enumerate(contract_ranks):
                if contract_rows[i] < df.shape[0]:
                    rank_data = {}
                    for j, pos in enumerate(positions):
                        if col_indices[j] < df.shape[1]:
                            val = self._safe_int(df.iloc[contract_rows[i], col_indices[j]])
                            rank_data[pos] = val
                    data['structure']['headers']['categories']['계약직']['data'][rank] = rank_data
            
            # 계약직 소계 (행 17)
            if 16 < df.shape[0]:
                subtotal_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[16, col_indices[j]])
                        subtotal_data[pos] = val
                data['structure']['headers']['categories']['계약직']['소계'] = subtotal_data
            
            # 총계 (행 18)
            if 17 < df.shape[0]:
                total_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[17, col_indices[j]])
                        total_data[pos] = val
                data['totals']['총계'] = total_data
            
            # 파견(도급) 데이터 추가 (0으로 설정)
            dispatch_ranks = ['GA', 'Retail']
            for rank in dispatch_ranks:
                rank_data = {}
                for pos in positions:
                    rank_data[pos] = 0
                data['structure']['headers']['categories']['파견(도급)']['data'][rank] = rank_data
            
            # 파견(도급) 소계 추가
            subtotal_data = {}
            for pos in positions:
                subtotal_data[pos] = 0
            data['structure']['headers']['categories']['파견(도급)']['소계'] = subtotal_data
            
            # 전월비증감 - 행 22
            if 21 < df.shape[0]:
                change_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[21, col_indices[j]])
                        change_data[pos] = val
                data['totals']['전월비증감(파견제외)'] = change_data
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing OK Asset data: {e}")
            return None
    
    def _parse_ppcbank_v2(self, df, report_date):
        """PPCBank (캄보디아) 데이터 파싱 - 정확한 구조"""
        try:
            data = {
                'corporation': 'PPCBank (캄보디아)',
                'report_date': report_date.strftime('%Y-%m-%d') if hasattr(report_date, 'strftime') else str(report_date),
                'structure': {
                    'headers': {
                        'positions': ['부문장/수석부사장', '수석부사장', '상무이사'],
                        'categories': {
                            '종합직': {
                                '직급': ['이사', '부장', '차장', '과장', '대리', '계장', '사원'],
                                'data': {}
                            },
                            '계약직': {
                                '직급': ['일반', '수습'],
                                'data': {}
                            },
                            '파견(도급)': {
                                '직급': ['GA', 'Retail'],
                                'data': {}
                            }
                        }
                    }
                },
                'totals': {},
                'summary': {}
            }
            
            # PPCBank 데이터는 R-Y 열 (인덱스 17-24)
            # 실제 직책 열은 U, V, W (인덱스 20, 21, 22)
            positions = ['부문장/수석부사장', '수석부사장', '상무이사', '기타', '계']
            col_indices = [20, 21, 22, 23, 24]  # U-Y 열
            
            # 종합직 데이터
            ranks = ['이사', '부장', '차장', '과장', '대리', '계장', '사원']
            row_indices = [5, 6, 7, 8, 9, 10, 11]  # 행 6-12
            
            for i, rank in enumerate(ranks):
                if row_indices[i] < df.shape[0]:
                    rank_data = {}
                    for j, pos in enumerate(positions):
                        if col_indices[j] < df.shape[1]:
                            val = self._safe_int(df.iloc[row_indices[i], col_indices[j]])
                            rank_data[pos] = val
                    data['structure']['headers']['categories']['종합직']['data'][rank] = rank_data
            
            # 종합직 소계 (행 14)
            if 13 < df.shape[0]:
                subtotal_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[13, col_indices[j]])
                        subtotal_data[pos] = val
                data['structure']['headers']['categories']['종합직']['소계'] = subtotal_data
            
            # 계약직 데이터
            contract_ranks = ['일반', '수습']
            contract_rows = [14, 15]
            
            for i, rank in enumerate(contract_ranks):
                if contract_rows[i] < df.shape[0]:
                    rank_data = {}
                    for j, pos in enumerate(positions):
                        if col_indices[j] < df.shape[1]:
                            val = self._safe_int(df.iloc[contract_rows[i], col_indices[j]])
                            rank_data[pos] = val
                    data['structure']['headers']['categories']['계약직']['data'][rank] = rank_data
            
            # 계약직 소계 (행 17)
            if 16 < df.shape[0]:
                subtotal_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[16, col_indices[j]])
                        subtotal_data[pos] = val
                data['structure']['headers']['categories']['계약직']['소계'] = subtotal_data
            
            # 총계 (행 18)
            if 17 < df.shape[0]:
                total_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[17, col_indices[j]])
                        total_data[pos] = val
                data['totals']['총계'] = total_data
            
            # 파견(도급) 데이터 추가 (0으로 설정)
            dispatch_ranks = ['GA', 'Retail']
            for rank in dispatch_ranks:
                rank_data = {}
                for pos in positions:
                    rank_data[pos] = 0
                data['structure']['headers']['categories']['파견(도급)']['data'][rank] = rank_data
            
            # 파견(도급) 소계 추가
            subtotal_data = {}
            for pos in positions:
                subtotal_data[pos] = 0
            data['structure']['headers']['categories']['파견(도급)']['소계'] = subtotal_data
            
            # 전월비증감
            if 21 < df.shape[0]:
                change_data = {}
                for j, pos in enumerate(positions):
                    if col_indices[j] < df.shape[1]:
                        val = self._safe_int(df.iloc[21, col_indices[j]])
                        change_data[pos] = val
                data['totals']['전월비증감(파견제외)'] = change_data
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing PPCBank data: {e}")
            return None
    
    def _parse_tianjin_v2(self, df, report_date):
        """천진법인 (중국) 데이터 파싱 - 정확한 구조"""
        try:
            data = {
                'corporation': '천진법인 (중국)',
                'report_date': report_date.strftime('%Y-%m-%d') if hasattr(report_date, 'strftime') else str(report_date),
                'structure': {
                    'headers': {
                        'positions': ['인원'],  # 천진법인은 직책 구분 없이 직급별만
                        'categories': {
                            '종합직': {
                                '직급': ['이사', '부장', '차장', '과장', '대리', '계장', '사원'],
                                'data': {}
                            },
                            '계약직': {
                                '직급': ['일반', '수습'],
                                'data': {}
                            },
                            '파견(도급)': {
                                '직급': ['GA', 'Retail'],
                                'data': {}
                            }
                        }
                    }
                },
                'totals': {},
                'summary': {}
            }
            
            # 천진법인 데이터는 AC 열 (인덱스 28)
            col_index = 28  # AC 열
            
            # 종합직 데이터
            ranks = ['이사', '부장', '차장', '과장', '대리', '계장', '사원']
            row_indices = [5, 6, 7, 8, 9, 10, 11]  # 행 6-12
            
            for i, rank in enumerate(ranks):
                if row_indices[i] < df.shape[0] and col_index < df.shape[1]:
                    val = self._safe_int(df.iloc[row_indices[i], col_index])
                    data['structure']['headers']['categories']['종합직']['data'][rank] = {'인원': val, '계': val}
            
            # 종합직 소계 (행 14)
            if 13 < df.shape[0] and col_index < df.shape[1]:
                val = self._safe_int(df.iloc[13, col_index])
                data['structure']['headers']['categories']['종합직']['소계'] = {'인원': val, '계': val}
            
            # 계약직 데이터 추가 (0으로 설정)
            contract_ranks = ['일반', '수습']
            for rank in contract_ranks:
                data['structure']['headers']['categories']['계약직']['data'][rank] = {'인원': 0, '계': 0}
            data['structure']['headers']['categories']['계약직']['소계'] = {'인원': 0, '계': 0}
            
            # 총계 (행 18)
            if 17 < df.shape[0] and col_index < df.shape[1]:
                val = self._safe_int(df.iloc[17, col_index])
                data['totals']['총계'] = {'인원': val, '계': val}
            
            # 파견(도급) 데이터 추가 (0으로 설정)
            dispatch_ranks = ['GA', 'Retail']
            for rank in dispatch_ranks:
                data['structure']['headers']['categories']['파견(도급)']['data'][rank] = {'인원': 0, '계': 0}
            data['structure']['headers']['categories']['파견(도급)']['소계'] = {'인원': 0, '계': 0}
            
            # 전월비증감
            if 21 < df.shape[0] and col_index < df.shape[1]:
                val = self._safe_int(df.iloc[21, col_index])
                data['totals']['전월비증감(파견제외)'] = {'인원': val, '계': val}
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing Tianjin data: {e}")
            return None
    
    def _safe_int(self, value):
        """안전하게 정수로 변환"""
        if pd.isna(value):
            return 0
        try:
            # 문자열인 경우 처리
            if isinstance(value, str):
                # 공백, 대시 제거
                value = value.strip().replace('-', '').replace(',', '')
                if not value:
                    return 0
            return int(float(value))
        except:
            return 0