"""
Production DB에 누락된 dummy 컬럼 추가
"""

from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Production DB에 누락된 dummy 컬럼 추가'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # 누락된 컬럼들 추가
            columns_to_add = [
                ('dummy_ssn', 'VARCHAR(20)'),
                ('dummy_name', 'VARCHAR(100)'),
                ('dummy_chinese_name', 'VARCHAR(100)'),
                ('dummy_phone', 'VARCHAR(20)'),
                ('dummy_address', 'TEXT'),
                ('dummy_actual_address', 'TEXT'),
                ('dummy_email', 'VARCHAR(255)')
            ]
            
            for column_name, column_type in columns_to_add:
                try:
                    cursor.execute(f"""
                        ALTER TABLE employees_employee 
                        ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                    """)
                    self.stdout.write(self.style.SUCCESS(f'[OK] {column_name} column added'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'[ERROR] {column_name}: {str(e)[:50]}'))
            
            # 컬럼 확인
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'employees_employee'
                AND column_name LIKE 'dummy%'
            """)
            
            dummy_columns = cursor.fetchall()
            if dummy_columns:
                self.stdout.write('\nCurrent dummy columns:')
                for col in dummy_columns:
                    self.stdout.write(f'  - {col[0]}')
            else:
                self.stdout.write('\nNo dummy columns found.')