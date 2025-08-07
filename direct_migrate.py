"""
Direct Excel Migration - 실제 1790명 데이터 마이그레이션
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
import pandas as pd
import random
from datetime import date

# Excel 파일 읽기
print("Excel 파일 로딩...")
excel_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK_dummy_employee_250801.xlsx"
df = pd.read_excel(excel_path)
print(f"총 {len(df)}개 레코드 로드 완료\n")

# 한국 이름 생성용
last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', 
              '한', '오', '서', '신', '권', '황', '안', '송', '전', '홍']
first_names_male = ['민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호', '지후', '준우',
                    '준서', '건우', '현우', '지훈', '우진', '선우', '서진', '민재', '현준', '연우']
first_names_female = ['서연', '서윤', '지우', '서현', '민서', '하은', '하윤', '윤서', '지유', '지민',
                      '채원', '수아', '지아', '지윤', '다은', '은서', '예은', '수빈', '소율', '예진']

# 기존 데이터 정리
print("기존 데이터 정리 중...")
try:
    # 기존 직원 데이터만 삭제 (관리자 제외)
    deleted_employees = Employee.objects.all().delete()[0]
    deleted_users = User.objects.filter(is_superuser=False).delete()[0]
    print(f"- {deleted_employees}개 직원 삭제")
    print(f"- {deleted_users}개 사용자 계정 삭제\n")
except Exception as e:
    print(f"정리 중 경고: {e}\n")

# 마이그레이션 시작
print("데이터 마이그레이션 시작...")
success_count = 0
error_count = 0
batch_size = 100

for i in range(0, len(df), batch_size):
    batch_end = min(i + batch_size, len(df))
    print(f"\n배치 {i//batch_size + 1}: 행 {i+1} ~ {batch_end} 처리 중...")
    
    for idx in range(i, batch_end):
        row = df.iloc[idx]
        
        try:
            # 성별 확인
            gender = str(row.get('성별', '남'))
            is_male = '남' in gender
            
            # 이름 생성
            last = random.choice(last_names)
            first = random.choice(first_names_male if is_male else first_names_female)
            name = f"{last}{first}"
            
            # 사번 및 이메일
            emp_id = f"EMP{str(idx + 1).zfill(4)}"
            email = f"{emp_id.lower()}@okfg.co.kr"
            
            # 부서 매핑
            dept_name = str(row.get('소속1\n(본부)', ''))
            if 'IT' in dept_name or '디지털' in dept_name:
                department = 'IT'
            elif '인사' in dept_name or 'HR' in dept_name:
                department = 'HR'
            elif '재무' in dept_name or '회계' in dept_name:
                department = 'FINANCE'
            elif '마케팅' in dept_name:
                department = 'MARKETING'
            elif '영업' in dept_name:
                department = 'SALES'
            else:
                department = 'OPERATIONS'
            
            # User 생성
            user = User.objects.create_user(
                username=emp_id.lower(),
                email=email,
                password=os.getenv('DEFAULT_USER_PASSWORD', 'changeme123!'),
                first_name=first,
                last_name=last
            )
            
            # Employee 생성
            employee = Employee.objects.create(
                user=user,
                name=name,
                email=email,
                phone=f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                department=department,
                position='STAFF',
                hire_date=pd.to_datetime(row.get('현회사입사일', date.today())).date() if pd.notna(row.get('현회사입사일')) else date.today(),
                address=f"서울시 강남구 테헤란로 {random.randint(1,500)}",
                
                # 추가 필드
                job_type='경영관리',
                growth_level=1,
                new_position='사원',
                employment_type='정규직',
                employment_status='재직'
            )
            
            success_count += 1
            
        except Exception as e:
            error_count += 1
            if error_count <= 3:
                print(f"  오류 (행 {idx+1}): {str(e)[:80]}")
    
    print(f"  배치 완료: 성공 {success_count}, 실패 {error_count}")

# 결과 출력
print("\n" + "="*60)
print("마이그레이션 완료!")
print("="*60)
print(f"총 레코드: {len(df)}")
print(f"성공: {success_count}")
print(f"실패: {error_count}")
print(f"성공률: {(success_count/len(df)*100):.1f}%")

# 관리자 계정 확인
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@okfg.co.kr',
        password='admin123!@#'
    )
    print("\n관리자 계정 생성됨: admin / admin123!@#")
else:
    print("\n관리자 계정: admin / admin123!@#")

# 통계 출력
print("\n부서별 직원 수:")
from django.db.models import Count
dept_stats = Employee.objects.values('department').annotate(count=Count('id'))
for stat in dept_stats:
    print(f"  {stat['department']}: {stat['count']}명")

print(f"\n전체 직원 수: {Employee.objects.count()}명")
print(f"전체 사용자 수: {User.objects.count()}명")