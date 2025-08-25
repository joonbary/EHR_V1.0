#!/usr/bin/env python
"""
Railway 인재풀 동기화 - 스키마 문제 해결 버전
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection
from django.utils import timezone

print("="*60)
print("Railway 인재풀 동기화 (Fixed)")
print("="*60)

def sync_talent_pool_direct():
    """직접 SQL로 인재풀 동기화"""
    print("\n1. 인재풀 데이터 직접 생성")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # AIAnalysisResult와 Employee 조인해서 데이터 가져오기
        cursor.execute("""
            SELECT ar.id, ar.employee_id, ar.score, ar.confidence, e.name
            FROM airiss_aianalysisresult ar
            JOIN employees_employee e ON ar.employee_id = e.id
            ORDER BY ar.score DESC
        """)
        results = cursor.fetchall()
        
        if not results:
            print("  [WARNING] AIAnalysisResult가 없습니다.")
            return 0
        
        created_count = 0
        for result_id, emp_id, score, confidence, emp_name in results:
            try:
                # 카테고리 결정
                if score >= 85:
                    category_code = 'CORE_TALENT'
                elif score >= 75:
                    category_code = 'HIGH_POTENTIAL'
                elif score >= 65:
                    category_code = 'SPECIALIST'
                else:
                    category_code = 'NEEDS_ATTENTION'
                
                # 카테고리 ID 가져오기
                cursor.execute("""
                    SELECT id FROM employees_talentcategory 
                    WHERE category_code = %s
                """, [category_code])
                category_result = cursor.fetchone()
                
                if not category_result:
                    print(f"  [WARNING] 카테고리 {category_code}가 없습니다.")
                    continue
                
                category_id = category_result[0]
                
                # 먼저 기존 데이터 확인
                cursor.execute("""
                    SELECT id FROM employees_talentpool 
                    WHERE employee_id = %s
                """, [emp_id])
                existing = cursor.fetchone()
                
                if existing:
                    # 업데이트
                    cursor.execute("""
                        UPDATE employees_talentpool 
                        SET ai_score = %s, category_id = %s, updated_at = %s
                        WHERE employee_id = %s
                    """, [float(score), category_id, timezone.now(), emp_id])
                    print(f"  [UPDATE] {emp_name} - {category_code} ({score:.1f}점)")
                else:
                    # 새로 삽입
                    cursor.execute("""
                        INSERT INTO employees_talentpool 
                        (employee_id, category_id, ai_analysis_result_id, ai_score, 
                         confidence_level, strengths, development_areas, recommendations,
                         status, added_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                    emp_id,
                    category_id,
                    result_id,
                    float(score),
                    float(confidence),
                    json.dumps(['리더십', '전문성', '협업']),
                    json.dumps(['전략적 사고', '의사결정']),
                    json.dumps([f'{emp_name}님은 {score:.1f}점의 우수한 성과를 보입니다.']),
                    'ACTIVE',
                    timezone.now(),
                    timezone.now()
                    ])
                    created_count += 1
                    print(f"  [OK] {emp_name} - {category_code} ({score:.1f}점)")
                
            except Exception as e:
                print(f"  [ERROR] {emp_name} 인재풀 생성 실패: {e}")
        
        print(f"\n[완료] {created_count}명 인재풀 등록")
        return created_count

def create_promotion_candidates():
    """승진 후보자 생성"""
    print("\n2. 승진 후보자 생성")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 고성과자 선별
        cursor.execute("""
            SELECT tp.employee_id, tp.ai_score, e.name, e.position
            FROM employees_talentpool tp
            JOIN employees_employee e ON tp.employee_id = e.id
            WHERE tp.ai_score >= 80
            ORDER BY tp.ai_score DESC
            LIMIT 5
        """)
        high_performers = cursor.fetchall()
        
        if not high_performers:
            print("  [WARNING] 고성과자가 없습니다.")
            return 0
        
        created_count = 0
        for emp_id, score, emp_name, current_pos in high_performers:
            try:
                # 기존 데이터 확인
                cursor.execute("""
                    SELECT id FROM employees_promotioncandidate
                    WHERE employee_id = %s
                """, [emp_id])
                existing = cursor.fetchone()
                
                if not existing:
                    # 새로 삽입
                    cursor.execute("""
                        INSERT INTO employees_promotioncandidate
                        (employee_id, current_position, target_position, readiness_level,
                         performance_score, potential_score, ai_recommendation_score,
                         expected_promotion_date, development_plan, recommendation_reason,
                         is_active, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                    emp_id,
                    current_pos or 'STAFF',
                    'SENIOR',  # 목표 직급
                    'READY' if score >= 85 else 'DEVELOPING',
                    float(score),
                    float(score * 0.9),
                    float(score),
                    timezone.now().date() + timedelta(days=180),
                    json.dumps({'programs': ['리더십 교육', 'MBA 과정']}),
                    f'AI 평가 {score:.1f}점으로 승진 준비 완료',
                    True,
                    timezone.now(),
                    timezone.now()
                    ])
                    created_count += 1
                    print(f"  [OK] {emp_name} - 승진 후보 등록 ({score:.1f}점)")
                
            except Exception as e:
                print(f"  [ERROR] {emp_name} 승진 후보 생성 실패: {e}")
        
        print(f"\n[완료] {created_count}명 승진 후보 등록")
        return created_count

def create_retention_risks():
    """이직 위험군 생성"""
    print("\n3. 이직 위험군 생성")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 저성과자 선별
        cursor.execute("""
            SELECT tp.employee_id, tp.ai_score, e.name
            FROM employees_talentpool tp
            JOIN employees_employee e ON tp.employee_id = e.id
            WHERE tp.ai_score < 75
            ORDER BY tp.ai_score ASC
            LIMIT 3
        """)
        low_performers = cursor.fetchall()
        
        if not low_performers:
            print("  [WARNING] 저성과자가 없습니다.")
            return 0
        
        created_count = 0
        for emp_id, score, emp_name in low_performers:
            try:
                # 위험도 계산
                if score < 65:
                    risk_level = 'HIGH'
                    risk_score = 85
                else:
                    risk_level = 'MEDIUM'
                    risk_score = 60
                
                # 기존 데이터 확인
                cursor.execute("""
                    SELECT id FROM employees_retentionrisk
                    WHERE employee_id = %s
                """, [emp_id])
                existing = cursor.fetchone()
                
                if not existing:
                    # 새로 삽입
                    cursor.execute("""
                        INSERT INTO employees_retentionrisk
                        (employee_id, risk_level, risk_score, risk_factors,
                         retention_strategy, action_items, action_status,
                         next_review_date, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                    emp_id,
                    risk_level,
                    risk_score,
                    json.dumps(['성과 부진', '동기 저하']),
                    '1:1 면담 및 경력 개발 계획 수립',
                    json.dumps(['면담 실시', '멘토링 연결']),
                    'PENDING',
                    timezone.now().date() + timedelta(days=30),
                    timezone.now(),
                    timezone.now()
                    ])
                    created_count += 1
                    print(f"  [OK] {emp_name} - 이직 위험 {risk_level} ({score:.1f}점)")
                
            except Exception as e:
                print(f"  [ERROR] {emp_name} 이직 위험군 생성 실패: {e}")
        
        print(f"\n[완료] {created_count}명 이직 위험군 등록")
        return created_count

def verify_data():
    """데이터 검증"""
    print("\n4. 최종 데이터 검증")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 카운트 확인
        tables = [
            ('employees_employee', 'Employee'),
            ('airiss_aianalysisresult', 'AIAnalysisResult'),
            ('employees_talentpool', 'TalentPool'),
            ('employees_promotioncandidate', 'PromotionCandidate'),
            ('employees_retentionrisk', 'RetentionRisk')
        ]
        
        for table, name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{name}: {count}개")
        
        # 카테고리별 인재풀 통계
        cursor.execute("""
            SELECT tc.category_code, COUNT(tp.id) as cnt
            FROM employees_talentpool tp
            JOIN employees_talentcategory tc ON tp.category_id = tc.id
            GROUP BY tc.category_code
            ORDER BY cnt DESC
        """)
        categories = cursor.fetchall()
        
        if categories:
            print("\n카테고리별 인재풀:")
            for cat_code, cnt in categories:
                print(f"  - {cat_code}: {cnt}명")
        
        # 샘플 데이터
        cursor.execute("""
            SELECT e.name, tp.ai_score, tc.category_code
            FROM employees_talentpool tp
            JOIN employees_employee e ON tp.employee_id = e.id
            JOIN employees_talentcategory tc ON tp.category_id = tc.id
            ORDER BY tp.ai_score DESC
            LIMIT 3
        """)
        talents = cursor.fetchall()
        
        if talents:
            print("\n상위 인재:")
            for name, score, cat in talents:
                print(f"  - {name}: {score:.1f}점 ({cat})")

def main():
    """메인 실행"""
    print("\n시작: Railway 인재풀 동기화 (Fixed)\n")
    
    # 1. 인재풀 동기화
    talent_count = sync_talent_pool_direct()
    
    if talent_count > 0:
        # 2. 승진 후보자 생성
        promotion_count = create_promotion_candidates()
        
        # 3. 이직 위험군 생성
        retention_count = create_retention_risks()
    
    # 4. 검증
    verify_data()
    
    print("\n" + "="*60)
    print("[SUCCESS] Railway 인재풀 동기화 완료!")
    print("="*60)
    print("\n확인 URL:")
    print("- 인재 관리: https://ehrv10-production.up.railway.app/ai-insights/")
    print("- API: https://ehrv10-production.up.railway.app/employees/api/talent/pool/")

if __name__ == "__main__":
    main()