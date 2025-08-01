"""
직무-직원 프로파일 매칭 엔진
직무기술서와 직원 프로파일 간의 유사도를 계산하여 매칭 점수와 갭 분석을 제공
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class MatchingResult:
    """매칭 결과를 담는 데이터 클래스"""
    match_score: float  # 0-100
    skill_match: Dict[str, Any]
    qualification_match: Dict[str, Any]
    gaps: Dict[str, List[str]]
    recommendations: List[str]
    details: Dict[str, Any]


class ProfileMatcher:
    """프로파일 매칭을 위한 유틸리티 클래스"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """텍스트 정규화 (소문자 변환, 공백 정리)"""
        return ' '.join(text.lower().strip().split())
    
    @staticmethod
    def extract_years_from_text(text: str) -> Optional[int]:
        """텍스트에서 연수 추출 (예: "3년 이상" -> 3)"""
        pattern = r'(\d+)\s*년'
        match = re.search(pattern, text)
        return int(match.group(1)) if match else None
    
    @staticmethod
    def calculate_similarity(list1: List[str], list2: List[str]) -> Tuple[float, List[str], List[str]]:
        """두 리스트 간의 유사도 계산"""
        set1 = set(ProfileMatcher.normalize_text(item) for item in list1)
        set2 = set(ProfileMatcher.normalize_text(item) for item in list2)
        
        matched = set1.intersection(set2)
        total = set1.union(set2)
        
        similarity = len(matched) / len(total) * 100 if total else 0
        missing = list(set1 - set2)
        extra = list(set2 - set1)
        
        return similarity, missing, extra
    
    @staticmethod
    def fuzzy_match(text1: str, text2: str, threshold: float = 0.7) -> bool:
        """간단한 fuzzy matching (임계값 기반)"""
        text1_norm = ProfileMatcher.normalize_text(text1)
        text2_norm = ProfileMatcher.normalize_text(text2)
        
        # 단어 단위 매칭
        words1 = set(text1_norm.split())
        words2 = set(text2_norm.split())
        
        if not words1 or not words2:
            return False
            
        overlap = len(words1.intersection(words2))
        total = max(len(words1), len(words2))
        
        return (overlap / total) >= threshold


def match_profile(job_profile: dict, employee_profile: dict) -> dict:
    """
    직무 프로파일과 직원 프로파일 간의 매칭 점수 계산
    
    Args:
        job_profile: 직무기술서 정보
        employee_profile: 직원 프로파일 정보
    
    Returns:
        매칭 결과 (점수, 스킬 매치, 자격요건 매치, 갭, 추천사항)
    """
    
    # 1. 기본 스킬 매칭
    employee_skills = (
        employee_profile.get('certifications', []) + 
        employee_profile.get('completed_courses', []) +
        employee_profile.get('skills', [])
    )
    
    basic_similarity, basic_missing, _ = ProfileMatcher.calculate_similarity(
        job_profile.get('basic_skills', []),
        employee_skills
    )
    
    # 2. 응용 스킬 매칭
    applied_similarity, applied_missing, _ = ProfileMatcher.calculate_similarity(
        job_profile.get('applied_skills', []),
        employee_skills
    )
    
    # 3. 자격요건 매칭
    qualification_score = 100.0
    qualification_details = {}
    
    # 경력 연수 체크
    required_years = ProfileMatcher.extract_years_from_text(
        job_profile.get('qualification', '')
    )
    if required_years:
        employee_years = employee_profile.get('career_years', 0)
        if employee_years >= required_years:
            qualification_details['career_years'] = {
                'required': required_years,
                'actual': employee_years,
                'satisfied': True
            }
        else:
            qualification_score -= 30
            qualification_details['career_years'] = {
                'required': required_years,
                'actual': employee_years,
                'satisfied': False
            }
    
    # 4. 전체 매칭 점수 계산 (가중치 적용)
    skill_score = (basic_similarity * 0.6 + applied_similarity * 0.4)
    total_score = (skill_score * 0.7 + qualification_score * 0.3)
    
    # 5. 갭 분석
    gaps = {
        'basic_skills': basic_missing,
        'applied_skills': applied_missing,
        'qualification': [] if qualification_score == 100 else ['경력 연수 부족']
    }
    
    # 6. 추천사항 생성
    recommendations = []
    if basic_missing:
        recommendations.append(f"다음 기본 스킬 습득 필요: {', '.join(basic_missing[:3])}")
    if applied_missing:
        recommendations.append(f"다음 응용 스킬 개발 권장: {', '.join(applied_missing[:3])}")
    if qualification_score < 100:
        recommendations.append("추가 경력 축적 필요")
    
    # 7. 결과 반환
    return {
        'match_score': round(total_score, 2),
        'skill_match': {
            'basic_skills': {
                'score': round(basic_similarity, 2),
                'missing': basic_missing,
                'matched_count': len(job_profile.get('basic_skills', [])) - len(basic_missing)
            },
            'applied_skills': {
                'score': round(applied_similarity, 2),
                'missing': applied_missing,
                'matched_count': len(job_profile.get('applied_skills', [])) - len(applied_missing)
            }
        },
        'qualification_match': qualification_details,
        'gaps': gaps,
        'recommendations': recommendations
    }


def match_multiple_profiles(job_profiles: List[dict], employee_profile: dict, 
                          top_n: int = 5, min_score: float = 60.0) -> List[dict]:
    """
    여러 직무에 대해 직원 프로파일 매칭 수행
    
    Args:
        job_profiles: 직무 프로파일 리스트
        employee_profile: 직원 프로파일
        top_n: 상위 N개 결과 반환
        min_score: 최소 매칭 점수 임계값
    
    Returns:
        매칭 결과 리스트 (점수 내림차순 정렬)
    """
    results = []
    
    for job_profile in job_profiles:
        match_result = match_profile(job_profile, employee_profile)
        if match_result['match_score'] >= min_score:
            results.append({
                'job_id': job_profile.get('job_id'),
                'job_name': job_profile.get('job_name', 'Unknown'),
                **match_result
            })
    
    # 점수 기준 내림차순 정렬
    results.sort(key=lambda x: x['match_score'], reverse=True)
    
    return results[:top_n]


def recommend_growth_path(current_profile: dict, target_profiles: List[dict]) -> List[dict]:
    """
    현재 프로파일에서 목표 직무까지의 성장 경로 추천
    
    Args:
        current_profile: 현재 직원 프로파일
        target_profiles: 목표 직무 프로파일 리스트
    
    Returns:
        성장 경로 추천 리스트
    """
    recommendations = []
    
    for target in target_profiles:
        match_result = match_profile(target, current_profile)
        
        # 갭이 적은 순서대로 단계별 성장 경로 제시
        total_gaps = (
            len(match_result['gaps']['basic_skills']) + 
            len(match_result['gaps']['applied_skills'])
        )
        
        recommendations.append({
            'target_job': target.get('job_id'),
            'current_match_score': match_result['match_score'],
            'total_skill_gaps': total_gaps,
            'priority_skills': match_result['gaps']['basic_skills'][:3],
            'estimated_readiness': 'High' if match_result['match_score'] >= 80 else 
                                 'Medium' if match_result['match_score'] >= 60 else 'Low'
        })
    
    # 갭이 적은 순서로 정렬
    recommendations.sort(key=lambda x: (x['total_skill_gaps'], -x['current_match_score']))
    
    return recommendations


# 실행 예시
if __name__ == "__main__":
    # 샘플 데이터
    job_profile = {
        "job_id": "uuid-HRM",
        "job_name": "HRM",
        "role_responsibility": "인사제도 기획 및 운영",
        "qualification": "인사 관련 경력 3년 이상",
        "basic_skills": ["노동법", "내부규정이해", "인사제도", "조직문화"],
        "applied_skills": ["제도기획", "노사관리", "데이터기반 인사운영", "HR Analytics"]
    }
    
    employee_profile = {
        "employee_id": "e001",
        "name": "김직원",
        "career_years": 4,
        "certifications": ["노동법자격증"],
        "completed_courses": ["내부규정", "노사관리기초", "조직문화"],
        "skills": ["인사제도", "데이터분석"]
    }
    
    # 단일 매칭 실행
    print("=== 직무-직원 프로파일 매칭 결과 ===\n")
    result = match_profile(job_profile, employee_profile)
    
    print(f"전체 매칭 점수: {result['match_score']}%\n")
    
    print("스킬 매칭 상세:")
    print(f"- 기본 스킬: {result['skill_match']['basic_skills']['score']}%")
    print(f"  매칭된 스킬 수: {result['skill_match']['basic_skills']['matched_count']}")
    if result['skill_match']['basic_skills']['missing']:
        print(f"  부족한 스킬: {', '.join(result['skill_match']['basic_skills']['missing'])}")
    
    print(f"\n- 응용 스킬: {result['skill_match']['applied_skills']['score']}%")
    print(f"  매칭된 스킬 수: {result['skill_match']['applied_skills']['matched_count']}")
    if result['skill_match']['applied_skills']['missing']:
        print(f"  부족한 스킬: {', '.join(result['skill_match']['applied_skills']['missing'])}")
    
    if result['qualification_match']:
        print("\n자격요건 매칭:")
        for key, value in result['qualification_match'].items():
            print(f"- {key}: {'충족' if value['satisfied'] else '미충족'} "
                  f"(요구: {value['required']}년, 보유: {value['actual']}년)")
    
    print("\n추천사항:")
    for idx, rec in enumerate(result['recommendations'], 1):
        print(f"{idx}. {rec}")
    
    # 여러 직무에 대한 매칭 (확장 예시)
    print("\n\n=== 추천 직무 (복수 매칭) ===")
    
    job_profiles = [
        job_profile,
        {
            "job_id": "uuid-IT-PLAN",
            "job_name": "IT기획",
            "qualification": "IT 관련 경력 2년 이상",
            "basic_skills": ["데이터분석", "프로젝트관리", "IT전략"],
            "applied_skills": ["시스템설계", "프로세스개선"]
        },
        {
            "job_id": "uuid-DATA-ANALYST",
            "job_name": "데이터분석가",
            "qualification": "데이터 분석 경력 1년 이상",
            "basic_skills": ["데이터분석", "통계", "SQL"],
            "applied_skills": ["머신러닝", "데이터시각화"]
        }
    ]
    
    matches = match_multiple_profiles(job_profiles, employee_profile, top_n=3)
    
    for idx, match in enumerate(matches, 1):
        print(f"\n{idx}. {match['job_name']} (매칭점수: {match['match_score']}%)")
        print(f"   - 기본스킬 매칭: {match['skill_match']['basic_skills']['score']}%")
        print(f"   - 응용스킬 매칭: {match['skill_match']['applied_skills']['score']}%")