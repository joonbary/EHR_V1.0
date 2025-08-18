"""
추천 코멘트 생성 테스트
다양한 평가 시나리오에 대한 자연어 추천 문장 생성 테스트
"""

from job_profiles.recommendation_comment_generator import generate_recommendation_comment


def test_high_performer_scenario():
    """고성과자 시나리오"""
    print("=" * 70)
    print("시나리오 1: 고성과자 - 즉시 승진 가능")
    print("=" * 70)
    
    employee = {
        "name": "김우수",
        "level": "Lv.4",
        "career_years": 10,
        "department": "전략기획팀",
        "skills": ["전략수립", "성과관리", "조직운영", "리더십", "의사결정", "프레젠테이션"],
        "recent_evaluation": {
            "professionalism": "S",
            "contribution": "Top 10%",
            "impact": "전사",
            "overall_grade": "S"
        },
        "evaluation_history": [
            {"overall_grade": "S"},
            {"overall_grade": "A+"},
            {"overall_grade": "A+"}
        ]
    }
    
    target_job = {
        "name": "전략기획팀장",
        "required_skills": ["전략수립", "성과관리", "조직운영", "예산관리", "리더십"],
        "min_required_level": "Lv.4"
    }
    
    # 한국어 코멘트
    ko_comment = generate_recommendation_comment(
        employee_profile=employee,
        target_job_profile=target_job,
        match_score=95.5,
        skill_gap=["예산관리"],
        promotion_ready=True,
        language="ko"
    )
    
    print(f"\n직원: {employee['name']} ({employee['department']} {employee['level']})")
    print(f"목표 직무: {target_job['name']}")
    print(f"매칭 점수: 95.5%")
    print(f"\n생성된 추천 코멘트:")
    print(f"📝 {ko_comment}")
    
    # 영어 코멘트
    en_comment = generate_recommendation_comment(
        employee_profile=employee,
        target_job_profile=target_job,
        match_score=95.5,
        skill_gap=["예산관리"],
        promotion_ready=True,
        language="en"
    )
    
    print(f"\n📝 (English) {en_comment}")


def test_high_potential_scenario():
    """잠재력 높은 직원 시나리오"""
    print("\n" + "=" * 70)
    print("시나리오 2: 잠재력 높은 직원 - 단기 개발 필요")
    print("=" * 70)
    
    employee = {
        "name": "이성장",
        "level": "Lv.3",
        "career_years": 5,
        "department": "마케팅팀",
        "skills": ["마케팅전략", "데이터분석", "프로젝트관리", "커뮤니케이션"],
        "recent_evaluation": {
            "professionalism": "A",
            "contribution": "Top 20%",
            "impact": "조직 간",
            "overall_grade": "A"
        }
    }
    
    target_job = {
        "name": "마케팅팀장",
        "required_skills": ["마케팅전략", "성과관리", "조직운영", "예산관리", "리더십"],
        "min_required_level": "Lv.3"
    }
    
    ko_comment = generate_recommendation_comment(
        employee_profile=employee,
        target_job_profile=target_job,
        match_score=72.8,
        skill_gap=["성과관리", "조직운영", "리더십"],
        promotion_ready=False,
        language="ko"
    )
    
    print(f"\n직원: {employee['name']} ({employee['department']} {employee['level']})")
    print(f"목표 직무: {target_job['name']}")
    print(f"매칭 점수: 72.8%")
    print(f"\n생성된 추천 코멘트:")
    print(f"📝 {ko_comment}")


def test_steady_performer_scenario():
    """안정적 성과자 시나리오"""
    print("\n" + "=" * 70)
    print("시나리오 3: 안정적 성과자 - 장기 개발 필요")
    print("=" * 70)
    
    employee = {
        "name": "박꾸준",
        "level": "Lv.2",
        "career_years": 8,
        "department": "인사팀",
        "skills": ["인사관리", "채용", "교육기획", "노무관리"],
        "recent_evaluation": {
            "professionalism": "B+",
            "contribution": "Top 50%",
            "impact": "조직 내",
            "overall_grade": "B+"
        }
    }
    
    target_job = {
        "name": "인사팀장",
        "required_skills": ["인사전략", "조직개발", "성과관리", "리더십", "예산관리"],
        "min_required_level": "Lv.4"
    }
    
    ko_comment = generate_recommendation_comment(
        employee_profile=employee,
        target_job_profile=target_job,
        match_score=58.5,
        skill_gap=["인사전략", "조직개발", "성과관리", "리더십"],
        promotion_ready=False,
        language="ko"
    )
    
    print(f"\n직원: {employee['name']} ({employee['department']} {employee['level']})")
    print(f"목표 직무: {target_job['name']}")
    print(f"매칭 점수: 58.5%")
    print(f"\n생성된 추천 코멘트:")
    print(f"📝 {ko_comment}")


def test_cross_functional_scenario():
    """직무 전환 시나리오"""
    print("\n" + "=" * 70)
    print("시나리오 4: 직무 전환 - IT에서 비즈니스로")
    print("=" * 70)
    
    employee = {
        "name": "최테크",
        "level": "Lv.4",
        "career_years": 9,
        "department": "IT개발팀",
        "skills": ["프로젝트관리", "시스템설계", "데이터분석", "프로세스개선", "커뮤니케이션"],
        "recent_evaluation": {
            "professionalism": "A+",
            "contribution": "Top 10%",
            "impact": "조직 간",
            "overall_grade": "A"
        }
    }
    
    target_job = {
        "name": "디지털전환리더",
        "required_skills": ["디지털전략", "변화관리", "프로젝트관리", "비즈니스분석", "리더십"],
        "min_required_level": "Lv.4"
    }
    
    ko_comment = generate_recommendation_comment(
        employee_profile=employee,
        target_job_profile=target_job,
        match_score=78.2,
        skill_gap=["디지털전략", "변화관리", "비즈니스분석"],
        promotion_ready=False,
        language="ko"
    )
    
    print(f"\n직원: {employee['name']} ({employee['department']} {employee['level']})")
    print(f"목표 직무: {target_job['name']}")
    print(f"매칭 점수: 78.2%")
    print(f"\n생성된 추천 코멘트:")
    print(f"📝 {ko_comment}")


def test_senior_executive_scenario():
    """시니어 임원 시나리오"""
    print("\n" + "=" * 70)
    print("시나리오 5: 시니어 임원 - C-level 승계")
    print("=" * 70)
    
    employee = {
        "name": "정임원",
        "level": "Lv.5",
        "career_years": 20,
        "department": "경영전략본부",
        "skills": ["경영전략", "M&A", "글로벌비즈니스", "재무관리", "이사회운영", "리더십"],
        "recent_evaluation": {
            "professionalism": "S",
            "contribution": "Top 5%",
            "impact": "전사",
            "overall_grade": "S"
        },
        "evaluation_history": [
            {"overall_grade": "S"},
            {"overall_grade": "S"},
            {"overall_grade": "A+"},
            {"overall_grade": "S"}
        ]
    }
    
    target_job = {
        "name": "최고전략책임자(CSO)",
        "required_skills": ["경영전략", "M&A", "글로벌비즈니스", "혁신전략", "이사회운영"],
        "min_required_level": "Lv.5"
    }
    
    ko_comment = generate_recommendation_comment(
        employee_profile=employee,
        target_job_profile=target_job,
        match_score=98.5,
        skill_gap=["혁신전략"],
        promotion_ready=True,
        language="ko"
    )
    
    print(f"\n직원: {employee['name']} ({employee['department']} {employee['level']})")
    print(f"목표 직무: {target_job['name']}")
    print(f"매칭 점수: 98.5%")
    print(f"\n생성된 추천 코멘트:")
    print(f"📝 {ko_comment}")
    
    # 영어 버전
    en_comment = generate_recommendation_comment(
        employee_profile=employee,
        target_job_profile=target_job,
        match_score=98.5,
        skill_gap=["혁신전략"],
        promotion_ready=True,
        language="en"
    )
    
    print(f"\n📝 (English) {en_comment}")


def test_young_talent_scenario():
    """젊은 인재 시나리오"""
    print("\n" + "=" * 70)
    print("시나리오 6: 젊은 인재 - Fast Track")
    print("=" * 70)
    
    employee = {
        "name": "강신입",
        "level": "Lv.2",
        "career_years": 3,
        "department": "재무팀",
        "skills": ["재무분석", "데이터분석", "프레젠테이션", "영어"],
        "recent_evaluation": {
            "professionalism": "A",
            "contribution": "Top 20%",
            "impact": "조직 내",
            "overall_grade": "A"
        }
    }
    
    target_job = {
        "name": "재무분석 파트장",
        "required_skills": ["재무분석", "재무전략", "팀관리", "보고서작성"],
        "min_required_level": "Lv.3"
    }
    
    ko_comment = generate_recommendation_comment(
        employee_profile=employee,
        target_job_profile=target_job,
        match_score=65.5,
        skill_gap=["재무전략", "팀관리"],
        promotion_ready=False,
        language="ko"
    )
    
    print(f"\n직원: {employee['name']} ({employee['department']} {employee['level']})")
    print(f"목표 직무: {target_job['name']}")
    print(f"매칭 점수: 65.5%")
    print(f"\n생성된 추천 코멘트:")
    print(f"📝 {ko_comment}")


def test_different_scores_comparison():
    """다양한 점수대별 코멘트 비교"""
    print("\n" + "=" * 70)
    print("시나리오 7: 동일 직원, 다양한 매칭 점수")
    print("=" * 70)
    
    employee = {
        "name": "테스트직원",
        "level": "Lv.3",
        "career_years": 6,
        "department": "기획팀",
        "skills": ["기획", "분석", "프로젝트관리"],
        "recent_evaluation": {
            "professionalism": "A",
            "contribution": "Top 30%",
            "impact": "조직 간",
            "overall_grade": "A"
        }
    }
    
    target_job = {
        "name": "기획팀장",
        "required_skills": ["전략기획", "성과관리", "조직운영", "리더십"],
        "min_required_level": "Lv.3"
    }
    
    # 다양한 점수대
    scores = [95.0, 85.0, 75.0, 65.0, 55.0]
    
    for score in scores:
        # 점수에 따른 스킬 갭 조정
        if score >= 90:
            skill_gap = []
            promotion_ready = True
        elif score >= 80:
            skill_gap = ["리더십"]
            promotion_ready = True
        elif score >= 70:
            skill_gap = ["성과관리", "리더십"]
            promotion_ready = False
        elif score >= 60:
            skill_gap = ["전략기획", "성과관리", "리더십"]
            promotion_ready = False
        else:
            skill_gap = ["전략기획", "성과관리", "조직운영", "리더십"]
            promotion_ready = False
        
        comment = generate_recommendation_comment(
            employee_profile=employee,
            target_job_profile=target_job,
            match_score=score,
            skill_gap=skill_gap,
            promotion_ready=promotion_ready,
            language="ko"
        )
        
        print(f"\n매칭 점수: {score}%")
        print(f"📝 {comment}")


def test_evaluation_variations():
    """다양한 평가 등급별 코멘트"""
    print("\n" + "=" * 70)
    print("시나리오 8: 평가 등급별 추천 코멘트 변화")
    print("=" * 70)
    
    base_employee = {
        "name": "평가대상자",
        "level": "Lv.3",
        "career_years": 7,
        "department": "영업팀",
        "skills": ["영업전략", "고객관리", "협상", "데이터분석"]
    }
    
    target_job = {
        "name": "영업팀장",
        "required_skills": ["영업전략", "성과관리", "조직운영", "고객관리"],
        "min_required_level": "Lv.3"
    }
    
    # 다양한 평가 조합
    evaluations = [
        {
            "name": "최우수 성과자",
            "eval": {
                "professionalism": "S",
                "contribution": "Top 10%",
                "impact": "전사",
                "overall_grade": "S"
            }
        },
        {
            "name": "우수 성과자",
            "eval": {
                "professionalism": "A+",
                "contribution": "Top 20%",
                "impact": "조직 간",
                "overall_grade": "A"
            }
        },
        {
            "name": "평균 성과자",
            "eval": {
                "professionalism": "B+",
                "contribution": "Top 50%",
                "impact": "조직 내",
                "overall_grade": "B+"
            }
        },
        {
            "name": "개선 필요자",
            "eval": {
                "professionalism": "B",
                "contribution": "Top 80%",
                "impact": "개인",
                "overall_grade": "B"
            }
        }
    ]
    
    for eval_case in evaluations:
        employee = base_employee.copy()
        employee['recent_evaluation'] = eval_case['eval']
        
        comment = generate_recommendation_comment(
            employee_profile=employee,
            target_job_profile=target_job,
            match_score=75.0,
            skill_gap=["성과관리", "조직운영"],
            promotion_ready=False,
            language="ko"
        )
        
        print(f"\n{eval_case['name']} (평가: {eval_case['eval']['overall_grade']})")
        print(f"📝 {comment}")


if __name__ == "__main__":
    print("=" * 70)
    print("리더 추천 자연어 코멘트 생성 테스트")
    print("=" * 70)
    
    # 모든 시나리오 테스트
    test_high_performer_scenario()
    test_high_potential_scenario()
    test_steady_performer_scenario()
    test_cross_functional_scenario()
    test_senior_executive_scenario()
    test_young_talent_scenario()
    test_different_scores_comparison()
    test_evaluation_variations()
    
    print("\n" + "=" * 70)
    print("모든 추천 코멘트 생성 테스트 완료!")
    print("=" * 70)