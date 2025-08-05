import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from employees.models import Employee
from datetime import datetime, date
import sys


class Command(BaseCommand):
    help = '엑셀 파일에서 직원 데이터를 로딩합니다 (1790개 레코드, 45개 필드)'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='엑셀 파일 경로')
        parser.add_argument(
            '--sheet', 
            type=str, 
            default=0, 
            help='시트명 또는 시트 인덱스 (기본: 0)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 저장 없이 검증만 수행'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='배치 크기 (기본: 100)'
        )

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        sheet = options['sheet']
        dry_run = options['dry_run']
        batch_size = options['batch_size']

        try:
            # 엑셀 파일 읽기
            self.stdout.write(f"엑셀 파일 읽는 중: {excel_file}")
            
            # 시트 파라미터 처리
            if sheet.isdigit():
                sheet = int(sheet)
            
            df = pd.read_excel(excel_file, sheet_name=sheet)
            
            self.stdout.write(f"총 {len(df)}개 레코드, {len(df.columns)}개 컬럼")
            self.stdout.write(f"컬럼: {list(df.columns)}")

            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN 모드 - 실제 저장하지 않습니다"))

            # 데이터 처리 및 저장
            success_count = 0
            error_count = 0
            employees_to_create = []

            for index, row in df.iterrows():
                try:
                    employee_data = self.process_row(row)
                    
                    if dry_run:
                        # 검증만 수행
                        Employee(**employee_data)
                        success_count += 1
                    else:
                        employees_to_create.append(Employee(**employee_data))
                        
                        # 배치 크기만큼 모이면 저장
                        if len(employees_to_create) >= batch_size:
                            with transaction.atomic():
                                Employee.objects.bulk_create(employees_to_create, 
                                                            ignore_conflicts=True)
                            success_count += len(employees_to_create)
                            employees_to_create = []
                            
                            self.stdout.write(f"진행상황: {success_count}/{len(df)}")

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"행 {index + 2} 처리 중 오류: {str(e)}")
                    )

            # 남은 데이터 저장
            if not dry_run and employees_to_create:
                with transaction.atomic():
                    Employee.objects.bulk_create(employees_to_create, 
                                                ignore_conflicts=True)
                success_count += len(employees_to_create)

            # 결과 출력
            self.stdout.write(
                self.style.SUCCESS(
                    f"완료! 성공: {success_count}, 오류: {error_count}"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"파일 처리 중 오류 발생: {str(e)}")
            )
            sys.exit(1)

    def process_row(self, row):
        """엑셀 행 데이터를 Employee 모델 필드로 매핑"""
        
        # 날짜 변환 헬퍼 함수
        def safe_date_convert(value):
            if pd.isna(value) or value == '':
                return None
            try:
                if isinstance(value, (datetime, date)):
                    return value.date() if isinstance(value, datetime) else value
                return pd.to_datetime(value).date()
            except:
                return None

        # 숫자 변환 헬퍼 함수
        def safe_int_convert(value):
            if pd.isna(value) or value == '':
                return None
            try:
                return int(float(value))
            except:
                return None

        # 문자열 변환 헬퍼 함수
        def safe_str_convert(value, max_length=None):
            if pd.isna(value) or value == '':
                return None
            str_value = str(value).strip()
            if max_length and len(str_value) > max_length:
                str_value = str_value[:max_length]
            return str_value

        # Decimal 변환 헬퍼 함수
        def safe_decimal_convert(value):
            if pd.isna(value) or value == '':
                return None
            try:
                return float(value)
            except:
                return None

        return {
            # 기본 정보 (익명화 필드들)
            'dummy_ssn': safe_str_convert(row.get('dummy_주민번호'), 20),
            'dummy_chinese_name': safe_str_convert(row.get('dummy_한자'), 100),
            'dummy_name': safe_str_convert(row.get('dummy_이름'), 100),
            'dummy_mobile': safe_str_convert(row.get('dummy_휴대폰'), 20),
            'dummy_registered_address': safe_str_convert(row.get('dummy_주민등록주소')),
            'dummy_residence_address': safe_str_convert(row.get('dummy_실거주지주소')),
            'dummy_email': safe_str_convert(row.get('dummy_e-mail'), 254),

            # 일련번호 및 회사 정보
            'no': safe_int_convert(row.get('NO')),
            'company': safe_str_convert(row.get('회사'), 10),

            # 직급 정보
            'previous_position': safe_str_convert(row.get('직급(전)'), 50),
            'current_position': safe_str_convert(row.get('직급'), 50),

            # 조직 구조
            'headquarters1': safe_str_convert(row.get('본부1'), 100),
            'headquarters2': safe_str_convert(row.get('본부2'), 100),
            'department1': safe_str_convert(row.get('소속1'), 100),
            'department2': safe_str_convert(row.get('소속2'), 100),
            'department3': safe_str_convert(row.get('소속3'), 100),
            'department4': safe_str_convert(row.get('소속4'), 100),
            'final_department': safe_str_convert(row.get('최종소속'), 100),

            # 직군/계열 및 인사 정보
            'job_series': safe_str_convert(row.get('직군/계열'), 50),
            'title': safe_str_convert(row.get('호칭'), 50),
            'responsibility': safe_str_convert(row.get('직책'), 50),
            'promotion_level': safe_str_convert(row.get('승급레벨'), 20),
            'salary_grade': safe_str_convert(row.get('급호'), 20),

            # 개인 정보
            'gender': safe_str_convert(row.get('성별'), 1),
            'age': safe_int_convert(row.get('나이')),
            'birth_date': safe_date_convert(row.get('생일')),

            # 입사 관련 날짜들
            'group_join_date': safe_date_convert(row.get('그룹입사일')),
            'career_join_date': safe_date_convert(row.get('경력입사일')),
            'new_join_date': safe_date_convert(row.get('신입입사일')),

            # 근무 년수 및 평가
            'promotion_accumulated_years': safe_decimal_convert(row.get('승급누적년수')),
            'final_evaluation': safe_str_convert(row.get('최종평가'), 10),

            # 태그 정보
            'job_tag_name': safe_str_convert(row.get('직무태그명'), 100),
            'rank_tag_name': safe_str_convert(row.get('순위태그명'), 100),

            # 추가 정보
            'education': safe_str_convert(row.get('학력'), 50),
            'marital_status': safe_str_convert(row.get('결혼여부'), 1),
            'job_family': safe_str_convert(row.get('직무군'), 50),
            'job_field': safe_str_convert(row.get('직무분야'), 50),
            'classification': safe_str_convert(row.get('분류'), 50),
            'current_headcount': safe_str_convert(row.get('현원'), 10),
            'detailed_classification': safe_str_convert(row.get('세부분류'), 100),
            'category': safe_str_convert(row.get('구분'), 50),
            'diversity_years': safe_decimal_convert(row.get('다양성년수')),

            # 기존 필드들 (필수)
            'name': safe_str_convert(row.get('dummy_이름') or row.get('이름'), 100) or 'Unknown',
            'email': f"user{safe_int_convert(row.get('NO')) or '0000'}@company.com",
            'department': safe_str_convert(row.get('최종소속') or '미정', 20)[:20],
            'position': safe_str_convert(row.get('직급') or 'STAFF', 20)[:20],
            'hire_date': safe_date_convert(row.get('그룹입사일')) or safe_date_convert(row.get('입사일')) or date.today(),
            'phone': safe_str_convert(row.get('dummy_휴대폰') or '000-0000-0000', 15)[:15],
        }