"""
직무-직원 프로파일 매칭 테스트 스크립트
다양한 시나리오에 대한 매칭 엔진 테스트
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from job_profiles.matching_engine import match_profile, match_multiple_profiles, recommend_growth_path
from job_profiles.embedding_matcher import HybridMatcher, SkillClusterAnalyzer


def test_basic_matching():
    """기본 매칭 테스트"""
    print("=" * 60)
    print("테스트 1: 기본 직무-직원 매칭")
    print("=" * 60)
    
    # HRM 직무
    job_hrm = {
        "job_id": "uuid-HRM",
        "job_name": "HRM",
        "role_responsibility": "인사제도 기획 및 운영, 조직문화 개선",
        "qualification": "인사 관련 경력 3년 이상",
        "basic_skills": ["노동법", "내부규정이해", "인사제도", "조직문화"],
        "applied_skills": ["제도기획", "노사관리", "데이터기반 인사운영", "HR Analytics"]
    }
    
    # 다양한 직원 프로파일
    employees = [
        {
            "employee_id": "e001",
            "name": "김인사",
            "career_years": 4,
            "certifications": ["노동법자격증"],
            "completed_courses": ["내부규정", "노사관리기초", "조직문화"],
            "skills": ["인사제도", "데이터분석"]
        },
        {
            "employee_id": "e002",
            "name": "박신입",
            "career_years": 1,
            "certifications": [],
            "completed_courses": ["신입사원교육"],
            "skills": ["문서작성", "엑셀"]
        },
        {
            "employee_id": "e003",
            "name": "이전문가",
            "career_years": 7,
            "certifications": ["노동법자격증", "SHRM-CP"],
            "completed_courses": ["노동법", "내부규정", "제도기획", "HR Analytics", "노사관리"],
            "skills": ["인사제도", "조직문화", "데이터기반 인사운영"]
        }
    ]
    
    for emp in employees:
        result = match_profile(job_hrm, emp)
        print(f"\n{emp['name']} (경력 {emp['career_years']}년)")
        print(f"  매칭 점수: {result['match_score']}%")
        print(f"  기본 스킬: {result['skill_match']['basic_skills']['score']}%")
        print(f"  응용 스킬: {result['skill_match']['applied_skills']['score']}%")
        if result['gaps']['basic_skills']:
            print(f"  부족한 기본 스킬: {', '.join(result['gaps']['basic_skills'][:3])}")


def test_multiple_job_matching():
    """복수 직무 매칭 테스트"""
    print("\n" + "=" * 60)
    print("테스트 2: 직원에게 적합한 직무 찾기")
    print("=" * 60)
    
    # 직원 프로파일
    employee = {
        "employee_id": "e004",
        "name": "최만능",
        "career_years": 5,
        "certifications": ["정보처리기사", "데이터분석전문가"],
        "completed_courses": ["프로젝트관리", "데이터분석", "Python"],
        "skills": ["데이터분석", "프로젝트관리", "문서작성", "프레젠테이션", "SQL"]
    }
    
    # 다양한 직무들
    job_profiles = [
        {
            "job_id": "uuid-HRM",
            "job_name": "HRM",
            "qualification": "인사 관련 경력 3년 이상",
            "basic_skills": ["노동법", "내부규정이해", "인사제도"],
            "applied_skills": ["제도기획", "노사관리", "HR Analytics"]
        },
        {
            "job_id": "uuid-IT-PLAN",
            "job_name": "IT기획",
            "qualification": "IT 관련 경력 3년 이상",
            "basic_skills": ["데이터분석", "프로젝트관리", "IT전략", "문서작성"],
            "applied_skills": ["시스템설계", "프로세스개선", "벤더관리"]
        },
        {
            "job_id": "uuid-DATA-ANALYST",
            "job_name": "데이터분석가",
            "qualification": "데이터 분석 경력 2년 이상",
            "basic_skills": ["데이터분석", "SQL", "통계", "Python"],
            "applied_skills": ["머신러닝", "데이터시각화", "A/B테스팅"]
        },
        {
            "job_id": "uuid-PM",
            "job_name": "프로젝트매니저",
            "qualification": "PM 경력 5년 이상",
            "basic_skills": ["프로젝트관리", "리스크관리", "일정관리", "예산관리"],
            "applied_skills": ["애자일", "스크럼", "이해관계자관리"]
        }
    ]
    
    matches = match_multiple_profiles(job_profiles, employee, top_n=3, min_score=50)
    
    print(f"\n{employee['name']}님께 추천하는 직무 TOP 3:\n")
    for idx, match in enumerate(matches, 1):
        print(f"{idx}. {match['job_name']} (매칭점수: {match['match_score']}%)")
        print(f"   - 기본스킬 매칭: {match['skill_match']['basic_skills']['score']}%")
        print(f"   - 응용스킬 매칭: {match['skill_match']['applied_skills']['score']}%")
        if match['recommendations']:
            print(f"   - 추천사항: {match['recommendations'][0]}")


def test_growth_path():
    """성장 경로 추천 테스트"""
    print("\n" + "=" * 60)
    print("테스트 3: 경력 개발 경로 추천")
    print("=" * 60)
    
    current_profile = {
        "employee_id": "e005",
        "name": "김성장",
        "career_years": 3,
        "current_job": "주니어 개발자",
        "certifications": ["정보처리기사"],
        "completed_courses": ["Java", "Spring", "SQL"],
        "skills": ["Java", "Spring", "SQL", "Git"]
    }
    
    target_profiles = [
        {
            "job_id": "uuid-SENIOR-DEV",
            "job_name": "시니어 개발자",
            "basic_skills": ["Java", "Spring", "SQL", "설계패턴", "코드리뷰"],
            "applied_skills": ["마이크로서비스", "DevOps", "성능최적화"]
        },
        {
            "job_id": "uuid-TECH-LEAD",
            "job_name": "테크리드",
            "basic_skills": ["Java", "Spring", "아키텍처설계", "기술리더십", "멘토링"],
            "applied_skills": ["기술전략", "팀빌딩", "프로젝트관리"]
        },
        {
            "job_id": "uuid-ARCHITECT",
            "job_name": "솔루션 아키텍트",
            "basic_skills": ["시스템설계", "클라우드", "보안", "성능최적화"],
            "applied_skills": ["엔터프라이즈아키텍처", "기술컨설팅", "비즈니스분석"]
        }
    ]
    
    recommendations = recommend_growth_path(current_profile, target_profiles)
    
    print(f"\n{current_profile['name']}님의 경력 개발 추천 경로:\n")
    for idx, rec in enumerate(recommendations, 1):
        print(f"{idx}. {rec['target_job']} 경로")
        print(f"   현재 준비도: {rec['estimated_readiness']} (매칭 {rec['current_match_score']}%)")
        print(f"   필요 스킬 갭: {rec['total_skill_gaps']}개")
        if rec['priority_skills']:
            print(f"   우선 습득 스킬: {', '.join(rec['priority_skills'])}")


def test_hybrid_matching():
    """하이브리드 매칭 테스트"""
    print("\n" + "=" * 60)
    print("테스트 4: 하이브리드 매칭 (규칙 + 임베딩)")
    print("=" * 60)
    
    from job_profiles.embedding_matcher import HybridMatcher
    
    job_profile = {
        "job_id": "uuid-ML-ENGINEER",
        "job_name": "머신러닝 엔지니어",
        "role_responsibility": "머신러닝 모델 개발 및 배포, MLOps 파이프라인 구축",
        "qualification": "ML 관련 경력 3년 이상, 석사 우대",
        "basic_skills": ["Python", "머신러닝", "통계", "선형대수"],
        "applied_skills": ["딥러닝", "MLOps", "분산처리", "모델최적화"]
    }
    
    employee = {
        "employee_id": "e006",
        "name": "박AI",
        "career_years": 4,
        "skills": ["Python", "데이터분석", "통계", "Tensorflow"],
        "certifications": ["텐서플로우자격증"],
        "experience_description": "추천시스템 개발 및 이미지 분류 모델 구축 경험"
    }
    
    matcher = HybridMatcher()
    result = matcher.hybrid_match(job_profile, employee, rule_weight=0.6, embedding_weight=0.4)
    
    print(f"\n{employee['name']} - {job_profile['job_name']} 하이브리드 매칭 결과:")
    print(f"\n종합 매칭 점수: {result['hybrid_match_score']}%")
    print(f"- 규칙 기반: {result['rule_based']['score']}% (가중치 {result['rule_based']['weight']})")
    print(f"- 임베딩 기반: {result['embedding_based']['score']}% (가중치 {result['embedding_based']['weight']})")
    
    print("\n추천사항:")
    for idx, rec in enumerate(result['recommendations'][:3], 1):
        print(f"{idx}. {rec}")


def test_skill_clustering():
    """스킬 클러스터링 테스트"""
    print("\n" + "=" * 60)
    print("테스트 5: 스킬 클러스터 분석")
    print("=" * 60)
    
    # 여러 직무의 스킬들
    all_profiles = [
        {
            "job_name": "백엔드 개발자",
            "basic_skills": ["Java", "Spring", "SQL", "REST API"],
            "applied_skills": ["마이크로서비스", "Docker", "Kubernetes"]
        },
        {
            "job_name": "프론트엔드 개발자",
            "basic_skills": ["JavaScript", "React", "HTML", "CSS"],
            "applied_skills": ["TypeScript", "Redux", "Webpack"]
        },
        {
            "job_name": "데이터 엔지니어",
            "basic_skills": ["Python", "SQL", "ETL", "데이터파이프라인"],
            "applied_skills": ["Spark", "Airflow", "Kafka"]
        },
        {
            "job_name": "DevOps 엔지니어",
            "basic_skills": ["Linux", "Docker", "CI/CD", "모니터링"],
            "applied_skills": ["Kubernetes", "Terraform", "AWS"]
        }
    ]
    
    analyzer = SkillClusterAnalyzer()
    clusters = analyzer.analyze_skill_clusters(all_profiles)
    
    print("\n발견된 스킬 클러스터:")
    for cluster_name, skills in list(clusters.items())[:5]:
        if len(skills) > 1:  # 2개 이상 스킬이 있는 클러스터만 표시
            print(f"\n{cluster_name}: {', '.join(skills)}")


if __name__ == "__main__":
    # 모든 테스트 실행
    test_basic_matching()
    test_multiple_job_matching()
    test_growth_path()
    test_hybrid_matching()
    test_skill_clustering()
    
    print("\n" + "=" * 60)
    print("모든 테스트 완료!")
    print("=" * 60)