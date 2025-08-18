"""
Railway 서버의 ImpactEvaluation 테이블에 누락된 컬럼 추가
"""
import os
import sys
import django

# UTF-8 인코딩 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection

def add_missing_impact_columns():
    """ImpactEvaluation 테이블의 누락된 컬럼 추가"""
    
    columns_to_add = [
        # 핵심가치 실천 및 리더십 발휘
        ('evaluations_impactevaluation', 'core_values_practice', "VARCHAR(20) DEFAULT 'limited_values'"),
        ('evaluations_impactevaluation', 'leadership_demonstration', "VARCHAR(20) DEFAULT 'limited_leadership'"),
        
        # 기존 평가 항목들 (하위 호환성)
        ('evaluations_impactevaluation', 'customer_focus', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'collaboration', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'innovation', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'team_leadership', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'organizational_impact', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'external_networking', 'INTEGER DEFAULT 2'),
    ]
    
    with connection.cursor() as cursor:
        for table_name, column_name, column_type in columns_to_add:
            try:
                # 컬럼 존재 확인
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = '{table_name}' 
                        AND column_name = '{column_name}'
                    );
                """)
                
                exists = cursor.fetchone()[0]
                
                if not exists:
                    # 컬럼 추가
                    cursor.execute(f"""
                        ALTER TABLE {table_name} 
                        ADD COLUMN {column_name} {column_type};
                    """)
                    print(f"✅ {table_name}.{column_name} 추가 완료")
                else:
                    print(f"⚪ {table_name}.{column_name} 이미 존재")
                    
            except Exception as e:
                print(f"❌ {table_name}.{column_name} 오류: {e}")

def verify_impact_schema():
    """ImpactEvaluation 스키마 완전성 확인"""
    with connection.cursor() as cursor:
        # ImpactEvaluation 필수 컬럼 확인
        impact_required = [
            'impact_scope', 'core_values_practice', 'leadership_demonstration',
            'customer_focus', 'collaboration', 'innovation',
            'team_leadership', 'organizational_impact', 'external_networking',
            'total_score', 'is_achieved', 'evaluated_date'
        ]
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'evaluations_impactevaluation'
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        print("\n📊 ImpactEvaluation 스키마 검증:")
        missing = []
        for col in impact_required:
            if col in existing_columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ❌ {col} - 누락됨")
                missing.append(col)
        
        if missing:
            print(f"\n⚠️ 누락된 컬럼: {', '.join(missing)}")
        else:
            print("\n✅ 모든 필수 컬럼 존재")

if __name__ == "__main__":
    print("="*60)
    print("Railway ImpactEvaluation 테이블 컬럼 수정")
    print("="*60)
    
    try:
        # 1. 누락된 컬럼 추가
        add_missing_impact_columns()
        
        # 2. 스키마 검증
        print("\n" + "="*60)
        print("스키마 검증")
        print("="*60)
        verify_impact_schema()
        
        print("\n✅ 모든 작업 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()