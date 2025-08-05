import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_date
from datetime import datetime
from employees.models import Employee


class Command(BaseCommand):
    help = 'OK금융그룹 직원 Excel 파일 일괄 업로드 (part1, part2)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--part1',
            type=str,
            default='OK_employee_new_part1.xlsx',
            help='Part 1 Excel 파일명 (기본값: OK_employee_new_part1.xlsx)'
        )
        parser.add_argument(
            '--part2',
            type=str,
            default='OK_employee_new_part2.xlsx',
            help='Part 2 Excel 파일명 (기본값: OK_employee_new_part2.xlsx)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 데이터를 모두 삭제하고 새로 로드'
        )

    def handle(self, *args, **options):
        part1_file = options['part1']
        part2_file = options['part2']
        
        if options['clear']:
            self.stdout.write(self.style.WARNING('기존 직원 데이터를 모두 삭제합니다...'))
            Employee.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('기존 데이터 삭제 완료'))
        
        total_created = 0
        total_updated = 0
        
        # Part 1 업로드
        self.stdout.write(f'\nPart 1 파일 처리 중: {part1_file}')
        created1, updated1 = self.load_excel_file(part1_file)
        total_created += created1
        total_updated += updated1
        
        # Part 2 업로드
        self.stdout.write(f'\nPart 2 파일 처리 중: {part2_file}')
        created2, updated2 = self.load_excel_file(part2_file)
        total_created += created2
        total_updated += updated2
        
        # 최종 결과 출력
        self.stdout.write(self.style.SUCCESS(f'\n=== 업로드 완료 ==='))
        self.stdout.write(self.style.SUCCESS(f'총 생성: {total_created}명'))
        self.stdout.write(self.style.SUCCESS(f'총 업데이트: {total_updated}명'))
        self.stdout.write(self.style.SUCCESS(f'전체 직원 수: {Employee.objects.count()}명'))

    def load_excel_file(self, file_path):
        """Excel 파일을 로드하여 Employee 모델에 저장"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'파일을 찾을 수 없습니다: {file_path}'))
            return 0, 0
        
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f'파일 로드 완료: {len(df)}개 행')
            
            created_count = 0
            updated_count = 0
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # 필수 필드 확인
                        email = str(row.get('이메일', '')).strip()
                        if not email or email == 'nan':
                            self.stdout.write(self.style.WARNING(f'행 {index + 2}: 이메일이 없어 건너뜁니다'))
                            continue
                        
                        # 입사일 처리
                        hire_date = None
                        hire_date_value = row.get('입사일')
                        if pd.notna(hire_date_value):
                            if isinstance(hire_date_value, str):
                                try:
                                    hire_date = datetime.strptime(hire_date_value, '%Y%m%d').date()
                                except:
                                    try:
                                        hire_date = parse_date(hire_date_value)
                                    except:
                                        pass
                            elif hasattr(hire_date_value, 'date'):
                                hire_date = hire_date_value.date()
                        
                        # 직원 데이터 준비
                        employee_data = {
                            'email': email,
                            'name': str(row.get('성명', '')).strip(),
                            'no': int(row.get('NO', 0)) if pd.notna(row.get('NO')) else None,
                            'company': str(row.get('회사', '')).strip(),
                            'final_department': str(row.get('부서', row.get('최종소속', ''))).strip(),
                            'current_position': str(row.get('직급', '')).strip(),
                            'responsibility': str(row.get('직책', '')).strip(),
                            'employment_type': str(row.get('재직구분', '정규직')).strip(),
                            'hire_date': hire_date,
                            'age': int(row.get('나이', 0)) if pd.notna(row.get('나이')) else None,
                            
                            # dummy 필드들
                            'dummy_name': str(row.get('dummy_성명', '')).strip() if pd.notna(row.get('dummy_성명')) else '',
                            'dummy_chinese_name': str(row.get('dummy_한자', '')).strip() if pd.notna(row.get('dummy_한자')) else '',
                            'dummy_email': str(row.get('dummy_email', '')).strip() if pd.notna(row.get('dummy_email')) else '',
                            'dummy_mobile': str(row.get('dummy_휴대전화', '')).strip() if pd.notna(row.get('dummy_휴대전화')) else '',
                            'dummy_registered_address': str(row.get('dummy_등록기준지', '')).strip() if pd.notna(row.get('dummy_등록기준지')) else '',
                            'dummy_residence_address': str(row.get('dummy_기숙사', '')).strip() if pd.notna(row.get('dummy_기숙사')) else '',
                        }
                        
                        # 추가 필드들
                        if '신분증만료일' in row:
                            employee_data['id_expiry_date'] = str(row.get('신분증만료일', '')).strip()
                        if '재직여부' in row:
                            employee_data['employment_status'] = str(row.get('재직여부', '')).strip()
                        if '회사' in row:
                            employee_data['company'] = str(row.get('회사', '')).strip()
                        
                        # Employee 생성 또는 업데이트
                        employee, created = Employee.objects.update_or_create(
                            email=email,
                            defaults=employee_data
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                        
                        if (index + 1) % 100 == 0:
                            self.stdout.write(f'진행 중: {index + 1}/{len(df)}')
                    
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'행 {index + 2} 처리 중 오류: {str(e)}'))
                        continue
            
            self.stdout.write(self.style.SUCCESS(f'파일 처리 완료 - 생성: {created_count}, 업데이트: {updated_count}'))
            return created_count, updated_count
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'파일 처리 중 오류 발생: {str(e)}'))
            return 0, 0