import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
from datetime import date

# admin 사용자에게 Employee 생성
admin_user = User.objects.filter(username='admin').first()
if admin_user and not hasattr(admin_user, 'employee'):
    employee = Employee.objects.create(
        user=admin_user,
        name='관리자',
        department='HR',
        position='EXECUTIVE',
        hire_date=date(2020, 1, 1),
        email='admin@okfn.com',
        phone='010-0000-0000',
        growth_level=3,
        manager=None,
        employment_status='재직'
    )
    print(f"Created employee for admin: {employee}")
else:
    print("Admin user not found or already has employee")