"""
리더/보임자 추천 엔진 테스트
다양한 시나리오에 대한 리더 추천 테스트
"""

from job_profiles.leader_recommender import (
    recommend_leader_candidates,
    analyze_organization_talent_pool,
    LeaderRecommender
)
import json


def test_team_leader_recommendation():
    """팀장 추천 테스트"""
    print("=" * 70)
    print("테스트 1: 팀장 후보 추천")
    print("=" * 70)
    
    # 팀장 직무 정의
    team_lead_job = {
        "job_id": "job_team_lead",
        "name": "영업팀장",
        "required_skills": ["조직 리더십", "성과관리", "전략 실행력", "고객관계관리", "협상력"],
        "min_required_level": "Lv.3",
        "evaluation_standard": {
            "overall": "B+",
            "professionalism": "A"
        },
        "qualification": "영업 경력 7년 이상, 리더십 경험 우대"
    }
    
    # 직원 데이터 (다양한 케이스)
    employees = [
        {
            "employee_id": "emp001",
            "name": "김우수",
            "position": "과장",
            "department": "영업1팀",
            "level": "Lv.4",
            "career_years": 9,
            "skills": ["조직 리더십", "성과관리", "고객관계관리", "협상력", "프레젠테이션"],
            "certifications": ["영업관리사", "리더십 아카데미 수료"],
            "recent_evaluation": {
                "overall_grade": "A",
                "professionalism": "A+",
                "contribution": "Top 20%",
                "impact": "조직 간"
            },
            "recent_evaluations": [
                {"overall_grade": "A", "professionalism": "A+"},
                {"overall_grade": "A", "professionalism": "A"},
                {"overall_grade": "B+", "professionalism": "A"}
            ],
            "leadership_experience": {
                "years": 3,
                "type": "프로젝트 리더"
            }
        },
        {
            "employee_id": "emp002",
            "name": "이성과",
            "position": "차장",
            "department": "영업2팀",
            "level": "Lv.5",
            "career_years": 12,
            "skills": ["조직 리더십", "성과관리", "전략 실행력", "시장분석", "팀빌딩"],
            "certifications": ["MBA", "6시그마"],
            "recent_evaluation": {
                "overall_grade": "S",
                "professionalism": "S",
                "contribution": "Top 10%",
                "impact": "전사"
            },
            "recent_evaluations": [
                {"overall_grade": "S", "professionalism": "S"},
                {"overall_grade": "A+", "professionalism": "S"}
            ],
            "leadership_experience": {
                "years": 5,
                "type": "팀장 대행"
            }
        },
        {
            "employee_id": "emp003",
            "name": "박잠재",
            "position": "과장",
            "department": "영업3팀",
            "level": "Lv.3",
            "career_years": 6,
            "skills": ["성과관리", "데이터분석", "프로세스개선", "커뮤니케이션"],
            "certifications": ["데이터분석전문가"],
            "recent_evaluation": {
                "overall_grade": "B+",
                "professionalism": "B+",
                "contribution": "Top 50%",
                "impact": "조직 내"
            },
            "recent_evaluations": [
                {"overall_grade": "B+", "professionalism": "B+"},
                {"overall_grade": "B", "professionalism": "B+"}
            ],
            "leadership_experience": {
                "years": 0
            }
        },
        {
            "employee_id": "emp004",
            "name": "정리더",
            "position": "과장",
            "department": "기획팀",
            "level": "Lv.4",
            "career_years": 8,
            "skills": ["조직 리더십", "전략 실행력", "프로젝트관리", "혁신추진"],
            "certifications": ["PMP", "Change Management"],
            "recent_evaluation": {
                "overall_grade": "A+",
                "professionalism": "A",
                "contribution": "Top 10%",
                "impact": "조직 간"
            },
            "recent_evaluations": [
                {"overall_grade": "A+", "professionalism": "A"},
                {"overall_grade": "A", "professionalism": "A+"}
            ],
            "leadership_experience": {
                "years": 2,
                "type": "TF 팀장"
            },
            "department_changes": 4  # 부서 이동 횟수
        }
    ]
    
    # 팀장 후보 추천
    candidates = recommend_leader_candidates(
        target_job=team_lead_job,
        all_employees=employees,
        min_evaluation_grade="B+",
        min_growth_level="Lv.3",
        top_n=5
    )
    
    print(f"\n{team_lead_job['name']} 후보 추천 결과:\n")
    
    for idx, candidate in enumerate(candidates, 1):
        print(f"{idx}. {candidate['name']} ({candidate['current_position']}, {candidate['department']})")
        print(f"   종합 점수: {candidate['match_score']:.1f}점")
        print(f"   ├─ 평가등급: {candidate['evaluation_grade']} | 성장레벨: {candidate['growth_level']}")
        print(f"   ├─ 경력: {candidate['experience_years']}년 | 자격증: {len(candidate['qualifications'])}개")
        print(f"   ├─ 스킬 매칭률: {candidate['skill_match_rate']*100:.0f}% ({len(candidate['matched_skills'])}/{len(team_lead_job['required_skills'])})")
        print(f"   ├─ 추천 사유: {candidate['recommendation_reason']}")
        
        if candidate['risk_factors']:
            print(f"   └─ ⚠️  리스크: {', '.join(candidate['risk_factors'])}")
        else:
            print(f"   └─ ✅ 리스크 없음")
        print()


def test_center_leader_recommendation():
    """센터장 추천 테스트"""
    print("\n" + "=" * 70)
    print("테스트 2: 센터장 후보 추천")
    print("=" * 70)
    
    # 센터장 직무 정의
    center_lead_job = {
        "job_id": "job_center_lead",
        "name": "고객센터장",
        "required_skills": ["경영 리더십", "조직관리", "전략기획", "성과관리", "변화관리", "의사결정"],
        "min_required_level": "Lv.4",
        "evaluation_standard": {
            "overall": "A",
            "professionalism": "A+"
        },
        "qualification": "관리 경력 10년 이상, 센터/팀 운영 경험 필수"
    }
    
    # 시니어 직원 데이터
    senior_employees = [
        {
            "employee_id": "sen001",
            "name": "김경영",
            "position": "부장",
            "department": "고객서비스팀",
            "level": "Lv.5",
            "career_years": 15,
            "skills": ["경영 리더십", "조직관리", "전략기획", "성과관리", "고객경험관리", "디지털전환"],
            "certifications": ["경영학석사", "서비스경영자격", "디지털리더십"],
            "recent_evaluation": {
                "overall_grade": "A+",
                "professionalism": "S",
                "contribution": "Top 10%",
                "impact": "전사"
            },
            "recent_evaluations": [
                {"overall_grade": "A+", "professionalism": "S"},
                {"overall_grade": "A+", "professionalism": "A+"}
            ],
            "leadership_experience": {
                "years": 8,
                "type": "팀장"
            }
        },
        {
            "employee_id": "sen002",
            "name": "이전략",
            "position": "팀장",
            "department": "전략기획팀",
            "level": "Lv.4",
            "career_years": 11,
            "skills": ["전략기획", "성과관리", "프로세스혁신", "데이터분석", "프로젝트관리"],
            "certifications": ["전략기획전문가", "PMP"],
            "recent_evaluation": {
                "overall_grade": "A",
                "professionalism": "A",
                "contribution": "Top 20%",
                "impact": "조직 간"
            },
            "recent_evaluations": [
                {"overall_grade": "A", "professionalism": "A"},
                {"overall_grade": "B+", "professionalism": "A"}
            ],
            "leadership_experience": {
                "years": 4,
                "type": "팀장"
            }
        },
        {
            "employee_id": "sen003",
            "name": "박혁신",
            "position": "부장",
            "department": "디지털혁신팀",
            "level": "Lv.5",
            "career_years": 13,
            "skills": ["경영 리더십", "변화관리", "디지털전환", "조직관리", "혁신전략"],
            "certifications": ["CDO과정", "애자일코치"],
            "recent_evaluation": {
                "overall_grade": "S",
                "professionalism": "A+",
                "contribution": "Top 10%",
                "impact": "전사"
            },
            "recent_evaluations": [
                {"overall_grade": "S", "professionalism": "A+"},
                {"overall_grade": "A+", "professionalism": "A+"}
            ],
            "leadership_experience": {
                "years": 6,
                "type": "본부장 대행"
            }
        }
    ]
    
    # 센터장 후보 추천
    candidates = recommend_leader_candidates(
        target_job=center_lead_job,
        all_employees=senior_employees,
        min_evaluation_grade="A",
        min_growth_level="Lv.4",
        top_n=3
    )
    
    print(f"\n{center_lead_job['name']} 후보 추천 결과:\n")
    
    for idx, candidate in enumerate(candidates, 1):
        print(f"{idx}. {candidate['name']} ({candidate['current_position']}, {candidate['department']})")
        print(f"   종합 점수: {candidate['match_score']:.1f}점")
        
        # 상세 자격 요건 충족도
        readiness = candidate['readiness_details']
        print(f"   자격 요건 충족도:")
        print(f"   ├─ 평가: {readiness['qualification_details']['evaluation']['current_grade']} "
              f"(요구: {readiness['qualification_details']['evaluation']['required_grade']}) "
              f"{'✅' if readiness['qualification_details']['evaluation']['is_satisfied'] else '❌'}")
        print(f"   ├─ 레벨: {readiness['qualification_details']['growth_level']['current_level']} "
              f"(요구: {readiness['qualification_details']['growth_level']['required_level']}) "
              f"{'✅' if readiness['qualification_details']['growth_level']['is_satisfied'] else '❌'}")
        print(f"   ├─ 스킬: {candidate['skill_match_rate']*100:.0f}% 매칭 "
              f"({'✅' if candidate['skill_match_rate'] >= 0.7 else '❌'})")
        print(f"   └─ 경력: {candidate['experience_years']}년 "
              f"{'✅' if readiness['qualification_details']['experience']['is_satisfied'] else '❌'}")
        print()


def test_organization_talent_pool():
    """조직별 인재 풀 분석 테스트"""
    print("\n" + "=" * 70)
    print("테스트 3: 조직별 인재 풀 분석")
    print("=" * 70)
    
    # 전체 조직 직원 데이터
    all_employees = [
        # 영업본부
        {"employee_id": "e001", "name": "김영업", "department": "영업1팀", "position": "차장", 
         "level": "Lv.4", "skills": ["영업전략", "고객관리", "협상"], 
         "recent_evaluation": {"overall_grade": "A+"}, "career_years": 10},
        {"employee_id": "e002", "name": "이실적", "department": "영업1팀", "position": "과장", 
         "level": "Lv.3", "skills": ["영업관리", "데이터분석"], 
         "recent_evaluation": {"overall_grade": "A"}, "career_years": 7},
        {"employee_id": "e003", "name": "박성과", "department": "영업2팀", "position": "차장", 
         "level": "Lv.4", "skills": ["조직관리", "성과관리", "영업전략"], 
         "recent_evaluation": {"overall_grade": "S"}, "career_years": 11},
        {"employee_id": "e004", "name": "정목표", "department": "영업2팀", "position": "대리", 
         "level": "Lv.2", "skills": ["영업", "고객상담"], 
         "recent_evaluation": {"overall_grade": "B+"}, "career_years": 4},
         
        # IT본부
        {"employee_id": "e005", "name": "최개발", "department": "개발팀", "position": "차장", 
         "level": "Lv.5", "skills": ["아키텍처", "프로젝트관리", "기술리더십"], 
         "recent_evaluation": {"overall_grade": "S"}, "career_years": 12},
        {"employee_id": "e006", "name": "강코딩", "department": "개발팀", "position": "과장", 
         "level": "Lv.3", "skills": ["개발", "코드리뷰", "멘토링"], 
         "recent_evaluation": {"overall_grade": "A"}, "career_years": 8},
        {"employee_id": "e007", "name": "윤데이터", "department": "데이터팀", "position": "과장", 
         "level": "Lv.4", "skills": ["데이터분석", "ML", "시각화"], 
         "recent_evaluation": {"overall_grade": "A+"}, "career_years": 9},
         
        # 기획본부
        {"employee_id": "e008", "name": "한전략", "department": "전략기획팀", "position": "부장", 
         "level": "Lv.5", "skills": ["전략기획", "조직관리", "의사결정"], 
         "recent_evaluation": {"overall_grade": "A+"}, "career_years": 14},
        {"employee_id": "e009", "name": "서기획", "department": "전략기획팀", "position": "차장", 
         "level": "Lv.4", "skills": ["사업기획", "프로젝트관리", "분석"], 
         "recent_evaluation": {"overall_grade": "A"}, "career_years": 10},
    ]
    
    # 직무 프로파일
    job_profiles = [
        {
            "job_id": "j001",
            "name": "팀장",
            "required_skills": ["조직관리", "성과관리", "리더십"],
            "min_required_level": "Lv.3"
        },
        {
            "job_id": "j002",
            "name": "본부장/센터장",
            "required_skills": ["경영관리", "전략실행", "조직운영"],
            "min_required_level": "Lv.5"
        }
    ]
    
    # 조직 인재 풀 분석
    talent_pool = analyze_organization_talent_pool(
        all_employees=all_employees,
        job_profiles=job_profiles,
        min_evaluation_grade="B+",
        min_growth_level="Lv.3"
    )
    
    print("\n조직별 인재 풀 현황:\n")
    
    # 전체 통계
    stats = talent_pool['organization_stats']
    print(f"전체 통계:")
    print(f"├─ 팀장 후보: {stats['total_team_lead_candidates']}명")
    print(f"├─ 센터장 후보: {stats['total_center_lead_candidates']}명")
    print(f"└─ 고성과자(S/A+): {stats['total_high_potentials']}명")
    print()
    
    # 부서별 상세
    print("부서별 인재 풀:")
    for dept, details in talent_pool['department_details'].items():
        print(f"\n{dept} (총 {details['total_employees']}명)")
        
        if details['team_lead_candidates']:
            print(f"  팀장 후보:")
            for candidate in details['team_lead_candidates']:
                print(f"  ├─ {candidate['name']} (점수: {candidate['score']:.1f})")
        
        if details['high_potentials']:
            print(f"  고성과자:")
            for hp in details['high_potentials'][:3]:
                print(f"  ├─ {hp['name']} ({hp['grade']})")
        
        if details['top_skills']:
            print(f"  주요 보유 스킬:")
            skills_str = ", ".join([f"{skill}({count}명)" for skill, count in details['top_skills'][:3]])
            print(f"  └─ {skills_str}")


def test_succession_planning():
    """승계 계획 시나리오 테스트"""
    print("\n" + "=" * 70)
    print("테스트 4: 승계 계획 시나리오")
    print("=" * 70)
    
    # 퇴직 예정 임원 직무
    executive_job = {
        "job_id": "job_cfo",
        "name": "CFO (재무총괄)",
        "required_skills": ["재무전략", "경영관리", "리스크관리", "투자관리", "이사회보고"],
        "min_required_level": "Lv.5",
        "evaluation_standard": {
            "overall": "A+",
            "professionalism": "S"
        },
        "qualification": "재무 경력 15년 이상, 임원 경험 필수"
    }
    
    # 내부 승계 후보군
    succession_candidates = [
        {
            "employee_id": "exec001",
            "name": "김재무",
            "position": "재무담당 상무",
            "department": "재무본부",
            "level": "Lv.5",
            "career_years": 18,
            "skills": ["재무전략", "경영관리", "M&A", "리스크관리", "IR"],
            "certifications": ["CPA", "CFA", "MBA"],
            "recent_evaluation": {
                "overall_grade": "S",
                "professionalism": "S",
                "contribution": "Top 10%",
                "impact": "전사"
            },
            "recent_evaluations": [
                {"overall_grade": "S", "professionalism": "S"},
                {"overall_grade": "A+", "professionalism": "S"}
            ],
            "leadership_experience": {
                "years": 10,
                "type": "본부장"
            }
        },
        {
            "employee_id": "exec002",
            "name": "이투자",
            "position": "투자전략 본부장",
            "department": "전략본부",
            "level": "Lv.5",
            "career_years": 16,
            "skills": ["투자관리", "전략기획", "재무분석", "포트폴리오관리"],
            "certifications": ["CFA", "FRM"],
            "recent_evaluation": {
                "overall_grade": "A+",
                "professionalism": "A+",
                "contribution": "Top 10%",
                "impact": "전사"
            },
            "recent_evaluations": [
                {"overall_grade": "A+", "professionalism": "A+"},
                {"overall_grade": "A+", "professionalism": "S"}
            ],
            "leadership_experience": {
                "years": 7,
                "type": "본부장"
            }
        }
    ]
    
    # 승계 후보 추천
    print(f"\n{executive_job['name']} 승계 후보 분석:\n")
    
    recommender = LeaderRecommender()
    
    for candidate in succession_candidates:
        readiness = recommender.evaluate_leadership_readiness(
            candidate,
            executive_job,
            evaluation_period="annual_average"
        )
        
        print(f"후보: {candidate['name']} ({candidate['position']})")
        print(f"├─ 적격 여부: {'✅ 적격' if readiness['is_qualified'] else '❌ 부적격'}")
        print(f"├─ 준비도 점수: {readiness['total_score']:.1f}/100")
        print(f"├─ 강점:")
        
        # 강점 분석
        if candidate.get('certifications'):
            print(f"│  ├─ 전문 자격: {', '.join(candidate['certifications'])}")
        if candidate['leadership_experience']['years'] >= 10:
            print(f"│  ├─ 풍부한 리더십 경험: {candidate['leadership_experience']['years']}년")
        if readiness['qualification_details']['evaluation']['current_grade'] in ['S', 'A+']:
            print(f"│  └─ 우수한 평가: {readiness['qualification_details']['evaluation']['current_grade']}")
        
        # 개발 필요 영역
        missing_skills = readiness['qualification_details']['skills']['missing_skills']
        if missing_skills:
            print(f"└─ 개발 필요: {', '.join(missing_skills)}")
        else:
            print(f"└─ 모든 요건 충족")
        print()


def test_cross_functional_movement():
    """직무 간 이동 가능성 테스트"""
    print("\n" + "=" * 70)
    print("테스트 5: Cross-functional 리더 추천")
    print("=" * 70)
    
    # 디지털 전환 리더 직무 (IT + 비즈니스)
    digital_lead_job = {
        "job_id": "job_digital_lead",
        "name": "디지털전환 리더",
        "required_skills": ["디지털전략", "변화관리", "프로젝트관리", "데이터분석", "혁신추진"],
        "min_required_level": "Lv.4",
        "evaluation_standard": {
            "overall": "A"
        },
        "qualification": "IT 또는 전략기획 경력 8년 이상"
    }
    
    # 다양한 부서의 후보자
    cross_functional_candidates = [
        {
            "employee_id": "cf001",
            "name": "김비즈텍",
            "position": "차장",
            "department": "IT기획팀",
            "level": "Lv.4",
            "career_years": 9,
            "skills": ["IT전략", "프로젝트관리", "디지털전환", "프로세스혁신"],
            "recent_evaluation": {"overall_grade": "A", "professionalism": "A+"}
        },
        {
            "employee_id": "cf002",
            "name": "이마케팅",
            "position": "팀장",
            "department": "디지털마케팅팀",
            "level": "Lv.4",
            "career_years": 10,
            "skills": ["디지털마케팅", "데이터분석", "고객경험", "혁신추진"],
            "recent_evaluation": {"overall_grade": "A+", "professionalism": "A"}
        },
        {
            "employee_id": "cf003",
            "name": "박운영",
            "position": "차장",
            "department": "운영혁신팀",
            "level": "Lv.3",
            "career_years": 8,
            "skills": ["프로세스개선", "변화관리", "식스시그마", "프로젝트관리"],
            "recent_evaluation": {"overall_grade": "B+", "professionalism": "A"}
        }
    ]
    
    # 추천 실행
    candidates = recommend_leader_candidates(
        target_job=digital_lead_job,
        all_employees=cross_functional_candidates,
        min_evaluation_grade="B+",
        min_growth_level="Lv.3",
        top_n=3
    )
    
    print(f"\n{digital_lead_job['name']} Cross-functional 후보:\n")
    
    for idx, candidate in enumerate(candidates, 1):
        print(f"{idx}. {candidate['name']} (현재: {candidate['department']})")
        print(f"   적합도: {candidate['match_score']:.1f}점")
        print(f"   전환 가능성: {'높음' if candidate['match_score'] >= 70 else '보통'}")
        print(f"   핵심 역량: {', '.join(candidate['matched_skills'][:3])}")
        if candidate['missing_skills']:
            print(f"   보완 필요: {', '.join(candidate['missing_skills'][:2])}")
        print()


if __name__ == "__main__":
    # 모든 테스트 실행
    test_team_leader_recommendation()
    test_center_leader_recommendation()
    test_organization_talent_pool()
    test_succession_planning()
    test_cross_functional_movement()
    
    print("\n" + "=" * 70)
    print("모든 리더 추천 테스트 완료!")
    print("=" * 70)