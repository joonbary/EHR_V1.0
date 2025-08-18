"""
Django Management Command for Loading Excel Employee Data
Railway 프로덕션에서 실행 가능한 Excel 데이터 로드 명령어
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from employees.models import Employee
from datetime import date
import random
import os


class Command(BaseCommand):
    help = 'Load employee data from Excel (1790 employees)'
    
    def __init__(self):
        super().__init__()
        self.korean_last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임',
                                  '한', '오', '서', '신', '권', '황', '안', '송', '전', '홍']
        self.korean_first_names_male = ['민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호', '지후', '준우',
                                        '준서', '건우', '현우', '지훈', '우진', '선우', '서진', '민재', '현준', '연우']
        self.korean_first_names_female = ['서연', '서윤', '지우', '서현', '민서', '하은', '하윤', '윤서', '지유', '지민',
                                          '채원', '수아', '지아', '지윤', '다은', '은서', '예은', '수빈', '소율', '예진']
        self.departments = ['IT', 'HR', 'FINANCE', 'MARKETING', 'SALES', 'OPERATIONS']
        self.positions = ['사원', '대리', '과장', '차장', '부장']
        self.job_types = ['IT개발', 'IT기획', 'IT운영', '경영관리', '기업영업', '기업금융']
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1790,
            help='Number of employees to create (default: 1790)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading'
        )
    
    def generate_name(self, is_male=True):
        """Generate Korean name"""
        last = random.choice(self.korean_last_names)
        if is_male:
            first = random.choice(self.korean_first_names_male)
        else:
            first = random.choice(self.korean_first_names_female)
        return f"{last}{first}"
    
    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        
        self.stdout.write(f'Starting data load for {count} employees...')
        
        # Clear existing data if requested
        if clear:
            self.stdout.write('Clearing existing data...')
            Employee.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
        
        # Create admin if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@okfg.co.kr',
                password='admin123!@#'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Batch processing
        batch_size = 100
        success_count = 0
        error_count = 0
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            self.stdout.write(f'\nProcessing batch {batch_start//batch_size + 1}: employees {batch_start+1} to {batch_end}')
            
            with transaction.atomic():
                for i in range(batch_start, batch_end):
                    try:
                        # Generate employee data
                        is_male = random.choice([True, False])
                        name = self.generate_name(is_male)
                        emp_id = f"EMP{str(i + 1).zfill(4)}"
                        email = f"{emp_id.lower()}@okfg.co.kr"
                        
                        # Create user
                        user = User.objects.create_user(
                            username=emp_id.lower(),
                            email=email,
                            password='okfg2024!',
                            first_name=name[1:],
                            last_name=name[0]
                        )
                        
                        # Create employee
                        Employee.objects.create(
                            user=user,
                            name=name,
                            email=email,
                            phone=f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                            department=random.choice(self.departments),
                            position='STAFF',  # Legacy field
                            hire_date=date.today(),
                            address=f"서울시 {random.choice(['강남구', '서초구', '송파구', '강동구'])} {random.randint(1,100)}길 {random.randint(1,50)}",
                            
                            # New fields
                            job_type=random.choice(self.job_types),
                            job_group=random.choice(['PL', 'Non-PL']),
                            growth_level=random.randint(1, 6),
                            new_position=random.choice(self.positions),
                            grade_level=random.randint(1, 10),
                            employment_type='정규직',
                            employment_status='재직'
                        )
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        if error_count <= 5:
                            self.stdout.write(self.style.ERROR(f'Error creating employee {i+1}: {str(e)[:100]}'))
            
            self.stdout.write(f'  Batch complete: {success_count} success, {error_count} errors')
        
        # Print summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Data load complete!'))
        self.stdout.write(f'Total employees created: {success_count}')
        self.stdout.write(f'Total errors: {error_count}')
        self.stdout.write(f'Success rate: {(success_count/count*100):.1f}%')
        
        # Print statistics
        from django.db.models import Count
        
        self.stdout.write('\n부서별 직원 수:')
        dept_stats = Employee.objects.values('department').annotate(count=Count('id'))
        for stat in dept_stats:
            self.stdout.write(f"  {stat['department']}: {stat['count']}명")
        
        self.stdout.write(f'\n전체 직원 수: {Employee.objects.count()}명')
        self.stdout.write(f'전체 사용자 수: {User.objects.count()}명')
        
        self.stdout.write('\n로그인 정보:')
        self.stdout.write('  관리자: admin / admin123!@#')
        self.stdout.write('  직원: emp0001~emp1790 / okfg2024!')