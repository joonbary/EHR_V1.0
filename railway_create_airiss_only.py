#!/usr/bin/env python
"""
Railway AIRISS 데이터만 생성
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
from airiss.models import AIAnalysisResult, AIAnalysisType
from employees.models_talent import TalentCategory, TalentPool

print("="*60)
print("Railway AIRISS 데이터 생성")
print("="*60)

def create_airiss_data():
    """AIRISS 데이터 생성"""
    print("\n1. AIRISS 분석 결과 생성")
    print("-" * 40)
    
    # 분석 타입 생성 또는 가져오기
    try:
        analysis_type = AIAnalysisType.objects.filter(type_code='RAILWAY_TEST').first()
        if not analysis_type:
            analysis_type = AIAnalysisType.objects.create(
                name='Railway AI 분석',
                type_code='RAILWAY_TEST',
                description='Railway 테스트 AI 분석',
                is_active=True
            )
            print(f"  [OK] AIAnalysisType 생성: {analysis_type.name}")
    except Exception as e:
        print(f"  [ERROR] AIAnalysisType 생성 실패: {e}")
        # 기존 타입 사용
        analysis_type = AIAnalysisType.objects.first()
        if not analysis_type:
            return 0
    
    # Employee 데이터 직접 조회
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, no, name FROM employees_employee LIMIT 10")
        employees = cursor.fetchall()
        
        if not employees:
            print("  [WARNING] Employee가 없습니다.")
            return 0
        
        created_count = 0
        for emp_id, emp_no, emp_name in employees:
            try:
                score = random.uniform(70, 95)
                
                # JSON 데이터를 제대로 생성
                result_data = json.dumps({
                    'performance_score': score,
                    'potential_score': score * 0.9,
                    'strengths': ['리더십', '전문성', '협업'],
                    'development_areas': ['전략적 사고', '의사결정']
                })
                
                # AIAnalysisResult 생성
                result, created = AIAnalysisResult.objects.update_or_create(
                    employee_id=emp_id,
                    analysis_type=analysis_type,
                    defaults={
                        'score': score,
                        'confidence': 0.85,
                        'result_data': result_data,
                        'recommendations': f'{emp_name} AI 분석 결과',
                        'analyzed_at': datetime.now(),
                        'valid_until': datetime.now() + timedelta(days=180)
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"  [OK] {emp_name} AIRISS 결과 생성 (점수: {score:.1f})")
                else:
                    print(f"  [UPDATE] {emp_name} AIRISS 결과 업데이트")
                    
            except Exception as e:
                print(f"  [ERROR] AIRISS 생성 실패: {e}")
        
        return created_count

def create_talent_pool():
    """인재풀 데이터 생성"""
    print("\n2. 인재풀 데이터 생성")
    print("-" * 40)
    
    # 카테고리 확인
    category = TalentCategory.objects.filter(category_code='CORE_TALENT').first()
    if not category:
        print("  [ERROR] 카테고리가 없습니다.")
        return 0
    
    # AIAnalysisResult 조회
    results = AIAnalysisResult.objects.select_related('employee').all()[:10]
    
    if not results:
        print("  [WARNING] AIAnalysisResult가 없습니다.")
        return 0
    
    created_count = 0
    for result in results:
        try:
            # 카테고리 결정
            if result.score >= 85:
                category_code = 'CORE_TALENT'
            elif result.score >= 75:
                category_code = 'HIGH_POTENTIAL'
            else:
                category_code = 'SPECIALIST'
            
            category = TalentCategory.objects.filter(category_code=category_code).first()
            if not category:
                category = TalentCategory.objects.filter(category_code='CORE_TALENT').first()
            
            # TalentPool 생성
            talent, created = TalentPool.objects.update_or_create(
                employee=result.employee,
                defaults={
                    'category': category,
                    'ai_analysis_result_id': result.id,
                    'ai_score': float(result.score),
                    'confidence_level': float(result.confidence),
                    'strengths': ['리더십', '전문성'],
                    'development_areas': ['전략적 사고'],
                    'status': 'ACTIVE',
                    'added_at': result.analyzed_at,
                    'updated_at': datetime.now()
                }
            )
            
            if created:
                created_count += 1
                print(f"  [OK] {result.employee.name} 인재풀 등록 ({category.name})")
            else:
                print(f"  [UPDATE] {result.employee.name} 인재풀 업데이트")
                
        except Exception as e:
            print(f"  [ERROR] 인재풀 생성 실패: {e}")
    
    return created_count

def verify_data():
    """데이터 검증"""
    print("\n3. 데이터 검증")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # Employee 수
        cursor.execute("SELECT COUNT(*) FROM employees_employee")
        emp_count = cursor.fetchone()[0]
        print(f"Employee: {emp_count}명")
        
        # AIAnalysisResult 수
        cursor.execute("SELECT COUNT(*) FROM airiss_aianalysisresult")
        airiss_count = cursor.fetchone()[0]
        print(f"AIAnalysisResult: {airiss_count}개")
        
        # TalentPool 수
        cursor.execute("SELECT COUNT(*) FROM employees_talentpool")
        talent_count = cursor.fetchone()[0]
        print(f"TalentPool: {talent_count}명")
        
        # 샘플 인재풀 데이터
        if talent_count > 0:
            cursor.execute("""
                SELECT e.name, tp.ai_score, tc.name
                FROM employees_talentpool tp
                JOIN employees_employee e ON tp.employee_id = e.id
                JOIN employees_talentcategory tc ON tp.category_id = tc.id
                LIMIT 5
            """)
            talents = cursor.fetchall()
            print("\n샘플 인재풀:")
            for talent in talents:
                print(f"  - {talent[0]}: {talent[1]:.1f}점 ({talent[2]})")

def main():
    """메인 실행"""
    print("\n시작: Railway AIRISS 데이터 생성\n")
    
    # 1. AIRISS 데이터 생성
    airiss_count = create_airiss_data()
    
    # 2. 인재풀 생성
    if airiss_count > 0:
        talent_count = create_talent_pool()
    
    # 3. 검증
    verify_data()
    
    print("\n" + "="*60)
    print("[SUCCESS] Railway AIRISS 데이터 생성 완료!")
    print("="*60)
    print("\n확인 URL:")
    print("- 인재 관리: https://ehrv10-production.up.railway.app/ai-insights/")
    print("- 관리자: https://ehrv10-production.up.railway.app/admin/")

if __name__ == "__main__":
    main()