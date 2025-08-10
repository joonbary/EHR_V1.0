"""
Railway 서버의 ComprehensiveEvaluation 테이블에 누락된 컬럼 추가
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

def add_missing_comprehensive_columns():
    """ComprehensiveEvaluation 테이블의 누락된 컬럼 추가"""
    
    columns_to_add = [
        # 달성 여부 컬럼들
        ('evaluations_comprehensiveevaluation', 'contribution_achieved', 'BOOLEAN DEFAULT FALSE'),
        ('evaluations_comprehensiveevaluation', 'expertise_achieved', 'BOOLEAN DEFAULT FALSE'),
        ('evaluations_comprehensiveevaluation', 'impact_achieved', 'BOOLEAN DEFAULT FALSE'),
        
        # 관리자 평가 컬럼들
        ('evaluations_comprehensiveevaluation', 'manager_id', 'INTEGER'),
        ('evaluations_comprehensiveevaluation', 'manager_grade', 'VARCHAR(5)'),
        ('evaluations_comprehensiveevaluation', 'manager_comments', 'TEXT'),
        ('evaluations_comprehensiveevaluation', 'manager_evaluated_date', 'DATE'),
        
        # Calibration 관련 컬럼들
        ('evaluations_comprehensiveevaluation', 'calibration_comments', 'TEXT'),
        ('evaluations_comprehensiveevaluation', 'calibration_date', 'DATE'),
        ('evaluations_comprehensiveevaluation', 'calibration_session_id', 'INTEGER'),
        
        # 종합 점수
        ('evaluations_comprehensiveevaluation', 'overall_score', 'DECIMAL(3,1)'),
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

def verify_comprehensive_schema():
    """ComprehensiveEvaluation 스키마 완전성 확인"""
    with connection.cursor() as cursor:
        # ComprehensiveEvaluation 필수 컬럼 확인
        comprehensive_required = [
            'employee_id', 'evaluation_period_id',
            'contribution_evaluation_id', 'expertise_evaluation_id', 'impact_evaluation_id',
            'contribution_score', 'expertise_score', 'impact_score',
            'contribution_achieved', 'expertise_achieved', 'impact_achieved',
            'manager_id', 'manager_grade', 'manager_comments', 'manager_evaluated_date',
            'final_grade', 'calibration_comments', 'calibration_date', 'calibration_session_id',
            'status', 'overall_score'
        ]
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'evaluations_comprehensiveevaluation'
            ORDER BY ordinal_position
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        print("\n📊 ComprehensiveEvaluation 스키마 검증:")
        print(f"총 {len(existing_columns)}개 컬럼 존재\n")
        
        missing = []
        for col in comprehensive_required:
            if col in existing_columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ❌ {col} - 누락됨")
                missing.append(col)
        
        if missing:
            print(f"\n⚠️ 누락된 컬럼: {', '.join(missing)}")
        else:
            print("\n✅ 모든 필수 컬럼 존재")
            
        # 현재 존재하는 모든 컬럼 표시
        print("\n📋 현재 테이블 구조:")
        for col in existing_columns:
            required_mark = "✓" if col in comprehensive_required else " "
            print(f"  [{required_mark}] {col}")

if __name__ == "__main__":
    print("="*60)
    print("Railway ComprehensiveEvaluation 테이블 컬럼 수정")
    print("="*60)
    
    try:
        # 1. 누락된 컬럼 추가
        add_missing_comprehensive_columns()
        
        # 2. 스키마 검증
        print("\n" + "="*60)
        print("스키마 검증")
        print("="*60)
        verify_comprehensive_schema()
        
        print("\n✅ 모든 작업 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()