#!/usr/bin/env python
"""
AIRISS AIAnalysisResult 데이터를 인재 관리 테이블로 동기화
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("AIRISS → 인재관리 데이터 동기화")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection, transaction
from airiss.models import AIAnalysisResult
from employees.models import Employee
from employees.models_talent import TalentCategory, TalentPool, PromotionCandidate, RetentionRisk


def check_airiss_data():
    """AIRISS 데이터 확인"""
    print("1. AIRISS 데이터 확인")
    print("-" * 40)
    
    try:
        # AIAnalysisResult 데이터 확인
        total_results = AIAnalysisResult.objects.count()
        print(f"총 AIAnalysisResult: {total_results}개")
        
        if total_results > 0:
            # 분석 타입별 통계
            from django.db.models import Count
            type_stats = AIAnalysisResult.objects.values('analysis_type__name').annotate(count=Count('id'))
            print("\n분석 타입별 통계:")
            for stat in type_stats:
                print(f"  - {stat['analysis_type__name'] or 'Unknown'}: {stat['count']}개")
            
            # 최근 분석 결과 샘플
            recent = AIAnalysisResult.objects.order_by('-analyzed_at').first()
            if recent:
                print(f"\n최근 분석:")
                print(f"  - ID: {recent.id}")
                print(f"  - 직원: {recent.employee.name if recent.employee else 'N/A'}")
                print(f"  - 타입: {recent.analysis_type.name if recent.analysis_type else 'N/A'}")
                print(f"  - 날짜: {recent.analyzed_at}")
                
                # result_data 내용 확인
                if recent.result_data:
                    print(f"  - 결과 데이터 키: {list(recent.result_data.keys())[:5]}")
        
        return total_results
        
    except Exception as e:
        print(f"[ERROR] AIRISS 데이터 확인 실패: {e}")
        return 0


def sync_talent_pool():
    """AIAnalysisResult를 TalentPool로 동기화"""
    print("\n2. 인재풀 동기화")
    print("-" * 40)
    
    try:
        # 카테고리 확인
        categories = {
            'CORE_TALENT': TalentCategory.objects.filter(category_code='CORE_TALENT').first(),
            'HIGH_POTENTIAL': TalentCategory.objects.filter(category_code='HIGH_POTENTIAL').first(),
            'NEEDS_ATTENTION': TalentCategory.objects.filter(category_code='NEEDS_ATTENTION').first(),
            'SPECIALIST': TalentCategory.objects.filter(category_code='SPECIALIST').first(),
        }
        
        # 기본 카테고리 생성 (없는 경우)
        if not categories['CORE_TALENT']:
            categories['CORE_TALENT'] = TalentCategory.objects.create(
                category_code='CORE_TALENT',
                name='핵심인재',
                description='조직의 핵심 성과를 이끄는 인재'
            )
            print("[OK] 핵심인재 카테고리 생성")
        
        # AIAnalysisResult 조회 (최근 100개)
        results = AIAnalysisResult.objects.select_related('employee', 'analysis_type').order_by('-analyzed_at')[:100]
        
        created_count = 0
        updated_count = 0
        
        for result in results:
            if not result.employee:
                continue
            
            # AI 점수 계산 (result_data에서 추출)
            ai_score = 75.0  # 기본값
            confidence = 0.8  # 기본값
            
            if result.result_data:
                # 다양한 키에서 점수 추출 시도
                if 'score' in result.result_data:
                    ai_score = float(result.result_data.get('score', 75))
                elif 'ai_score' in result.result_data:
                    ai_score = float(result.result_data.get('ai_score', 75))
                elif 'overall_score' in result.result_data:
                    ai_score = float(result.result_data.get('overall_score', 75))
                elif 'performance_score' in result.result_data:
                    ai_score = float(result.result_data.get('performance_score', 75))
                
                if 'confidence' in result.result_data:
                    confidence = float(result.result_data.get('confidence', 0.8))
                elif 'confidence_level' in result.result_data:
                    confidence = float(result.result_data.get('confidence_level', 0.8))
            
            # 카테고리 결정 (점수 기반)
            if ai_score >= 85:
                category = categories['CORE_TALENT']
            elif ai_score >= 75:
                category = categories['HIGH_POTENTIAL']
            elif ai_score >= 60:
                category = categories['SPECIALIST']
            else:
                category = categories['NEEDS_ATTENTION']
            
            # TalentPool 생성 또는 업데이트
            talent_pool, created = TalentPool.objects.update_or_create(
                employee=result.employee,
                defaults={
                    'category': category,
                    'ai_analysis_result_id': result.id,
                    'ai_score': ai_score,
                    'confidence_level': confidence,
                    'strengths': result.result_data.get('strengths', []) if result.result_data else [],
                    'development_areas': result.result_data.get('development_areas', []) if result.result_data else [],
                    'recommendations': result.result_data.get('recommendations', []) if result.result_data else [],
                    'status': 'ACTIVE',
                    'added_at': result.analyzed_at,
                    'updated_at': datetime.now()
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        print(f"[OK] 인재풀 동기화 완료: {created_count}개 생성, {updated_count}개 업데이트")
        
        return created_count + updated_count
        
    except Exception as e:
        print(f"[ERROR] 인재풀 동기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return 0


def sync_promotion_candidates():
    """승진 후보자 데이터 동기화"""
    print("\n3. 승진 후보자 동기화")
    print("-" * 40)
    
    try:
        # 고성과자 선별 (AI 점수 80점 이상)
        high_performers = TalentPool.objects.filter(
            ai_score__gte=80,
            status='ACTIVE'
        ).select_related('employee')[:20]
        
        created_count = 0
        
        for tp in high_performers:
            if not tp.employee:
                continue
            
            # 현재 직급 확인
            current_position = tp.employee.position or '사원'
            
            # 목표 직급 설정 (간단한 매핑)
            position_map = {
                '사원': '대리',
                '대리': '과장',
                '과장': '차장',
                '차장': '부장',
                '부장': '이사',
                '팀장': '본부장',
            }
            target_position = position_map.get(current_position, '차상위직급')
            
            # 승진 후보자 생성
            candidate, created = PromotionCandidate.objects.update_or_create(
                employee=tp.employee,
                defaults={
                    'current_position': current_position,
                    'target_position': target_position,
                    'readiness_level': 'READY' if tp.ai_score >= 85 else 'DEVELOPING',
                    'performance_score': tp.ai_score,
                    'potential_score': tp.ai_score * 0.9,  # 잠재력 점수는 성과의 90%
                    'ai_recommendation_score': tp.ai_score,
                    'expected_promotion_date': datetime.now().date() + timedelta(days=180),
                    'development_plan': {
                        'summary': '리더십 및 전문성 개발 프로그램',
                        'programs': ['리더십 교육', 'MBA 과정', '멘토링']
                    },
                    'recommendation_reason': f'AI 평가 점수 {tp.ai_score:.1f}점으로 우수 성과 달성',
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
        
        print(f"[OK] 승진 후보자 {created_count}명 생성")
        return created_count
        
    except Exception as e:
        print(f"[ERROR] 승진 후보자 동기화 실패: {e}")
        return 0


def sync_retention_risks():
    """이직 위험군 데이터 동기화"""
    print("\n4. 이직 위험군 동기화")
    print("-" * 40)
    
    try:
        # 저성과자 또는 관리필요 인력 선별
        at_risk = TalentPool.objects.filter(
            ai_score__lt=70,
            status='ACTIVE'
        ).select_related('employee')[:15]
        
        created_count = 0
        
        for tp in at_risk:
            if not tp.employee:
                continue
            
            # 위험도 계산
            if tp.ai_score < 50:
                risk_level = 'CRITICAL'
                risk_score = 90
            elif tp.ai_score < 60:
                risk_level = 'HIGH'
                risk_score = 75
            else:
                risk_level = 'MEDIUM'
                risk_score = 60
            
            # 이직 위험 생성
            risk, created = RetentionRisk.objects.update_or_create(
                employee=tp.employee,
                defaults={
                    'risk_level': risk_level,
                    'risk_score': risk_score,
                    'risk_factors': ['성과 부진', '경력 정체', '보상 불만족'],
                    'retention_strategy': '개인 면담 및 경력 개발 계획 수립, 보상 체계 재검토',
                    'action_items': [
                        '1:1 면담 실시',
                        '경력 개발 계획 수립',
                        '멘토링 프로그램 연결',
                        '보상 수준 재검토'
                    ],
                    'action_status': 'PENDING',
                    'next_review_date': datetime.now().date() + timedelta(days=30)
                }
            )
            
            if created:
                created_count += 1
        
        print(f"[OK] 이직 위험군 {created_count}명 생성")
        return created_count
        
    except Exception as e:
        print(f"[ERROR] 이직 위험군 동기화 실패: {e}")
        return 0


def verify_sync():
    """동기화 결과 검증"""
    print("\n5. 동기화 결과 검증")
    print("-" * 40)
    
    try:
        talent_count = TalentPool.objects.count()
        promotion_count = PromotionCandidate.objects.filter(is_active=True).count()
        retention_count = RetentionRisk.objects.count()
        
        print(f"인재풀: {talent_count}명")
        print(f"승진 후보자: {promotion_count}명")
        print(f"이직 위험군: {retention_count}명")
        
        # 카테고리별 통계
        from django.db.models import Count
        category_stats = TalentPool.objects.values('category__name').annotate(count=Count('id'))
        
        if category_stats:
            print("\n카테고리별 인재풀:")
            for stat in category_stats:
                print(f"  - {stat['category__name'] or 'Unknown'}: {stat['count']}명")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 검증 실패: {e}")
        return False


def main():
    """메인 실행"""
    
    print("\n시작: AIRISS → 인재관리 동기화\n")
    
    # 1. AIRISS 데이터 확인
    airiss_count = check_airiss_data()
    
    if airiss_count == 0:
        print("\n[WARNING] AIRISS 데이터가 없습니다.")
        print("먼저 AIRISS 분석을 실행해주세요.")
        return
    
    # 2. 인재풀 동기화
    with transaction.atomic():
        talent_count = sync_talent_pool()
        
        # 3. 승진 후보자 동기화
        promotion_count = sync_promotion_candidates()
        
        # 4. 이직 위험군 동기화
        retention_count = sync_retention_risks()
    
    # 5. 검증
    verify_sync()
    
    print("\n" + "="*60)
    print("[SUCCESS] AIRISS → 인재관리 동기화 완료!")
    print("="*60)
    print("\n다음 URL에서 확인 가능:")
    print("- 로컬: http://localhost:8000/ai-insights/")
    print("- Railway: https://ehrv10-production.up.railway.app/ai-insights/")


if __name__ == "__main__":
    main()