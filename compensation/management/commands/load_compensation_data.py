"""
보상 관련 CSV 시드 데이터 로더
작업지시서 기반 구현
"""

import csv
import os
from decimal import Decimal
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.db import transaction
from compensation.models_enhanced import (
    GradeMaster, PositionMaster, JobProfileMaster,
    BaseSalaryTable, PositionAllowanceTable, CompetencyAllowanceTable,
    PITable, MonthlyPITable
)


class Command(BaseCommand):
    help = 'Load compensation seed data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading',
        )
        parser.add_argument(
            '--csv-dir',
            type=str,
            default='compensation/seed_data',
            help='Directory containing CSV seed files',
        )

    def handle(self, *args, **options):
        csv_dir = options['csv_dir']
        clear_data = options.get('clear', False)

        if clear_data:
            self.stdout.write('Clearing existing compensation data...')
            self.clear_all_data()

        self.stdout.write(self.style.SUCCESS('Loading compensation seed data...'))
        
        # 1. 마스터 데이터 로드
        self.load_grade_master(csv_dir)
        self.load_position_master(csv_dir)
        self.load_job_profile_master(csv_dir)
        
        # 2. 보상 테이블 로드
        self.load_base_salary_table(csv_dir)
        self.load_position_allowance_table(csv_dir)
        self.load_competency_allowance_table(csv_dir)
        
        # 3. 변동급 테이블 로드
        self.load_pi_table(csv_dir)
        self.load_monthly_pi_table(csv_dir)
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded all compensation data'))

    def clear_all_data(self):
        """모든 보상 데이터 삭제"""
        models_to_clear = [
            MonthlyPITable, PITable,
            CompetencyAllowanceTable, PositionAllowanceTable, BaseSalaryTable,
            JobProfileMaster, PositionMaster, GradeMaster
        ]
        for model in models_to_clear:
            model.objects.all().delete()
            self.stdout.write(f'  - Cleared {model.__name__}')

    def load_grade_master(self, csv_dir):
        """등급 마스터 로드"""
        file_path = os.path.join(csv_dir, 'grade_master.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Grade master file not found: {file_path}'))
            self.create_default_grade_master()
            return
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                GradeMaster.objects.update_or_create(
                    grade_code=row['grade_code'],
                    defaults={
                        'level': int(row['level']),
                        'step': int(row['step']),
                        'title': row['title'],
                        'valid_from': datetime.strptime(row['valid_from'], '%Y-%m-%d').date(),
                        'valid_to': datetime.strptime(row['valid_to'], '%Y-%m-%d').date() if row.get('valid_to') else None,
                    }
                )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Loaded grade master data'))

    def create_default_grade_master(self):
        """기본 등급 마스터 생성"""
        default_grades = [
            {'code': 'GRD11', 'level': 1, 'step': 1, 'title': '주임'},
            {'code': 'GRD12', 'level': 1, 'step': 2, 'title': '전임'},
            {'code': 'GRD21', 'level': 2, 'step': 1, 'title': '선임'},
            {'code': 'GRD31', 'level': 3, 'step': 1, 'title': '책임'},
            {'code': 'GRD32', 'level': 3, 'step': 2, 'title': '프로'},
            {'code': 'GRD41', 'level': 4, 'step': 1, 'title': '수석'},
            {'code': 'GRD51', 'level': 5, 'step': 1, 'title': '팀장'},
            {'code': 'GRD61', 'level': 6, 'step': 1, 'title': '부장'},
            {'code': 'GRD71', 'level': 7, 'step': 1, 'title': '상무'},
            {'code': 'GRD81', 'level': 8, 'step': 1, 'title': '전무'},
            {'code': 'GRD91', 'level': 9, 'step': 1, 'title': '부사장'},
        ]
        
        for grade in default_grades:
            GradeMaster.objects.update_or_create(
                grade_code=grade['code'],
                defaults={
                    'level': grade['level'],
                    'step': grade['step'],
                    'title': grade['title'],
                    'valid_from': date(2024, 1, 1),
                    'valid_to': None,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created default grade master data'))

    def load_position_master(self, csv_dir):
        """직책 마스터 로드"""
        file_path = os.path.join(csv_dir, 'position_master.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Position master file not found: {file_path}'))
            self.create_default_position_master()
            return
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                PositionMaster.objects.update_or_create(
                    position_code=row['position_code'],
                    defaults={
                        'position_name': row['position_name'],
                        'domain': row['domain'],
                        'manager_level': int(row['manager_level']) if row.get('manager_level') else None,
                        'valid_from': datetime.strptime(row['valid_from'], '%Y-%m-%d').date(),
                        'valid_to': datetime.strptime(row['valid_to'], '%Y-%m-%d').date() if row.get('valid_to') else None,
                    }
                )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Loaded position master data'))

    def create_default_position_master(self):
        """기본 직책 마스터 생성"""
        default_positions = [
            # 본사 직책
            {'code': 'POS01', 'name': '팀장', 'domain': 'HQ', 'level': 1},
            {'code': 'POS02', 'name': '부문장', 'domain': 'HQ', 'level': 2},
            {'code': 'POS03', 'name': '본부장', 'domain': 'HQ', 'level': 3},
            # Non-PL 직책
            {'code': 'POS11', 'name': '팀장', 'domain': 'Non-PL', 'level': 1},
            {'code': 'POS12', 'name': '센터장', 'domain': 'Non-PL', 'level': 2},
            {'code': 'POS13', 'name': '지점장', 'domain': 'Non-PL', 'level': 2},
            {'code': 'POS16', 'name': 'RM지점장', 'domain': 'Non-PL', 'level': 2},
            # PL 직책
            {'code': 'POS21', 'name': '팀장', 'domain': 'PL', 'level': 1},
            {'code': 'POS22', 'name': '센터장', 'domain': 'PL', 'level': 2},
            {'code': 'POS23', 'name': '본부장', 'domain': 'PL', 'level': 3},
        ]
        
        for pos in default_positions:
            PositionMaster.objects.update_or_create(
                position_code=pos['code'],
                defaults={
                    'position_name': pos['name'],
                    'domain': pos['domain'],
                    'manager_level': pos['level'],
                    'valid_from': date(2024, 1, 1),
                    'valid_to': None,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created default position master data'))

    def load_job_profile_master(self, csv_dir):
        """직무 프로파일 마스터 로드"""
        file_path = os.path.join(csv_dir, 'job_profile_master.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Job profile master file not found: {file_path}'))
            self.create_default_job_profile_master()
            return
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                JobProfileMaster.objects.update_or_create(
                    job_profile_id=row['job_profile_id'],
                    defaults={
                        'job_family': row['job_family'],
                        'job_series': row['job_series'],
                        'job_role': row['job_role'],
                        'description': row.get('description', ''),
                        'valid_from': datetime.strptime(row['valid_from'], '%Y-%m-%d').date(),
                        'valid_to': datetime.strptime(row['valid_to'], '%Y-%m-%d').date() if row.get('valid_to') else None,
                    }
                )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Loaded job profile master data'))

    def create_default_job_profile_master(self):
        """기본 직무 프로파일 마스터 생성"""
        default_profiles = [
            {'id': 'JP001', 'family': '경영관리', 'series': '경영기획', 'role': '전략기획'},
            {'id': 'JP002', 'family': '경영관리', 'series': '인사', 'role': 'HR기획'},
            {'id': 'JP003', 'family': '경영관리', 'series': '재무', 'role': '재무관리'},
            {'id': 'JP004', 'family': 'IT', 'series': '개발', 'role': '시스템개발'},
            {'id': 'JP005', 'family': 'IT', 'series': '인프라', 'role': '시스템운영'},
            {'id': 'JP006', 'family': '영업', 'series': '기업영업', 'role': '법인영업'},
            {'id': 'JP007', 'family': '영업', 'series': '리테일', 'role': '개인영업'},
            {'id': 'JP008', 'family': '리스크', 'series': '심사', 'role': '여신심사'},
            {'id': 'JP009', 'family': '리스크', 'series': '채권', 'role': '채권관리'},
            {'id': 'JP010', 'family': '마케팅', 'series': '상품', 'role': '상품개발'},
        ]
        
        for profile in default_profiles:
            JobProfileMaster.objects.update_or_create(
                job_profile_id=profile['id'],
                defaults={
                    'job_family': profile['family'],
                    'job_series': profile['series'],
                    'job_role': profile['role'],
                    'description': f"{profile['family']} {profile['series']} {profile['role']}",
                    'valid_from': date(2024, 1, 1),
                    'valid_to': None,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created default job profile master data'))

    def load_base_salary_table(self, csv_dir):
        """기본급 테이블 로드"""
        file_path = os.path.join(csv_dir, 'base_salary_table.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Base salary table file not found: {file_path}'))
            self.create_default_base_salary_table()
            return
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    grade = GradeMaster.objects.get(grade_code=row['grade_code'])
                    BaseSalaryTable.objects.update_or_create(
                        grade_code=grade,
                        employment_type=row['employment_type'],
                        valid_from=datetime.strptime(row['valid_from'], '%Y-%m-%d').date(),
                        defaults={
                            'base_salary': Decimal(row['base_salary']),
                            'valid_to': datetime.strptime(row['valid_to'], '%Y-%m-%d').date() if row.get('valid_to') else None,
                        }
                    )
                except GradeMaster.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'    Grade not found: {row["grade_code"]}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Loaded base salary table'))

    def create_default_base_salary_table(self):
        """기본급 테이블 기본값 생성"""
        # 성장레벨별 기본급 (예시)
        base_salaries = {
            'GRD11': 3000000,  # Lv1-1 주임
            'GRD12': 3200000,  # Lv1-2 전임
            'GRD21': 3500000,  # Lv2-1 선임
            'GRD31': 4000000,  # Lv3-1 책임
            'GRD32': 4500000,  # Lv3-2 프로
            'GRD41': 5500000,  # Lv4-1 수석
            'GRD51': 6500000,  # Lv5-1 팀장급
            'GRD61': 7500000,  # Lv6-1 부장급
            'GRD71': 9000000,  # Lv7-1 상무
            'GRD81': 11000000, # Lv8-1 전무
            'GRD91': 13000000, # Lv9-1 부사장
        }
        
        for grade_code, base_salary in base_salaries.items():
            try:
                grade = GradeMaster.objects.get(grade_code=grade_code)
                for emp_type in ['정규직', 'Non-PL', 'PL']:
                    # PL은 10% 추가, Non-PL은 5% 추가
                    multiplier = 1.1 if emp_type == 'PL' else (1.05 if emp_type == 'Non-PL' else 1.0)
                    BaseSalaryTable.objects.update_or_create(
                        grade_code=grade,
                        employment_type=emp_type,
                        valid_from=date(2024, 1, 1),
                        defaults={
                            'base_salary': Decimal(base_salary * multiplier),
                            'valid_to': None,
                        }
                    )
            except GradeMaster.DoesNotExist:
                pass
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created default base salary table'))

    def load_position_allowance_table(self, csv_dir):
        """직책급 테이블 로드"""
        file_path = os.path.join(csv_dir, 'position_allowance_table.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Position allowance table file not found: {file_path}'))
            self.create_default_position_allowance_table()
            return
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    position = PositionMaster.objects.get(position_code=row['position_code'])
                    PositionAllowanceTable.objects.update_or_create(
                        position_code=position,
                        allowance_tier=row['allowance_tier'],
                        valid_from=datetime.strptime(row['valid_from'], '%Y-%m-%d').date(),
                        defaults={
                            'monthly_amount': Decimal(row['monthly_amount']),
                            'allowance_rate': Decimal(row.get('allowance_rate', '1.0')),
                            'valid_to': datetime.strptime(row['valid_to'], '%Y-%m-%d').date() if row.get('valid_to') else None,
                        }
                    )
                except PositionMaster.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'    Position not found: {row["position_code"]}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Loaded position allowance table'))

    def create_default_position_allowance_table(self):
        """직책급 테이블 기본값 생성"""
        position_allowances = {
            # 본사 직책급
            'POS01': {'A': 800000, 'B+': 700000, 'B': 600000},  # 팀장
            'POS02': {'A': 1200000, 'B+': 1100000, 'B': 1000000},  # 부문장
            'POS03': {'A': 1500000, 'B+': 1400000, 'B': 1300000},  # 본부장
            # 영업 직책급 (단일)
            'POS11': {'N/A': 700000},  # 팀장
            'POS12': {'N/A': 900000},  # 센터장
            'POS13': {'N/A': 1000000},  # 지점장
            'POS16': {'N/A': 1100000},  # RM지점장
            # PL 직책급
            'POS21': {'N/A': 750000},  # 팀장
            'POS22': {'N/A': 950000},  # 센터장
            'POS23': {'N/A': 1300000},  # 본부장
        }
        
        for pos_code, tiers in position_allowances.items():
            try:
                position = PositionMaster.objects.get(position_code=pos_code)
                for tier, amount in tiers.items():
                    PositionAllowanceTable.objects.update_or_create(
                        position_code=position,
                        allowance_tier=tier,
                        valid_from=date(2024, 1, 1),
                        defaults={
                            'monthly_amount': Decimal(amount),
                            'allowance_rate': Decimal('1.0'),
                            'valid_to': None,
                        }
                    )
            except PositionMaster.DoesNotExist:
                pass
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created default position allowance table'))

    def load_competency_allowance_table(self, csv_dir):
        """직무역량급 테이블 로드"""
        file_path = os.path.join(csv_dir, 'competency_allowance_table.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Competency allowance table file not found: {file_path}'))
            self.create_default_competency_allowance_table()
            return
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    job_profile = JobProfileMaster.objects.get(job_profile_id=row['job_profile_id'])
                    CompetencyAllowanceTable.objects.update_or_create(
                        job_profile_id=job_profile,
                        competency_tier=row['competency_tier'],
                        valid_from=datetime.strptime(row['valid_from'], '%Y-%m-%d').date(),
                        defaults={
                            'monthly_amount': Decimal(row['monthly_amount']),
                            'valid_to': datetime.strptime(row['valid_to'], '%Y-%m-%d').date() if row.get('valid_to') else None,
                        }
                    )
                except JobProfileMaster.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'    Job profile not found: {row["job_profile_id"]}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Loaded competency allowance table'))

    def create_default_competency_allowance_table(self):
        """직무역량급 테이블 기본값 생성"""
        # 직무별 역량급 (T1 > T2 > T3)
        competency_allowances = {
            'JP001': {'T1': 500000, 'T2': 400000, 'T3': 300000},  # 전략기획
            'JP002': {'T1': 450000, 'T2': 350000, 'T3': 250000},  # HR기획
            'JP003': {'T1': 480000, 'T2': 380000, 'T3': 280000},  # 재무관리
            'JP004': {'T1': 550000, 'T2': 450000, 'T3': 350000},  # 시스템개발
            'JP005': {'T1': 500000, 'T2': 400000, 'T3': 300000},  # 시스템운영
            'JP006': {'T1': 600000, 'T2': 500000, 'T3': 400000},  # 법인영업
            'JP007': {'T1': 550000, 'T2': 450000, 'T3': 350000},  # 개인영업
            'JP008': {'T1': 520000, 'T2': 420000, 'T3': 320000},  # 여신심사
            'JP009': {'T1': 500000, 'T2': 400000, 'T3': 300000},  # 채권관리
            'JP010': {'T1': 530000, 'T2': 430000, 'T3': 330000},  # 상품개발
        }
        
        for job_id, tiers in competency_allowances.items():
            try:
                job_profile = JobProfileMaster.objects.get(job_profile_id=job_id)
                for tier, amount in tiers.items():
                    CompetencyAllowanceTable.objects.update_or_create(
                        job_profile_id=job_profile,
                        competency_tier=tier,
                        valid_from=date(2024, 1, 1),
                        defaults={
                            'monthly_amount': Decimal(amount),
                            'valid_to': None,
                        }
                    )
            except JobProfileMaster.DoesNotExist:
                pass
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created default competency allowance table'))

    def load_pi_table(self, csv_dir):
        """PI 지급률 테이블 로드"""
        file_path = os.path.join(csv_dir, 'pi_table.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'PI table file not found: {file_path}'))
            self.create_default_pi_table()
            return
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                PITable.objects.update_or_create(
                    organization_type=row['organization_type'],
                    role_type=row['role_type'],
                    evaluation_grade=row['evaluation_grade'],
                    valid_from=datetime.strptime(row['valid_from'], '%Y-%m-%d').date(),
                    defaults={
                        'payment_rate': Decimal(row['payment_rate']),
                        'valid_to': datetime.strptime(row['valid_to'], '%Y-%m-%d').date() if row.get('valid_to') else None,
                    }
                )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Loaded PI table'))

    def create_default_pi_table(self):
        """PI 지급률 테이블 기본값 생성"""
        # PI 지급률 (본사/영업 × 팀원/직책자 × 등급)
        pi_rates = {
            ('본사', '팀원'): {'S': 150, 'A+': 130, 'A': 110, 'B+': 90, 'B': 70, 'C': 50, 'D': 0},
            ('본사', '직책자'): {'S': 180, 'A+': 160, 'A': 140, 'B+': 120, 'B': 100, 'C': 80, 'D': 0},
            ('영업', '팀원'): {'S': 160, 'A+': 140, 'A': 120, 'B+': 100, 'B': 80, 'C': 60, 'D': 0},
            ('영업', '직책자'): {'S': 200, 'A+': 180, 'A': 160, 'B+': 140, 'B': 120, 'C': 100, 'D': 0},
        }
        
        for (org_type, role_type), grades in pi_rates.items():
            for grade, rate in grades.items():
                PITable.objects.update_or_create(
                    organization_type=org_type,
                    role_type=role_type,
                    evaluation_grade=grade,
                    valid_from=date(2024, 1, 1),
                    defaults={
                        'payment_rate': Decimal(rate),
                        'valid_to': None,
                    }
                )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created default PI table'))

    def load_monthly_pi_table(self, csv_dir):
        """월성과급 테이블 로드"""
        file_path = os.path.join(csv_dir, 'monthly_pi_table.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Monthly PI table file not found: {file_path}'))
            self.create_default_monthly_pi_table()
            return
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                MonthlyPITable.objects.update_or_create(
                    role_level=row['role_level'],
                    evaluation_grade=row['evaluation_grade'],
                    valid_from=datetime.strptime(row['valid_from'], '%Y-%m-%d').date(),
                    defaults={
                        'payment_amount': Decimal(row['payment_amount']),
                        'valid_to': datetime.strptime(row['valid_to'], '%Y-%m-%d').date() if row.get('valid_to') else None,
                    }
                )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Loaded monthly PI table'))

    def create_default_monthly_pi_table(self):
        """월성과급 테이블 기본값 생성"""
        # 월성과급 지급액 (역할레벨 × 등급)
        monthly_pi_amounts = {
            '센터장': {'S': 1500000, 'A+': 1300000, 'A': 1100000, 'A-': 1000000,
                     'B+': 900000, 'B': 800000, 'B-': 700000, 'C': 600000, 'D': 0},
            '팀장': {'S': 1200000, 'A+': 1050000, 'A': 900000, 'A-': 800000,
                    'B+': 700000, 'B': 600000, 'B-': 500000, 'C': 400000, 'D': 0},
            'Lv.2-3': {'S': 900000, 'A+': 800000, 'A': 700000, 'A-': 650000,
                       'B+': 600000, 'B': 550000, 'B-': 500000, 'C': 400000, 'D': 0},
            'Lv.1': {'S': 600000, 'A+': 550000, 'A': 500000, 'A-': 450000,
                     'B+': 400000, 'B': 350000, 'B-': 300000, 'C': 250000, 'D': 0},
        }
        
        for role_level, grades in monthly_pi_amounts.items():
            for grade, amount in grades.items():
                MonthlyPITable.objects.update_or_create(
                    role_level=role_level,
                    evaluation_grade=grade,
                    valid_from=date(2024, 1, 1),
                    defaults={
                        'payment_amount': Decimal(amount),
                        'valid_to': None,
                    }
                )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created default monthly PI table'))