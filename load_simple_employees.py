#!/usr/bin/env python
"""
Faker 없이 간단한 직원 데이터 로드
Railway 배포용 최소 직원 데이터 생성
"""
import os
import sys
import django
from datetime import date, timedelta
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee

def generate_simple_employees():
    """간단한 직원 데이터 1000명 생성"""
    
    try:
        # 이미 충분한 데이터가 있는지 확인
        existing_count = Employee.objects.count()
        if existing_count >= 100:  # 100명 이상 있으면 스킵
            print(f"이미 {existing_count}명의 직원 데이터가 있습니다. 스킵합니다.")
            return
    except Exception as e:
        print(f"직원 수 확인 중 오류: {e}")
        existing_count = 0
    
    print(f"현재 직원 수: {existing_count}명")
    print("OK저축은행 직원 데이터를 생성합니다...")
    
    # 성과 이름 목록
    last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', 
                  '한', '오', '서', '신', '권', '황', '안', '송', '류', '홍']
    first_names_male = ['민수', '영호', '성민', '정훈', '대현', '준호', '성준', '지훈', '현우', '준영',
                        '태현', '승현', '동현', '재현', '진우', '현준', '성진', '민재', '준혁', '상현']
    first_names_female = ['지영', '민정', '수진', '현정', '미영', '은주', '혜진', '수연', '지은', '민지',
                          '서연', '지현', '수민', '예진', '은정', '혜원', '지원', '서영', '민서', '예은']
    
    # 본부별 부서 구조
    HEADQUARTERS = {
        '영업본부': {
            'departments': ['리테일영업부', '기업영업부', '채널영업부', '영업지원부', '영업전략부'],
            'ratio': 0.35  # 35%
        },
        '여신본부': {
            'departments': ['여신심사부', '여신관리부', '신용평가부', '채권관리부', '특별자산부'],
            'ratio': 0.20  # 20%
        },
        'IT본부': {
            'departments': ['시스템개발부', '인프라운영부', '정보보안부', '데이터관리부', 'IT기획부'],
            'ratio': 0.20  # 20%
        },
        '경영지원본부': {
            'departments': ['인사총무부', '재무회계부', '기획부', '리스크관리부', '준법지원부'],
            'ratio': 0.15  # 15%
        },
        '디지털혁신본부': {
            'departments': ['디지털전략부', '빅데이터부', '핀테크사업부', 'AI혁신부', '고객경험부'],
            'ratio': 0.10  # 10%
        }
    }
    
    # 직위 및 직급 분포
    POSITIONS = [
        {'title': '사원', 'code': 'STAFF', 'level': 1, 'ratio': 0.30, 'job_group': 'Non-PL'},
        {'title': '주임', 'code': 'SENIOR_STAFF', 'level': 2, 'ratio': 0.20, 'job_group': 'Non-PL'},
        {'title': '대리', 'code': 'SENIOR', 'level': 2, 'ratio': 0.20, 'job_group': 'Non-PL'},
        {'title': '과장', 'code': 'MANAGER', 'level': 3, 'ratio': 0.15, 'job_group': 'Non-PL'},
        {'title': '차장', 'code': 'DEPUTY_DIRECTOR', 'level': 4, 'ratio': 0.08, 'job_group': 'PL'},
        {'title': '부장', 'code': 'DIRECTOR', 'level': 5, 'ratio': 0.05, 'job_group': 'PL'},
        {'title': '상무', 'code': 'EXECUTIVE', 'level': 6, 'ratio': 0.015, 'job_group': 'PL'},
        {'title': '전무', 'code': 'SENIOR_EXECUTIVE', 'level': 7, 'ratio': 0.004, 'job_group': 'PL'},
        {'title': '부사장', 'code': 'VICE_PRESIDENT', 'level': 8, 'ratio': 0.001, 'job_group': 'PL'}
    ]
    
    # 총 생성할 직원 수
    total_employees = 1000 - existing_count
    if total_employees <= 0:
        print("생성할 직원이 없습니다.")
        return
    
    employees_created = 0
    employee_no = existing_count + 1001  # 사번 시작
    
    # 본부별 직원 생성
    for hq_name, hq_info in HEADQUARTERS.items():
        hq_employee_count = int(total_employees * hq_info['ratio'])
        departments = hq_info['departments']
        
        for i in range(hq_employee_count):
            if employees_created >= total_employees:
                break
                
            # 직위 선택 (가중치 적용)
            position_choice = random.choices(
                POSITIONS, 
                weights=[p['ratio'] for p in POSITIONS],
                k=1
            )[0]
            
            # 부서 선택
            department = random.choice(departments)
            
            # 성별 (60% 남성, 40% 여성)
            gender = random.choice(['M'] * 6 + ['F'] * 4)
            
            # 이름 생성
            last_name = random.choice(last_names)
            if gender == 'M':
                first_name = random.choice(first_names_male)
            else:
                first_name = random.choice(first_names_female)
            name = last_name + first_name
            
            # 입사일 (직급에 따라 다르게)
            years_ago = position_choice['level'] * 2 + random.randint(-2, 2)
            years_ago = max(0, min(years_ago, 25))  # 0~25년 사이
            hire_date = date.today() - timedelta(days=years_ago * 365 + random.randint(0, 364))
            
            # 이메일 생성 (영문으로)
            email_id = f"emp{employee_no:04d}"
            email = f"{email_id}@oksavingsbank.com"
            
            # 휴대폰 번호 (간단히)
            phone = f"010-{random.randint(1000, 9999):04d}-{random.randint(1000, 9999):04d}"
            
            # 재직 상태 (95% 재직, 5% 기타)
            employment_status = random.choice(['재직'] * 95 + ['휴직', '파견'] * 5)
            
            try:
                Employee.objects.create(
                    no=employee_no,
                    name=name,
                    email=email,
                    phone=phone,
                    department=department.replace('부', ''),  # '부' 제거
                    position=position_choice['code'],
                    company='OK저축은행',
                    headquarters1=hq_name,
                    headquarters2='',  # headquarters2는 있음
                    final_department=department,
                    current_position=position_choice['title'],
                    employment_status=employment_status,
                    hire_date=hire_date,
                    gender=gender,
                    job_group=position_choice['job_group'],
                    growth_level=position_choice['level'],
                    birth_date=date(random.randint(1965, 2000), random.randint(1, 12), random.randint(1, 28)),
                    education=random.choice(['고졸', '전문대졸', '대졸', '석사', '박사']),
                    address=f"{random.choice(['서울', '경기', '인천', '부산', '대구', '광주', '대전'])}시",
                    emergency_contact=f"010-{random.randint(1000, 9999):04d}-{random.randint(1000, 9999):04d}"
                )
                employees_created += 1
                employee_no += 1
                
                if employees_created % 100 == 0:
                    print(f"  {employees_created}명 생성 완료...")
                    
            except Exception as e:
                print(f"직원 생성 오류: {e}")
    
    # 통계 출력
    print(f"\n생성 완료! 총 {employees_created}명의 직원이 추가되었습니다.")
    print(f"전체 직원 수: {Employee.objects.count()}명")
    
    # 본부별 분포 출력
    print("\n본부별 직원 분포:")
    for hq_name in HEADQUARTERS.keys():
        count = Employee.objects.filter(headquarters1=hq_name).count()
        print(f"  {hq_name}: {count}명")

if __name__ == "__main__":
    try:
        generate_simple_employees()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()