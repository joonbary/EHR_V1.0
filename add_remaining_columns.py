"""
Railway 서버의 평가 테이블에 남은 누락 컬럼 추가
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

def add_remaining_columns():
    """누락된 컬럼 추가"""
    
    columns_to_add = [
        # ExpertiseEvaluation 테이블에 추가 컬럼들
        ('evaluations_expertiseevaluation', 'mentoring', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'cross_functional', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'business_acumen', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'industry_trend', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'continuous_learning', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'strategic_contribution', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'interactive_contribution', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'technical_expertise', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'business_understanding', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'evaluated_date', 'DATE'),
        
        # ImpactEvaluation 테이블에 추가 컬럼들
        ('evaluations_impactevaluation', 'impact_scope', "VARCHAR(20) DEFAULT 'individual'"),
        ('evaluations_impactevaluation', 'leadership_behavior', "VARCHAR(30) DEFAULT 'limited_leadership'"),
        ('evaluations_impactevaluation', 'values_behavior', "VARCHAR(30) DEFAULT 'limited_values'"),
        ('evaluations_impactevaluation', 'evaluated_date', 'DATE'),
        
        # 나머지 체크리스트 필드들 (미리 추가하지 않은 것들)
        ('evaluations_expertiseevaluation', 'problem_solving', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'domain_expertise', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'analytical_thinking', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'execution_capability', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'communication_skill', 'INTEGER DEFAULT 2'),
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

def verify_schema():
    """스키마 완전성 확인"""
    with connection.cursor() as cursor:
        # ExpertiseEvaluation 필수 컬럼 확인
        expertise_required = [
            'mentoring', 'cross_functional', 'strategic_thinking', 'business_acumen',
            'industry_trend', 'continuous_learning', 'strategic_contribution',
            'interactive_contribution', 'technical_expertise', 'business_understanding',
            'creative_solution', 'technical_innovation', 'process_improvement',
            'knowledge_sharing', 'total_score', 'evaluated_date'
        ]
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'evaluations_expertiseevaluation'
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        print("\n📊 ExpertiseEvaluation 스키마 검증:")
        missing = []
        for col in expertise_required:
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
    print("Railway 평가 테이블 남은 컬럼 추가")
    print("="*60)
    
    try:
        # 1. 누락된 컬럼 추가
        add_remaining_columns()
        
        # 2. 스키마 검증
        print("\n" + "="*60)
        print("스키마 검증")
        print("="*60)
        verify_schema()
        
        print("\n✅ 모든 작업 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()