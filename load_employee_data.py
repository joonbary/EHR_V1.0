"""
emp_upload.xlsx 파일에서 직원 데이터를 로드하는 스크립트
"""
import os
import sys
import django
import pandas as pd
from datetime import date, datetime
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_evaluation.settings')
django.setup()

from employees.models import Employee

def load_employee_data():
    """Excel 파일에서 직원 데이터 로드"""
    
    try:
        # Excel 파일 읽기 (UTF-8 인코딩 시도)
        df = pd.read_excel('emp_upload.xlsx', engine='openpyxl')
        
        print(f"파일 읽기 성공: {len(df)} 행")
        print(f"컬럼: {list(df.columns)}")
        
        # 컬럼명 정리 (인코딩 문제 해결)
        # 첫 번째 컬럼부터 순서대로: 구분, 회사, 직책, 직위
        df.columns = ['구분', '회사', '직책', '직위']
        
        # 기존 데이터 삭제 옵션
        if input("기존 데이터를 삭제하시겠습니까? (y/n): ").lower() == 'y':
            Employee.objects.all().delete()
            print("기존 데이터 삭제 완료")
        
        # 부서 매핑 (회사별 기본 부서)
        department_mapping = {
            'OK홀딩스주식회사': 'OK홀딩스',
            'OK홀딩스': 'OK홀딩스',
            'OK저축은행': 'OK저축은행',
            'OK저축은행(서울)': 'OK저축은행 서울지점',
            'OK저축은행(부산)': 'OK저축은행 부산본사',
            'OK저축은행(센터/지점)': 'OK저축은행 영업점',
            'OK캐피탈': 'OK캐피탈',
            'OK신용정보': 'OK신용정보',
            'OK데이터시스템': 'OK데이터시스템',
            'ON/OKIP/OKV/EX': 'OK넥스트',
            'OK넥스트': 'OK넥스트'
        }
        
        # 직책별 기본 부서
        responsibility_dept = {
            '부장': '경영관리부',
            '본사팀장': '본사',
            '센터장': '영업센터',
            '지점장': '영업지점',
            '팀장': '운영팀',
            '팀원': '업무지원팀'
        }
        
        created_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                구분 = row['구분']
                회사 = row['회사']
                직책 = row['직책']
                직위 = row['직위']
                
                # 회사명 정규화
                회사명 = department_mapping.get(회사, 회사)
                
                # 부서 결정 (직책 기반)
                부서 = responsibility_dept.get(직책, '일반부서')
                
                # 직급 정규화
                직급_mapping = {
                    '부장': '부장',
                    '부장(N)': '부장',
                    '차장': '차장',
                    '차장(N)': '차장',
                    '과장': '과장',
                    '과장(N)': '과장',
                    '대리': '대리',
                    '대리(N)': '대리',
                    '주임': '주임',
                    '사원': '사원',
                    '수석': '수석',
                    '책임': '책임',
                    '선임': '선임',
                    '전임': '전임',
                    '원': '원'
                }
                
                직급 = 직급_mapping.get(직위, 직위)
                
                # 고유한 이메일 생성
                email_base = f"{구분.lower()}_{회사명.replace(' ', '_').lower()}_{index}"
                email = f"{email_base}@ok.com"
                
                # 직원 생성
                employee = Employee.objects.create(
                    name=f"{회사명}_{직책}_{index+1}",
                    email=email,
                    company=회사명,
                    department=f"{회사명} {부서}",
                    final_department=부서,
                    position=직급,
                    current_position=직급,
                    new_position=직급,
                    responsibility=직책,
                    job_group=구분,
                    employment_status='재직',
                    hire_date=date.today().replace(day=1, month=random.randint(1, 12), year=random.randint(2015, 2023))
                )
                created_count += 1
                
                if created_count % 100 == 0:
                    print(f"진행 중... {created_count}명 생성")
                    
            except Exception as e:
                error_count += 1
                print(f"행 {index} 처리 중 오류: {e}")
                continue
        
        print(f"\n=== 데이터 로드 완료 ===")
        print(f"성공: {created_count}명")
        print(f"실패: {error_count}명")
        print(f"총 직원 수: {Employee.objects.count()}명")
        print(f"부서 수: {Employee.objects.values_list('department', flat=True).distinct().count()}개")
        print(f"재직자 수: {Employee.objects.filter(employment_status='재직').count()}명")
        
    except Exception as e:
        print(f"파일 읽기 실패: {e}")
        return

if __name__ == '__main__':
    load_employee_data()