#!/usr/bin/env python
"""
Railway PostgreSQL 직접 연결하여 Employee 데이터 업로드
Django 모델 우회하여 직접 SQL 사용
"""

import json
import psycopg2
from urllib.parse import urlparse
from datetime import datetime, date
import os

def get_db_config():
    """Railway DATABASE_URL에서 연결 정보 추출"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Railway CLI 환경에서 자동으로 설정됨
        print("[ERROR] DATABASE_URL 환경변수가 필요합니다.")
        print("Railway 환경에서 실행하거나 DATABASE_URL을 설정해주세요.")
        return None
    
    parsed = urlparse(database_url)
    return {
        'host': parsed.hostname,
        'port': parsed.port,
        'database': parsed.path[1:],  # 첫 번째 '/' 제거
        'user': parsed.username,
        'password': parsed.password
    }

def connect_database():
    """PostgreSQL 연결"""
    db_config = get_db_config()
    if not db_config:
        return None
    
    try:
        conn = psycopg2.connect(**db_config)
        print("[OK] Railway PostgreSQL 연결 성공")
        return conn
    except Exception as e:
        print(f"[ERROR] 데이터베이스 연결 실패: {e}")
        return None

def check_table_schema(conn):
    """employees_employee 테이블 스키마 확인"""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        if not columns:
            print("[ERROR] employees_employee 테이블이 존재하지 않습니다.")
            return None
        
        print(f"[INFO] 테이블 스키마 확인: {len(columns)}개 컬럼")
        schema = {}
        for col_name, data_type, nullable in columns:
            schema[col_name] = {'type': data_type, 'nullable': nullable == 'YES'}
            
        return schema

def prepare_employee_data(employee_data, schema):
    """Employee 데이터를 PostgreSQL INSERT용으로 변환"""
    prepared = {}
    
    # 기본 필드 매핑
    field_mapping = {
        'name': 'name',
        'email': 'email',
        'phone': 'phone',
        'no': 'no',
        'company': 'company',
        'headquarters1': 'headquarters1',
        'department1': 'department',  # department1 -> department 매핑
        'final_department': 'final_department',
        'current_position': 'current_position',
        'initial_position': 'initial_position',
        'salary_grade': 'salary_grade',
        'promotion_level': 'promotion_level',
        'gender': 'gender',
        'age': 'age',
        'birth_date': 'birth_date',
        'education': 'education',
        'marital_status': 'marital_status',
        'hire_date': 'hire_date',
        'group_join_date': 'group_join_date',
        'career_join_date': 'career_join_date',
        'new_join_date': 'new_join_date',
        'promotion_accumulated_years': 'promotion_accumulated_years',
        'final_evaluation': 'final_evaluation',
        'job_tag_name': 'job_tag_name',
        'rank_tag_name': 'rank_tag_name',
        'job_family': 'job_family',
        'job_field': 'job_field',
        'dummy_mobile': 'dummy_mobile',
        'dummy_email': 'dummy_email',
        'dummy_name': 'dummy_name',
        'dummy_registered_address': 'dummy_registered_address',
        'dummy_residence_address': 'dummy_residence_address',
    }
    
    # 필수 필드 기본값 설정 (NOT NULL 제약조건 해결)
    required_defaults = {
        'department': 'IT',  # department 필드 기본값
        'position': 'STAFF',  # position 필드 기본값
        'address': '',  # 주소 필드 기본값 (빈 문자열)
        'emergency_contact': '',  # 비상연락처 기본값
        'emergency_phone': '',  # 비상연락처 번호 기본값
        'job_group': 'Non-PL',  # 직군 기본값
        'job_type': '경영관리',  # 직종 기본값
        'growth_level': 1,  # 성장레벨 기본값
        'new_position': '사원',  # 신직책 기본값
        'grade_level': 1,  # 급호 기본값
        'employment_type': '정규직',  # 입사구분 기본값
        'employment_status': '재직',  # 재직상태 기본값
        'job_role': '',  # 구체적 직무 기본값
    }
    
    # 스키마에 존재하는 필드만 처리
    for json_field, db_field in field_mapping.items():
        if db_field in schema and json_field in employee_data:
            value = employee_data[json_field]
            
            # 날짜 필드 처리
            if schema[db_field]['type'] == 'date':
                if isinstance(value, str) and value:
                    try:
                        prepared[db_field] = datetime.strptime(value, '%Y-%m-%d').date()
                    except:
                        prepared[db_field] = None
                else:
                    prepared[db_field] = None
            
            # NULL 처리
            elif value is None or value == '':
                prepared[db_field] = None
            else:
                prepared[db_field] = value
    
    # 필수 Django 필드
    prepared['created_at'] = datetime.now()
    prepared['updated_at'] = datetime.now()
    
    # 필수 필드 기본값 설정
    for field_name, default_value in required_defaults.items():
        if field_name in schema and field_name not in prepared:
            prepared[field_name] = default_value
    
    return prepared

def insert_employee_data(conn, employees_data):
    """Employee 데이터 일괄 삽입"""
    schema = check_table_schema(conn)
    if not schema:
        return False
    
    success_count = 0
    error_count = 0
    
    print(f"[INFO] {len(employees_data)}명 직원 데이터 업로드 시작...")
    
    with conn.cursor() as cursor:
        for i, emp_data in enumerate(employees_data):
            try:
                # 중복 확인
                email = emp_data.get('email', '')
                if email:
                    cursor.execute("SELECT id FROM employees_employee WHERE email = %s", (email,))
                    if cursor.fetchone():
                        print(f"[SKIP] 중복 이메일: {emp_data.get('name', 'Unknown')} ({email})")
                        continue
                
                # 데이터 준비
                prepared_data = prepare_employee_data(emp_data, schema)
                
                # INSERT 쿼리 동적 생성
                columns = list(prepared_data.keys())
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                
                insert_query = f"""
                    INSERT INTO employees_employee ({column_names})
                    VALUES ({placeholders})
                """
                
                values = list(prepared_data.values())
                cursor.execute(insert_query, values)
                
                success_count += 1
                
                if (i + 1) % 10 == 0:
                    print(f"[PROGRESS] {i + 1}명 처리 완료...")
                
            except Exception as e:
                error_count += 1
                print(f"[ERROR] 데이터 삽입 실패 [{i+1}]: {emp_data.get('name', 'Unknown')} - {e}")
                continue
        
        # 커밋
        try:
            conn.commit()
            print(f"\n[SUCCESS] 업로드 완료!")
            print(f"  성공: {success_count}명")
            print(f"  실패: {error_count}명")
            return success_count > 0
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] 트랜잭션 커밋 실패: {e}")
            return False

def verify_upload(conn):
    """업로드 결과 검증"""
    with conn.cursor() as cursor:
        # 총 레코드 수
        cursor.execute("SELECT COUNT(*) FROM employees_employee")
        total_count = cursor.fetchone()[0]
        
        # 회사별 통계
        cursor.execute("""
            SELECT company, COUNT(*) 
            FROM employees_employee 
            WHERE company IS NOT NULL 
            GROUP BY company 
            ORDER BY COUNT(*) DESC
        """)
        company_stats = cursor.fetchall()
        
        print(f"\n[VERIFICATION] 업로드 결과:")
        print(f"  총 직원 수: {total_count}명")
        print(f"  회사별 분포:")
        for company, count in company_stats:
            print(f"    - {company}: {count}명")
        
        return total_count

def main():
    print("=" * 60)
    print("Railway Employee 데이터 직접 업로드")
    print("=" * 60)
    
    # JSON 파일 찾기
    import glob
    json_files = glob.glob('employee_dataset_*.json')
    
    if not json_files:
        print("[ERROR] employee_dataset_*.json 파일을 찾을 수 없습니다.")
        print("먼저 generate_employee_dataset.py를 실행하세요.")
        return
    
    # 가장 최근 파일 사용
    json_file = max(json_files, key=os.path.getmtime)
    print(f"[INFO] 사용할 파일: {json_file}")
    
    # JSON 데이터 로드
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            employees_data = json.load(f)
        print(f"[INFO] {len(employees_data)}개 레코드 로드")
    except Exception as e:
        print(f"[ERROR] JSON 파일 로드 실패: {e}")
        return
    
    # 데이터베이스 연결 및 업로드
    conn = connect_database()
    if not conn:
        return
    
    try:
        # 데이터 삽입
        success = insert_employee_data(conn, employees_data)
        
        if success:
            # 결과 검증
            verify_upload(conn)
            print(f"\n[SUCCESS] Railway 업로드 완료!")
            print(f"확인: https://ehrv10-production.up.railway.app/employees/")
        else:
            print("\n[FAILED] 업로드 실패")
    
    except Exception as e:
        print(f"[ERROR] 업로드 프로세스 오류: {e}")
    finally:
        conn.close()
        print("[INFO] 데이터베이스 연결 종료")

if __name__ == "__main__":
    main()