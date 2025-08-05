"""
Safe Data Loading Command - Railway Production
에러 처리가 강화된 안전한 데이터 로딩 명령어
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction, connection
from employees.models import Employee
from datetime import date, datetime
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Safely load employee data (handles existing data gracefully)'
    
    def __init__(self):
        super().__init__()
        self.korean_last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
        self.korean_first_names = ['민준', '서준', '도윤', '예준', '시우', '서연', '서윤', '지우', '서현', '민서']
        self.departments = ['IT', 'HR', 'FINANCE', 'MARKETING', 'SALES', 'OPERATIONS']
        
    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1790, help='Number of employees')
        
    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Starting safe data load for {count} employees...')
        
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('✓ Database connection OK'))
        
        # Safely clear existing data
        try:
            self.stdout.write('Clearing existing employee data...')
            # Use raw SQL to avoid foreign key issues
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM employees_employee WHERE id > 0")
                deleted = cursor.rowcount
                self.stdout.write(f'  Deleted {deleted} employees')
                
                cursor.execute("DELETE FROM auth_user WHERE is_superuser = false")
                deleted = cursor.rowcount
                self.stdout.write(f'  Deleted {deleted} user accounts')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not clear data: {e}'))
            self.stdout.write('Continuing with data creation...')
        
        # Create admin
        try:
            admin, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@okfg.co.kr',
                    'is_superuser': True,
                    'is_staff': True,
                    'last_login': timezone.now()
                }
            )
            if created:
                admin.set_password('admin123!@#')
                admin.save()
                self.stdout.write(self.style.SUCCESS('✓ Admin user created'))
            else:
                self.stdout.write('✓ Admin user already exists')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Admin creation warning: {e}'))
        
        # Create employees in smaller batches
        batch_size = 50
        success = 0
        errors = 0
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            
            try:
                with transaction.atomic():
                    for i in range(batch_start, batch_end):
                        try:
                            # Generate data
                            name = random.choice(self.korean_last_names) + random.choice(self.korean_first_names)
                            emp_id = f"emp{i+1:04d}"
                            email = f"{emp_id}@okfg.co.kr"
                            
                            # Create user
                            user, created = User.objects.get_or_create(
                                username=emp_id,
                                defaults={
                                    'email': email,
                                    'first_name': name[1:],
                                    'last_name': name[0],
                                    'last_login': timezone.now()
                                }
                            )
                            
                            if created:
                                user.set_password('okfg2024!')
                                user.save()
                            
                            # Create or update employee
                            employee, created = Employee.objects.update_or_create(
                                user=user,
                                defaults={
                                    'name': name,
                                    'email': email,
                                    'phone': f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                                    'department': random.choice(self.departments),
                                    'position': 'STAFF',
                                    'hire_date': date.today(),
                                    'address': f"서울시 강남구 {random.randint(1,100)}번지"
                                }
                            )
                            
                            success += 1
                            
                        except Exception as e:
                            errors += 1
                            if errors <= 3:
                                self.stdout.write(f'    Error {i+1}: {str(e)[:50]}')
                
                self.stdout.write(f'  Batch {batch_start//batch_size + 1}: {success} created')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Batch error: {str(e)[:100]}'))
                continue
        
        # Final summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Data load complete!'))
        self.stdout.write(f'Successfully created: {success} employees')
        self.stdout.write(f'Errors: {errors}')
        self.stdout.write(f'Total employees in DB: {Employee.objects.count()}')
        self.stdout.write('\n로그인 정보:')
        self.stdout.write('  관리자: admin / admin123!@#')
        self.stdout.write(f'  직원: emp0001 ~ emp{count:04d} / okfg2024!')