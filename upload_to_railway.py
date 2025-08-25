#!/usr/bin/env python
"""
Railway 프로덕션 환경에 조직구조 CSV 파일 업로드 스크립트
"""

import os
import sys
import django
import pandas as pd

# Railway 환경 변수 설정
os.environ['RAILWAY_ENVIRONMENT'] = 'production'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings_railway')

print("=" * 60)
print("Railway 프로덕션 환경 조직구조 업로드")
print("=" * 60)

try:
    django.setup()
    print("[OK] Django 초기화 (Railway PostgreSQL)")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from employees.models_organization import OrganizationStructure
from django.db import connection

def check_database():
    """데이터베이스 연결 확인"""
    print("\n데이터베이스 연결 확인...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user, version()")
        db_info = cursor.fetchone()
        print(f"  데이터베이스: {db_info[0]}")
        print(f"  사용자: {db_info[1]}")
        print(f"  PostgreSQL 버전: {db_info[2][:30]}...")
        
        # 테이블 확인
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'employees_organizationstructure'
        """)
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print(f"  [OK] OrganizationStructure 테이블 존재")
        else:
            print(f"  [WARNING] OrganizationStructure 테이블 없음 - 생성 필요")

def upload_csv():
    """CSV 파일 업로드"""
    
    # 데이터베이스 확인
    check_database()
    
    # CSV 파일 읽기
    print("\nCSV 파일 읽기...")
    try:
        # cp949 인코딩으로 읽기
        df = pd.read_csv('조직구조_업로드_최종.csv', encoding='cp949')
        print(f"[OK] CSV 파일 읽기 성공: {len(df)}개 행")
    except Exception as e:
        print(f"[ERROR] CSV 파일 읽기 실패: {e}")
        return
    
    # 컬럼 매핑
    column_mapping = {
        'A': '조직코드',
        'B': '조직명',
        'C': '조직레벨',
        'D': '상위조직코드',
        'E': '조직장',
        'F': '상태',
        'G': '정렬순서',
        'H': '설명'
    }
    
    df = df.rename(columns=column_mapping)
    print(f"[OK] 컬럼 매핑 완료")
    
    # 기존 데이터 개수 확인
    existing_count = OrganizationStructure.objects.count()
    if existing_count > 0:
        confirm = input(f"\n[주의] 기존 데이터 {existing_count}개가 있습니다. 모두 삭제하시겠습니까? (yes/no): ")
        if confirm.lower() == 'yes':
            print("기존 데이터 삭제 중...")
            OrganizationStructure.objects.all().delete()
            print("[OK] 기존 데이터 삭제 완료")
        else:
            print("업로드 취소")
            return
    
    # 데이터 업로드
    print("\n데이터 업로드 시작...")
    created_count = 0
    errors = []
    
    # 먼저 parent 없이 모든 조직 생성
    for idx, row in df.iterrows():
        try:
            org_code = row['조직코드']
            org_name = row['조직명']
            org_level = int(row['조직레벨'])
            
            org = OrganizationStructure.objects.create(
                org_code=org_code,
                org_name=org_name,
                org_level=org_level,
                status=row['상태'] if pd.notna(row['상태']) else 'active',
                sort_order=int(row['정렬순서']) if pd.notna(row['정렬순서']) else 0,
                description=row['설명'] if pd.notna(row['설명']) else ''
            )
            created_count += 1
            print(f"  [{created_count}] {org_code}: {org_name} (레벨 {org_level})")
            
        except Exception as e:
            errors.append(f"행 {idx+1}: {e}")
            print(f"  [ERROR] {org_code}: {e}")
    
    # 상위 조직 설정
    print("\n상위 조직 매핑...")
    mapped_count = 0
    for idx, row in df.iterrows():
        if pd.notna(row['상위조직코드']):
            try:
                org = OrganizationStructure.objects.get(org_code=row['조직코드'])
                parent = OrganizationStructure.objects.get(org_code=row['상위조직코드'])
                org.parent = parent
                org.save()
                mapped_count += 1
                print(f"  [{mapped_count}] {org.org_code} -> {parent.org_code}")
            except Exception as e:
                print(f"  [WARNING] {row['조직코드']} 상위 설정 실패: {e}")
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("Railway 프로덕션 업로드 완료!")
    print(f"생성된 조직: {created_count}개")
    print(f"상위조직 매핑: {mapped_count}개")
    if errors:
        print(f"오류: {len(errors)}개")
        for error in errors[:5]:
            print(f"  - {error}")
    
    # 계층별 통계
    print("\n계층별 통계:")
    for level in range(1, 6):
        count = OrganizationStructure.objects.filter(org_level=level).count()
        level_names = {1: '그룹', 2: '계열사', 3: '본부', 4: '부서', 5: '팀'}
        print(f"  레벨 {level} ({level_names[level]}): {count}개")
    
    # 최종 검증
    total_in_db = OrganizationStructure.objects.count()
    print(f"\n최종 데이터베이스 조직 수: {total_in_db}개")
    
    print("=" * 60)
    print("Railway 프로덕션 환경 업로드 성공!")
    print("https://ehrv10-production.up.railway.app/employees/organization/structure/")
    print("=" * 60)

if __name__ == "__main__":
    upload_csv()
