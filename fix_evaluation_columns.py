"""
Railway 서버의 평가 테이블에 누락된 컬럼 추가
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

def add_missing_columns():
    """누락된 컬럼 추가"""
    
    columns_to_add = [
        # ContributionEvaluation 테이블
        ('evaluations_contributionevaluation', 'total_achievement_rate', 'DECIMAL(5,2)'),
        ('evaluations_contributionevaluation', 'evaluated_date', 'DATE'),
        
        # ExpertiseEvaluation 테이블 추가 컬럼들
        ('evaluations_expertiseevaluation', 'required_level', 'INTEGER DEFAULT 3'),
        ('evaluations_expertiseevaluation', 'expertise_focus', "VARCHAR(20) DEFAULT 'balanced'"),
        ('evaluations_expertiseevaluation', 'creative_solution', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'technical_innovation', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'process_improvement', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'knowledge_sharing', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'problem_solving', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'domain_expertise', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'analytical_thinking', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'strategic_thinking', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'execution_capability', 'INTEGER DEFAULT 2'),
        ('evaluations_expertiseevaluation', 'communication_skill', 'INTEGER DEFAULT 2'),
        
        # ImpactEvaluation 테이블 추가 컬럼들
        ('evaluations_impactevaluation', 'contribution_to_org', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'collaboration_effectiveness', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'team_development', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'value_creation', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'stakeholder_satisfaction', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'leadership_influence', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'cultural_contribution', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'external_recognition', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'customer_impact', 'INTEGER DEFAULT 2'),
        ('evaluations_impactevaluation', 'business_results', 'INTEGER DEFAULT 2'),
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

def verify_columns():
    """컬럼 확인"""
    tables = [
        'evaluations_contributionevaluation',
        'evaluations_expertiseevaluation', 
        'evaluations_impactevaluation'
    ]
    
    with connection.cursor() as cursor:
        for table_name in tables:
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"\n📊 {table_name} 컬럼 목록:")
            for col_name, col_type in columns:
                print(f"  ✓ {col_name} ({col_type})")

if __name__ == "__main__":
    print("="*60)
    print("Railway 평가 테이블 컬럼 수정")
    print("="*60)
    
    try:
        # 1. 누락된 컬럼 추가
        add_missing_columns()
        
        # 2. 검증
        print("\n" + "="*60)
        print("컬럼 확인")
        print("="*60)
        verify_columns()
        
        print("\n✅ 모든 작업 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()