from django.core.management.base import BaseCommand
from django.core.management import call_command
from employees.models import Employee
import os

class Command(BaseCommand):
    help = 'Initialize database with employee data'

    def handle(self, *args, **options):
        self.stdout.write('Checking current employee count...')
        count = Employee.objects.count()
        
        if count == 0:
            self.stdout.write('Database is empty. Loading initial data...')
            if os.path.exists('employees_only.json'):
                try:
                    call_command('loaddata', 'employees_only.json', verbosity=2)
                    new_count = Employee.objects.count()
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully loaded {new_count} employees')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to load data: {e}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING('employees_only.json not found')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Database already has {count} employees')
            )