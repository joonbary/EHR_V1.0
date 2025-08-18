"""
Django Management Command for Loading Initial Employee Data
This creates 50 sample employees for testing
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from employees.models import Employee
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Load initial employee data (50 sample employees)'
    
    def __init__(self):
        super().__init__()
        self.departments = ['IT', 'HR', 'FINANCE', 'MARKETING', 'SALES', 'OPERATIONS']
        self.positions = ['STAFF', 'SENIOR', 'MANAGER', 'DIRECTOR']
        self.korean_last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
        self.korean_first_names = ['민준', '서준', '도윤', '예준', '시우', '서연', '서윤', '지우', '서현', '민서']
    
    def generate_name(self):
        """Generate Korean name"""
        last = random.choice(self.korean_last_names)
        first = random.choice(self.korean_first_names)
        return f"{last}{first}"
    
    def handle(self, *args, **options):
        self.stdout.write('Starting initial data load...')
        
        # Create admin if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@okfg.co.kr',
                password='admin123!@#'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Delete existing non-admin users
        User.objects.filter(is_superuser=False).delete()
        Employee.objects.all().delete()
        
        # Create 50 sample employees
        with transaction.atomic():
            for i in range(1, 51):
                name = self.generate_name()
                email = f"emp{i:03d}@okfg.co.kr"
                username = f"emp{i:03d}"
                
                # Create user
                user = User.objects.create_user(
                    username=username,
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
                    position=random.choice(self.positions),
                    hire_date=date.today() - timedelta(days=random.randint(30, 1825)),
                    address=f"서울시 강남구 테헤란로 {random.randint(1,500)}",
                    job_type=random.choice(['IT개발', 'IT기획', '경영관리', '기업영업']),
                    growth_level=random.randint(1, 4),
                    new_position=random.choice(['사원', '대리', '과장', '차장', '부장']),
                    employment_type='정규직',
                    employment_status='재직'
                )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created 50 employees'))
            self.stdout.write('Login credentials:')
            self.stdout.write('  Admin: admin / admin123!@#')
            self.stdout.write('  Employees: emp001-emp050 / okfg2024!')