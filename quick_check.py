#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()
from employees.models import Employee

total = Employee.objects.count()
good = Employee.objects.exclude(name='').exclude(name__isnull=True).count()
bad = Employee.objects.filter(name='').count()

print(f'Total employees: {total}')
print(f'Good employees (with name): {good}')
print(f'Bad employees (no name): {bad}')