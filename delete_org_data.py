#!/usr/bin/env python
"""
조직구조 데이터 삭제 스크립트
"""

import os
import sys
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

try:
    django.setup()
    print("[OK] Django 초기화")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def show_current_data():
    """현재 조직 데이터 확인"""
    print("\n현재 조직 데이터:")
    print("-" * 50)
    
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT org_code, org_name, org_level, parent_id
                FROM employees_organizationstructure 
                ORDER BY org_level, sort_order, org_code
            """)
            
            rows = cursor.fetchall()
            if rows:
                print(f"{'코드':<10} {'조직명':<20} {'레벨':<5} {'상위ID':<8}")
                print("-" * 50)
                for row in rows:
                    parent_id = row[3] if row[3] else ""
                    print(f"{row[0]:<10} {row[1]:<20} {row[2]:<5} {parent_id:<8}")
                print(f"\n총 {len(rows)}개 조직")
            else:
                print("조직 데이터가 없습니다.")
                
        except Exception as e:
            print(f"데이터 조회 오류: {e}")

def delete_all_org_data():
    """모든 조직 데이터 삭제"""
    print("\n모든 조직 데이터를 삭제합니다...")
    
    with connection.cursor() as cursor:
        try:
            # 1. 매핑 테이블 먼저 삭제 (외래키 제약조건)
            cursor.execute("DELETE FROM employees_employeeorganizationmapping")
            mapping_count = cursor.rowcount
            
            # 2. 업로드 히스토리 삭제
            cursor.execute("DELETE FROM employees_organizationuploadhistory")
            history_count = cursor.rowcount
            
            # 3. 조직구조 데이터 삭제 (하위 → 상위 순서로)
            cursor.execute("""
                DELETE FROM employees_organizationstructure 
                WHERE org_level = 5  -- 팀
            """)
            level5_count = cursor.rowcount
            
            cursor.execute("""
                DELETE FROM employees_organizationstructure 
                WHERE org_level = 4  -- 부서
            """)
            level4_count = cursor.rowcount
            
            cursor.execute("""
                DELETE FROM employees_organizationstructure 
                WHERE org_level = 3  -- 본부
            """)
            level3_count = cursor.rowcount
            
            cursor.execute("""
                DELETE FROM employees_organizationstructure 
                WHERE org_level = 2  -- 계열사
            """)
            level2_count = cursor.rowcount
            
            cursor.execute("""
                DELETE FROM employees_organizationstructure 
                WHERE org_level = 1  -- 그룹
            """)
            level1_count = cursor.rowcount
            
            total_org_count = level1_count + level2_count + level3_count + level4_count + level5_count
            
            print(f"삭제 결과:")
            print(f"  - 조직-직원 매핑: {mapping_count}개")
            print(f"  - 업로드 히스토리: {history_count}개")
            print(f"  - 조직구조 (총 {total_org_count}개):")
            print(f"    * 레벨 5 (팀): {level5_count}개")
            print(f"    * 레벨 4 (부서): {level4_count}개") 
            print(f"    * 레벨 3 (본부): {level3_count}개")
            print(f"    * 레벨 2 (계열사): {level2_count}개")
            print(f"    * 레벨 1 (그룹): {level1_count}개")
            
            print("\n모든 조직 데이터 삭제 완료!")
            
        except Exception as e:
            print(f"삭제 오류: {e}")

def delete_specific_org(org_code):
    """특정 조직 삭제"""
    print(f"\n조직코드 '{org_code}' 삭제 중...")
    
    with connection.cursor() as cursor:
        try:
            # 해당 조직과 하위 조직들 찾기
            cursor.execute("""
                WITH RECURSIVE org_tree AS (
                    SELECT id, org_code, org_name, org_level
                    FROM employees_organizationstructure
                    WHERE org_code = %s
                    
                    UNION ALL
                    
                    SELECT o.id, o.org_code, o.org_name, o.org_level
                    FROM employees_organizationstructure o
                    JOIN org_tree ot ON o.parent_id = ot.id
                )
                SELECT org_code, org_name FROM org_tree ORDER BY org_level DESC
            """, [org_code])
            
            orgs_to_delete = cursor.fetchall()
            
            if not orgs_to_delete:
                print(f"조직코드 '{org_code}'를 찾을 수 없습니다.")
                return
            
            print("다음 조직들이 삭제됩니다:")
            for org in orgs_to_delete:
                print(f"  - {org[0]}: {org[1]}")
            
            # 실제 삭제 (하위부터)
            for org in orgs_to_delete:
                cursor.execute("""
                    DELETE FROM employees_organizationstructure 
                    WHERE org_code = %s
                """, [org[0]])
                print(f"  삭제완료: {org[0]}")
            
            print(f"\n총 {len(orgs_to_delete)}개 조직 삭제 완료!")
            
        except Exception as e:
            print(f"삭제 오류: {e}")

def main():
    """메인 실행"""
    print("=" * 60)
    print("조직구조 데이터 삭제")
    print("=" * 60)
    
    # 현재 데이터 확인
    show_current_data()
    
    print("\n삭제 옵션:")
    print("1. 모든 조직 데이터 삭제")
    print("2. 특정 조직 삭제 (하위 조직 포함)")
    print("3. 취소")
    
    choice = input("\n선택하세요 (1-3): ").strip()
    
    if choice == '1':
        confirm = input("\n정말로 모든 조직 데이터를 삭제하시겠습니까? (yes/no): ").lower()
        if confirm == 'yes':
            delete_all_org_data()
        else:
            print("취소되었습니다.")
            
    elif choice == '2':
        org_code = input("\n삭제할 조직코드를 입력하세요: ").strip().upper()
        if org_code:
            confirm = input(f"'{org_code}' 조직과 모든 하위 조직을 삭제하시겠습니까? (yes/no): ").lower()
            if confirm == 'yes':
                delete_specific_org(org_code)
            else:
                print("취소되었습니다.")
        else:
            print("조직코드가 입력되지 않았습니다.")
            
    else:
        print("취소되었습니다.")
    
    # 삭제 후 현재 데이터 확인
    show_current_data()

if __name__ == "__main__":
    main()