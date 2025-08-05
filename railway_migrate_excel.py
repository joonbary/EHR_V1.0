"""
Railway Production Migration Script
Excel 데이터를 Railway 프로덕션 DB로 마이그레이션
"""

import os
import sys
import django
import pandas as pd
import random
import string
from datetime import datetime, date
import re

# Django 설정 - Railway 환경 사용
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

# DATABASE_URL이 설정되어 있는지 확인
if 'DATABASE_URL' not in os.environ:
    print("DATABASE_URL 환경변수가 설정되지 않았습니다.")
    print("Railway 프로덕션 DB에 연결하려면 DATABASE_URL을 설정하세요.")
    sys.exit(1)

django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from employees.models import Employee


class RailwayExcelMigration:
    """Railway 프로덕션 DB로 Excel 데이터 마이그레이션"""
    
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.df = None
        self.korean_last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
        self.korean_first_names_male = ['민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호', '지후', '준우']
        self.korean_first_names_female = ['서연', '서윤', '지우', '서현', '민서', '하은', '하윤', '윤서', '지유', '지민']
        
    def load_excel(self):
        """Excel 파일 로드"""
        print("Excel 파일 로딩 중...")
        self.df = pd.read_excel(self.excel_path)
        print(f"총 {len(self.df)}개 행 로드 완료")
        return self.df
    
    def generate_name(self, gender):
        """한국 이름 생성"""
        last = random.choice(self.korean_last_names)
        if gender == '남':
            first = random.choice(self.korean_first_names_male)
        else:
            first = random.choice(self.korean_first_names_female)
        return f"{last}{first}"
    
    def generate_phone(self):
        """전화번호 생성"""
        return f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    
    def generate_email(self, name, index):
        """이메일 생성"""
        eng_name = ''.join(random.choices(string.ascii_lowercase, k=5))
        return f"{eng_name}{index}@okfg.co.kr"
    
    def map_department(self, dept_str):
        """부서 매핑"""
        if pd.isna(dept_str):
            return 'OPERATIONS'
        dept_str = str(dept_str)
        if 'IT' in dept_str or '디지털' in dept_str:
            return 'IT'
        elif '인사' in dept_str or 'HR' in dept_str:
            return 'HR'
        elif '재무' in dept_str or '회계' in dept_str:
            return 'FINANCE'
        elif '마케팅' in dept_str:
            return 'MARKETING'
        elif '영업' in dept_str:
            return 'SALES'
        return 'OPERATIONS'
    
    @transaction.atomic
    def migrate_batch(self, start_idx=0, batch_size=100):
        """배치 단위로 마이그레이션"""
        end_idx = min(start_idx + batch_size, len(self.df))
        batch_df = self.df.iloc[start_idx:end_idx]
        
        success = 0
        for idx, row in batch_df.iterrows():
            try:
                # 더미 데이터 생성
                name = self.generate_name(row.get('성별', '남'))
                email = self.generate_email(name, idx)
                phone = self.generate_phone()
                
                # User 생성
                username = f"emp_{idx:05d}"
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': name[1:],
                        'last_name': name[0]
                    }
                )
                
                if created:
                    user.set_password('okfg2024!')
                    user.save()
                
                # Employee 생성/업데이트
                employee, created = Employee.objects.update_or_create(
                    user=user,
                    defaults={
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'department': self.map_department(row.get('소속1\n(본부)')),
                        'position': 'STAFF',
                        'hire_date': pd.to_datetime(row.get('현회사입사일', date.today())).date() if pd.notna(row.get('현회사입사일')) else date.today(),
                    }
                )
                success += 1
                
            except Exception as e:
                print(f"오류 (Row {idx}): {str(e)}")
        
        print(f"배치 완료: {success}/{end_idx-start_idx} 성공")
        return success
    
    def run_migration(self):
        """전체 마이그레이션 실행"""
        print("\n" + "="*60)
        print("Railway 프로덕션 DB 마이그레이션 시작")
        print("="*60)
        
        total = len(self.df)
        batch_size = 100
        total_success = 0
        
        for start in range(0, total, batch_size):
            print(f"\n배치 {start//batch_size + 1}/{(total-1)//batch_size + 1} 처리 중...")
            success = self.migrate_batch(start, batch_size)
            total_success += success
        
        print("\n" + "="*60)
        print(f"마이그레이션 완료: {total_success}/{total} 레코드 성공")
        print("="*60)


if __name__ == "__main__":
    excel_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK_dummy_employee_250801.xlsx"
    
    migrator = RailwayExcelMigration(excel_path)
    migrator.load_excel()
    
    # Railway DB 연결 확인
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM employees_employee")
        current_count = cursor.fetchone()[0]
        print(f"현재 DB 직원 수: {current_count}")
    
    # 마이그레이션 실행
    migrator.run_migration()