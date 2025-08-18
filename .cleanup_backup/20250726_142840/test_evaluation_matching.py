"""
평가 결과 반영 매칭 테스트
다양한 평가 시나리오에 대한 매칭 결과 검증
"""

from job_profiles.evaluation_matcher import (
    match_profile_with_evaluation,
    match_multiple_profiles_with_evaluation,
    analyze_promotion_readiness,
    EvaluationScoreCalculator,
    EvaluationGradeConverter
)


def test_evaluation_score_calculation():
    """평가 점수 계산 테스트"""
    print("=" * 60)
    print("테스트 1: 평가 등급별 점수 계산")
    print("=" * 60)
    
    test_evaluations = [
        {
            "name": "최우수 직원",
            "evaluation": {
                "professionalism": "S",
                "contribution": "Top 10%",
                "impact": "전사",
                "overall_grade": "S"
            }
        },
        {
            "name": "우수 직원",
            "evaluation": {
                "professionalism": "A",
                "contribution": "Top 20%",
                "impact": "조직 간",
                "overall_grade": "A"
            }
        },
        {
            "name": "평균 직원",
            "evaluation": {
                "professionalism": "B+",
                "contribution": "Top 50~80%",
                "impact": "조직 내",
                "overall_grade": "B+"
            }
        },
        {
            "name": "저성과자",
            "evaluation": {
                "professionalism": "C",
                "contribution": "Bottom 20%",
                "impact": "개인",
                "overall_grade": "C"
            }
        }
    ]
    
    for test_case in test_evaluations:
        score = EvaluationScoreCalculator.calculate_evaluation_score(
            test_case["evaluation"]
        )
        print(f"\n{test_case['name']}:")
        print(f"  전문성: {test_case['evaluation']['professionalism']} → {score.professionalism_bonus}점")
        print(f"  기여도: {test_case['evaluation']['contribution']} → {score.contribution_bonus}점")
        print(f"  영향력: {test_case['evaluation']['impact']} → {score.impact_bonus}점")
        print(f"  종합등급: {test_case['evaluation']['overall_grade']} → {score.overall_grade_bonus}점")
        print(f"  총 보너스: {score.total_bonus}점")
        print(f"  자격 여부: {'적격' if score.is_eligible else '부적격'}")
        if score.penalty_reason:
            print(f"  사유: {score.penalty_reason}")


def test_evaluation_matching():
    """평가 반영 매칭 테스트"""
    print("\n" + "=" * 60)
    print("테스트 2: 평가 결과 반영 직무 매칭")
    print("=" * 60)
    
    # 직무 프로파일
    job_profile = {
        "job_id": "j001",
        "job_name": "팀 리더",
        "basic_skills": ["리더십", "프로젝트관리", "의사소통", "전략기획"],
        "applied_skills": ["성과관리", "갈등해결", "코칭", "예산관리"],
        "qualification": "관련 경력 5년 이상"
    }
    
    # 다양한 평가 결과를 가진 직원들
    employees = [
        {
            "employee_id": "e001",
            "name": "김성과",
            "career_years": 6,
            "skills": ["리더십", "프로젝트관리", "의사소통"],
            "recent_evaluation": {
                "professionalism": "A+",
                "contribution": "Top 20%",
                "impact": "조직 간",
                "overall_grade": "A+"
            }
        },
        {
            "employee_id": "e002",
            "name": "이평균",
            "career_years": 5,
            "skills": ["프로젝트관리", "의사소통"],
            "recent_evaluation": {
                "professionalism": "B+",
                "contribution": "Top 50~80%",
                "impact": "조직 내",
                "overall_grade": "B+"
            }
        },
        {
            "employee_id": "e003",
            "name": "박개선",
            "career_years": 7,
            "skills": ["리더십", "프로젝트관리", "의사소통", "전략기획"],
            "recent_evaluation": {
                "professionalism": "C",
                "contribution": "Bottom 20%",
                "impact": "개인",
                "overall_grade": "C"
            }
        }
    ]
    
    for emp in employees:
        print(f"\n{emp['name']} (경력 {emp['career_years']}년)")
        
        # 평가 반영 매칭
        result = match_profile_with_evaluation(
            job_profile, 
            emp,
            exclude_low_performers=True,
            evaluation_weight=0.3
        )
        
        if result.get('is_eligible', True):
            print(f"  기본 매칭: {result.get('original_match_score', 0):.1f}%")
            print(f"  평가 보너스: {result.get('evaluation_bonus', 0):.1f}점")
            print(f"  최종 점수: {result['match_score']}%")
            
            # 평가 상세
            eval_details = result.get('evaluation_details', {})
            if eval_details:
                print("  평가 영향:")
                for category in ['professionalism', 'contribution', 'impact', 'overall_grade']:
                    if category in eval_details and isinstance(eval_details[category], dict):
                        detail = eval_details[category]
                        print(f"    - {category}: {detail['grade']} ({detail['bonus']:+d}점)")
        else:
            print(f"  결과: 부적격 - {result.get('exclusion_reason', '알 수 없음')}")


def test_promotion_readiness():
    """승진 준비도 분석 테스트"""
    print("\n" + "=" * 60)
    print("테스트 3: 승진 준비도 분석")
    print("=" * 60)
    
    # 승진 대상 직무
    senior_position = {
        "job_id": "j002",
        "job_name": "시니어 매니저",
        "basic_skills": ["전략기획", "리더십", "의사결정", "이해관계자관리"],
        "applied_skills": ["비즈니스개발", "조직관리", "위기관리", "혁신추진"],
        "qualification": "매니저 경력 3년 이상"
    }
    
    # 승진 후보자들
    candidates = [
        {
            "employee_id": "e004",
            "name": "정준비",
            "career_years": 8,
            "skills": ["전략기획", "리더십", "의사결정", "프로젝트관리"],
            "recent_evaluation": {
                "professionalism": "A+",
                "contribution": "Top 10%",
                "impact": "조직 간",
                "overall_grade": "A+"
            }
        },
        {
            "employee_id": "e005",
            "name": "최노력",
            "career_years": 6,
            "skills": ["리더십", "의사소통"],
            "recent_evaluation": {
                "professionalism": "B+",
                "contribution": "Top 20~50%",
                "impact": "조직 내",
                "overall_grade": "B+"
            }
        }
    ]
    
    for candidate in candidates:
        print(f"\n{candidate['name']}의 승진 준비도:")
        
        readiness = analyze_promotion_readiness(
            candidate,
            senior_position,
            min_evaluation_grade='B+'
        )
        
        print(f"  승진 준비: {'완료' if readiness['is_ready'] else '미완'}")
        print(f"  매칭 점수: {readiness['match_score']}%")
        
        if readiness['strengths']:
            print(f"  강점: {', '.join(readiness['strengths'])}")
        
        if readiness['improvement_areas']:
            print(f"  개선필요: {', '.join(readiness['improvement_areas'])}")
        
        print(f"  추천: {readiness['recommendation']}")


def test_multiple_jobs_with_evaluation():
    """평가 반영 복수 직무 매칭 테스트"""
    print("\n" + "=" * 60)
    print("테스트 4: 평가 반영 복수 직무 추천")
    print("=" * 60)
    
    # 우수 성과자
    high_performer = {
        "employee_id": "e006",
        "name": "한우수",
        "career_years": 5,
        "skills": ["데이터분석", "프로젝트관리", "커뮤니케이션", "Python"],
        "certifications": ["PMP", "데이터분석전문가"],
        "recent_evaluation": {
            "professionalism": "A",
            "contribution": "Top 20%",
            "impact": "조직 간",
            "overall_grade": "A"
        }
    }
    
    # 다양한 직무들
    job_opportunities = [
        {
            "job_id": "j003",
            "job_name": "데이터 팀장",
            "basic_skills": ["데이터분석", "팀관리", "프로젝트관리"],
            "applied_skills": ["데이터전략", "성과관리"]
        },
        {
            "job_id": "j004",
            "job_name": "프로젝트 매니저",
            "basic_skills": ["프로젝트관리", "리스크관리", "일정관리"],
            "applied_skills": ["이해관계자관리", "예산관리"]
        },
        {
            "job_id": "j005",
            "job_name": "비즈니스 분석가",
            "basic_skills": ["데이터분석", "비즈니스이해", "문서작성"],
            "applied_skills": ["전략기획", "프로세스개선"]
        },
        {
            "job_id": "j006",
            "job_name": "AI 엔지니어",
            "basic_skills": ["Python", "머신러닝", "통계", "딥러닝"],
            "applied_skills": ["MLOps", "모델최적화"]
        }
    ]
    
    # 평가 반영 매칭
    matches = match_multiple_profiles_with_evaluation(
        job_opportunities,
        high_performer,
        top_n=3,
        min_score=50,
        evaluation_weight=0.35
    )
    
    print(f"\n{high_performer['name']}님의 평가 반영 추천 직무:")
    print(f"(현재 평가: 전문성 {high_performer['recent_evaluation']['professionalism']}, "
          f"기여도 {high_performer['recent_evaluation']['contribution']}, "
          f"종합 {high_performer['recent_evaluation']['overall_grade']})")
    
    for idx, match in enumerate(matches, 1):
        print(f"\n{idx}. {match['job_name']}")
        print(f"   최종 점수: {match['match_score']}%")
        print(f"   (기본: {match.get('original_match_score', 0):.1f}% + "
              f"평가보너스: {match.get('evaluation_bonus', 0):.1f}점)")
        
        # 주요 갭
        gaps = match.get('gaps', {})
        total_gaps = len(gaps.get('basic_skills', [])) + len(gaps.get('applied_skills', []))
        if total_gaps > 0:
            print(f"   스킬 갭: {total_gaps}개")


def test_grade_converter():
    """평가 등급 변환 테스트"""
    print("\n" + "=" * 60)
    print("테스트 5: 평가 등급 변환 유틸리티")
    print("=" * 60)
    
    # 백분율 -> 기여도 레벨 변환
    print("\n백분율 → 기여도 레벨:")
    test_percentages = [95, 85, 75, 60, 40, 15]
    for pct in test_percentages:
        level = EvaluationGradeConverter.percentage_to_contribution_level(pct)
        print(f"  {pct}% → {level}")
    
    # 점수 -> 영향력 레벨 변환
    print("\n점수 → 영향력 레벨:")
    test_scores = [(90, 100), (75, 100), (50, 100), (30, 100)]
    for score, max_score in test_scores:
        level = EvaluationGradeConverter.score_to_impact_level(score, max_score)
        print(f"  {score}/{max_score} → {level}")
    
    # 숫자 -> 문자 등급 변환
    print("\n숫자 → 문자 등급:")
    for num, letter in EvaluationGradeConverter.NUMERIC_TO_LETTER.items():
        print(f"  {num} → {letter}")


if __name__ == "__main__":
    # 모든 테스트 실행
    test_evaluation_score_calculation()
    test_evaluation_matching()
    test_promotion_readiness()
    test_multiple_jobs_with_evaluation()
    test_grade_converter()
    
    print("\n" + "=" * 60)
    print("모든 테스트 완료!")
    print("=" * 60)