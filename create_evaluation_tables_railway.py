"""
Railway 서버에 평가 테이블 생성 및 데이터 삽입
"""
import os
import sys
import django
from datetime import date

# UTF-8 인코딩 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection
from evaluations.models import EvaluationPeriod

def create_tables_if_not_exists():
    """평가 관련 테이블이 없으면 생성"""
    
    with connection.cursor() as cursor:
        # evaluations_evaluationperiod 테이블 존재 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'evaluations_evaluationperiod'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("Creating evaluations_evaluationperiod table...")
            
            # 테이블 생성
            cursor.execute("""
                CREATE TABLE evaluations_evaluationperiod (
                    id SERIAL PRIMARY KEY,
                    year INTEGER NOT NULL,
                    period_type VARCHAR(10) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT FALSE,
                    status VARCHAR(20) NOT NULL DEFAULT 'PLANNING',
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(year, period_type)
                );
            """)
            print("✅ evaluations_evaluationperiod table created successfully!")
        else:
            print("Table evaluations_evaluationperiod already exists.")

def create_evaluation_periods():
    """평가 기간 데이터 생성"""
    
    current_year = 2024
    
    # 기존 활성화된 평가 기간 비활성화
    EvaluationPeriod.objects.filter(is_active=True).update(is_active=False)
    
    # 2024년 4분기 평가 기간 생성 (활성화)
    q4_period, created = EvaluationPeriod.objects.get_or_create(
        year=current_year,
        period_type='Q4',
        defaults={
            'start_date': date(2024, 10, 1),
            'end_date': date(2024, 12, 31),
            'is_active': True,
            'status': 'ONGOING'
        }
    )
    
    if not created:
        q4_period.is_active = True
        q4_period.status = 'ONGOING'
        q4_period.save()
    
    print(f"✅ 2024년 4분기 평가 기간 {'생성' if created else '활성화'} 완료")
    
    # 이전 분기들도 생성
    quarters = [
        ('Q1', date(2024, 1, 1), date(2024, 3, 31), 'COMPLETED'),
        ('Q2', date(2024, 4, 1), date(2024, 6, 30), 'COMPLETED'),
        ('Q3', date(2024, 7, 1), date(2024, 9, 30), 'COMPLETED'),
    ]
    
    for period_type, start_date, end_date, status in quarters:
        period, created = EvaluationPeriod.objects.get_or_create(
            year=current_year,
            period_type=period_type,
            defaults={
                'start_date': start_date,
                'end_date': end_date,
                'is_active': False,
                'status': status
            }
        )
        if created:
            print(f"✅ 2024년 {period_type} 평가 기간 생성 완료")
    
    # 2024년 연간 평가 기간 생성
    annual_period, created = EvaluationPeriod.objects.get_or_create(
        year=current_year,
        period_type='ANNUAL',
        defaults={
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 12, 31),
            'is_active': False,
            'status': 'ONGOING'
        }
    )
    
    if created:
        print(f"✅ 2024년 연간 평가 기간 생성 완료")
    
    # 전체 평가 기간 확인
    all_periods = EvaluationPeriod.objects.all()
    print(f"\n📊 전체 평가 기간: {all_periods.count()}개")
    for period in all_periods:
        status_icon = "🟢" if period.is_active else "⚪"
        print(f"  {status_icon} {period} ({period.status})")

if __name__ == "__main__":
    print("=" * 60)
    print("Railway 평가 테이블 생성 및 데이터 삽입")
    print("=" * 60)
    
    try:
        # 1. 테이블 생성
        create_tables_if_not_exists()
        
        # 2. 데이터 생성
        create_evaluation_periods()
        
        print("\n✅ 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()