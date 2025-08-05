"""
가장 간단한 데이터 로딩 - 필수 필드만 사용
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Employee
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = '가장 간단한 1790명 직원 데이터 생성'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1790, help='생성할 직원 수')

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(f'{count}명 직원 데이터 생성 시작...')
        
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
        
        korean_names = ['김민준', '이서연', '박도윤', '최서윤', '정시우', '강지우', '조하준', '윤서현', '장지호', '임민서']
        departments = ['IT', 'HR', 'FINANCE', 'MARKETING', 'SALES', 'OPERATIONS']

        for i in range(1, count + 1):
            try:
                username = f"emp{i:04d}"
                email = f"{username}@okfg.co.kr"
                
                # User 생성 또는 가져오기
                user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': '직원',
                        'last_name': str(i)
                    }
                )
                
                if user_created:
                    user.set_password('okfg2024!')
                    user.save()
                
                # Employee 생성 또는 업데이트 - 최소 필드만
                employee, emp_created = Employee.objects.get_or_create(
                    user=user,
                    defaults={
                        'name': random.choice(korean_names),
                        'email': email,
                        'phone': f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                        'department': random.choice(departments),
                        'position': 'STAFF',
                        'hire_date': date.today() - timedelta(days=random.randint(30, 3650))
                    }
                )
                
                # employment_status와 employment_type이 있으면 업데이트
                try:
                    if hasattr(employee, 'employment_status'):
                        employee.employment_status = '재직'
                    if hasattr(employee, 'employment_type'):
                        employee.employment_type = '정규직'
                    employee.save()
                except:
                    pass
                
                success_count += 1
                
                if success_count % 100 == 0:
                    self.stdout.write(f'진행: {success_count}/{count}')
                    
            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    self.stdout.write(f'오류 {i}: {str(e)[:50]}')

        # 결과 출력
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'완료!')
        self.stdout.write(f'  성공: {success_count}명')
        self.stdout.write(f'  오류: {error_count}명')
        self.stdout.write(f'  전체 직원: {Employee.objects.count()}명')
        self.stdout.write(f'  전체 사용자: {User.objects.count()}명')
        
        self.stdout.write('\n로그인 정보:')
        self.stdout.write(f'  관리자: admin / admin123!@#')
        self.stdout.write(f'  직원: emp0001 ~ emp{count:04d} / okfg2024!')