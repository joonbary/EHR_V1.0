"""
Excel to EHR Database Migration Script
실제 회사 직원 데이터를 EHR 시스템으로 마이그레이션
민감 정보는 가상 데이터로 대체
"""

import os
import sys
import django
import pandas as pd
import random
import string
from datetime import datetime, date, timedelta
import re

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from employees.models import Employee


class ExcelToDBMigration:
    """Excel 데이터를 Django DB로 마이그레이션하는 클래스"""
    
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.df = None
        self.korean_last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', 
                                  '한', '오', '서', '신', '권', '황', '안', '송', '전', '홍']
        self.korean_first_names = ['민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호', '지후', '준우',
                                   '준서', '건우', '현우', '지훈', '우진', '선우', '서진', '민재', '현준', '연우',
                                   '지원', '서연', '서윤', '지우', '서현', '민서', '하은', '하윤', '윤서', '지유',
                                   '지민', '채원', '수아', '지아', '지윤', '다은', '은서', '예은', '수빈', '소율']
        
        # 회사별 이메일 도메인
        self.email_domains = {
            'OK저축은행': 'oksb.co.kr',
            'OK캐피탈': 'okcapital.co.kr', 
            'OK금융투자': 'okfi.co.kr',
            'OK금융그룹': 'okfg.co.kr',
            'DEFAULT': 'okfg.co.kr'
        }
        
        # 서울시 주요 구/동 목록
        self.seoul_districts = ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
                                '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
                                '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구']
        
        self.seoul_dongs = ['역삼동', '논현동', '청담동', '삼성동', '대치동', '도곡동', '개포동', '일원동', '수서동',
                           '세곡동', '압구정동', '신사동', '논현동', '방배동', '서초동', '잠원동', '반포동', '양재동',
                           '우면동', '원지동', '신원동', '내곡동', '염곡동', '신월동', '신정동', '목동']
        
        self.created_users = []  # 생성된 User 객체들을 추적
        
    def load_excel(self):
        """Excel 파일 로드"""
        print("Excel 파일 로딩 중...")
        self.df = pd.read_excel(self.excel_path)
        print(f"총 {len(self.df)}개 행 로드 완료")
        return self.df
    
    def generate_korean_name(self, gender=None):
        """한국식 이름 생성"""
        last_name = random.choice(self.korean_last_names)
        first_name = random.choice(self.korean_first_names)
        return f"{last_name}{first_name}"
    
    def generate_resident_number(self, age, gender):
        """주민등록번호 생성 (가상)"""
        current_year = datetime.now().year
        birth_year = current_year - age
        
        # 2000년 이후 출생자는 3,4 / 이전은 1,2
        if birth_year >= 2000:
            gender_digit = '3' if gender == '남' else '4'
            year_prefix = str(birth_year)[2:]
        else:
            gender_digit = '1' if gender == '남' else '2'
            year_prefix = str(birth_year)[2:]
        
        month = str(random.randint(1, 12)).zfill(2)
        day = str(random.randint(1, 28)).zfill(2)
        
        # 뒷자리는 임의 생성 (실제 검증 로직 없음)
        back_part = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        return f"{year_prefix}{month}{day}-{gender_digit}{back_part}"
    
    def generate_employee_id(self, index, company):
        """사번 생성"""
        # 회사별 prefix
        company_prefix = {
            'OK저축은행': 'SB',
            'OK캐피탈': 'CP',
            'OK금융투자': 'FI',
            'OK금융그룹': 'FG'
        }.get(company, 'OK')
        
        year = datetime.now().year
        return f"{company_prefix}{year}{str(index).zfill(4)}"
    
    def generate_phone_number(self):
        """전화번호 생성"""
        return f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    
    def generate_address(self):
        """주소 생성"""
        district = random.choice(self.seoul_districts)
        dong = random.choice(self.seoul_dongs)
        street_num = random.randint(1, 200)
        detail_num = random.randint(1, 50)
        
        return f"서울특별시 {district} {dong} {street_num}길 {detail_num}"
    
    def generate_email(self, name, company):
        """이메일 생성"""
        # 이름을 영문으로 변환 (간단한 매핑)
        name_eng = ''.join(random.choices(string.ascii_lowercase, k=6))
        domain = self.email_domains.get(company, self.email_domains['DEFAULT'])
        
        # 중복 방지를 위해 랜덤 숫자 추가
        random_num = random.randint(100, 999)
        return f"{name_eng}{random_num}@{domain}"
    
    def map_department(self, dept1, dept2, dept3, dept4):
        """소속 정보를 부서로 매핑"""
        # 본부 레벨로 대분류
        if pd.notna(dept1):
            dept1_str = str(dept1)
            if any(keyword in dept1_str for keyword in ['IT', '디지털', '정보', '시스템']):
                return 'IT'
            elif any(keyword in dept1_str for keyword in ['인사', 'HR', '인재', '조직']):
                return 'HR'
            elif any(keyword in dept1_str for keyword in ['재무', '회계', '자금', '결산']):
                return 'FINANCE'
            elif any(keyword in dept1_str for keyword in ['마케팅', '홍보', '브랜드']):
                return 'MARKETING'
            elif any(keyword in dept1_str for keyword in ['영업', '고객', '지점']):
                return 'SALES'
            else:
                return 'OPERATIONS'
        return 'OPERATIONS'
    
    def map_position(self, position_str):
        """직책을 새로운 position 필드로 매핑"""
        if pd.isna(position_str):
            return '사원'
        
        position_str = str(position_str)
        
        # 직책 매핑
        position_map = {
            '사원': '사원',
            '선임': '선임',
            '주임': '주임',
            '대리': '대리',
            '과장': '과장',
            '차장': '차장',
            '부부장': '부부장',
            '부장': '부장',
            '팀장': '팀장',
            '지점장': '지점장',
            '본부장': '본부장'
        }
        
        for key, value in position_map.items():
            if key in position_str:
                return value
        
        return '사원'
    
    def map_job_group(self, job_group_str):
        """직군 매핑"""
        if pd.isna(job_group_str):
            return 'Non-PL'
        
        job_group_str = str(job_group_str)
        if 'PL' in job_group_str and 'Non' not in job_group_str:
            return 'PL'
        return 'Non-PL'
    
    def map_job_type(self, job_type_str):
        """직종 매핑"""
        if pd.isna(job_type_str):
            return '경영관리'
        
        job_type_str = str(job_type_str)
        
        # 직종 매핑
        job_type_map = {
            '고객지원': '고객지원',
            'IT기획': 'IT기획',
            'IT개발': 'IT개발',
            'IT운영': 'IT운영',
            '경영관리': '경영관리',
            '기업영업': '기업영업',
            '기업금융': '기업금융',
            '리테일금융': '리테일금융',
            '투자금융': '투자금융'
        }
        
        for key, value in job_type_map.items():
            if key in job_type_str:
                return value
        
        # 키워드 기반 매핑
        if any(keyword in job_type_str for keyword in ['IT', '시스템', '개발']):
            return 'IT개발'
        elif any(keyword in job_type_str for keyword in ['영업', '세일즈']):
            return '기업영업'
        elif any(keyword in job_type_str for keyword in ['금융', '투자']):
            return '투자금융'
        
        return '경영관리'
    
    def map_growth_level(self, level_str):
        """성장레벨 매핑"""
        if pd.isna(level_str):
            return 1
        
        level_str = str(level_str)
        
        # 숫자 추출
        numbers = re.findall(r'\d+', level_str)
        if numbers:
            level = int(numbers[0])
            if 1 <= level <= 6:
                return level
        
        return 1
    
    def map_employment_type(self, emp_type_str):
        """고용유형 매핑"""
        if pd.isna(emp_type_str):
            return '정규직'
        
        emp_type_str = str(emp_type_str)
        
        if '정규' in emp_type_str:
            return '정규직'
        elif '계약' in emp_type_str:
            return '계약직'
        elif '파견' in emp_type_str:
            return '파견'
        elif '인턴' in emp_type_str:
            return '인턴'
        
        return '정규직'
    
    def extract_grade_level(self, grade_str):
        """급호에서 숫자 추출"""
        if pd.isna(grade_str):
            return 1
        
        grade_str = str(grade_str)
        
        # '-' 또는 비어있으면 1 반환
        if grade_str == '-' or not grade_str:
            return 1
        
        # 숫자 추출 (예: '3급' -> 3)
        numbers = re.findall(r'\d+', grade_str)
        if numbers:
            return int(numbers[0])
        
        return 1
    
    def delete_existing_data(self):
        """기존 가상 데이터 삭제"""
        print("\n기존 데이터 삭제 중...")
        
        try:
            # 기존 Employee 데이터 삭제
            deleted_count = Employee.objects.all().delete()[0]
            print(f"- {deleted_count}개의 기존 직원 데이터 삭제")
        except Exception as e:
            print(f"- Employee 데이터 삭제 중 오류 발생: {str(e)}")
            print("- 데이터베이스를 재설정합니다...")
            
        try:
            # 연결된 User 계정도 삭제 (superuser 제외)
            users_to_delete = User.objects.filter(is_superuser=False)
            user_count = users_to_delete.count()
            users_to_delete.delete()
            print(f"- {user_count}개의 사용자 계정 삭제 (관리자 계정 제외)")
        except Exception as e:
            print(f"- User 계정 삭제 중 오류 발생: {str(e)}")
    
    def migrate_data(self):
        """데이터 마이그레이션 실행"""
        print("\n데이터 마이그레이션 시작...")
        
        success_count = 0
        error_count = 0
        errors = []
        
        # 배치 처리를 위해 트랜잭션 제거
        for index, row in self.df.iterrows():
            try:
                # 더미 데이터 생성
                name = self.generate_korean_name(row.get('성별'))
                resident_number = self.generate_resident_number(
                    int(row.get('나이\n(만)', 30)),
                    row.get('성별', '남')
                )
                employee_id = self.generate_employee_id(index + 1, row.get('회사', 'OK금융그룹'))
                phone = self.generate_phone_number()
                address_reg = self.generate_address()  # 주민등록지 주소
                address_actual = self.generate_address()  # 실거주지 주소
                email = self.generate_email(name, row.get('회사', 'OK금융그룹'))
                
                # User 객체 생성
                username = f"user_{employee_id.lower()}"
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='okfg2024!',  # 기본 비밀번호
                    first_name=name[1:],  # 이름
                    last_name=name[0]  # 성
                )
                self.created_users.append(user)
                
                # Employee 객체 생성
                employee = Employee(
                    user=user,
                    name=name,
                    email=email,
                    phone=phone,
                    address=address_actual,
                    
                    # 부서 매핑
                    department=self.map_department(
                        row.get('소속1\n(본부)'),
                        row.get('소속2\n(부)'),
                        row.get('소속3\n(센터/영업점/본사팀)'),
                        row.get('소속4\n(PL/센터팀)')
                    ),
                    
                    # 직급/직책 매핑
                    position='STAFF',  # 기본값 (레거시 필드)
                    new_position=self.map_position(row.get('직책')),
                    growth_level=self.map_growth_level(row.get('성장레벨')),
                    
                    # 직군/직종 매핑
                    job_group=self.map_job_group(row.get('직군')),
                    job_type=self.map_job_type(row.get('직종')),
                    job_role=str(row.get('직무', '')) if pd.notna(row.get('직무')) else '',
                    
                    # 급호 (숫자 추출)
                    grade_level=self.extract_grade_level(row.get('급호')),
                    
                    # 입사일 매핑
                    hire_date=pd.to_datetime(row.get('현회사입사일', date.today())).date() if pd.notna(row.get('현회사입사일')) else date.today(),
                    
                    # 고용형태
                    employment_type=self.map_employment_type(row.get('직원구분\n(고용유형)')),
                    employment_status='재직',  # 기본값
                    
                    # 비상연락처 (더미)
                    emergency_contact=self.generate_korean_name(),
                    emergency_phone=self.generate_phone_number()
                )
                
                employee.save()
                success_count += 1
                
                if (index + 1) % 100 == 0:
                    print(f"  {index + 1}/{len(self.df)} 처리 완료...")
                    
            except Exception as e:
                error_count += 1
                errors.append(f"Row {index + 1}: {str(e)}")
                print(f"  오류 발생 (Row {index + 1}): {str(e)}")
        
        print(f"\n마이그레이션 완료:")
        print(f"- 성공: {success_count}건")
        print(f"- 실패: {error_count}건")
        
        if errors:
            print("\n오류 상세:")
            for error in errors[:10]:  # 처음 10개만 표시
                print(f"  {error}")
            if len(errors) > 10:
                print(f"  ... 외 {len(errors) - 10}건")
        
        return success_count, error_count
    
    def create_sample_admin(self):
        """샘플 관리자 계정 생성"""
        print("\n관리자 계정 확인/생성 중...")
        
        # 기존 superuser 확인
        if not User.objects.filter(is_superuser=True).exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@okfg.co.kr',
                password='admin123!@#'
            )
            print("- 관리자 계정 생성: admin / admin123!@#")
        else:
            print("- 기존 관리자 계정 유지")
    
    def print_summary(self):
        """마이그레이션 요약 정보 출력"""
        print("\n" + "="*80)
        print("마이그레이션 요약")
        print("="*80)
        
        # 부서별 인원
        dept_counts = Employee.objects.values('department').annotate(
            count=models.Count('id')
        ).order_by('department')
        
        print("\n부서별 인원:")
        for dept in dept_counts:
            print(f"  {dept['department']}: {dept['count']}명")
        
        # 직종별 인원
        job_type_counts = Employee.objects.values('job_type').annotate(
            count=models.Count('id')
        ).order_by('job_type')
        
        print("\n직종별 인원:")
        for jt in job_type_counts:
            print(f"  {jt['job_type']}: {jt['count']}명")
        
        # 성장레벨별 인원
        level_counts = Employee.objects.values('growth_level').annotate(
            count=models.Count('id')
        ).order_by('growth_level')
        
        print("\n성장레벨별 인원:")
        for lv in level_counts:
            print(f"  Level {lv['growth_level']}: {lv['count']}명")
        
        print("\n" + "="*80)
        print("생성된 계정 정보:")
        print(f"- 일반 직원: {len(self.created_users)}개 계정 (비밀번호: okfg2024!)")
        print(f"- 관리자: admin / admin123!@#")
        print("="*80)


def main():
    """메인 실행 함수"""
    excel_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK_dummy_employee_250801.xlsx"
    
    print("="*80)
    print("OK금융그룹 EHR 시스템 데이터 마이그레이션")
    print("="*80)
    
    # 마이그레이션 객체 생성
    migrator = ExcelToDBMigration(excel_path)
    
    # 1. Excel 로드
    migrator.load_excel()
    
    # 2. 기존 데이터 삭제
    print("\n기존 데이터를 삭제합니다...")
    migrator.delete_existing_data()
    
    # 3. 데이터 마이그레이션
    success, errors = migrator.migrate_data()
    
    # 4. 관리자 계정 생성
    migrator.create_sample_admin()
    
    # 5. 요약 정보 출력
    migrator.print_summary()
    
    print("\n마이그레이션 완료!")


if __name__ == "__main__":
    # models 모듈 import 추가
    from django.db import models
    main()