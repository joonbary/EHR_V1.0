"""
간단한 Production 데이터 로딩 명령어
필드 문제 없이 바로 실행 가능
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from employees.models import Employee
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = '간단한 1790명 직원 데이터 생성'

    def __init__(self):
        super().__init__()
        self.korean_last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
        self.korean_first_names_male = ['민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호']
        self.korean_first_names_female = ['서연', '서윤', '지우', '서현', '민서', '하은', '하윤', '윤서']
        
        # 회사별 인원 분포
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
        
        self.headquarters = ['경영관리', 'IT', '영업', '리스크', '마케팅', '고객지원', '재무', '인사']
        self.departments = ['기획팀', '운영팀', '개발팀', '지원팀', '관리팀', '영업1팀', '영업2팀']
        self.positions = ['사원', '대리', '과장', '차장', '부장']

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='기존 데이터 삭제')

    def handle(self, *args, **options):
        clear = options['clear']
        
        self.stdout.write('데이터 생성 시작...')
        
        if clear:
            self.stdout.write('기존 데이터 삭제 중...')
            try:
                # Employee 삭제 시도 (관련 테이블 문제 무시)
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM employees_employee WHERE 1=1")
                self.stdout.write('Employee 데이터 삭제 완료')
            except Exception as e:
                self.stdout.write(f'Employee 삭제 중 오류 (무시): {str(e)[:100]}')
            
            # User 삭제
            try:
                User.objects.filter(is_superuser=False).delete()
                self.stdout.write('User 데이터 삭제 완료')
            except Exception as e:
                self.stdout.write(f'User 삭제 중 오류 (무시): {str(e)[:100]}')

        # Admin 확인
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@okfg.co.kr', 
                password='admin123!@#'
            )
            self.stdout.write('Admin 계정 생성 완료')

        success_count = 0
        error_count = 0
        employee_no = 1

        for company, count in self.company_distribution.items():
            self.stdout.write(f'{company}: {count}명 생성 중...')
            
            for i in range(count):
                try:
                    # 기본 정보 생성
                    gender = random.choice(['M', 'F'])
                    age = random.randint(25, 60)
                    
                    if gender == 'M':
                        last = random.choice(self.korean_last_names)
                        first = random.choice(self.korean_first_names_male)
                    else:
                        last = random.choice(self.korean_last_names)
                        first = random.choice(self.korean_first_names_female)
                    
                    name = f"{last}{first}"
                    email = f"emp{employee_no:04d}@okfg.co.kr"
                    username = f"emp{employee_no:04d}"
                    
                    # User 생성
                    if not User.objects.filter(username=username).exists():
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password='okfg2024!',
                            first_name=first,
                            last_name=last
                        )
                    else:
                        user = User.objects.get(username=username)

                    # Employee 생성 (필수 필드만)
                    defaults_dict = {
                        'name': name,
                        'email': email,
                        'phone': f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                        'department': random.choice(['IT', 'HR', 'FINANCE', 'MARKETING', 'SALES', 'OPERATIONS']),
                        'position': 'STAFF',
                        'hire_date': date.today() - timedelta(days=random.randint(30, 3650)),
                        'employment_status': '재직',
                        'employment_type': '정규직',
                    }
                    
                    # 옵션 필드 체크 후 추가
                    try:
                        # company 필드가 있으면 추가
                        Employee._meta.get_field('company')
                        defaults_dict['company'] = company
                    except:
                        pass
                    
                    try:
                        # age 필드가 있으면 추가
                        Employee._meta.get_field('age')
                        defaults_dict['age'] = age
                    except:
                        pass
                    
                    try:
                        # gender 필드가 있으면 추가  
                        Employee._meta.get_field('gender')
                        defaults_dict['gender'] = gender
                    except:
                        pass
                    
                    try:
                        # headquarters1 필드가 있으면 추가
                        Employee._meta.get_field('headquarters1')
                        defaults_dict['headquarters1'] = random.choice(self.headquarters)
                    except:
                        pass
                    
                    try:
                        # current_position 필드가 있으면 추가
                        Employee._meta.get_field('current_position')
                        defaults_dict['current_position'] = random.choice(self.positions)
                    except:
                        pass
                    
                    employee, created = Employee.objects.update_or_create(
                        user=user,
                        defaults=defaults_dict
                    )
                    
                    success_count += 1
                    employee_no += 1
                    
                    if success_count % 100 == 0:
                        self.stdout.write(f'진행: {success_count}/1790')
                        
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:
                        self.stdout.write(f'오류: {str(e)[:100]}')
                    employee_no += 1
                    continue

        # 결과 출력
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'완료! 성공: {success_count}, 오류: {error_count}')
        self.stdout.write(f'전체 직원 수: {Employee.objects.count()}')
        self.stdout.write(f'전체 사용자 수: {User.objects.count()}')
        
        # 회사별 통계
        if hasattr(Employee, 'company'):
            from django.db.models import Count
            stats = Employee.objects.values('company').annotate(count=Count('id')).order_by('-count')
            self.stdout.write('\n회사별 직원 수:')
            for stat in stats[:10]:
                self.stdout.write(f"  {stat['company']}: {stat['count']}명")
        
        self.stdout.write('\n로그인 정보:')
        self.stdout.write('  관리자: admin / admin123!@#')
        self.stdout.write('  직원: emp0001 ~ emp1790 / okfg2024!')