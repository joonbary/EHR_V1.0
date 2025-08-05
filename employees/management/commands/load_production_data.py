"""
Production 환경용 직원 데이터 로딩 명령어
실제 엑셀 파일 없이 1790명의 더미 데이터 생성
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from employees.models import Employee
from datetime import date, timedelta
import random
import string


class Command(BaseCommand):
    help = 'Production 환경용 1790명 직원 데이터 생성 (OK금융그룹 구조 반영)'

    def __init__(self):
        super().__init__()
        # 익명화용 데이터
        self.korean_last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임',
                                  '한', '오', '서', '신', '권', '황', '안', '송', '전', '홍']
        self.korean_first_names_male = ['민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호', '지후', '준우']
        self.korean_first_names_female = ['서연', '서윤', '지우', '서현', '민서', '하은', '하윤', '윤서', '지유', '지민']
        
        # 회사별 인원 분포 (실제 비율 반영)
        self.company_distribution = {
            'OK': 975,
            'OCI': 242,
            'OC': 225,
            'OFI': 149,
            'OKDS': 92,
            'OKH': 79,
            'ON': 16,
            'OKIP': 5,
            'OT': 5,
            'OKV': 1,
            'EX': 1
        }
        
        # 본부 리스트
        self.headquarters = ['경영관리', 'IT', '영업', '리스크', '마케팅', '고객지원', '재무', '인사', '감사', '전략기획']
        
        # 부서 리스트
        self.departments = ['기획팀', '운영팀', '개발팀', '지원팀', '관리팀', '영업1팀', '영업2팀', '전략팀']
        
        # 직급 분포
        self.positions = ['사원', '대리', '과장', '차장', '부장', '이사', '상무', '전무', '부사장']
        self.position_weights = [30, 25, 20, 10, 7, 4, 2, 1, 1]
        
        # 직종
        self.job_types = ['경영관리', 'IT개발', 'IT기획', 'IT운영', '기업영업', '기업금융', '리테일금융', '투자금융', '고객지원']
        
        # 학력
        self.educations = ['고졸', '전문대졸', '대졸', '석사', '박사']
        self.education_weights = [5, 10, 60, 20, 5]
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 데이터 삭제 후 로딩'
        )

    def generate_dummy_name(self, gender=None):
        """더미 이름 생성"""
        last = random.choice(self.korean_last_names)
        if gender == 'M' or (gender is None and random.choice([True, False])):
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
        
        if gender == 'M':
            gender_digit = random.choice([1, 3])
        elif gender == 'F':
            gender_digit = random.choice([2, 4])
        else:
            gender_digit = random.randint(1, 4)
            
        return f"{year}{month}{day}-{gender_digit}{''.join([str(random.randint(0, 9)) for _ in range(6)])}"

    def generate_dummy_phone(self):
        """더미 휴대폰 번호 생성"""
        return f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

    def generate_dummy_address(self):
        """더미 주소 생성"""
        districts = ['강남구', '서초구', '송파구', '강동구', '종로구', '중구', '용산구', '성동구', '광진구', '동대문구']
        district = random.choice(districts)
        return f"서울시 {district} {random.randint(1, 100)}길 {random.randint(1, 50)}"

    def generate_dummy_email(self, name, no):
        """더미 이메일 생성"""
        domains = ['okfg.co.kr', 'okcorp.kr', 'okgroup.com']
        return f"emp{no:04d}@{random.choice(domains)}"

    def generate_hire_date(self, age):
        """나이에 맞는 입사일 생성"""
        # 대졸 기준 23세 입사, 나이에 따라 입사일 계산
        years_since_graduation = max(0, age - 23)
        # 최근 20년 내 입사로 제한
        years_since_hire = min(years_since_graduation, random.randint(0, min(20, years_since_graduation)))
        hire_date = date.today() - timedelta(days=years_since_hire * 365 + random.randint(0, 364))
        return hire_date

    def handle(self, *args, **options):
        clear = options['clear']

        self.stdout.write('Production 데이터 생성 시작...')

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

        # 데이터 생성
        success_count = 0
        error_count = 0
        employee_no = 1

        for company, count in self.company_distribution.items():
            self.stdout.write(f'\n{company} 직원 {count}명 생성 중...')
            
            for i in range(count):
                try:
                    # 성별 결정
                    gender = random.choice(['M', 'F'])
                    
                    # 나이 결정 (25-60세)
                    age = random.choices(
                        range(25, 61),
                        weights=[1 if x < 30 else 2 if x < 40 else 3 if x < 50 else 2 for x in range(25, 61)]
                    )[0]
                    
                    # 생년월일 계산
                    birth_year = date.today().year - age
                    birth_date = date(birth_year, random.randint(1, 12), random.randint(1, 28))
                    
                    # 더미 데이터 생성
                    dummy_name = self.generate_dummy_name(gender)
                    dummy_ssn = self.generate_dummy_ssn(birth_date, gender)
                    dummy_phone = self.generate_dummy_phone()
                    dummy_email = self.generate_dummy_email(dummy_name, employee_no)
                    dummy_address = self.generate_dummy_address()
                    
                    # 직급 결정 (나이 고려)
                    if age < 30:
                        position = random.choices(self.positions[:3], weights=[50, 35, 15])[0]
                    elif age < 40:
                        position = random.choices(self.positions[:5], weights=[20, 30, 30, 15, 5])[0]
                    elif age < 50:
                        position = random.choices(self.positions[2:7], weights=[20, 25, 25, 20, 10])[0]
                    else:
                        position = random.choices(self.positions[3:], weights=[15, 25, 25, 20, 10, 5])[0]
                    
                    # 본부 및 부서 결정
                    headquarters1 = random.choice(self.headquarters)
                    department1 = random.choice(self.departments)
                    
                    # 입사일 생성
                    hire_date = self.generate_hire_date(age)
                    
                    # User 생성
                    username = f"emp{employee_no:04d}"
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

                    # Employee 생성
                    employee_data = {
                        # User 연결
                        'user': user,
                        
                        # 기본 필수 필드
                        'name': dummy_name,
                        'email': dummy_email,
                        'phone': dummy_phone,
                        'department': department1[:20],
                        'position': 'STAFF',  # 기존 시스템 호환성
                        
                        # 익명화 필드들
                        'dummy_ssn': dummy_ssn,
                        'dummy_chinese_name': f"{dummy_name}(漢)",
                        'dummy_name': dummy_name,
                        'dummy_mobile': dummy_phone,
                        'dummy_registered_address': dummy_address,
                        'dummy_residence_address': dummy_address,
                        'dummy_email': dummy_email,
                        
                        # 실제 데이터 필드들
                        'no': employee_no,
                        'company': company,
                        'current_position': position,
                        'headquarters1': headquarters1,
                        'headquarters2': headquarters1,  # 동일하게 설정
                        'department1': department1,
                        'department2': f"{department1} {random.randint(1, 3)}파트",
                        'department3': f"{department1} {random.choice(['A', 'B', 'C'])}팀",
                        'final_department': f"{headquarters1} {department1}",
                        'job_series': random.choice(['일반직', '전문직', '특정직']),
                        'title': position,
                        'responsibility': position if random.random() > 0.7 else None,
                        'promotion_level': str(random.randint(1, 5)),
                        'salary_grade': str(random.randint(1, 10)),
                        'gender': gender,
                        'age': age,
                        'birth_date': birth_date,
                        'hire_date': hire_date,
                        'group_join_date': hire_date,
                        'career_join_date': hire_date if random.random() > 0.5 else None,
                        'new_join_date': hire_date if random.random() > 0.7 else None,
                        'promotion_accumulated_years': min((date.today() - hire_date).days / 365, 20),
                        'recruitment_type': random.choice(['신입', '경력']),
                        'education': random.choices(self.educations, weights=self.education_weights)[0],
                        'marital_status': random.choice(['Y', 'N']) if age > 30 else 'N',
                        'final_evaluation': random.choice(['S', 'A', 'B', 'C']),
                        'job_tag_name': random.choice(self.job_types),
                        'job_family': random.choice(['PL', 'Non-PL']),
                        'job_field': random.choice(['프론트', '백오피스']),
                        'classification': '정규직',
                        'current_headcount': '1',
                        'employment_type': '정규직',
                        'employment_status': '재직',
                    }
                    
                    # Employee 생성 또는 업데이트
                    employee, created = Employee.objects.update_or_create(
                        no=employee_no,
                        defaults=employee_data
                    )
                    
                    success_count += 1
                    employee_no += 1
                    
                    if success_count % 100 == 0:
                        self.stdout.write(f'진행 중: {success_count}/1790')
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'직원 {employee_no} 생성 중 오류: {str(e)[:100]}')
                    )
                    employee_no += 1

        # 결과 출력
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'데이터 생성 완료!'))
        self.stdout.write(f'성공: {success_count}개')
        self.stdout.write(f'오류: {error_count}개')

        # 통계 출력
        self.stdout.write('\n=== 회사별 직원 수 ===')
        from django.db.models import Count
        company_stats = Employee.objects.values('company').annotate(count=Count('id')).order_by('-count')
        for stat in company_stats:
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