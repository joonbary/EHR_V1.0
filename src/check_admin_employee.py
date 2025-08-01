import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

# admin 사용자 확인
admin_user = User.objects.filter(username='admin').first()
if admin_user:
    print(f"Admin user found: {admin_user.username}")
    
    # employee 관계 확인
    if hasattr(admin_user, 'employee'):
        print(f"Admin has employee: {admin_user.employee}")
    else:
        print("Admin does NOT have an employee record!")
        
        # 다른 사용자들 확인
        print("\nUsers with employee records:")
        for user in User.objects.all():
            if hasattr(user, 'employee'):
                print(f"  - {user.username} -> {user.employee.name} ({user.employee.department})")
else:
    print("Admin user not found!")