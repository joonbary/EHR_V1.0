"""
성과평가 결과를 반영한 직무-직원 매칭 확장 모듈
기존 매칭 결과에 평가 등급을 반영하여 더 정교한 적합도 계산
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from .matching_engine import match_profile, ProfileMatcher


@dataclass
class EvaluationScore:
    """평가 점수 환산 결과"""
    professionalism_bonus: int = 0
    contribution_bonus: int = 0
    impact_bonus: int = 0
    overall_grade_bonus: int = 0
    total_bonus: int = 0
    penalty_reason: Optional[str] = None
    is_eligible: bool = True  # 자격 여부


class EvaluationScoreCalculator:
    """평가 결과 점수 계산기"""
    
    # 평가 등급별 점수 매핑
    PROFESSIONALISM_SCORES = {
        'S': 20,
        'A+': 15,
        'A': 15,
        'B+': 10,
        'B': 5,
        'C': 0,
        'D': -10
    }
    
    CONTRIBUTION_SCORES = {
        'Top 10%': 15,
        'Top 20%': 10,
        'Top 10~20%': 10,  # 별칭
        'Top 20~50%': 7,
        'Top 50~80%': 5,
        'Top 20~80%': 5,   # 범위 통합
        'Bottom 20%': -5,
        'Bottom 10%': -10
    }
    
    IMPACT_SCORES = {
        '전사': 10,
        '조직 간': 5,
        '조직 내': 0,
        '개인': -5
    }
    
    OVERALL_GRADE_SCORES = {
        'S': 10,
        'A+': 5,
        'A': 3,
        'B+': 0,
        'B': 0,
        'C': -20,
        'D': -30
    }
    
    @classmethod
    def calculate_evaluation_score(cls, evaluation: Dict[str, str]) -> EvaluationScore:
        """평가 결과를 점수로 환산"""
        score = EvaluationScore()
        
        # 전문성 점수
        professionalism = evaluation.get('professionalism', 'B')
        score.professionalism_bonus = cls.PROFESSIONALISM_SCORES.get(professionalism, 0)
        
        # 기여도 점수
        contribution = evaluation.get('contribution', 'Top 50~80%')
        score.contribution_bonus = cls.CONTRIBUTION_SCORES.get(contribution, 0)
        
        # 영향력 점수
        impact = evaluation.get('impact', '조직 내')
        score.impact_bonus = cls.IMPACT_SCORES.get(impact, 0)
        
        # 종합등급 점수
        overall_grade = evaluation.get('overall_grade', 'B+')
        score.overall_grade_bonus = cls.OVERALL_GRADE_SCORES.get(overall_grade, 0)
        
        # 총 보너스 점수
        score.total_bonus = (
            score.professionalism_bonus +
            score.contribution_bonus +
            score.impact_bonus +
            score.overall_grade_bonus
        )
        
        # 자격 여부 판단 (C, D 등급은 부적격 처리 옵션)
        if overall_grade in ['C', 'D']:
            score.is_eligible = False
            score.penalty_reason = f"종합등급 {overall_grade}로 인한 자격 제한"
        
        # 극히 낮은 기여도도 부적격 처리
        if contribution in ['Bottom 10%', 'Bottom 20%']:
            score.is_eligible = False
            score.penalty_reason = f"기여도 {contribution}로 인한 자격 제한"
        
        return score


def match_profile_with_evaluation(
    job_profile: dict, 
    employee_profile: dict,
    exclude_low_performers: bool = True,
    evaluation_weight: float = 0.3
) -> dict:
    """
    평가 결과를 반영한 직무-직원 매칭
    
    Args:
        job_profile: 직무 프로파일
        employee_profile: 직원 프로파일 (recent_evaluation 포함)
        exclude_low_performers: 저성과자 자동 제외 여부
        evaluation_weight: 평가 결과 반영 비중 (0-1)
    
    Returns:
        평가 보정된 매칭 결과
    """
    
    # 기본 매칭 수행
    base_result = match_profile(job_profile, employee_profile)
    
    # 평가 정보 확인
    evaluation = employee_profile.get('recent_evaluation', {})
    
    if not evaluation:
        # 평가 정보가 없으면 기본 결과 반환
        base_result['evaluation_applied'] = False
        base_result['evaluation_comment'] = "최근 평가 정보 없음"
        return base_result
    
    # 평가 점수 계산
    eval_score = EvaluationScoreCalculator.calculate_evaluation_score(evaluation)
    
    # 저성과자 제외 옵션 적용
    if exclude_low_performers and not eval_score.is_eligible:
        base_result['match_score'] = 0
        base_result['is_eligible'] = False
        base_result['exclusion_reason'] = eval_score.penalty_reason
        base_result['evaluation_details'] = eval_score.__dict__
        return base_result
    
    # 평가 보너스 적용
    original_score = base_result['match_score']
    
    # 가중치를 적용한 보너스 계산
    weighted_bonus = eval_score.total_bonus * evaluation_weight
    
    # 최종 점수 계산 (0-100 범위로 제한)
    final_score = max(0, min(100, original_score + weighted_bonus))
    
    # 결과 업데이트
    base_result['match_score'] = round(final_score, 2)
    base_result['original_match_score'] = original_score
    base_result['evaluation_applied'] = True
    base_result['evaluation_bonus'] = round(weighted_bonus, 2)
    base_result['evaluation_details'] = {
        'professionalism': {
            'grade': evaluation.get('professionalism'),
            'bonus': eval_score.professionalism_bonus
        },
        'contribution': {
            'grade': evaluation.get('contribution'),
            'bonus': eval_score.contribution_bonus
        },
        'impact': {
            'grade': evaluation.get('impact'),
            'bonus': eval_score.impact_bonus
        },
        'overall_grade': {
            'grade': evaluation.get('overall_grade'),
            'bonus': eval_score.overall_grade_bonus
        },
        'total_bonus': eval_score.total_bonus,
        'weighted_bonus': round(weighted_bonus, 2)
    }
    
    # 평가 기반 추천사항 추가
    evaluation_recommendations = _generate_evaluation_recommendations(
        evaluation, eval_score, job_profile
    )
    base_result['recommendations'].extend(evaluation_recommendations)
    
    return base_result


def _generate_evaluation_recommendations(
    evaluation: dict, 
    eval_score: EvaluationScore, 
    job_profile: dict
) -> List[str]:
    """평가 결과 기반 추천사항 생성"""
    recommendations = []
    
    # 전문성이 낮은 경우
    if evaluation.get('professionalism') in ['C', 'D']:
        recommendations.append(
            f"{job_profile.get('job_name', '해당 직무')}에 필요한 전문성 향상 필요"
        )
    
    # 기여도가 낮은 경우
    if eval_score.contribution_bonus <= 0:
        recommendations.append(
            "목표 달성률 및 업무 기여도 개선 필요"
        )
    
    # 영향력이 개인 수준인 경우
    if evaluation.get('impact') == '개인':
        recommendations.append(
            "조직 차원의 영향력 확대를 위한 프로젝트 참여 권장"
        )
    
    # 종합등급이 우수한 경우
    if evaluation.get('overall_grade') in ['S', 'A+']:
        recommendations.append(
            "우수한 성과를 바탕으로 상위 직무 도전 가능"
        )
    
    return recommendations


def match_multiple_profiles_with_evaluation(
    job_profiles: List[dict], 
    employee_profile: dict,
    top_n: int = 5,
    min_score: float = 60.0,
    exclude_low_performers: bool = True,
    evaluation_weight: float = 0.3
) -> List[dict]:
    """
    평가 결과를 반영한 복수 직무 매칭
    """
    results = []
    
    for job_profile in job_profiles:
        match_result = match_profile_with_evaluation(
            job_profile, 
            employee_profile,
            exclude_low_performers=exclude_low_performers,
            evaluation_weight=evaluation_weight
        )
        
        # 자격 미달이 아니고 최소 점수 이상인 경우만 포함
        if match_result.get('is_eligible', True) and match_result['match_score'] >= min_score:
            results.append({
                'job_id': job_profile.get('job_id'),
                'job_name': job_profile.get('job_name', 'Unknown'),
                **match_result
            })
    
    # 점수 기준 내림차순 정렬
    results.sort(key=lambda x: x['match_score'], reverse=True)
    
    return results[:top_n]


def analyze_promotion_readiness(
    employee_profile: dict,
    target_job_profile: dict,
    min_evaluation_grade: str = 'B+'
) -> dict:
    """
    승진 준비도 분석 (평가 결과 중심)
    
    Args:
        employee_profile: 직원 프로파일
        target_job_profile: 목표 직무 프로파일
        min_evaluation_grade: 최소 요구 평가 등급
    
    Returns:
        승진 준비도 분석 결과
    """
    
    # 기본 매칭 with 평가
    match_result = match_profile_with_evaluation(
        target_job_profile, 
        employee_profile,
        exclude_low_performers=False  # 분석 목적이므로 제외하지 않음
    )
    
    evaluation = employee_profile.get('recent_evaluation', {})
    readiness = {
        'is_ready': False,
        'match_score': match_result['match_score'],
        'requirements': [],
        'strengths': [],
        'improvement_areas': []
    }
    
    # 평가 등급 체크
    overall_grade = evaluation.get('overall_grade', 'N/A')
    grade_order = ['S', 'A+', 'A', 'B+', 'B', 'C', 'D']
    
    if overall_grade in grade_order:
        min_grade_index = grade_order.index(min_evaluation_grade)
        current_grade_index = grade_order.index(overall_grade)
        
        if current_grade_index <= min_grade_index:
            readiness['requirements'].append(f"평가 등급 요건 충족 ({overall_grade} >= {min_evaluation_grade})")
            readiness['strengths'].append("평가 등급 우수")
        else:
            readiness['requirements'].append(f"평가 등급 미달 ({overall_grade} < {min_evaluation_grade})")
            readiness['improvement_areas'].append("평가 등급 향상 필요")
    
    # 전문성 체크
    if evaluation.get('professionalism') in ['S', 'A+', 'A']:
        readiness['strengths'].append("높은 전문성 보유")
    else:
        readiness['improvement_areas'].append("전문성 향상 필요")
    
    # 기여도/영향력 체크
    if evaluation.get('contribution') in ['Top 10%', 'Top 20%']:
        readiness['strengths'].append("우수한 업무 기여도")
    
    if evaluation.get('impact') in ['전사', '조직 간']:
        readiness['strengths'].append("조직 차원의 영향력 보유")
    
    # 스킬 매칭 체크
    if match_result['skill_match']['basic_skills']['score'] >= 80:
        readiness['strengths'].append("기본 역량 충분")
    else:
        readiness['improvement_areas'].append("기본 스킬 보완 필요")
    
    # 종합 판단
    readiness['is_ready'] = (
        len(readiness['improvement_areas']) == 0 and
        match_result['match_score'] >= 75 and
        overall_grade in ['S', 'A+', 'A', 'B+']
    )
    
    if readiness['is_ready']:
        readiness['recommendation'] = "승진 준비 완료 - 적극 추천"
    elif match_result['match_score'] >= 60:
        readiness['recommendation'] = "단기 준비 후 승진 가능"
    else:
        readiness['recommendation'] = "중장기 역량 개발 필요"
    
    return readiness


# 평가 등급 변환 유틸리티
class EvaluationGradeConverter:
    """다양한 평가 체계 간 변환"""
    
    # 5단계 -> 문자 등급 변환
    NUMERIC_TO_LETTER = {
        5: 'S',
        4: 'A',
        3: 'B+',
        2: 'B',
        1: 'C'
    }
    
    # 백분율 -> 기여도 레벨 변환
    @staticmethod
    def percentage_to_contribution_level(percentage: float) -> str:
        if percentage >= 90:
            return 'Top 10%'
        elif percentage >= 80:
            return 'Top 20%'
        elif percentage >= 50:
            return 'Top 20~50%'
        elif percentage >= 20:
            return 'Top 50~80%'
        else:
            return 'Bottom 20%'
    
    # 점수 -> 영향력 레벨 변환
    @staticmethod
    def score_to_impact_level(score: int, max_score: int = 100) -> str:
        ratio = score / max_score
        if ratio >= 0.9:
            return '전사'
        elif ratio >= 0.7:
            return '조직 간'
        elif ratio >= 0.4:
            return '조직 내'
        else:
            return '개인'


# 사용 예시
if __name__ == "__main__":
    # 평가 정보가 포함된 직원 프로파일
    employee_with_evaluation = {
        "employee_id": "e001",
        "name": "김우수",
        "career_years": 5,
        "certifications": ["PMP", "정보처리기사"],
        "skills": ["프로젝트관리", "리스크관리", "일정관리"],
        "recent_evaluation": {
            "professionalism": "A",
            "contribution": "Top 20%",
            "impact": "조직 간",
            "overall_grade": "A"
        }
    }
    
    # 평가 정보가 부족한 직원
    employee_low_performer = {
        "employee_id": "e002",
        "name": "박개선",
        "career_years": 3,
        "skills": ["문서작성", "데이터입력"],
        "recent_evaluation": {
            "professionalism": "C",
            "contribution": "Bottom 20%",
            "impact": "개인",
            "overall_grade": "C"
        }
    }
    
    # 목표 직무
    target_job = {
        "job_id": "j001",
        "job_name": "프로젝트 매니저",
        "basic_skills": ["프로젝트관리", "리스크관리", "일정관리", "예산관리"],
        "applied_skills": ["이해관계자관리", "품질관리", "변경관리"]
    }
    
    print("=== 평가 반영 매칭 테스트 ===\n")
    
    # 우수 직원 매칭
    print(f"1. {employee_with_evaluation['name']} - {target_job['job_name']} 매칭")
    result1 = match_profile_with_evaluation(target_job, employee_with_evaluation)
    print(f"   기본 매칭 점수: {result1['original_match_score']}%")
    print(f"   평가 보너스: {result1['evaluation_bonus']}점")
    print(f"   최종 매칭 점수: {result1['match_score']}%")
    print(f"   평가 상세:")
    for key, detail in result1['evaluation_details'].items():
        if isinstance(detail, dict):
            print(f"     - {key}: {detail['grade']} (보너스: {detail['bonus']})")
    
    # 저성과자 매칭
    print(f"\n2. {employee_low_performer['name']} - {target_job['job_name']} 매칭")
    result2 = match_profile_with_evaluation(target_job, employee_low_performer)
    if result2.get('is_eligible', True):
        print(f"   최종 매칭 점수: {result2['match_score']}%")
    else:
        print(f"   자격 미달: {result2.get('exclusion_reason')}")
    
    # 승진 준비도 분석
    print(f"\n3. {employee_with_evaluation['name']}의 승진 준비도 분석")
    readiness = analyze_promotion_readiness(employee_with_evaluation, target_job)
    print(f"   승진 준비 여부: {'준비됨' if readiness['is_ready'] else '준비 중'}")
    print(f"   강점: {', '.join(readiness['strengths'])}")
    if readiness['improvement_areas']:
        print(f"   개선 필요: {', '.join(readiness['improvement_areas'])}")
    print(f"   추천사항: {readiness['recommendation']}")