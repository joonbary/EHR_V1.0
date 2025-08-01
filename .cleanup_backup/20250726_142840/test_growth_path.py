"""
성장 경로 추천 시스템 테스트
다양한 직원 프로파일에 대한 성장 경로 시뮬레이션
"""

from job_profiles.growth_path_recommender import (
    recommend_growth_path,
    GrowthPathRecommender
)


def test_developer_growth_path():
    """개발자 성장 경로 테스트"""
    print("=" * 60)
    print("테스트 1: 주니어 개발자의 성장 경로")
    print("=" * 60)
    
    # 주니어 개발자 프로파일
    junior_developer = {
        "employee_id": "e001",
        "name": "김주니어",
        "current_job": "주니어 백엔드 개발자",
        "career_years": 2,
        "skills": ["Java", "Spring", "MySQL", "Git", "REST API"],
        "certifications": ["정보처리기사"],
        "recent_evaluation": {
            "overall_grade": "B+",
            "professionalism": "B+",
            "contribution": "Top 50~80%"
        }
    }
    
    # 개발 직군 직무들
    dev_job_profiles = [
        {
            "job_id": "dev_senior",
            "job_name": "시니어 백엔드 개발자",
            "basic_skills": ["Java", "Spring", "MySQL", "설계패턴", "성능최적화"],
            "applied_skills": ["마이크로서비스", "코드리뷰", "멘토링", "Docker"],
            "qualification": "백엔드 개발 경력 5년 이상"
        },
        {
            "job_id": "dev_lead",
            "job_name": "개발 팀 리드",
            "basic_skills": ["기술리더십", "프로젝트관리", "아키텍처설계", "코드리뷰"],
            "applied_skills": ["팀빌딩", "기술전략", "이해관계자관리", "예산관리"],
            "qualification": "개발 경력 7년 이상, 리더십 경험"
        },
        {
            "job_id": "architect",
            "job_name": "솔루션 아키텍트",
            "basic_skills": ["시스템설계", "클라우드아키텍처", "보안", "성능최적화"],
            "applied_skills": ["엔터프라이즈패턴", "기술컨설팅", "비즈니스분석"],
            "qualification": "설계 경력 8년 이상"
        },
        {
            "job_id": "fullstack",
            "job_name": "풀스택 개발자",
            "basic_skills": ["Java", "JavaScript", "React", "Spring", "Database"],
            "applied_skills": ["DevOps", "UI/UX", "모바일개발"],
            "qualification": "프론트/백엔드 경력 4년 이상"
        }
    ]
    
    # 개발자 전환 이력 (실제 데이터 시뮬레이션)
    dev_transitions = {
        "주니어 백엔드 개발자": [
            "시니어 백엔드 개발자", "시니어 백엔드 개발자", "시니어 백엔드 개발자",
            "풀스택 개발자", "풀스택 개발자",
            "데이터 엔지니어", "DevOps 엔지니어"
        ],
        "시니어 백엔드 개발자": [
            "개발 팀 리드", "개발 팀 리드", "개발 팀 리드",
            "솔루션 아키텍트", "솔루션 아키텍트",
            "테크니컬 매니저", "프로덕트 오너"
        ],
        "풀스택 개발자": [
            "개발 팀 리드", "프론트엔드 팀 리드",
            "테크니컬 리드", "스타트업 CTO"
        ],
        "개발 팀 리드": [
            "엔지니어링 매니저", "솔루션 아키텍트",
            "VP of Engineering", "CTO"
        ]
    }
    
    # 성장 경로 추천
    recommendations = recommend_growth_path(
        junior_developer,
        dev_job_profiles,
        dev_transitions,
        top_n=3
    )
    
    print(f"\n{junior_developer['name']}님의 추천 성장 경로:\n")
    
    for idx, rec in enumerate(recommendations, 1):
        print(f"\n{idx}. {rec['target_job']} 경로")
        growth_path = rec['growth_path']
        
        print(f"   📊 경로 개요:")
        print(f"   - 목표 달성 예상 기간: {growth_path.total_years:.1f}년")
        print(f"   - 성공 가능성: {growth_path.success_probability*100:.0f}%")
        print(f"   - 전체 난이도: {growth_path.difficulty_score:.0f}/100")
        print(f"   - 과거 사례: {growth_path.historical_examples}건")
        
        print(f"\n   📈 단계별 성장 로드맵:")
        for stage_idx, stage in enumerate(growth_path.stages, 1):
            status_icon = "✅" if stage.is_achievable else "⚠️"
            print(f"\n   {status_icon} {stage_idx}단계: {stage.job_name}")
            print(f"      예상 소요 기간: {stage.expected_years:.1f}년")
            print(f"      스킬 갭: {stage.skill_gap}개")
            
            if stage.required_skills:
                print(f"      필수 습득 스킬: {', '.join(stage.required_skills[:3])}")
            
            if stage.blockers:
                print(f"      ⚠️  장애요인: {', '.join(stage.blockers)}")
        
        print(f"\n   💡 추천 액션 플랜:")
        for action_idx, action in enumerate(growth_path.recommended_actions, 1):
            print(f"   {action_idx}. {action}")
        
        if rec.get('alternative_paths'):
            print(f"\n   🔄 대안 경로:")
            for alt_idx, alt_path in enumerate(rec['alternative_paths'][:2], 1):
                print(f"   {alt_idx}. {' → '.join(alt_path)}")


def test_hr_growth_path():
    """HR 직군 성장 경로 테스트"""
    print("\n\n" + "=" * 60)
    print("테스트 2: HR 담당자의 성장 경로")
    print("=" * 60)
    
    # HR 담당자 프로파일
    hr_specialist = {
        "employee_id": "e002",
        "name": "이인사",
        "current_job": "HR 스페셜리스트",
        "career_years": 4,
        "skills": ["채용관리", "교육기획", "인사제도", "노동법", "데이터분석"],
        "certifications": ["PHR", "노무사"],
        "recent_evaluation": {
            "overall_grade": "A",
            "professionalism": "A",
            "contribution": "Top 20%"
        }
    }
    
    # HR 직군 직무들
    hr_job_profiles = [
        {
            "job_id": "hr_manager",
            "job_name": "HR 매니저",
            "basic_skills": ["인사전략", "조직개발", "성과관리", "노사관계", "예산관리"],
            "applied_skills": ["변화관리", "HR Analytics", "리더십개발", "보상설계"],
            "qualification": "HR 경력 6년 이상, 팀 관리 경험"
        },
        {
            "job_id": "hrbp",
            "job_name": "HR 비즈니스 파트너",
            "basic_skills": ["비즈니스이해", "전략적사고", "데이터분석", "커뮤니케이션"],
            "applied_skills": ["조직진단", "인재관리", "변화관리", "코칭"],
            "qualification": "HR 경력 5년 이상, 비즈니스 경험"
        },
        {
            "job_id": "hr_director",
            "job_name": "HR 디렉터",
            "basic_skills": ["경영전략", "조직설계", "리더십", "재무관리", "글로벌HR"],
            "applied_skills": ["M&A", "기업문화", "임원코칭", "이사회보고"],
            "qualification": "HR 경력 10년 이상, 임원급"
        },
        {
            "job_id": "talent_manager",
            "job_name": "인재개발 매니저",
            "basic_skills": ["교육체계설계", "리더십개발", "경력개발", "역량평가"],
            "applied_skills": ["디지털러닝", "코칭", "퍼실리테이션", "성과향상"],
            "qualification": "HRD 경력 5년 이상"
        }
    ]
    
    # HR 전환 이력
    hr_transitions = {
        "HR 스페셜리스트": [
            "HR 매니저", "HR 매니저", "HR 매니저",
            "HRBP", "HRBP",
            "인재개발 매니저", "채용 매니저"
        ],
        "HR 매니저": [
            "HR 디렉터", "HR 디렉터",
            "HRBP 리더", "조직개발 리더"
        ],
        "HRBP": [
            "HRBP 리더", "HR 디렉터",
            "사업부 HR 헤드", "COO"
        ],
        "인재개발 매니저": [
            "HRD 팀장", "조직개발 리더",
            "CLO", "HR 디렉터"
        ]
    }
    
    # 성장 경로 추천
    recommendations = recommend_growth_path(
        hr_specialist,
        hr_job_profiles,
        hr_transitions,
        top_n=2
    )
    
    print(f"\n{hr_specialist['name']}님의 추천 성장 경로:\n")
    
    for idx, rec in enumerate(recommendations, 1):
        print(f"\n{idx}. {rec['target_job']} 경로")
        growth_path = rec['growth_path']
        
        print(f"   총 예상 기간: {growth_path.total_years:.1f}년")
        print(f"   성공 확률: {growth_path.success_probability*100:.0f}%")
        
        print("\n   단계별 성장 계획:")
        for stage in growth_path.stages:
            print(f"   → {stage.job_name} ({stage.expected_years:.1f}년)")
            if stage.required_skills:
                print(f"     필요 역량: {', '.join(stage.required_skills[:3])}")


def test_career_change_path():
    """경력 전환 경로 테스트"""
    print("\n\n" + "=" * 60)
    print("테스트 3: 경력 전환 시나리오 (개발자 → 데이터 분야)")
    print("=" * 60)
    
    # 전환 희망 개발자
    developer_to_data = {
        "employee_id": "e003",
        "name": "박전환",
        "current_job": "백엔드 개발자",
        "career_years": 5,
        "skills": ["Python", "SQL", "Django", "PostgreSQL", "API개발"],
        "certifications": ["AWS Solutions Architect"],
        "interests": ["데이터분석", "머신러닝"]
    }
    
    # 데이터 분야 직무들
    data_job_profiles = [
        {
            "job_id": "data_analyst",
            "job_name": "데이터 분석가",
            "basic_skills": ["SQL", "Python", "통계", "데이터시각화", "비즈니스분석"],
            "applied_skills": ["A/B테스팅", "대시보드개발", "데이터스토리텔링"],
            "qualification": "데이터 분석 경력 3년 이상"
        },
        {
            "job_id": "data_engineer",
            "job_name": "데이터 엔지니어",
            "basic_skills": ["Python", "SQL", "ETL", "데이터파이프라인", "클라우드"],
            "applied_skills": ["Spark", "Airflow", "Kafka", "DataLake"],
            "qualification": "데이터 엔지니어링 경력 4년 이상"
        },
        {
            "job_id": "ml_engineer",
            "job_name": "머신러닝 엔지니어",
            "basic_skills": ["Python", "머신러닝", "통계", "MLOps", "모델개발"],
            "applied_skills": ["딥러닝", "모델최적화", "A/B테스팅", "프로덕션배포"],
            "qualification": "ML 경력 3년 이상"
        },
        {
            "job_id": "data_scientist",
            "job_name": "데이터 사이언티스트",
            "basic_skills": ["통계", "머신러닝", "Python", "실험설계", "인과추론"],
            "applied_skills": ["딥러닝", "NLP", "추천시스템", "최적화"],
            "qualification": "데이터사이언스 경력 5년 이상, 석사 우대"
        }
    ]
    
    # 경력 전환 이력 (개발자 → 데이터)
    career_change_transitions = {
        "백엔드 개발자": [
            "데이터 엔지니어", "데이터 엔지니어", "데이터 엔지니어",
            "데이터 분석가", "ML 엔지니어",
            "풀스택 개발자", "DevOps 엔지니어"
        ],
        "데이터 엔지니어": [
            "시니어 데이터 엔지니어", "ML 엔지니어",
            "데이터 아키텍트", "데이터 팀 리드"
        ],
        "데이터 분석가": [
            "시니어 데이터 분석가", "데이터 사이언티스트",
            "프로덕트 분석가", "비즈니스 인텔리전스 매니저"
        ],
        "ML 엔지니어": [
            "시니어 ML 엔지니어", "ML 팀 리드",
            "AI 리서처", "MLOps 리드"
        ]
    }
    
    # 성장 경로 추천
    recommendations = recommend_growth_path(
        developer_to_data,
        data_job_profiles,
        career_change_transitions,
        top_n=3
    )
    
    print(f"\n{developer_to_data['name']}님의 데이터 분야 전환 경로:\n")
    
    for idx, rec in enumerate(recommendations, 1):
        print(f"\n옵션 {idx}: {rec['target_job']}")
        growth_path = rec['growth_path']
        
        print(f"   전환 가능성: {growth_path.success_probability*100:.0f}%")
        print(f"   예상 전환 기간: {growth_path.total_years:.1f}년")
        
        # 첫 단계 상세 정보
        if growth_path.stages:
            first_stage = growth_path.stages[0]
            print(f"\n   즉시 필요한 준비사항:")
            print(f"   - 스킬 갭: {first_stage.skill_gap}개")
            if first_stage.required_skills:
                print(f"   - 우선 학습: {', '.join(first_stage.required_skills[:3])}")
            
            print(f"\n   경력 활용 가능 부분:")
            current_skills = set(developer_to_data['skills'])
            target_skills = set(data_job_profiles[idx-1]['basic_skills'])
            common_skills = current_skills & target_skills
            if common_skills:
                print(f"   - 보유 스킬 활용: {', '.join(common_skills)}")


def test_reverse_path_analysis():
    """역방향 경로 분석 테스트"""
    print("\n\n" + "=" * 60)
    print("테스트 4: 목표 직무에서 역방향 경로 분석")
    print("=" * 60)
    
    # 목표 직무: CTO
    target_job = {
        "job_id": "cto",
        "job_name": "CTO (최고기술책임자)",
        "basic_skills": ["기술전략", "조직관리", "비즈니스전략", "기술리더십"],
        "applied_skills": ["이사회소통", "투자유치", "M&A", "글로벌확장"],
        "qualification": "기술 리더십 경력 15년 이상"
    }
    
    # 기술 리더십 전환 이력
    tech_leadership_transitions = {
        "시니어 개발자": ["테크 리드", "개발 매니저"],
        "테크 리드": ["개발 매니저", "엔지니어링 매니저", "아키텍트"],
        "개발 매니저": ["엔지니어링 디렉터", "VP of Engineering"],
        "엔지니어링 매니저": ["엔지니어링 디렉터", "VP of Engineering"],
        "VP of Engineering": ["CTO (최고기술책임자)", "COO"],
        "아키텍트": ["수석 아키텍트", "CTO (최고기술책임자)"],
        "엔지니어링 디렉터": ["VP of Engineering", "CTO (최고기술책임자)"]
    }
    
    recommender = GrowthPathRecommender()
    recommender.build_transition_graph(tech_leadership_transitions)
    
    # 역방향 경로 찾기
    reverse_paths = recommender.find_reverse_path(
        target_job,
        [],  # 전체 직무 프로파일은 생략
        max_depth=4
    )
    
    print(f"\n{target_job['job_name']}가 되기 위한 경로들:\n")
    
    for idx, path in enumerate(reverse_paths[:5], 1):
        print(f"{idx}. {' → '.join(path)}")
        
        # 각 단계별 예상 기간 (휴리스틱)
        total_years = 0
        for i in range(len(path)-1):
            if "시니어" in path[i]:
                years = 3
            elif "리드" in path[i] or "매니저" in path[i]:
                years = 4
            elif "디렉터" in path[i]:
                years = 5
            elif "VP" in path[i]:
                years = 4
            else:
                years = 3
            total_years += years
        
        print(f"   예상 총 기간: 약 {total_years}년")


def test_skill_based_growth():
    """스킬 기반 성장 분석"""
    print("\n\n" + "=" * 60)
    print("테스트 5: 스킬 기반 성장 가능성 분석")
    print("=" * 60)
    
    # 다양한 스킬을 가진 직원
    versatile_employee = {
        "employee_id": "e004",
        "name": "최다재",
        "current_job": "프로덕트 매니저",
        "career_years": 6,
        "skills": [
            "프로덕트전략", "데이터분석", "UX디자인", 
            "프로젝트관리", "SQL", "Python", "비즈니스분석"
        ],
        "certifications": ["PMP", "Google Analytics"]
    }
    
    # 다양한 분야의 직무들
    diverse_job_profiles = [
        {
            "job_id": "senior_pm",
            "job_name": "시니어 프로덕트 매니저",
            "basic_skills": ["프로덕트전략", "데이터분석", "UX", "로드맵관리"],
            "applied_skills": ["그로스해킹", "A/B테스팅", "수익화전략"],
            "qualification": "PM 경력 7년 이상"
        },
        {
            "job_id": "growth_manager",
            "job_name": "그로스 매니저",
            "basic_skills": ["데이터분석", "A/B테스팅", "마케팅", "SQL"],
            "applied_skills": ["그로스해킹", "퍼포먼스마케팅", "자동화"],
            "qualification": "그로스 경력 5년 이상"
        },
        {
            "job_id": "product_analyst",
            "job_name": "프로덕트 애널리스트",
            "basic_skills": ["데이터분석", "SQL", "Python", "통계"],
            "applied_skills": ["실험설계", "인과추론", "대시보드개발"],
            "qualification": "분석 경력 4년 이상"
        },
        {
            "job_id": "ux_director",
            "job_name": "UX 디렉터",
            "basic_skills": ["UX전략", "디자인시스템", "사용자연구", "리더십"],
            "applied_skills": ["서비스디자인", "디자인운영", "조직관리"],
            "qualification": "UX 리더십 경력 8년 이상"
        }
    ]
    
    # PM 관련 전환 이력
    pm_transitions = {
        "프로덕트 매니저": [
            "시니어 프로덕트 매니저", "시니어 프로덕트 매니저",
            "그로스 매니저", "프로덕트 애널리스트",
            "프로덕트 오너", "UX 매니저"
        ],
        "시니어 프로덕트 매니저": [
            "프로덕트 디렉터", "프로덕트 VP",
            "스타트업 대표", "CPO"
        ],
        "그로스 매니저": [
            "그로스 팀 리드", "마케팅 디렉터",
            "CMO", "스타트업 대표"
        ]
    }
    
    recommendations = recommend_growth_path(
        versatile_employee,
        diverse_job_profiles,
        pm_transitions,
        top_n=4
    )
    
    print(f"\n{versatile_employee['name']}님의 스킬 기반 성장 옵션:\n")
    
    # 스킬 매칭 분석
    for idx, rec in enumerate(recommendations, 1):
        print(f"\n{idx}. {rec['target_job']}")
        
        # 현재 스킬과의 매칭
        current_skills = set(versatile_employee['skills'])
        target_skills = set(
            diverse_job_profiles[idx-1]['basic_skills'] + 
            diverse_job_profiles[idx-1]['applied_skills']
        )
        
        matched_skills = current_skills & target_skills
        missing_skills = target_skills - current_skills
        
        print(f"   스킬 매칭: {len(matched_skills)}/{len(target_skills)} "
              f"({len(matched_skills)/len(target_skills)*100:.0f}%)")
        print(f"   활용 가능 스킬: {', '.join(list(matched_skills)[:4])}")
        
        if missing_skills:
            print(f"   습득 필요 스킬: {', '.join(list(missing_skills)[:3])}")
        
        # 성장 경로 요약
        growth_path = rec['growth_path']
        print(f"   예상 전환 기간: {growth_path.total_years:.1f}년")
        print(f"   추천 우선순위: {'⭐' * int(rec['priority_score'] * 5)}")


if __name__ == "__main__":
    # 모든 테스트 실행
    test_developer_growth_path()
    test_hr_growth_path()
    test_career_change_path()
    test_reverse_path_analysis()
    test_skill_based_growth()
    
    print("\n" + "=" * 60)
    print("모든 성장 경로 테스트 완료!")
    print("=" * 60)