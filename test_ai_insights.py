#!/usr/bin/env python
"""
AI Insights 기능 테스트 스크립트
"""
import os
import sys
import django
from datetime import date, timedelta

# Django 설정
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from ai_insights.models import AIInsight, DailyMetrics, ActionItem
from ai_insights.services import AIInsightGenerator

def create_test_data():
    """테스트 데이터 생성"""
    print("AI Insights 테스트 데이터 생성 중...")
    
    # 1. 일일 메트릭 생성
    today = date.today()
    for i in range(7):  # 최근 7일
        test_date = today - timedelta(days=i)
        DailyMetrics.objects.get_or_create(
            date=test_date,
            defaults={
                'total_employees': 150 + i,
                'new_hires': 2 if i < 3 else 0,
                'resignations': 1 if i == 1 else 0,
                'avg_performance_score': 3.5 + (i * 0.1),
                'high_performers_count': 15 + i,
                'low_performers_count': 5 - (i // 2),
                'avg_engagement_score': 4.0 + (i * 0.05),
                'burnout_risk_count': 8 - i,
                'avg_compensation': 50000 + (i * 1000),
                'compensation_budget_used': 75.5 + i,
                'ai_summary': f"{test_date} 메트릭 요약",
                'ai_predictions': {
                    'trend': 'stable' if i % 2 == 0 else 'improving',
                    'risk_level': 'low'
                }
            }
        )
    
    # 2. AI 인사이트 생성
    insights_data = [
        {
            'title': '[위험] 팀 A 이직 위험도 증가',
            'description': '팀 A에서 최근 업무량 증가와 스트레스 지표 상승이 감지되었습니다. 조기 개입이 필요합니다.',
            'category': 'TURNOVER',
            'priority': 'HIGH',
            'affected_department': '개발팀 A',
            'ai_confidence': 0.85,
            'ai_model_used': 'test-model',
            'recommended_actions': [
                '팀 미팅을 통한 업무 분담 조정',
                '스트레스 관리 프로그램 제공',
                'work-life balance 개선 방안 검토'
            ]
        },
        {
            'title': '[성과] 성과 우수 직원 동기부여 방안',
            'description': '고성과자들의 동기부여를 위한 맞춤형 인센티브 제도 도입을 권장합니다.',
            'category': 'PERFORMANCE',
            'priority': 'MEDIUM',
            'affected_department': '전체',
            'ai_confidence': 0.78,
            'ai_model_used': 'test-model',
            'recommended_actions': [
                '성과급 재검토',
                '경력 개발 기회 제공',
                '리더십 교육 참여 기회'
            ]
        },
        {
            'title': '[긴급] IT팀 번아웃 위험 감지',
            'description': 'IT팀의 야근 시간이 평균 대비 40% 증가하여 번아웃 위험이 높습니다.',
            'category': 'ENGAGEMENT',
            'priority': 'URGENT',
            'affected_department': 'IT팀',
            'ai_confidence': 0.92,
            'ai_model_used': 'test-model',
            'recommended_actions': [
                '업무량 재분배 즉시 실행',
                '추가 인력 충원 검토',
                '휴가 사용 독려'
            ]
        }
    ]
    
    for insight_data in insights_data:
        insight = AIInsight.objects.create(**insight_data)
        
        # 각 인사이트에 대한 액션 아이템 생성
        for i, action in enumerate(insight_data['recommended_actions']):
            ActionItem.objects.create(
                insight=insight,
                title=action,
                description=f"{action}에 대한 구체적인 실행 계획을 수립해야 합니다.",
                priority=insight.priority,
                expected_impact="팀 성과 및 만족도 개선 예상",
                ai_confidence=insight.ai_confidence,
                due_date=date.today() + timedelta(days=7)
            )
    
    print(f"테스트 데이터 생성 완료:")
    print(f"   - 일일 메트릭: {DailyMetrics.objects.count()}개")
    print(f"   - AI 인사이트: {AIInsight.objects.count()}개")
    print(f"   - 액션 아이템: {ActionItem.objects.count()}개")

def test_ai_service():
    """AI 서비스 테스트"""
    print("\nAI 서비스 기능 테스트 중...")
    
    try:
        ai_generator = AIInsightGenerator()
        
        # 기본 HR 데이터 수집 테스트
        hr_data = ai_generator._collect_hr_metrics()
        print(f"HR 데이터 수집 성공: {len(hr_data)}개 지표")
        
        # 인사이트 생성 테스트 (폴백 모드)
        insights = ai_generator.generate_daily_insights()
        print(f"인사이트 생성 성공: {len(insights)}개")
        
        # 액션 아이템 조회 테스트
        actions = ai_generator.get_action_items()
        print(f"액션 아이템 조회 성공: {len(actions)}개")
        
        # 예측 분석 테스트
        predictions = ai_generator.predict_trends()
        print(f"예측 분석 성공: {len(predictions)}개 카테고리")
        
    except Exception as e:
        print(f"AI 서비스 테스트 실패: {e}")

def main():
    """메인 실행 함수"""
    print("AIRISS AI Quick Win - Phase 2 테스트 시작")
    print("=" * 50)
    
    # 기존 테스트 데이터 정리
    print("기존 테스트 데이터 정리 중...")
    AIInsight.objects.all().delete()
    DailyMetrics.objects.all().delete()
    ActionItem.objects.all().delete()
    
    # 테스트 데이터 생성
    create_test_data()
    
    # AI 서비스 테스트
    test_ai_service()
    
    print("\n" + "=" * 50)
    print("Phase 2 테스트 완료!")
    print("대시보드 확인: http://localhost:8000/ai-insights/")
    print("API 테스트:")
    print("   - http://localhost:8000/ai-insights/api/insights/daily/")
    print("   - http://localhost:8000/ai-insights/api/actions/")

if __name__ == "__main__":
    main()