#!/usr/bin/env python
"""
OK저축은행 1000명 직원 데이터를 Railway PostgreSQL에 업로드
엑셀 파일에서 읽어서 직접 데이터베이스에 삽입
"""

import os
import sys
import pandas as pd
import psycopg2
from urllib.parse import urlparse
from datetime import datetime, date
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OKEmployeeUploader:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다.")
        
        self.conn = None
    
    def connect_database(self):
        """Railway PostgreSQL 연결"""
        try:
            parsed = urlparse(self.database_url)
            self.conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password
            )
            logger.info("[OK] Railway PostgreSQL 연결 성공")
            return True
        except Exception as e:
            logger.error(f"[ERROR] 데이터베이스 연결 실패: {e}")
            return False
    
    def close_connection(self):
        """연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("[INFO] 데이터베이스 연결 종료")
    
    def load_excel_data(self, filename='OK저축은행_직원명부_1000명.xlsx'):
        """엑셀 파일에서 데이터 로드"""
        try:
            df = pd.read_excel(filename, sheet_name='직원명부')
            logger.info(f"[OK] 엑셀 파일 로드 완료: {len(df)}명")
            return df
        except Exception as e:
            logger.error(f"[ERROR] 엑셀 파일 로드 실패: {e}")
            return None
    
    def prepare_employee_data(self, row):
        """엑셀 데이터를 데이터베이스 형식으로 변환"""
        # 날짜 변환 함수
        def parse_date(date_str):
            if pd.isna(date_str):
                return None
            if isinstance(date_str, str):
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            return date_str
        
        # 직급 매핑
        position_map = {
            '수습': 'INTERN',
            '사원': 'STAFF',
            '선임': 'SENIOR',
            '주임': 'STAFF',
            '대리': 'SENIOR',
            '과장': 'MANAGER',
            '차장': 'MANAGER',
            '책임': 'MANAGER',
            '수석': 'DIRECTOR',
            '부장': 'DIRECTOR',
            '부부장': 'DIRECTOR',
            '팀장': 'DIRECTOR',
            '상무': 'EXECUTIVE',
            '전무': 'EXECUTIVE',
            '부사장': 'EXECUTIVE'
        }
        
        # 부서 매핑
        department_map = {
            '경영기획부': 'FINANCE',
            '인사총무부': 'HR',
            '준법감시부': 'OPERATIONS',
            '리스크관리부': 'OPERATIONS',
            '리테일영업부': 'SALES',
            '기업영업부': 'SALES',
            '디지털영업부': 'MARKETING',
            '영업지원부': 'SALES',
            '여신심사부': 'FINANCE',
            '여신관리부': 'FINANCE',
            '신용평가부': 'FINANCE',
            'IT기획부': 'IT',
            '시스템개발부': 'IT',
            '인프라운영부': 'IT',
            '정보보안부': 'IT',
            '디지털전략부': 'MARKETING',
            '데이터사업부': 'IT',
            '핀테크사업부': 'IT'
        }
        
        # 성별 매핑
        gender_map = {
            '남성': 'M',
            '여성': 'F'
        }
        
        # 결혼여부 매핑
        marital_map = {
            '미혼': 'N',
            '기혼': 'Y'
        }
        
        prepared = {
            # 기본 정보
            'no': int(row['사번']),
            'name': str(row['이름']),
            'email': str(row['이메일']),
            'phone': str(row['휴대폰']),
            
            # 조직 정보
            'company': 'OK',  # OK저축은행
            'headquarters1': str(row['본부']),
            'department1': str(row['부서']),
            'department': department_map.get(row['부서'], 'OPERATIONS'),  # Django 모델 필수 필드
            'final_department': str(row['팀']),
            
            # 직급 정보
            'current_position': str(row['직급']),
            'position': position_map.get(row['직급'], 'STAFF'),  # Django 모델 필수 필드
            'new_position': str(row['직급']),
            'growth_level': int(row['성장레벨']),
            'job_group': str(row['직군']),
            'job_type': str(row['직무분류']) if pd.notna(row['직무분류']) else '일반사무',
            
            # 날짜 정보
            'hire_date': parse_date(row['입사일']),
            'group_join_date': parse_date(row['그룹입사일']),
            'birth_date': parse_date(row['생년월일']),
            
            # 개인 정보
            'gender': gender_map.get(row['성별'], 'M'),
            'age': int(row['나이']),
            'education': str(row['학력']),
            'marital_status': marital_map.get(row['결혼여부'], 'N'),
            
            # 평가 정보
            'final_evaluation': str(row['최종평가등급']),
            
            # 연봉 정보 (만원 단위)
            'salary_grade': f"{int(row['성장레벨'])}급",
            
            # 기타 필수 필드
            'address': str(row['주소']) if pd.notna(row['주소']) else '',
            'emergency_contact': '',
            'emergency_phone': str(row['비상연락처']) if pd.notna(row['비상연락처']) else '',
            'employment_type': str(row['고용형태']) if pd.notna(row['고용형태']) else '정규직',
            'employment_status': str(row['재직상태']) if pd.notna(row['재직상태']) else '재직',
            'grade_level': int(row['성장레벨']),
            'job_role': '',
            
            # 추가 정보
            'job_tag_name': str(row['보유자격증']) if pd.notna(row['보유자격증']) else '',
            'job_field': str(row['직무분류']) if pd.notna(row['직무분류']) else '',
            # 'special_notes': str(row['특기사항']) if pd.notna(row['특기사항']) else '',  # 필드 없음
            
            # 타임스탬프
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Null 값 처리
        for key, value in prepared.items():
            if pd.isna(value):
                prepared[key] = None
        
        return prepared
    
    def insert_employees(self, df):
        """직원 데이터 일괄 삽입"""
        success_count = 0
        error_count = 0
        
        logger.info(f"\n[INFO] {len(df)}명 직원 데이터 업로드 시작...")
        
        with self.conn.cursor() as cursor:
            # 기존 데이터 개수 확인
            cursor.execute("SELECT COUNT(*) FROM employees_employee")
            existing_count = cursor.fetchone()[0]
            logger.info(f"[INFO] 기존 직원 수: {existing_count}명")
            
            # 배치 단위로 처리
            batch_size = 50
            for i in range(0, len(df), batch_size):
                batch_df = df.iloc[i:i+batch_size]
                batch_success = 0
                
                for _, row in batch_df.iterrows():
                    try:
                        prepared = self.prepare_employee_data(row)
                        
                        # 중복 확인 (이메일 기준)
                        cursor.execute("SELECT id FROM employees_employee WHERE email = %s", 
                                     (prepared['email'],))
                        if cursor.fetchone():
                            logger.debug(f"[SKIP] 중복: {prepared['name']} ({prepared['email']})")
                            continue
                        
                        # INSERT 쿼리
                        columns = list(prepared.keys())
                        placeholders = ', '.join(['%s'] * len(columns))
                        column_names = ', '.join(columns)
                        
                        insert_query = f"""
                            INSERT INTO employees_employee ({column_names})
                            VALUES ({placeholders})
                        """
                        
                        values = list(prepared.values())
                        cursor.execute(insert_query, values)
                        
                        batch_success += 1
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        logger.error(f"[ERROR] {row['이름']}: {e}")
                
                # 배치 커밋
                if batch_success > 0:
                    self.conn.commit()
                    logger.info(f"[PROGRESS] {success_count}명 업로드 완료...")
        
        logger.info(f"\n[COMPLETE] 업로드 완료!")
        logger.info(f"  성공: {success_count}명")
        logger.info(f"  실패: {error_count}명")
        
        return success_count, error_count
    
    def verify_upload(self):
        """업로드 결과 검증"""
        with self.conn.cursor() as cursor:
            # 총 직원 수
            cursor.execute("SELECT COUNT(*) FROM employees_employee WHERE company = 'OK'")
            ok_count = cursor.fetchone()[0]
            
            # 본부별 통계
            cursor.execute("""
                SELECT headquarters1, COUNT(*) 
                FROM employees_employee 
                WHERE company = 'OK' 
                GROUP BY headquarters1 
                ORDER BY COUNT(*) DESC
            """)
            headquarters_stats = cursor.fetchall()
            
            logger.info(f"\n[VERIFICATION] OK저축은행 직원 현황")
            logger.info(f"  총 직원: {ok_count}명")
            logger.info(f"  본부별 분포:")
            for hq, count in headquarters_stats:
                logger.info(f"    - {hq}: {count}명")
            
            return ok_count

def main():
    print("=" * 70)
    print("OK저축은행 직원 데이터 Railway 업로드")
    print("=" * 70)
    
    uploader = OKEmployeeUploader()
    
    try:
        # 데이터베이스 연결
        if not uploader.connect_database():
            return
        
        # 엑셀 파일 로드
        df = uploader.load_excel_data()
        if df is None:
            return
        
        # 데이터 업로드
        success, errors = uploader.insert_employees(df)
        
        if success > 0:
            # 결과 검증
            uploader.verify_upload()
            print(f"\n[SUCCESS] Railway 업로드 성공!")
            print(f"확인: https://ehrv10-production.up.railway.app/employees/")
        else:
            print(f"\n[FAILED] 업로드 실패")
    
    except Exception as e:
        logger.error(f"[ERROR] 업로드 프로세스 오류: {e}")
    finally:
        uploader.close_connection()

if __name__ == "__main__":
    main()