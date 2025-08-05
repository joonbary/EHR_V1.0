"""
리더/보임자 추천 엔진
신인사제도에 따른 직책 보임 조건 충족 직원 자동 선별 및 추천
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from enum import Enum


class GrowthLevel(Enum):
    """성장 레벨 정의"""
    LV1 = "Lv.1"
    LV2 = "Lv.2"
    LV3 = "Lv.3"
    LV4 = "Lv.4"
    LV5 = "Lv.5"
    
    @classmethod
    def from_string(cls, level_str: str):
        """문자열을 GrowthLevel로 변환"""
        for level in cls:
            if level.value == level_str:
                return level
        return cls.LV1
    
    def __ge__(self, other):
        """레벨 비교 연산자"""
        levels = list(GrowthLevel)
        return levels.index(self) >= levels.index(other)


@dataclass
class LeaderCandidate:
    """리더 후보자 정보"""
    employee_id: str
    name: str
    current_position: str
    department: str
    growth_level: str
    evaluation_grade: str
    match_score: float
    skill_match: Dict[str, float]
    experience_years: int
    qualifications: List[str]
    strengths: List[str]
    development_areas: List[str]
    recommendation_reason: str
    risk_factors: List[str] = None


class LeaderRecommender:
    """리더 추천 엔진"""
    
    def __init__(self):
        self.evaluation_weight = 0.3
        self.skill_weight = 0.3
        self.experience_weight = 0.2
        self.growth_level_weight = 0.2
        
    def evaluate_leadership_readiness(
        self,
        employee: dict,
        target_job: dict,
        evaluation_period: str = "recent_2_quarters"
    ) -> Dict[str, any]:
        """리더십 준비도 평가"""
        
        readiness = {
            'is_qualified': False,
            'qualification_details': {},
            'missing_requirements': [],
            'score_breakdown': {}
        }
        
        # 1. 평가 등급 확인
        eval_check = self._check_evaluation_requirements(
            employee, 
            target_job.get('evaluation_standard', {}),
            evaluation_period
        )
        readiness['qualification_details']['evaluation'] = eval_check
        
        # 2. 성장 레벨 확인
        level_check = self._check_growth_level(
            employee.get('level', 'Lv.1'),
            target_job.get('min_required_level', 'Lv.3')
        )
        readiness['qualification_details']['growth_level'] = level_check
        
        # 3. 필수 스킬 확인
        skill_check = self._check_required_skills(
            employee.get('skills', []),
            target_job.get('required_skills', [])
        )
        readiness['qualification_details']['skills'] = skill_check
        
        # 4. 경력 요건 확인
        exp_check = self._check_experience_requirements(
            employee,
            target_job
        )
        readiness['qualification_details']['experience'] = exp_check
        
        # 전체 자격 판단
        readiness['is_qualified'] = (
            eval_check['is_satisfied'] and
            level_check['is_satisfied'] and
            skill_check['match_rate'] >= 0.7 and
            exp_check['is_satisfied']
        )
        
        # 점수 계산
        readiness['total_score'] = self._calculate_readiness_score(
            readiness['qualification_details']
        )
        
        return readiness
    
    def _check_evaluation_requirements(
        self,
        employee: dict,
        eval_standard: dict,
        period: str
    ) -> dict:
        """평가 요건 확인"""
        result = {
            'is_satisfied': False,
            'current_grade': None,
            'required_grade': eval_standard.get('overall', 'B+'),
            'details': {}
        }
        
        # 평가 기간별 데이터 가져오기
        if period == "recent_2_quarters":
            evaluations = employee.get('recent_evaluations', [])[:2]
        elif period == "annual_average":
            evaluations = employee.get('recent_evaluations', [])[:4]
        else:
            evaluations = [employee.get('recent_evaluation', {})]
        
        if not evaluations:
            return result
        
        # 평균 등급 계산
        grade_values = {
            'S': 5.0, 'A+': 4.5, 'A': 4.0, 
            'B+': 3.5, 'B': 3.0, 'C': 2.0, 'D': 1.0
        }
        
        total_score = 0
        valid_count = 0
        
        for eval in evaluations:
            if eval and 'overall_grade' in eval:
                grade = eval['overall_grade']
                total_score += grade_values.get(grade, 3.0)
                valid_count += 1
        
        if valid_count > 0:
            avg_score = total_score / valid_count
            # 점수를 등급으로 변환
            for grade, score in sorted(grade_values.items(), key=lambda x: -x[1]):
                if avg_score >= score:
                    result['current_grade'] = grade
                    break
        
        # 요건 충족 여부
        if result['current_grade']:
            current_value = grade_values.get(result['current_grade'], 0)
            required_value = grade_values.get(result['required_grade'], 3.5)
            result['is_satisfied'] = current_value >= required_value
        
        # 세부 평가 항목
        if evaluations and evaluations[0]:
            latest_eval = evaluations[0]
            result['details'] = {
                'professionalism': latest_eval.get('professionalism', 'N/A'),
                'contribution': latest_eval.get('contribution', 'N/A'),
                'impact': latest_eval.get('impact', 'N/A')
            }
            
            # 전문성 추가 체크
            if 'professionalism' in eval_standard:
                prof_value = grade_values.get(result['details']['professionalism'], 0)
                prof_required = grade_values.get(eval_standard['professionalism'], 4.0)
                if prof_value < prof_required:
                    result['is_satisfied'] = False
                    result['details']['professionalism_check'] = 'Failed'
        
        return result
    
    def _check_growth_level(self, current_level: str, required_level: str) -> dict:
        """성장 레벨 확인"""
        result = {
            'is_satisfied': False,
            'current_level': current_level,
            'required_level': required_level,
            'gap': 0
        }
        
        try:
            current = GrowthLevel.from_string(current_level)
            required = GrowthLevel.from_string(required_level)
            
            result['is_satisfied'] = current >= required
            
            # 레벨 갭 계산
            levels = list(GrowthLevel)
            current_idx = levels.index(current)
            required_idx = levels.index(required)
            result['gap'] = max(0, required_idx - current_idx)
            
        except Exception:
            result['is_satisfied'] = False
            result['gap'] = -1
        
        return result
    
    def _check_required_skills(
        self, 
        employee_skills: List[str], 
        required_skills: List[str]
    ) -> dict:
        """필수 스킬 확인"""
        if not required_skills:
            return {
                'is_satisfied': True,
                'match_rate': 1.0,
                'matched_skills': [],
                'missing_skills': []
            }
        
        employee_skills_set = set(skill.lower() for skill in employee_skills)
        matched = []
        missing = []
        
        for req_skill in required_skills:
            req_skill_lower = req_skill.lower()
            
            # 정확한 매칭 또는 부분 매칭 확인
            if req_skill_lower in employee_skills_set:
                matched.append(req_skill)
            elif any(req_skill_lower in emp_skill for emp_skill in employee_skills_set):
                matched.append(req_skill)
            elif any(emp_skill in req_skill_lower for emp_skill in employee_skills_set):
                matched.append(req_skill)
            else:
                missing.append(req_skill)
        
        match_rate = len(matched) / len(required_skills) if required_skills else 0
        
        return {
            'is_satisfied': match_rate >= 0.7,
            'match_rate': match_rate,
            'matched_skills': matched,
            'missing_skills': missing
        }
    
    def _check_experience_requirements(
        self, 
        employee: dict, 
        target_job: dict
    ) -> dict:
        """경력 요건 확인"""
        result = {
            'is_satisfied': True,
            'details': {}
        }
        
        # 총 경력 년수
        career_years = employee.get('career_years', 0)
        
        # 리더십 경험
        leadership_exp = employee.get('leadership_experience', {})
        has_leadership = (
            leadership_exp.get('years', 0) > 0 or
            any(keyword in employee.get('current_position', '').lower() 
                for keyword in ['팀장', '리더', '매니저', 'lead', 'manager'])
        )
        
        # 관련 분야 경력
        relevant_exp_years = employee.get('relevant_experience_years', career_years)
        
        result['details'] = {
            'total_years': career_years,
            'relevant_years': relevant_exp_years,
            'has_leadership_experience': has_leadership,
            'leadership_years': leadership_exp.get('years', 0)
        }
        
        # 최소 경력 요건 체크
        min_years = self._extract_min_years_from_job(target_job)
        if min_years > 0:
            result['is_satisfied'] = career_years >= min_years
            result['details']['required_years'] = min_years
        
        # 리더십 경험 필수인 경우
        if '팀장' in target_job.get('name', '') or 'lead' in target_job.get('name', '').lower():
            if not has_leadership:
                result['is_satisfied'] = False
                result['details']['leadership_required'] = True
        
        return result
    
    def _extract_min_years_from_job(self, job: dict) -> int:
        """직무에서 최소 경력 년수 추출"""
        # 직무 설명에서 경력 요건 추출
        qualification = job.get('qualification', '')
        
        import re
        pattern = r'(\d+)년\s*이상'
        match = re.search(pattern, qualification)
        
        if match:
            return int(match.group(1))
        
        # 직책별 기본 경력 요건
        job_name = job.get('name', '').lower()
        if '팀장' in job_name or 'team lead' in job_name:
            return 7
        elif '센터장' in job_name:
            return 10
        elif '매니저' in job_name:
            return 5
        
        return 0
    
    def _calculate_readiness_score(self, qualification_details: dict) -> float:
        """준비도 종합 점수 계산"""
        score = 0
        
        # 평가 점수 (30%)
        eval_detail = qualification_details.get('evaluation', {})
        if eval_detail.get('is_satisfied'):
            score += 30
            # 추가 보너스
            if eval_detail.get('current_grade') in ['S', 'A+']:
                score += 5
        
        # 스킬 매칭 (30%)
        skill_detail = qualification_details.get('skills', {})
        skill_score = skill_detail.get('match_rate', 0) * 30
        score += skill_score
        
        # 성장 레벨 (20%)
        level_detail = qualification_details.get('growth_level', {})
        if level_detail.get('is_satisfied'):
            score += 20
            # 초과 달성 보너스
            if level_detail.get('gap', 0) < 0:
                score += 5
        
        # 경력 (20%)
        exp_detail = qualification_details.get('experience', {})
        if exp_detail.get('is_satisfied'):
            score += 20
            # 리더십 경험 보너스
            if exp_detail.get('details', {}).get('has_leadership_experience'):
                score += 5
        
        return min(100, score)
    
    def generate_recommendation_reason(
        self,
        employee: dict,
        target_job: dict,
        readiness: dict
    ) -> str:
        """추천 사유 생성"""
        reasons = []
        
        # 평가 우수
        eval_detail = readiness['qualification_details'].get('evaluation', {})
        if eval_detail.get('current_grade') in ['S', 'A+', 'A']:
            reasons.append(f"최근 평가 {eval_detail['current_grade']} 등급 획득")
        
        # 스킬 매칭
        skill_detail = readiness['qualification_details'].get('skills', {})
        if skill_detail.get('match_rate', 0) >= 0.8:
            matched_count = len(skill_detail.get('matched_skills', []))
            reasons.append(f"필수 역량 {matched_count}개 보유")
        
        # 경력 우수
        exp_detail = readiness['qualification_details'].get('experience', {}).get('details', {})
        if exp_detail.get('has_leadership_experience'):
            reasons.append(f"리더십 경험 {exp_detail.get('leadership_years', 0)}년 보유")
        elif exp_detail.get('total_years', 0) >= 10:
            reasons.append(f"풍부한 경력 {exp_detail['total_years']}년")
        
        # 성장 잠재력
        if employee.get('growth_trajectory') == 'fast':
            reasons.append("빠른 성장 궤적")
        
        if not reasons:
            reasons.append("종합적으로 적합한 후보")
        
        return " / ".join(reasons)
    
    def identify_risk_factors(
        self,
        employee: dict,
        target_job: dict
    ) -> List[str]:
        """리스크 요인 식별"""
        risks = []
        
        # 스킬 갭이 큰 경우
        employee_skills = set(skill.lower() for skill in employee.get('skills', []))
        required_skills = set(skill.lower() for skill in target_job.get('required_skills', []))
        skill_gap = len(required_skills - employee_skills)
        
        if skill_gap > 2:
            risks.append(f"핵심 역량 {skill_gap}개 부족")
        
        # 리더십 경험 부족
        if '팀장' in target_job.get('name', '') and not employee.get('leadership_experience', {}).get('years', 0):
            risks.append("리더십 경험 부재")
        
        # 최근 평가 하락 추세
        recent_evals = employee.get('recent_evaluations', [])
        if len(recent_evals) >= 2:
            grade_values = {'S': 5, 'A+': 4.5, 'A': 4, 'B+': 3.5, 'B': 3, 'C': 2, 'D': 1}
            if recent_evals[0].get('overall_grade') and recent_evals[1].get('overall_grade'):
                recent_score = grade_values.get(recent_evals[0]['overall_grade'], 3)
                prev_score = grade_values.get(recent_evals[1]['overall_grade'], 3)
                if recent_score < prev_score:
                    risks.append("최근 평가 하락 추세")
        
        # 부서 이동 빈번
        if employee.get('department_changes', 0) > 3:
            risks.append("잦은 부서 이동")
        
        return risks


def recommend_leader_candidates(
    target_job: dict,
    all_employees: List[dict],
    min_evaluation_grade: str = "B+",
    min_growth_level: str = "Lv.3",
    top_n: int = 5,
    exclude_low_performers: bool = True
) -> List[dict]:
    """
    리더 후보자 추천 메인 함수
    
    Args:
        target_job: 보임 대상 직무기술서
        all_employees: 전체 직원 리스트
        min_evaluation_grade: 최소 평가 등급
        min_growth_level: 최소 성장 레벨
        top_n: 추천 인원 수
        exclude_low_performers: 저성과자 제외 여부
    
    Returns:
        추천 후보자 리스트
    """
    recommender = LeaderRecommender()
    candidates = []
    
    # 평가 기준 설정
    if 'evaluation_standard' not in target_job:
        target_job['evaluation_standard'] = {
            'overall': min_evaluation_grade
        }
    
    if 'min_required_level' not in target_job:
        target_job['min_required_level'] = min_growth_level
    
    for employee in all_employees:
        # 저성과자 제외
        if exclude_low_performers:
            recent_eval = employee.get('recent_evaluation', {})
            if recent_eval.get('overall_grade') in ['C', 'D']:
                continue
        
        # 리더십 준비도 평가
        readiness = recommender.evaluate_leadership_readiness(
            employee,
            target_job
        )
        
        # 자격 충족자만 포함
        if readiness['is_qualified']:
            # 추천 사유 생성
            recommendation_reason = recommender.generate_recommendation_reason(
                employee,
                target_job,
                readiness
            )
            
            # 리스크 요인 식별
            risk_factors = recommender.identify_risk_factors(
                employee,
                target_job
            )
            
            # 후보자 객체 생성
            candidate = LeaderCandidate(
                employee_id=employee['employee_id'],
                name=employee['name'],
                current_position=employee.get('position', ''),
                department=employee.get('department', ''),
                growth_level=employee.get('level', 'Lv.1'),
                evaluation_grade=employee.get('recent_evaluation', {}).get('overall_grade', 'N/A'),
                match_score=readiness['total_score'],
                skill_match=readiness['qualification_details']['skills'],
                experience_years=employee.get('career_years', 0),
                qualifications=employee.get('certifications', []),
                strengths=readiness['qualification_details']['skills'].get('matched_skills', []),
                development_areas=readiness['qualification_details']['skills'].get('missing_skills', []),
                recommendation_reason=recommendation_reason,
                risk_factors=risk_factors
            )
            
            candidates.append({
                'employee_id': candidate.employee_id,
                'name': candidate.name,
                'current_position': candidate.current_position,
                'department': candidate.department,
                'growth_level': candidate.growth_level,
                'evaluation_grade': candidate.evaluation_grade,
                'match_score': candidate.match_score,
                'skill_match_rate': candidate.skill_match.get('match_rate', 0),
                'matched_skills': candidate.skill_match.get('matched_skills', []),
                'missing_skills': candidate.skill_match.get('missing_skills', []),
                'experience_years': candidate.experience_years,
                'qualifications': candidate.qualifications,
                'recommendation_reason': candidate.recommendation_reason,
                'risk_factors': candidate.risk_factors,
                'readiness_details': readiness
            })
    
    # 점수 기준 내림차순 정렬
    candidates.sort(key=lambda x: x['match_score'], reverse=True)
    
    # 상위 N명 반환
    return candidates[:top_n]


def analyze_organization_talent_pool(
    all_employees: List[dict],
    job_profiles: List[dict],
    min_evaluation_grade: str = "B+",
    min_growth_level: str = "Lv.3"
) -> Dict[str, any]:
    """조직별 인재 풀 분석"""
    
    # 부서별 집계
    dept_pools = defaultdict(lambda: {
        'total_employees': 0,
        'qualified_for_team_lead': [],
        'qualified_for_center_lead': [],
        'high_potentials': [],
        'skill_distribution': defaultdict(int)
    })
    
    # 직무별 적격자 찾기
    team_lead_job = next((j for j in job_profiles if '팀장' in j.get('name', '')), None)
    center_lead_job = next((j for j in job_profiles if '센터장' in j.get('name', '')), None)
    
    for employee in all_employees:
        dept = employee.get('department', 'Unknown')
        dept_pools[dept]['total_employees'] += 1
        
        # 스킬 분포
        for skill in employee.get('skills', []):
            dept_pools[dept]['skill_distribution'][skill] += 1
        
        # 고성과자 식별
        if employee.get('recent_evaluation', {}).get('overall_grade') in ['S', 'A+']:
            dept_pools[dept]['high_potentials'].append({
                'id': employee['employee_id'],
                'name': employee['name'],
                'grade': employee.get('recent_evaluation', {}).get('overall_grade')
            })
        
        # 팀장 적격자
        if team_lead_job:
            team_lead_candidates = recommend_leader_candidates(
                team_lead_job,
                [employee],
                min_evaluation_grade=min_evaluation_grade,
                min_growth_level=min_growth_level,
                top_n=1
            )
            if team_lead_candidates:
                dept_pools[dept]['qualified_for_team_lead'].append({
                    'id': employee['employee_id'],
                    'name': employee['name'],
                    'score': team_lead_candidates[0]['match_score']
                })
        
        # 센터장 적격자
        if center_lead_job:
            center_lead_candidates = recommend_leader_candidates(
                center_lead_job,
                [employee],
                min_evaluation_grade="A",
                min_growth_level="Lv.4",
                top_n=1
            )
            if center_lead_candidates:
                dept_pools[dept]['qualified_for_center_lead'].append({
                    'id': employee['employee_id'],
                    'name': employee['name'],
                    'score': center_lead_candidates[0]['match_score']
                })
    
    # 부서별 통계 생성
    summary = {
        'total_departments': len(dept_pools),
        'department_details': {},
        'organization_stats': {
            'total_team_lead_candidates': 0,
            'total_center_lead_candidates': 0,
            'total_high_potentials': 0
        }
    }
    
    for dept, pool in dept_pools.items():
        # 상위 3명씩만 포함
        pool['qualified_for_team_lead'].sort(key=lambda x: x['score'], reverse=True)
        pool['qualified_for_center_lead'].sort(key=lambda x: x['score'], reverse=True)
        
        summary['department_details'][dept] = {
            'total_employees': pool['total_employees'],
            'team_lead_candidates': pool['qualified_for_team_lead'][:3],
            'center_lead_candidates': pool['qualified_for_center_lead'][:3],
            'high_potentials': pool['high_potentials'][:5],
            'top_skills': sorted(
                pool['skill_distribution'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
        
        # 전체 통계
        summary['organization_stats']['total_team_lead_candidates'] += len(pool['qualified_for_team_lead'])
        summary['organization_stats']['total_center_lead_candidates'] += len(pool['qualified_for_center_lead'])
        summary['organization_stats']['total_high_potentials'] += len(pool['high_potentials'])
    
    return summary


# 사용 예시
if __name__ == "__main__":
    # 팀장 직무
    team_lead_job = {
        "job_id": "uuid-팀장직무",
        "name": "팀장",
        "required_skills": ["조직 리더십", "성과관리", "전략 실행력", "커뮤니케이션"],
        "min_required_level": "Lv.3",
        "evaluation_standard": {
            "overall": "B+",
            "professionalism": "A"
        },
        "qualification": "경력 7년 이상, 리더십 경험 필수"
    }
    
    # 샘플 직원 데이터
    sample_employees = [
        {
            "employee_id": "e001",
            "name": "김성과",
            "position": "과장",
            "department": "영업1팀",
            "level": "Lv.4",
            "career_years": 8,
            "skills": ["조직 리더십", "성과관리", "프로젝트 관리", "커뮤니케이션"],
            "certifications": ["PMP", "리더십 과정 수료"],
            "recent_evaluation": {
                "overall_grade": "A",
                "professionalism": "A+",
                "contribution": "Top 20%",
                "impact": "조직 간"
            },
            "recent_evaluations": [
                {"overall_grade": "A", "professionalism": "A+"},
                {"overall_grade": "A", "professionalism": "A"}
            ],
            "leadership_experience": {
                "years": 2,
                "type": "TF 리더"
            }
        },
        {
            "employee_id": "e002",
            "name": "이우수",
            "position": "대리",
            "department": "영업1팀",
            "level": "Lv.3",
            "career_years": 5,
            "skills": ["성과관리", "데이터 분석", "전략 기획"],
            "certifications": ["데이터 분석 전문가"],
            "recent_evaluation": {
                "overall_grade": "B+",
                "professionalism": "A",
                "contribution": "Top 50%",
                "impact": "조직 내"
            },
            "recent_evaluations": [
                {"overall_grade": "B+", "professionalism": "A"},
                {"overall_grade": "B+", "professionalism": "B+"}
            ]
        },
        {
            "employee_id": "e003",
            "name": "박탁월",
            "position": "차장",
            "department": "기획팀",
            "level": "Lv.5",
            "career_years": 12,
            "skills": ["조직 리더십", "전략 실행력", "성과관리", "혁신 추진", "커뮤니케이션"],
            "certifications": ["MBA", "6시그마 블랙벨트"],
            "recent_evaluation": {
                "overall_grade": "S",
                "professionalism": "S",
                "contribution": "Top 10%",
                "impact": "전사"
            },
            "recent_evaluations": [
                {"overall_grade": "S", "professionalism": "S"},
                {"overall_grade": "A+", "professionalism": "A+"}
            ],
            "leadership_experience": {
                "years": 5,
                "type": "팀장 대행"
            }
        }
    ]
    
    # 리더 후보 추천
    print("=== 팀장 후보 추천 ===\n")
    candidates = recommend_leader_candidates(
        target_job=team_lead_job,
        all_employees=sample_employees,
        min_evaluation_grade="B+",
        min_growth_level="Lv.3",
        top_n=3
    )
    
    for idx, candidate in enumerate(candidates, 1):
        print(f"{idx}. {candidate['name']} ({candidate['department']} {candidate['current_position']})")
        print(f"   매칭 점수: {candidate['match_score']:.1f}점")
        print(f"   평가 등급: {candidate['evaluation_grade']} / 성장 레벨: {candidate['growth_level']}")
        print(f"   추천 사유: {candidate['recommendation_reason']}")
        if candidate['risk_factors']:
            print(f"   주의 사항: {', '.join(candidate['risk_factors'])}")
        print(f"   보유 역량: {', '.join(candidate['matched_skills'])}")
        if candidate['missing_skills']:
            print(f"   개발 필요: {', '.join(candidate['missing_skills'])}")
        print()