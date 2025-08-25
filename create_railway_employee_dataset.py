#!/usr/bin/env python
"""
Railway용 현실적인 Employee 가상 데이터셋 생성 스크립트

금융권 일반적인 인력 분포를 반영한 가상 데이터 생성:
- 계열사별 인원 분포
- 직급별 피라미드 구조
- 연령대별 분포
- 보상 수준 분포
- 성과 등급 분포
"""

import os
import sys
import django
import random
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway Employee 가상 데이터셋 생성")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection, transaction
from employees.models import Employee
from django.contrib.auth.models import User

# ========================================
# 1. 데이터 분포 정의 (금융권 일반적 분포)
# ========================================

# 조직 구조 (OK금융그룹)
ORGANIZATION_STRUCTURE = {
    'OK금융그룹': {
        'OK저축은행': {
            '리테일본부': ['영업1팀', '영업2팀', '영업3팀', '고객지원팀'],
            '기업금융본부': ['기업금융1팀', '기업금융2팀', '심사팀'],
            'IT본부': ['IT개발팀', 'IT운영팀', '정보보안팀', '데이터팀'],
            '경영지원본부': ['인사팀', '재무팀', '총무팀', '리스크관리팀'],
            '전략기획본부': ['경영기획팀', '신사업팀', '마케팅팀']
        },
        'OK캐피탈': {
            '자산운용본부': ['운용1팀', '운용2팀', '리서치팀'],
            '영업본부': ['법인영업팀', '리테일영업팀'],
            '경영지원본부': ['인사팀', '재무팀', '리스크팀']
        },
        'OK증권': {
            'IB본부': ['ECM팀', 'DCM팀', 'M&A팀'],
            '리테일본부': ['지점영업팀', '온라인영업팀', 'PB팀'],
            '자산운용본부': ['주식운용팀', '채권운용팀'],
            '경영지원본부': ['인사팀', '재무팀', '컴플라이언스팀']
        }
    }
}

# 직급 체계 및 분포 (피라미드 구조)
POSITION_DISTRIBUTION = {
    '사원': 0.30,      # 30%
    '대리': 0.25,      # 25%
    '과장': 0.20,      # 20%
    '차장': 0.12,      # 12%
    '부장': 0.08,      # 8%
    '팀장': 0.03,      # 3%
    '본부장': 0.015,   # 1.5%
    '임원': 0.005      # 0.5%
}

# 직급별 연령 범위 (한국 금융권 기준)
POSITION_AGE_RANGE = {
    '사원': (24, 30),
    '대리': (28, 35),
    '과장': (32, 40),
    '차장': (36, 45),
    '부장': (40, 50),
    '팀장': (42, 52),
    '본부장': (45, 55),
    '임원': (48, 60)
}

# 직급별 연봉 범위 (단위: 만원)
POSITION_SALARY_RANGE = {
    '사원': (3500, 5000),
    '대리': (4500, 6500),
    '과장': (6000, 8000),
    '차장': (7500, 10000),
    '부장': (9000, 12000),
    '팀장': (10000, 14000),
    '본부장': (12000, 18000),
    '임원': (15000, 25000)
}

# 성과 등급 분포 (정규분포)
PERFORMANCE_DISTRIBUTION = {
    'S': 0.05,   # 5% - 최우수
    'A': 0.20,   # 20% - 우수
    'B': 0.50,   # 50% - 보통
    'C': 0.20,   # 20% - 미흡
    'D': 0.05    # 5% - 부진
}

# 학력 분포
EDUCATION_DISTRIBUTION = {
    '고졸': 0.05,
    '전문대졸': 0.10,
    '대졸': 0.70,
    '석사': 0.13,
    '박사': 0.02
}

# 성별 분포 (금융권 평균)
GENDER_DISTRIBUTION = {
    'M': 0.65,  # 65% 남성
    'F': 0.35   # 35% 여성
}

# 결혼 여부 (연령대별)
def get_marriage_probability(age):
    """연령별 결혼 확률"""
    if age < 28:
        return 0.1
    elif age < 35:
        return 0.6
    elif age < 40:
        return 0.8
    else:
        return 0.85

# 한국 성씨 분포 (상위 20개)
KOREAN_LAST_NAMES = [
    '김', '이', '박', '최', '정', '강', '조', '윤', '장', '임',
    '한', '오', '서', '신', '권', '황', '안', '송', '류', '홍'
]

# 한국 이름 글자 (예시)
KOREAN_FIRST_NAMES_1 = ['민', '서', '지', '현', '수', '영', '정', '성', '태', '준']
KOREAN_FIRST_NAMES_2 = ['우', '호', '진', '혁', '준', '영', '수', '희', '경', '원']

# 직군/직종 분류
JOB_FAMILIES = {
    '영업직': ['영업', '마케팅', '고객관리'],
    '기술직': ['IT개발', 'IT운영', '데이터분석', '정보보안'],
    '지원직': ['인사', '재무', '총무', '기획'],
    '전문직': ['리스크관리', '컴플라이언스', '법무', '감사'],
    '투자직': ['자산운용', 'IB', '리서치']
}


class EmployeeDataGenerator:
    """Employee 가상 데이터 생성기"""
    
    def __init__(self, total_employees: int = 500):
        self.total_employees = total_employees
        self.generated_employee_numbers = set()
        self.generated_employees = []
        
    def generate_korean_name(self, gender: str) -> str:
        """한국식 이름 생성"""
        last_name = random.choice(KOREAN_LAST_NAMES)
        first_name = random.choice(KOREAN_FIRST_NAMES_1) + random.choice(KOREAN_FIRST_NAMES_2)
        return f"{last_name}{first_name}"
    
    def generate_employee_number(self) -> str:
        """사번 생성 (YYYYNNNN 형식)"""
        while True:
            year = random.randint(2000, 2024)
            number = random.randint(1, 9999)
            emp_no = f"{year}{number:04d}"
            if emp_no not in self.generated_employee_numbers:
                self.generated_employee_numbers.add(emp_no)
                return emp_no
    
    def generate_email(self, name: str, emp_no: str) -> str:
        """회사 이메일 생성"""
        # 간단한 영문 변환 (실제로는 더 정교한 변환 필요)
        email_id = f"emp{emp_no[-4:]}"
        return f"{email_id}@okfn.co.kr"
    
    def generate_phone(self) -> str:
        """휴대폰 번호 생성"""
        return f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    
    def generate_address(self) -> str:
        """주소 생성 (시/구 수준)"""
        cities = ['서울시', '경기도', '인천시', '부산시', '대구시', '대전시', '광주시']
        districts = ['강남구', '서초구', '송파구', '강서구', '마포구', '영등포구', '중구']
        return f"{random.choice(cities)} {random.choice(districts)}"
    
    def calculate_hire_date(self, age: int, position: str) -> date:
        """입사일 계산 (나이와 직급 고려)"""
        today = date.today()
        
        # 직급별 평균 근속년수
        tenure_by_position = {
            '사원': random.randint(0, 3),
            '대리': random.randint(3, 6),
            '과장': random.randint(6, 10),
            '차장': random.randint(10, 14),
            '부장': random.randint(14, 18),
            '팀장': random.randint(15, 20),
            '본부장': random.randint(18, 25),
            '임원': random.randint(20, 30)
        }
        
        tenure_years = tenure_by_position.get(position, 5)
        hire_date = today - timedelta(days=tenure_years * 365 + random.randint(0, 365))
        return hire_date
    
    def generate_employees(self) -> List[Dict]:
        """전체 직원 데이터 생성"""
        employees = []
        
        # 직급별 인원 계산
        position_counts = {}
        remaining = self.total_employees
        
        for position, ratio in POSITION_DISTRIBUTION.items():
            if position == '임원':  # 마지막 직급
                count = remaining
            else:
                count = int(self.total_employees * ratio)
                remaining -= count
            position_counts[position] = count
        
        print(f"직급별 인원 분포:")
        for position, count in position_counts.items():
            print(f"  - {position}: {count}명")
        
        # 조직별 인원 배치
        all_departments = []
        for group, companies in ORGANIZATION_STRUCTURE.items():
            for company, headquarters in companies.items():
                for hq, teams in headquarters.items():
                    for team in teams:
                        all_departments.append({
                            'group': group,
                            'company': company,
                            'headquarters': hq,
                            'team': team
                        })
        
        # 각 직급별로 직원 생성
        emp_id = 1
        for position, count in position_counts.items():
            age_min, age_max = POSITION_AGE_RANGE[position]
            salary_min, salary_max = POSITION_SALARY_RANGE[position]
            
            for _ in range(count):
                # 기본 정보 생성
                gender = 'M' if random.random() < GENDER_DISTRIBUTION['M'] else 'F'
                age = random.randint(age_min, age_max)
                name = self.generate_korean_name(gender)
                emp_no = self.generate_employee_number()
                
                # 조직 배치 (랜덤)
                dept = random.choice(all_departments)
                
                # 급여 (정규분포 적용)
                base_salary = random.randint(salary_min, salary_max)
                # 성과급 반영 (성과 등급에 따라)
                performance = random.choices(
                    list(PERFORMANCE_DISTRIBUTION.keys()),
                    weights=list(PERFORMANCE_DISTRIBUTION.values())
                )[0]
                
                performance_bonus = {
                    'S': 1.3, 'A': 1.15, 'B': 1.0, 'C': 0.9, 'D': 0.8
                }[performance]
                
                total_salary = int(base_salary * performance_bonus)
                
                # 학력
                education = random.choices(
                    list(EDUCATION_DISTRIBUTION.keys()),
                    weights=list(EDUCATION_DISTRIBUTION.values())
                )[0]
                
                # 결혼 여부
                marital_status = 'Y' if random.random() < get_marriage_probability(age) else 'N'
                
                # 직군/직종 결정
                if '영업' in dept['team']:
                    job_family = '영업직'
                    job_role = '영업'
                elif 'IT' in dept['team'] or '데이터' in dept['team']:
                    job_family = '기술직'
                    job_role = 'IT개발' if '개발' in dept['team'] else 'IT운영'
                elif '인사' in dept['team'] or '재무' in dept['team'] or '총무' in dept['team']:
                    job_family = '지원직'
                    job_role = dept['team'].replace('팀', '')
                elif '리스크' in dept['team'] or '컴플라이언스' in dept['team']:
                    job_family = '전문직'
                    job_role = '리스크관리'
                else:
                    job_family = '투자직'
                    job_role = '자산운용'
                
                employee = {
                    'id': emp_id,
                    'employee_no': emp_no,
                    'name': name,
                    'email': self.generate_email(name, emp_no),
                    'phone': self.generate_phone(),
                    'gender': gender,
                    'birth_date': date.today() - timedelta(days=age * 365 + random.randint(0, 365)),
                    'age': age,
                    'address': self.generate_address(),
                    'hire_date': self.calculate_hire_date(age, position),
                    
                    # 조직 정보
                    'group': dept['group'],
                    'company': dept['company'],
                    'headquarters': dept['headquarters'],
                    'department': dept['team'],
                    'team': dept['team'],
                    
                    # 직급/직책
                    'position': position,
                    'job_title': position if position in ['팀장', '본부장', '임원'] else None,
                    
                    # 직군/직종
                    'job_family': job_family,
                    'job_role': job_role,
                    
                    # 인사 정보
                    'education': education,
                    'marital_status': marital_status,
                    'military_service': 'Y' if gender == 'M' and age > 28 else 'N',
                    
                    # 평가/보상
                    'performance_grade': performance,
                    'salary_grade': position,
                    'annual_salary': total_salary,
                    
                    # 상태
                    'employment_status': '재직',
                    'employment_type': '정규직' if random.random() > 0.1 else '계약직',
                    
                    # 추가 정보
                    'awards_count': random.randint(0, 3) if performance in ['S', 'A'] else 0,
                    'discipline_count': random.randint(0, 1) if performance == 'D' else 0,
                }
                
                employees.append(employee)
                emp_id += 1
        
        self.generated_employees = employees
        return employees
    
    def save_to_database(self, employees: List[Dict]) -> int:
        """데이터베이스에 저장"""
        created_count = 0
        
        with transaction.atomic():
            for emp_data in employees:
                try:
                    # User 생성 (있으면 가져오기)
                    user, user_created = User.objects.get_or_create(
                        username=emp_data['employee_no'],
                        defaults={
                            'email': emp_data['email'],
                            'first_name': emp_data['name'][1:],
                            'last_name': emp_data['name'][0],
                            'is_active': True
                        }
                    )
                    
                    if user_created:
                        user.set_password('password123')  # 기본 비밀번호
                        user.save()
                    
                    # Employee 생성
                    employee, created = Employee.objects.update_or_create(
                        no=emp_data['employee_no'],
                        defaults={
                            'user': user,
                            'name': emp_data['name'],
                            'email': emp_data['email'],
                            'phone': emp_data['phone'],
                            'gender': emp_data['gender'],
                            'birth_date': emp_data['birth_date'],
                            'age': emp_data['age'],
                            'address': emp_data['address'],
                            'hire_date': emp_data['hire_date'],
                            
                            # 조직 정보
                            'group_name': emp_data['group'],
                            'company': emp_data['company'],
                            'headquarters1': emp_data['headquarters'],
                            'department': emp_data['department'],
                            'department1': emp_data['department'],
                            
                            # 직급/직책
                            'position': emp_data['position'],
                            'title': emp_data['job_title'] or '',
                            
                            # 직군/직종
                            'job_family': emp_data['job_family'],
                            'job_role': emp_data['job_role'],
                            
                            # 인사 정보
                            'education': emp_data['education'],
                            'marital_status': emp_data['marital_status'],
                            
                            # 평가/보상
                            'salary_grade': emp_data['salary_grade'],
                            
                            # 상태
                            'employment_status': emp_data['employment_status'],
                            'employment_type': emp_data['employment_type'],
                        }
                    )
                    
                    if created:
                        created_count += 1
                        
                except Exception as e:
                    print(f"[ERROR] {emp_data['name']} 생성 실패: {e}")
        
        return created_count
    
    def export_to_json(self, filename: str = 'employee_dataset.json'):
        """JSON 파일로 내보내기"""
        # datetime 객체를 문자열로 변환
        export_data = []
        for emp in self.generated_employees:
            emp_copy = emp.copy()
            emp_copy['birth_date'] = emp_copy['birth_date'].isoformat()
            emp_copy['hire_date'] = emp_copy['hire_date'].isoformat()
            export_data.append(emp_copy)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] {filename}에 {len(export_data)}명의 데이터 저장")
    
    def print_statistics(self):
        """생성된 데이터 통계 출력"""
        if not self.generated_employees:
            return
        
        print("\n" + "="*60)
        print("생성된 데이터 통계")
        print("="*60)
        
        # 회사별 통계
        company_stats = {}
        for emp in self.generated_employees:
            company = emp['company']
            if company not in company_stats:
                company_stats[company] = 0
            company_stats[company] += 1
        
        print("\n1. 계열사별 인원:")
        for company, count in company_stats.items():
            print(f"   - {company}: {count}명 ({count/len(self.generated_employees)*100:.1f}%)")
        
        # 연령대별 통계
        age_ranges = {'20대': 0, '30대': 0, '40대': 0, '50대': 0, '60대': 0}
        for emp in self.generated_employees:
            age = emp['age']
            if age < 30:
                age_ranges['20대'] += 1
            elif age < 40:
                age_ranges['30대'] += 1
            elif age < 50:
                age_ranges['40대'] += 1
            elif age < 60:
                age_ranges['50대'] += 1
            else:
                age_ranges['60대'] += 1
        
        print("\n2. 연령대별 분포:")
        for age_range, count in age_ranges.items():
            print(f"   - {age_range}: {count}명 ({count/len(self.generated_employees)*100:.1f}%)")
        
        # 성과 등급 분포
        performance_stats = {}
        for emp in self.generated_employees:
            grade = emp['performance_grade']
            if grade not in performance_stats:
                performance_stats[grade] = 0
            performance_stats[grade] += 1
        
        print("\n3. 성과 등급 분포:")
        for grade in ['S', 'A', 'B', 'C', 'D']:
            count = performance_stats.get(grade, 0)
            print(f"   - {grade}등급: {count}명 ({count/len(self.generated_employees)*100:.1f}%)")
        
        # 평균 연봉 (직급별)
        salary_by_position = {}
        count_by_position = {}
        for emp in self.generated_employees:
            position = emp['position']
            if position not in salary_by_position:
                salary_by_position[position] = 0
                count_by_position[position] = 0
            salary_by_position[position] += emp['annual_salary']
            count_by_position[position] += 1
        
        print("\n4. 직급별 평균 연봉:")
        for position in ['사원', '대리', '과장', '차장', '부장', '팀장', '본부장', '임원']:
            if position in salary_by_position:
                avg_salary = salary_by_position[position] / count_by_position[position]
                print(f"   - {position}: {avg_salary:,.0f}만원")


def main():
    """메인 실행 함수"""
    print("\n시작: Employee 가상 데이터셋 생성\n")
    
    # 생성할 직원 수
    total_employees = 500
    
    # 생성기 초기화
    generator = EmployeeDataGenerator(total_employees)
    
    # 1. 데이터 생성
    print(f"1. {total_employees}명의 가상 직원 데이터 생성 중...")
    employees = generator.generate_employees()
    print(f"[OK] {len(employees)}명 생성 완료")
    
    # 2. 통계 출력
    generator.print_statistics()
    
    # 3. JSON 파일로 저장
    print("\n2. JSON 파일로 내보내기...")
    generator.export_to_json('railway_employee_dataset.json')
    
    # 4. 데이터베이스 저장 여부 확인
    save_to_db = input("\n데이터베이스에 저장하시겠습니까? (y/n): ")
    if save_to_db.lower() == 'y':
        print("\n3. 데이터베이스에 저장 중...")
        created_count = generator.save_to_database(employees)
        print(f"[OK] {created_count}명 저장 완료")
    
    print("\n" + "="*60)
    print("[SUCCESS] Employee 가상 데이터셋 생성 완료!")
    print("="*60)


if __name__ == "__main__":
    main()