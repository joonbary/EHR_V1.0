"""
성장레벨 인증 시스템 통합 데모
ESS API → 교육 추천 → 인증 체크의 전체 플로우 시연
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from certifications.certification_services import CertificationService
from trainings.training_services import TrainingRecommendationService
from job_profiles.ess_leader_api import get_my_leader_recommendation_summary
import json


def print_section(title):
    """섹션 구분선 출력"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def demo_full_flow():
    """전체 플로우 데모"""
    
    # 테스트용 직원 선택 (첫 번째 직원)
    try:
        employee = Employee.objects.first()
        if not employee:
            print("직원 데이터가 없습니다. 먼저 직원을 생성하세요.")
            return
            
        print(f"\n테스트 직원: {employee.name} ({employee.position})")
        
    except Exception as e:
        print(f"직원 조회 오류: {str(e)}")
        return
    
    # 1. ESS 리더 추천 상태 확인
    print_section("1단계: ESS 리더 추천 상태 확인")
    
    leader_summary = get_my_leader_recommendation_summary(employee.id)
    
    if leader_summary.get('has_recommendation'):
        print(f"✓ 추천 직무: {leader_summary.get('best_match_job')}")
        print(f"✓ 매칭 점수: {leader_summary.get('match_score')}%")
        print(f"✓ 현재 평가: {leader_summary.get('evaluation_grade')}")
        print(f"✓ 즉시 가능: {'예' if leader_summary.get('is_ready') else '아니오'}")
    else:
        print("추천 가능한 리더 직무가 없습니다.")
    
    # 2. 성장레벨 인증 체크
    print_section("2단계: 성장레벨 인증 체크")
    
    cert_service = CertificationService()
    
    # 현재 레벨 확인
    current_level = cert_service._get_current_level(employee)
    print(f"현재 성장레벨: {current_level}")
    
    # 다음 레벨 목표 설정
    level_map = {
        'Lv.1': 'Lv.2', 'Lv.2': 'Lv.3',
        'Lv.3': 'Lv.4', 'Lv.4': 'Lv.5'
    }
    target_level = level_map.get(current_level, 'Lv.5')
    
    # 인증 체크 실행
    cert_result = cert_service.check_growth_level_certification(
        employee=employee,
        target_level=target_level
    )
    
    print(f"\n목표 레벨: {target_level}")
    print(f"인증 상태: {cert_result['certification_result']}")
    
    # 체크 결과 상세
    checks = cert_result['checks']
    print("\n요건별 충족 여부:")
    print(f"  - 평가: {'✓' if checks['evaluation'] else '✗'}")
    print(f"  - 교육: {'✓' if checks['training'] else '✗'}")
    print(f"  - 스킬: {'✓' if checks['skills'] else '✗'}")
    print(f"  - 경력: {'✓' if checks['experience'] else '✗'}")
    
    # 진행률
    progress = cert_result.get('progress', {})
    print(f"\n전체 진행률: {progress.get('overall', 0):.1f}%")
    
    # 부족한 요건
    if cert_result['details']['missing_courses']:
        print(f"\n부족한 교육: {', '.join(cert_result['details']['missing_courses'])}")
    
    if cert_result['details']['missing_skills']:
        print(f"부족한 스킬: {', '.join(cert_result['details']['missing_skills'])}")
    
    if cert_result['expected_certification_date']:
        print(f"\n예상 인증일: {cert_result['expected_certification_date']}")
    
    # 3. 교육 추천
    print_section("3단계: 맞춤형 교육 추천")
    
    training_service = TrainingRecommendationService()
    
    # 부족한 스킬 기반 교육 추천
    missing_skills = cert_result['details']['missing_skills']
    
    if missing_skills:
        training_result = training_service.get_employee_training_recommendations(
            employee=employee,
            target_job=leader_summary.get('best_match_job'),
            missing_skills=missing_skills,
            max_recommendations=5
        )
        
        recommendations = training_result.get('recommendations', [])
        
        if recommendations:
            print(f"\n추천 교육과정 ({len(recommendations)}개):")
            for i, course in enumerate(recommendations[:3], 1):
                print(f"\n{i}. [{course['course_code']}] {course['title']}")
                print(f"   - 매칭 점수: {course['match_score']:.1f}%")
                print(f"   - 우선순위: {course['priority']}")
                print(f"   - 교육시간: {course['duration_hours']}시간")
                print(f"   - 추천 이유: {course['recommendation_reason']}")
        
        # 학습 로드맵
        roadmap = training_result.get('roadmap', [])
        if roadmap:
            print(f"\n학습 로드맵 (총 {len(roadmap)}개월):")
            for month_plan in roadmap:
                month = month_plan['month']
                courses = month_plan['courses']
                total_hours = month_plan['total_hours']
                skills = month_plan['skills_covered']
                
                print(f"\n{month}개월차 ({total_hours}시간):")
                for course in courses:
                    print(f"  - {course['title']}")
                print(f"  습득 스킬: {', '.join(skills)}")
    else:
        print("부족한 스킬이 없어 교육 추천이 필요 없습니다.")
    
    # 4. 종합 분석
    print_section("4단계: 종합 분석 및 권고사항")
    
    print(f"\n직원: {employee.name}")
    print(f"현재 직급: {employee.position}")
    print(f"현재 레벨: {current_level} → 목표 레벨: {target_level}")
    
    if leader_summary.get('has_recommendation'):
        print(f"\n추천 리더 직무: {leader_summary.get('best_match_job')}")
        print(f"직무 적합도: {leader_summary.get('match_score')}%")
    
    print(f"\n성장레벨 인증 상태: {cert_result['certification_result']}")
    print(f"전체 준비도: {progress.get('overall', 0):.1f}%")
    
    if cert_result['certification_result'] == '충족':
        print("\n✓ 모든 요건을 충족하여 성장레벨 인증 신청이 가능합니다!")
    else:
        print("\n권고사항:")
        for i, rec in enumerate(cert_result.get('recommendations', []), 1):
            print(f"  {i}. {rec}")
        
        if missing_skills and recommendations:
            print(f"\n교육 이수 예상 기간: 약 {len(roadmap)}개월")
            print(f"총 교육 시간: {sum(r['duration_hours'] for r in recommendations)}시간")


def demo_api_integration():
    """API 통합 시나리오 데모"""
    print_section("API 통합 시나리오")
    
    print("""
1. 직원이 ESS에 로그인
   → GET /api/my-leader-growth-status/
   → 리더십 추천 상태 확인

2. 성장레벨 상태 확인
   → GET /api/my-growth-level-status/
   → 현재 레벨 및 다음 레벨 요건 확인

3. 부족한 스킬 확인 시 교육 추천
   → GET /api/my-growth-training-recommendations/
   → 맞춤형 교육과정 추천

4. 교육 수강 신청
   → POST /api/training-enrollment/
   → 추천 교육 신청

5. 인증 요건 충족 확인
   → POST /api/growth-level-certification-check/
   → 실시간 충족도 체크

6. 인증 신청
   → POST /api/growth-level-certification-apply/
   → 성장레벨 인증 신청
    """)


if __name__ == '__main__':
    print("="*60)
    print(" eHR 성장레벨 인증 시스템 통합 데모")
    print("="*60)
    
    # 전체 플로우 실행
    demo_full_flow()
    
    # API 시나리오 설명
    demo_api_integration()
    
    print("\n" + "="*60)
    print(" 데모 완료!")
    print("="*60)