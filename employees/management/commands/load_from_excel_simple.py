"""
간단한 Excel 로드 명령어 - dummy_ssn 없이
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Employee
import pandas as pd
import sys

class Command(BaseCommand):
    help = 'Excel 파일에서 직원 데이터 로드 (간단 버전)'

    def add_arguments(self, parser):
        parser.add_argument('--excel', type=str, required=True, help='Excel 파일 경로')
        parser.add_argument('--clear', action='store_true', help='기존 데이터 삭제')

    def handle(self, *args, **options):
        excel_path = options['excel']
        
        if options['clear']:
            self.stdout.write('기존 데이터 삭제 중...')
            Employee.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
        
        # Excel 파일 읽기
        self.stdout.write(f'Excel 파일 로드 중: {excel_path}')
        try:
            df = pd.read_excel(excel_path)
            total = len(df)
            self.stdout.write(f'총 {total}개 레코드 발견')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'파일 읽기 실패: {e}'))
            sys.exit(1)
        
        success = 0
        errors = 0
        
        for idx, row in df.iterrows():
            try:
                # User 생성
                username = f"u{idx+10000}"  # 고유한 username
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': row.get('이메일', f'{username}@okfg.co.kr'),
                        'first_name': row.get('이름', '직원'),
                        'last_name': str(idx+1)
                    }
                )
                
                if created:
                    user.set_password('okfg2024!')
                    user.save()
                
                # Employee 생성 - 필수 필드만
                employee_data = {
                    'user': user,
                    'name': row.get('이름', f'직원{idx+1}'),
                    'email': row.get('이메일', f'{username}@okfg.co.kr'),
                    'phone': row.get('전화번호', '010-0000-0000'),
                    'hire_date': row.get('입사일', '2020-01-01'),
                    'department': row.get('부서', row.get('최종소속', '경영관리')),
                    'position': 'STAFF',
                    'employment_status': '재직',
                    'employment_type': '정규직',
                }
                
                # 선택 필드들 - 있으면 추가
                if pd.notna(row.get('회사')):
                    employee_data['company'] = row['회사']
                if pd.notna(row.get('성별')):
                    employee_data['gender'] = row['성별']
                if pd.notna(row.get('나이')):
                    try:
                        employee_data['age'] = int(row['나이'])
                    except:
                        pass
                
                Employee.objects.update_or_create(
                    email=employee_data['email'],
                    defaults=employee_data
                )
                
                success += 1
                if success % 100 == 0:
                    self.stdout.write(f'진행: {success}/{total}')
                    
            except Exception as e:
                errors += 1
                if errors <= 5:
                    self.stdout.write(self.style.ERROR(f'행 {idx+2} 오류: {str(e)[:50]}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n완료! 성공: {success}, 실패: {errors}'))
        self.stdout.write(f'전체 직원: {Employee.objects.count()}명')