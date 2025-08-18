"""
실제 OK금융그룹 엑셀 데이터 로딩 명령어
dummy_ 접두사 필드는 익명화, 나머지는 원본 데이터 사용
"""

import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from employees.models import Employee
from datetime import datetime, date
import random
import string
import sys


class Command(BaseCommand):
    help = 'OK금융그룹 엑셀 파일에서 직원 데이터를 로딩합니다 (dummy_ 필드 익명화)'

    def __init__(self):
        super().__init__()
        # 익명화용 데이터
        self.korean_last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임',
                                  '한', '오', '서', '신', '권', '황', '안', '송', '전', '홍']
        self.korean_first_names_male = ['민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호', '지후', '준우']
        self.korean_first_names_female = ['서연', '서윤', '지우', '서현', '민서', '하은', '하윤', '윤서', '지유', '지민']
        self.districts = ['강남구', '서초구', '송파구', '강동구', '종로구', '중구', '용산구', '성동구', '광진구', '동대문구']
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--excel-path',
            type=str,
            default=r'C:\Users\apro\OneDrive\Desktop\인사자료\OK_dummy_employee_250801.xlsx',
            help='엑셀 파일 경로'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 데이터 삭제 후 로딩'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='배치 크기 (기본: 100)'
        )

    def generate_dummy_name(self, gender=None):
        """더미 이름 생성"""
        last = random.choice(self.korean_last_names)
        if gender == '남' or (gender is None and random.choice([True, False])):
            first = random.choice(self.korean_first_names_male)
        else:
            first = random.choice(self.korean_first_names_female)
        return f"{last}{first}"

    def generate_dummy_ssn(self, birth_date=None, gender=None):
        """더미 주민번호 생성"""
        if birth_date:
            year = str(birth_date.year)[2:]
            month = f"{birth_date.month:02d}"
            day = f"{birth_date.day:02d}"
        else:
            year = random.randint(60, 99)
            month = f"{random.randint(1, 12):02d}"
            day = f"{random.randint(1, 28):02d}"
        
        if gender == '남':
            gender_digit = random.choice([1, 3])
        elif gender == '여':
            gender_digit = random.choice([2, 4])
        else:
            gender_digit = random.randint(1, 4)
            
        return f"{year}{month}{day}-{gender_digit}{''.join([str(random.randint(0, 9)) for _ in range(6)])}"

    def generate_dummy_phone(self):
        """더미 휴대폰 번호 생성"""
        return f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

    def generate_dummy_address(self):
        """더미 주소 생성"""
        district = random.choice(self.districts)
        return f"서울시 {district} {random.randint(1, 100)}길 {random.randint(1, 50)}"

    def generate_dummy_email(self, name, no):
        """더미 이메일 생성"""
        domains = ['okfg.co.kr', 'okcorp.kr', 'okgroup.com']
        return f"emp{no:04d}@{random.choice(domains)}"

    def safe_convert(self, value, converter=str, default=None):
        """안전한 데이터 변환"""
        if pd.isna(value) or value == '' or value is None:
            return default
        try:
            if converter == str:
                return str(value).strip()
            elif converter == int:
                return int(float(value))
            elif converter == float:
                return float(value)
            elif converter == date:
                if isinstance(value, (datetime, date)):
                    return value.date() if isinstance(value, datetime) else value
                return pd.to_datetime(value).date()
        except:
            return default

    def handle(self, *args, **options):
        excel_path = options['excel_path']
        clear = options['clear']
        batch_size = options['batch_size']

        self.stdout.write(f'엑셀 파일 로딩 중: {excel_path}')

        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(excel_path)
            total_count = len(df)
            
            self.stdout.write(f'총 {total_count}개 레코드 발견')
            self.stdout.write(f'컬럼 수: {len(df.columns)}개')

            # 기존 데이터 삭제
            if clear:
                self.stdout.write('기존 데이터 삭제 중...')
                Employee.objects.all().delete()
                User.objects.filter(is_superuser=False).delete()

            # Admin 계정 생성
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@okfg.co.kr',
                    password='admin123!@#'
                )
                self.stdout.write(self.style.SUCCESS('Admin 계정 생성 완료'))

            # 데이터 처리
            success_count = 0
            error_count = 0
            employees_to_create = []

            for index, row in df.iterrows():
                try:
                    # NO 필드 추출
                    no = self.safe_convert(row.get('NO'), int, index + 1)
                    
                    # 성별 정보 추출 (실제 데이터)
                    gender = self.safe_convert(row.get('성별'), str)
                    
                    # 생일 정보 추출 (실제 데이터)
                    birth_date = self.safe_convert(row.get('생일'), date)
                    
                    # dummy_ 필드는 생성, 나머지는 실제 데이터 사용
                    dummy_name = self.generate_dummy_name(gender)
                    dummy_ssn = self.generate_dummy_ssn(birth_date, gender)
                    dummy_phone = self.generate_dummy_phone()
                    dummy_email = self.generate_dummy_email(dummy_name, no)
                    dummy_address = self.generate_dummy_address()
                    
                    # User 생성
                    username = f"emp{no:04d}"
                    if not User.objects.filter(username=username).exists():
                        user = User.objects.create_user(
                            username=username,
                            email=dummy_email,
                            password='okfg2024!',
                            first_name=dummy_name[1:],
                            last_name=dummy_name[0]
                        )
                    else:
                        user = User.objects.get(username=username)

                    # Employee 데이터 준비
                    employee_data = {
                        # User 연결
                        'user': user,
                        
                        # 기본 필수 필드 (기존 시스템 호환성)
                        'name': dummy_name,
                        'email': dummy_email,
                        'phone': dummy_phone,
                        'department': self.safe_convert(row.get('최종소속'), str, 'OPERATIONS')[:20],
                        'position': 'STAFF',  # 기존 시스템 호환성
                        
                        # 익명화 필드들 (생성된 더미 데이터)
                        'dummy_ssn': dummy_ssn,
                        'dummy_chinese_name': f"{dummy_name}(漢)",
                        'dummy_name': dummy_name,
                        'dummy_mobile': dummy_phone,
                        'dummy_registered_address': dummy_address,
                        'dummy_residence_address': dummy_address,
                        'dummy_email': dummy_email,
                        
                        # 실제 데이터 필드들
                        'no': no,
                        'company': self.safe_convert(row.get('회사'), str, 'OK'),
                        'previous_position': self.safe_convert(row.get('직급(전)'), str),
                        'current_position': self.safe_convert(row.get('직급'), str),
                        'headquarters1': self.safe_convert(row.get('본부1'), str),
                        'headquarters2': self.safe_convert(row.get('본부2'), str),
                        'department1': self.safe_convert(row.get('소속1(부문)'), str),
                        'department2': self.safe_convert(row.get('소속2(부)'), str),
                        'department3': self.safe_convert(row.get('소속3(팀/실/점/센터)'), str),
                        'department4': self.safe_convert(row.get('소속4(PL/파트명)'), str),
                        'final_department': self.safe_convert(row.get('최종소속'), str),
                        'job_series': self.safe_convert(row.get('직군/계열'), str),
                        'title': self.safe_convert(row.get('호칭'), str),
                        'responsibility': self.safe_convert(row.get('직책'), str),
                        'promotion_level': self.safe_convert(row.get('승급레벨'), str),
                        'salary_grade': self.safe_convert(row.get('급호'), str),
                        'gender': gender,
                        'age': self.safe_convert(row.get('나이'), int),
                        'birth_date': birth_date,
                        'hire_date': self.safe_convert(row.get('입사일(20-10-01)'), date, date.today()),
                        'group_join_date': self.safe_convert(row.get('그룹입사일'), date),
                        'career_join_date': self.safe_convert(row.get('경력입사일'), date),
                        'new_join_date': self.safe_convert(row.get('신입입사일'), date),
                        'promotion_accumulated_years': self.safe_convert(row.get('승급누적년수'), float),
                        'recruitment_type': self.safe_convert(row.get('채용구분'), str),
                        'education': self.safe_convert(row.get('학력'), str),
                        'marital_status': self.safe_convert(row.get('결혼여부'), str),
                        'final_evaluation': self.safe_convert(row.get('최종평가(종합평가)'), str),
                        'job_tag_name': self.safe_convert(row.get('직무태그명'), str),
                        'rank_tag_name': self.safe_convert(row.get('순위태그명'), str),
                        'job_family': self.safe_convert(row.get('직무군'), str),
                        'job_field': self.safe_convert(row.get('직무분야'), str),
                        'classification': self.safe_convert(row.get('분류(정규/계)'), str),
                        'current_headcount': self.safe_convert(row.get('현원'), str),
                        'detailed_classification': self.safe_convert(row.get('세부분류'), str),
                        'category': self.safe_convert(row.get('구분'), str),
                        'diversity_years': self.safe_convert(row.get('다양성년수'), float),
                        
                        # 기존 시스템 필드들 (기본값)
                        'employment_type': self.safe_convert(row.get('입사구분'), str, '정규직'),
                        'employment_status': '재직',
                    }
                    
                    # Employee 생성 또는 업데이트
                    employee, created = Employee.objects.update_or_create(
                        no=no,
                        defaults=employee_data
                    )
                    
                    success_count += 1
                    
                    if success_count % 10 == 0:
                        self.stdout.write(f'진행 중: {success_count}/{total_count}')
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'행 {index + 2} 처리 중 오류: {str(e)[:100]}')
                    )
                    if error_count > 10:
                        self.stdout.write(self.style.ERROR('오류가 너무 많아 중단합니다.'))
                        break

            # 결과 출력
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS(f'데이터 로딩 완료!'))
            self.stdout.write(f'성공: {success_count}개')
            self.stdout.write(f'오류: {error_count}개')
            self.stdout.write(f'성공률: {(success_count/total_count*100):.1f}%')

            # 통계 출력
            self.stdout.write('\n=== 회사별 직원 수 ===')
            from django.db.models import Count
            company_stats = Employee.objects.values('company').annotate(count=Count('id')).order_by('-count')
            for stat in company_stats[:10]:
                self.stdout.write(f"  {stat['company'] or '미지정'}: {stat['count']}명")

            self.stdout.write('\n=== 본부별 직원 수 (상위 10개) ===')
            dept_stats = Employee.objects.values('headquarters1').annotate(count=Count('id')).order_by('-count')
            for stat in dept_stats[:10]:
                self.stdout.write(f"  {stat['headquarters1'] or '미지정'}: {stat['count']}명")

            self.stdout.write(f'\n전체 직원 수: {Employee.objects.count()}명')
            self.stdout.write(f'전체 사용자 수: {User.objects.count()}명')
            
            self.stdout.write('\n=== 로그인 정보 ===')
            self.stdout.write('관리자: admin / admin123!@#')
            self.stdout.write('직원: emp0001 ~ emp1790 / okfg2024!')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'파일 처리 중 오류 발생: {str(e)}')
            )
            import traceback
            traceback.print_exc()
            sys.exit(1)