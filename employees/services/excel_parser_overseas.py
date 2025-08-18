"""
해외 인력현황 Excel 파서 - 엑셀 형식 그대로 파싱
대구분(종합직/계약직/파견) - 소구분(직급) 구조
"""

import pandas as pd
import re
import os
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class OverseasWorkforceParser:
    """해외 인력현황 엑셀 파서 - 표 형식 그대로 파싱"""
    
    def parse_file(self, file_path):
        """엑셀 파일을 파싱하여 원본 형식 그대로 반환"""
        logger.info(f"Parsing overseas workforce file: {file_path}")
        
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(file_path, sheet_name=0, header=None)
            logger.info(f"Excel shape: {df.shape}")
            
            # 기준일 찾기 (X3 셀)
            report_date = None
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
            
            # 각 법인별 데이터 파싱
            corporations = []
            
            # 1. OK Bank (인니) 파싱
            ok_bank = self._parse_ok_bank(df, report_date)
            if ok_bank:
                corporations.append(ok_bank)
            
            # 2. OK Asset (인니) 파싱
            ok_asset = self._parse_ok_asset(df, report_date)
            if ok_asset:
                corporations.append(ok_asset)
            
            # 3. PPCBank (캄보디아) 파싱
            ppcbank = self._parse_ppcbank(df, report_date)
            if ppcbank:
                corporations.append(ppcbank)
            
            # 4. 천진법인 (중국) 파싱
            tianjin = self._parse_tianjin(df, report_date)
            if tianjin:
                corporations.append(tianjin)
            
            return corporations
            
        except Exception as e:
            logger.error(f"Error parsing overseas workforce file: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def _parse_ok_bank(self, df, report_date):
        """OK Bank (인니) 데이터 파싱"""
        try:
            data = {
                'corporation': 'OK Bank (인니)',
                'report_date': report_date,
                'positions': {},  # 직책별
                'ranks': {},      # 직급별
                'total': 0
            }
            
            # 직책별 데이터 (행 5-13, 열 C-H)
            # 이사급
            if df.shape[0] > 5 and df.shape[1] > 7:
                data['positions']['대표이사'] = self._safe_int(df.iloc[5, 2])  # C6
                data['ranks']['이사'] = self._safe_int(df.iloc[5, 7])  # H6
            
            # 부장급
            if df.shape[0] > 6 and df.shape[1] > 7:
                data['positions']['본부장'] = self._safe_int(df.iloc[6, 3])  # D7
                data['ranks']['부장급'] = self._safe_int(df.iloc[6, 7])  # H7
            
            # 차장
            if df.shape[0] > 7 and df.shape[1] > 7:
                data['positions']['부서장'] = self._safe_int(df.iloc[7, 4])  # E8
                data['positions']['지점장'] = self._safe_int(df.iloc[7, 5])  # F8
                data['positions']['팀장'] = self._safe_int(df.iloc[7, 6])  # G8
                data['ranks']['차장'] = self._safe_int(df.iloc[7, 7])  # H8
            
            # 과장
            if df.shape[0] > 8 and df.shape[1] > 7:
                data['positions']['과장_직책'] = self._safe_int(df.iloc[8, 6])  # G9 (Staff)
                data['ranks']['과장'] = self._safe_int(df.iloc[8, 7])  # H9
            
            # 대리
            if df.shape[0] > 9 and df.shape[1] > 7:
                data['positions']['대리_직책'] = self._safe_int(df.iloc[9, 6])  # G10 (Staff)
                data['ranks']['대리'] = self._safe_int(df.iloc[9, 7])  # H10
            
            # 사원
            if df.shape[0] > 10 and df.shape[1] > 7:
                data['positions']['사원_직책'] = self._safe_int(df.iloc[10, 6])  # G11 (Staff)
                data['ranks']['사원'] = self._safe_int(df.iloc[10, 7])  # H11
            
            # MP (행 12)
            if df.shape[0] > 11 and df.shape[1] > 7:
                data['positions']['MP'] = self._safe_int(df.iloc[11, 6])  # G12
            
            # 전체 합계 (행 14)
            if df.shape[0] > 13 and df.shape[1] > 7:
                data['total'] = self._safe_int(df.iloc[13, 7])  # H14
            
            # 자동 계산된 합계와 비교
            calculated_total = sum(data['ranks'].values())
            if calculated_total != data['total'] and data['total'] > 0:
                logger.warning(f"OK Bank 합계 불일치: 계산={calculated_total}, 엑셀={data['total']}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing OK Bank data: {e}")
            return None
    
    def _parse_ok_asset(self, df, report_date):
        """OK Asset (인니) 데이터 파싱"""
        try:
            data = {
                'corporation': 'OK Asset (인니)',
                'report_date': report_date,
                'positions': {},  # 직책별
                'ranks': {},      # 직급별
                'total': 0
            }
            
            # 직책별 데이터 (행 5-13, 열 J-P)
            # 이사급
            if df.shape[0] > 5 and df.shape[1] > 15:
                data['positions']['최고사업책임자'] = self._safe_int(df.iloc[5, 11])  # L6
                data['ranks']['이사'] = self._safe_int(df.iloc[5, 15])  # P6
            
            # 부장급
            if df.shape[0] > 6 and df.shape[1] > 15:
                data['positions']['부장급_직책'] = self._safe_int(df.iloc[6, 12])  # M7 (Div Head)
                data['ranks']['부장급'] = self._safe_int(df.iloc[6, 15])  # P7
            
            # 차장
            if df.shape[0] > 7 and df.shape[1] > 15:
                data['positions']['차장_직책'] = self._safe_int(df.iloc[7, 13])  # N8 (Team Head)
                data['ranks']['차장'] = self._safe_int(df.iloc[7, 15])  # P8
            
            # 과장
            if df.shape[0] > 8 and df.shape[1] > 15:
                data['positions']['과장_직책'] = self._safe_int(df.iloc[8, 14])  # O9 (Staff)
                data['ranks']['과장'] = self._safe_int(df.iloc[8, 15])  # P9
            
            # 대리
            if df.shape[0] > 9 and df.shape[1] > 15:
                data['positions']['대리_직책'] = self._safe_int(df.iloc[9, 14])  # O10 (Staff)
                data['ranks']['대리'] = self._safe_int(df.iloc[9, 15])  # P10
            
            # 사원
            if df.shape[0] > 10 and df.shape[1] > 15:
                data['positions']['사원_직책'] = self._safe_int(df.iloc[10, 14])  # O11 (Staff)
                data['ranks']['사원'] = self._safe_int(df.iloc[10, 15])  # P11
            
            # 전체 합계 (행 14)
            if df.shape[0] > 13 and df.shape[1] > 15:
                data['total'] = self._safe_int(df.iloc[13, 15])  # P14
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing OK Asset data: {e}")
            return None
    
    def _parse_ppcbank(self, df, report_date):
        """PPCBank (캄보디아) 데이터 파싱"""
        try:
            data = {
                'corporation': 'PPCBank (캄보디아)',
                'report_date': report_date,
                'positions': {},  # 직책별
                'ranks': {},      # 직급별
                'total': 0
            }
            
            # 직책별 데이터 (행 5-13, 열 R-Y)
            # 이사급
            if df.shape[0] > 5 and df.shape[1] > 24:
                data['positions']['부문장'] = self._safe_int(df.iloc[5, 20])  # U6
                data['ranks']['이사'] = self._safe_int(df.iloc[5, 24])  # Y6
            
            # 부장급
            if df.shape[0] > 6 and df.shape[1] > 24:
                data['positions']['수석부사장'] = self._safe_int(df.iloc[6, 21])  # V7
                data['ranks']['부장급'] = self._safe_int(df.iloc[6, 24])  # Y7
            
            # 차장
            if df.shape[0] > 7 and df.shape[1] > 24:
                data['positions']['상무이사'] = self._safe_int(df.iloc[7, 22])  # W8
                data['ranks']['차장'] = self._safe_int(df.iloc[7, 24])  # Y8
            
            # 과장
            if df.shape[0] > 8 and df.shape[1] > 24:
                data['positions']['과장_직책'] = self._safe_int(df.iloc[8, 23])  # X9
                data['ranks']['과장'] = self._safe_int(df.iloc[8, 24])  # Y9
            
            # 대리
            if df.shape[0] > 9 and df.shape[1] > 24:
                data['positions']['대리_직책'] = self._safe_int(df.iloc[9, 23])  # X10
                data['ranks']['대리'] = self._safe_int(df.iloc[9, 24])  # Y10
            
            # 사원
            if df.shape[0] > 10 and df.shape[1] > 24:
                data['positions']['사원_직책'] = self._safe_int(df.iloc[10, 23])  # X11
                data['ranks']['사원'] = self._safe_int(df.iloc[10, 24])  # Y11
            
            # 전체 합계 (행 14)
            if df.shape[0] > 13 and df.shape[1] > 24:
                data['total'] = self._safe_int(df.iloc[13, 24])  # Y14
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing PPCBank data: {e}")
            return None
    
    def _parse_tianjin(self, df, report_date):
        """천진법인 (중국) 데이터 파싱"""
        try:
            data = {
                'corporation': '천진법인 (중국)',
                'report_date': report_date,
                'positions': {},  # 직책별 (없음)
                'ranks': {},      # 직급별
                'total': 0
            }
            
            # 직급별 데이터만 존재 (행 5-13, 열 AC)
            # 이사
            if df.shape[0] > 5 and df.shape[1] > 28:
                data['ranks']['이사'] = self._safe_int(df.iloc[5, 28])  # AC6
            
            # 부장급
            if df.shape[0] > 6 and df.shape[1] > 28:
                data['ranks']['부장급'] = self._safe_int(df.iloc[6, 28])  # AC7
            
            # 차장
            if df.shape[0] > 7 and df.shape[1] > 28:
                data['ranks']['차장'] = self._safe_int(df.iloc[7, 28])  # AC8
            
            # 과장
            if df.shape[0] > 8 and df.shape[1] > 28:
                data['ranks']['과장'] = self._safe_int(df.iloc[8, 28])  # AC9
            
            # 대리
            if df.shape[0] > 9 and df.shape[1] > 28:
                data['ranks']['대리'] = self._safe_int(df.iloc[9, 28])  # AC10
            
            # 사원
            if df.shape[0] > 10 and df.shape[1] > 28:
                data['ranks']['사원'] = self._safe_int(df.iloc[10, 28])  # AC11
            
            # 전체 합계 (행 14)
            if df.shape[0] > 13 and df.shape[1] > 28:
                data['total'] = self._safe_int(df.iloc[13, 28])  # AC14
            
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