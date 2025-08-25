#!/usr/bin/env python
"""
Employee 데이터셋 생성 스크립트
OK금융그룹 계열사 기준 실제적인 조직구조와 직급체계 반영
"""

import os
import sys
import django
import json
from faker import Faker
from datetime import date, datetime, timedelta
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from users.models import User

# 한국어 Faker
fake = Faker('ko_KR')

class EmployeeDataGenerator:
    def __init__(self):
        self.companies = [
            ('OK', 'OK저축은행'),
            ('OCI', 'OCI카드'),
            ('OFI', 'OK금융투자'),
            ('OKDS', 'OK디지털서비스'),
            ('OKH', 'OK캐피탈'),
            ('OKIP', 'OK인베스트먼트파트너스'),
        ]
        
        # 실제 금융권 조직구조
        self.organization_structure = {
            'OK': {
                '경영기획본부': ['전략기획부', '리스크관리부', '준법감시부'],
                '영업본부': ['리테일영업부', '기업금융부', '디지털영업부'],
                '운영본부': ['여신관리부', '자금부', '운영지원부'],
                'IT본부': ['IT기획부', '시스템개발부', '정보보안부'],
                '인사총무본부': ['인사부', '총무부', '교육연수부'],
            },
            'OCI': {
                '카드영업본부': ['개인카드부', '법인카드부', 'VIP영업부'],
                '심사본부': ['개인심사부', '법인심사부', '여신관리부'],
                'IT본부': ['IT기획부', '카드시스템부', '디지털혁신부'],
                '경영지원본부': ['경영기획부', '인사부', '재무부'],
            },
            'OFI': {
                '투자은행본부': ['기업금융부', 'M&A부', '자본시장부'],
                '자산운용본부': ['펀드운용부', '대체투자부', '리서치센터'],
                '리스크관리본부': ['리스크관리부', '준법감시부', '내부통제부'],
                '경영지원본부': ['경영기획부', 'IT부', '인사부'],
            }
        }
        
        # 실제 금융권 직급체계
        self.position_levels = [
            ('사원', 1), ('대리', 2), ('과장', 3), ('차장', 4), 
            ('부장', 5), ('상무', 6), ('전무', 7), ('부사장', 8), ('사장', 9)
        ]
        
        # 교육 수준
        self.education_levels = [
            '고등학교', '전문대학', '대학교', '대학원(석사)', '대학원(박사)'
        ]
        
        # 직무군별 태그
        self.job_tags = {
            '경영기획': ['전략기획', '사업계획', '성과관리', '조직관리'],
            '영업': ['개인영업', '기업영업', '신용분석', '고객관리'],
            'IT': ['시스템개발', '데이터분석', '정보보안', 'AI/ML'],
            '리스크': ['신용리스크', '시장리스크', '운영리스크', '준법감시'],
            '인사': ['채용', '교육', '평가', '복리후생'],
        }

    def generate_employee_data(self, count=100):
        """Employee 데이터 생성"""
        employees = []
        
        print(f"[INFO] {count}명의 직원 데이터 생성 중...")
        
        for i in range(count):
            # 회사 및 조직 선택
            company_code, company_name = random.choice(self.companies)
            
            if company_code in self.organization_structure:
                org_structure = self.organization_structure[company_code]
                headquarters = random.choice(list(org_structure.keys()))
                department = random.choice(org_structure[headquarters])
            else:
                headquarters = "경영지원본부"
                department = "총무부"
            
            # 직급 및 경력
            position_name, position_level = random.choice(self.position_levels)
            
            # 나이와 입사일 (직급에 따라 조정)
            base_age = 25 + (position_level * 3) + random.randint(-2, 5)
            age = max(23, min(65, base_age))
            
            # 입사일 (경력에 따라 조정)
            years_of_service = random.randint(position_level, position_level * 2 + 5)
            hire_date = date.today() - timedelta(days=years_of_service * 365 + random.randint(-180, 180))
            
            # 생년월일
            birth_date = date.today() - timedelta(days=age * 365 + random.randint(0, 365))
            
            # 성별 및 이름
            gender = random.choice(['M', 'F'])
            if gender == 'M':
                name = fake.name_male()
            else:
                name = fake.name_female()
            
            # 이메일 (회사 도메인)
            email_domains = {
                'OK': 'oksb.co.kr',
                'OCI': 'oci.co.kr', 
                'OFI': 'okfn.co.kr',
                'OKDS': 'okds.co.kr',
                'OKH': 'okcap.co.kr',
                'OKIP': 'okip.co.kr'
            }
            domain = email_domains.get(company_code, 'okgroup.co.kr')
            email = f"{fake.user_name()}.{i+1:03d}@{domain}"
            
            # 급여 등급 (직급에 따라)
            salary_grades = ['1급', '2급', '3급', '4급', '5급', '6급', '7급', '8급', '9급']
            salary_grade = salary_grades[min(position_level-1, len(salary_grades)-1)]
            
            # 직무태그 (부서에 따라)
            job_category = self.get_job_category(department)
            job_tag = random.choice(self.job_tags.get(job_category, ['일반사무']))
            
            # 평가 등급
            evaluation_grades = ['S', 'A+', 'A', 'B+', 'B', 'C']
            weights = [5, 15, 35, 25, 15, 5]  # 정규분포 형태
            final_evaluation = random.choices(evaluation_grades, weights=weights)[0]
            
            employee_data = {
                # 기본 정보
                'no': 20250000 + i + 1,
                'name': name,
                'email': email,
                'company': company_code,
                
                # 조직 정보
                'headquarters1': headquarters,
                'department1': department,
                'final_department': f"{headquarters} {department}",
                
                # 직급 정보
                'current_position': position_name,
                'initial_position': self.get_initial_position(position_level),
                'salary_grade': salary_grade,
                'promotion_level': str(position_level),
                
                # 개인 정보
                'gender': gender,
                'age': age,
                'birth_date': birth_date,
                'education': random.choice(self.education_levels),
                'marital_status': random.choice(['Y', 'N', 'N', 'N', 'Y']),  # 미혼이 더 많도록
                
                # 입사 정보
                'hire_date': hire_date,
                'group_join_date': hire_date,
                'career_join_date': hire_date if random.random() > 0.3 else None,
                'new_join_date': hire_date if random.random() > 0.7 else None,
                
                # 근무 정보
                'promotion_accumulated_years': round(years_of_service + random.uniform(-1, 2), 1),
                'final_evaluation': final_evaluation,
                
                # 직무 태그
                'job_tag_name': job_tag,
                'rank_tag_name': f"{position_name}급",
                'job_family': job_category,
                'job_field': department,
                
                # 연락처 (익명화)
                'phone': fake.phone_number(),
                'dummy_mobile': fake.phone_number(),
                'dummy_email': email,
                'dummy_name': name,
                'dummy_registered_address': fake.address(),
                'dummy_residence_address': fake.address(),
            }
            
            employees.append(employee_data)
            
            if (i + 1) % 20 == 0:
                print(f"[OK] {i + 1}명 생성 완료...")
        
        return employees

    def get_job_category(self, department):
        """부서명으로 직무군 판단"""
        if '기획' in department or '전략' in department:
            return '경영기획'
        elif '영업' in department or '고객' in department:
            return '영업'
        elif 'IT' in department or '시스템' in department or '개발' in department:
            return 'IT'
        elif '리스크' in department or '심사' in department or '준법' in department:
            return '리스크'
        elif '인사' in department or '총무' in department:
            return '인사'
        else:
            return '일반사무'

    def get_initial_position(self, current_level):
        """입사시 직급 추정"""
        # 대부분 사원으로 입사, 일부 경력직은 상위 직급으로 입사
        if current_level <= 2:
            return '사원'
        elif current_level <= 4:
            return random.choice(['사원', '대리'])
        else:
            return random.choice(['사원', '대리', '과장'])

    def save_to_database(self, employees_data):
        """데이터베이스에 저장"""
        print(f"\n[DB] 데이터베이스에 {len(employees_data)}명 저장 중...")
        
        created_count = 0
        updated_count = 0
        
        for emp_data in employees_data:
            try:
                # 이메일 중복 확인
                employee, created = Employee.objects.get_or_create(
                    email=emp_data['email'],
                    defaults=emp_data
                )
                
                if created:
                    created_count += 1
                else:
                    # 기존 데이터 업데이트
                    for key, value in emp_data.items():
                        setattr(employee, key, value)
                    employee.save()
                    updated_count += 1
                    
            except Exception as e:
                print(f"[ERROR] 데이터 저장 오류: {emp_data.get('name', 'Unknown')} - {e}")
                continue
        
        print(f"[OK] 저장 완료: {created_count}명 생성, {updated_count}명 업데이트")
        return created_count, updated_count

    def save_to_json(self, employees_data, filename='employee_dataset.json'):
        """JSON 파일로 저장"""
        # Date 객체를 문자열로 변환
        json_data = []
        for emp in employees_data:
            emp_json = emp.copy()
            for key, value in emp_json.items():
                if isinstance(value, date):
                    emp_json[key] = value.strftime('%Y-%m-%d')
            json_data.append(emp_json)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"[FILE] JSON 파일 저장 완료: {filename}")

def main():
    import sys
    
    # 명령행 인수로 직원 수 받기
    count = 50  # 기본값
    save_to_db = False  # 기본적으로 JSON만 생성
    
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("잘못된 입력입니다. 기본값 50으로 설정합니다.")
    
    if len(sys.argv) > 2 and sys.argv[2].lower() == 'save':
        save_to_db = True
    
    generator = EmployeeDataGenerator()
    
    print("=" * 60)
    print("OK금융그룹 Employee 데이터셋 생성기")
    print("=" * 60)
    print(f"생성할 직원 수: {count}명")
    print(f"데이터베이스 저장: {'예' if save_to_db else '아니오 (JSON만)'}")
    print()
    
    # 데이터 생성
    employees = generator.generate_employee_data(count)
    
    # JSON 파일로 저장
    generator.save_to_json(employees, f'employee_dataset_{count}명.json')
    
    if save_to_db:
        created, updated = generator.save_to_database(employees)
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("데이터 생성 및 저장 완료!")
        print("=" * 60)
        print(f"[STAT] 생성된 데이터: {len(employees)}명")
        print(f"✅ DB 저장: {created}명 신규, {updated}명 업데이트")
        print(f"📂 JSON 파일: employee_dataset_{count}명.json")
        
        # 회사별 통계
        company_stats = {}
        for emp in employees:
            company = emp['company']
            company_stats[company] = company_stats.get(company, 0) + 1
        
        print("\n📈 회사별 분포:")
        for company, count in company_stats.items():
            print(f"  - {company}: {count}명")
            
    else:
        print("\n[FILE] JSON 파일로 저장되었습니다.")
        print("Railway에 업로드하려면 upload_to_railway.py 스크립트를 사용하세요.")
        
        # 회사별 통계 표시
        company_stats = {}
        for emp in employees:
            company = emp['company']
            company_stats[company] = company_stats.get(company, 0) + 1
        
        print(f"\n[STAT] 생성된 데이터: {len(employees)}명")
        print("[STAT] 회사별 분포:")
        for company, count in company_stats.items():
            print(f"  - {company}: {count}명")

if __name__ == "__main__":
    main()