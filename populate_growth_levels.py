"""
성장레벨 기본 데이터 생성 스크립트
OK금융그룹 성장레벨 체계 구축
"""

import os
import django
import sys

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from evaluations.models import GrowthLevel, GrowthLevelRequirement


def create_growth_levels():
    """성장레벨 기본 데이터 생성"""
    
    # 기존 데이터 삭제
    GrowthLevelRequirement.objects.all().delete()
    GrowthLevel.objects.all().delete()
    
    growth_levels_data = [
        {
            'level': 1,
            'name': '초급',
            'description': '신입 또는 업무 경험 1년 미만의 초급 수준',
            'min_score': 2.0,
            'consecutive_achievements': 2,
            'requirements': [
                {'type': 'SCORE', 'desc': '종합 점수 2.5점 이상', 'value': '2.5'},
                {'type': 'CONSECUTIVE', 'desc': '2회 연속 목표 달성', 'value': '2'},
            ]
        },
        {
            'level': 2,
            'name': '중급',
            'description': '업무 경험 1-3년, 독립적인 업무 수행 가능',
            'min_score': 2.5,
            'consecutive_achievements': 2,
            'requirements': [
                {'type': 'SCORE', 'desc': '종합 점수 3.0점 이상', 'value': '3.0'},
                {'type': 'CONSECUTIVE', 'desc': '2회 연속 목표 달성', 'value': '2'},
                {'type': 'EXPERTISE', 'desc': '전문성 영역 3.0점 이상', 'value': '3.0'},
            ]
        },
        {
            'level': 3,
            'name': '고급',
            'description': '업무 경험 3-5년, 전문 지식과 기술 보유',
            'min_score': 3.0,
            'consecutive_achievements': 3,
            'requirements': [
                {'type': 'SCORE', 'desc': '종합 점수 3.5점 이상', 'value': '3.5'},
                {'type': 'CONSECUTIVE', 'desc': '3회 연속 목표 달성', 'value': '3'},
                {'type': 'CONTRIBUTION', 'desc': '기여도 영역 3.5점 이상', 'value': '3.5'},
                {'type': 'IMPACT', 'desc': '영향력 영역 3.0점 이상', 'value': '3.0'},
            ]
        },
        {
            'level': 4,
            'name': '전문가',
            'description': '업무 경험 5-7년, 해당 분야 전문가 수준',
            'min_score': 3.5,
            'consecutive_achievements': 3,
            'requirements': [
                {'type': 'SCORE', 'desc': '종합 점수 4.0점 이상', 'value': '4.0'},
                {'type': 'CONSECUTIVE', 'desc': '3회 연속 목표 달성', 'value': '3'},
                {'type': 'CONTRIBUTION', 'desc': '기여도 영역 4.0점 이상', 'value': '4.0'},
                {'type': 'EXPERTISE', 'desc': '전문성 영역 4.0점 이상', 'value': '4.0'},
                {'type': 'LEADERSHIP', 'desc': '리더십 발휘 경험', 'value': '1'},
            ]
        },
        {
            'level': 5,
            'name': '선임전문가',
            'description': '업무 경험 7-10년, 조직 내 핵심 인재',
            'min_score': 4.0,
            'consecutive_achievements': 3,
            'requirements': [
                {'type': 'SCORE', 'desc': '종합 점수 4.5점 이상', 'value': '4.5'},
                {'type': 'CONSECUTIVE', 'desc': '3회 연속 목표 달성', 'value': '3'},
                {'type': 'IMPACT', 'desc': '영향력 영역 4.0점 이상', 'value': '4.0'},
                {'type': 'MENTORING', 'desc': '후배 멘토링 경험', 'value': '2'},
                {'type': 'PROJECT_LEAD', 'desc': '프로젝트 리더 경험', 'value': '1'},
            ]
        },
        {
            'level': 6,
            'name': '수석전문가',
            'description': '업무 경험 10년 이상, 조직을 이끄는 핵심 리더',
            'min_score': 4.5,
            'consecutive_achievements': 4,
            'requirements': [
                {'type': 'SCORE', 'desc': '종합 점수 5.0점 이상', 'value': '5.0'},
                {'type': 'CONSECUTIVE', 'desc': '4회 연속 목표 달성', 'value': '4'},
                {'type': 'STRATEGIC', 'desc': '전략적 기여도 인정', 'value': '1'},
                {'type': 'INNOVATION', 'desc': '혁신 사례 창출', 'value': '1'},
                {'type': 'EXTERNAL', 'desc': '외부 네트워킹 활동', 'value': '1'},
            ]
        },
    ]
    
    print("성장레벨 데이터 생성 중...")
    
    for level_data in growth_levels_data:
        # 성장레벨 생성
        growth_level = GrowthLevel.objects.create(
            level=level_data['level'],
            name=level_data['name'],
            description=level_data['description']
        )
        
        print(f"레벨 {level_data['level']} - {level_data['name']} 생성")
        
        # 요구사항 생성
        for req in level_data['requirements']:
            GrowthLevelRequirement.objects.create(
                growth_level=growth_level,
                category=req['type'] if req['type'] in ['TECHNICAL', 'LEADERSHIP', 'BUSINESS', 'COMMUNICATION', 'PROBLEM_SOLVING'] else 'TECHNICAL',
                requirement=req['desc']
            )
            print(f"   - 요구사항: {req['desc']}")
    
    print(f"\n총 {len(growth_levels_data)}개의 성장레벨이 생성되었습니다!")
    

def display_summary():
    """생성된 데이터 요약 출력"""
    print("\n" + "="*60)
    print("성장레벨 체계 요약")
    print("="*60)
    
    levels = GrowthLevel.objects.all().order_by('level')
    for level in levels:
        requirements_count = level.requirements.count()
        print(f"레벨 {level.level}: {level.name}")
        print(f"  - 설명: {level.description}")
        print(f"  - 최소 점수: 기본 요구사항 참조")
        print(f"  - 연속 달성: 기본 요구사항 참조")
        print(f"  - 요구사항: {requirements_count}개")
        print()


if __name__ == "__main__":
    try:
        create_growth_levels()
        display_summary()
        
        print("성장레벨 기본 데이터 생성이 완료되었습니다!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)