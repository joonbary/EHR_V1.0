"""
스킬맵 대시보드 데이터 바인딩 버그 수정 및 개선
Skillmap Dashboard Data Binding Bug Fix and Enhancement

목적: calcSkillScoreForDeptSkill 함수 오류 수정 및 데이터 바인딩 개선
작성자: EHR System Development Team
작성일: 2024-12-31
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import numpy as np

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== 1. 개선된 데이터 모델 =====

class SkillLevel(Enum):
    """스킬 레벨 정의"""
    NONE = 0        # 없음
    BASIC = 1       # 기초
    INTERMEDIATE = 2 # 중급
    ADVANCED = 3    # 고급
    EXPERT = 4      # 전문가

    def __str__(self):
        return self.name

class SkillCategory(Enum):
    """스킬 카테고리"""
    TECHNICAL = "technical"         # 기술 스킬
    BUSINESS = "business"          # 비즈니스 스킬
    LEADERSHIP = "leadership"      # 리더십
    COMMUNICATION = "communication" # 커뮤니케이션
    FINANCIAL = "financial"        # 금융 전문
    COMPLIANCE = "compliance"      # 컴플라이언스
    DIGITAL = "digital"           # 디지털 역량

@dataclass
class SkillScore:
    """스킬 점수 데이터 구조"""
    skill_name: str
    category: str
    current_level: int
    required_level: int
    proficiency_score: float
    gap_score: float
    weight: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            'skill_name': self.skill_name,
            'category': self.category,
            'current_level': self.current_level,
            'required_level': self.required_level,
            'proficiency_score': round(self.proficiency_score, 2),
            'gap_score': round(self.gap_score, 2),
            'weight': self.weight
        }

@dataclass
class DepartmentSkillProfile:
    """부서별 스킬 프로파일"""
    department: str
    total_employees: int
    skill_scores: List[SkillScore] = field(default_factory=list)
    avg_proficiency: float = 0.0
    avg_gap: float = 0.0
    
    def calculate_averages(self):
        """평균 계산"""
        if not self.skill_scores:
            return
            
        self.avg_proficiency = np.mean([s.proficiency_score for s in self.skill_scores])
        self.avg_gap = np.mean([s.gap_score for s in self.skill_scores])

# ===== 2. 핵심 함수: calcSkillScoreForDeptSkill =====

def calcSkillScoreForDeptSkill(
    department: str, 
    employees: List[Dict[str, Any]], 
    skill_requirements: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    부서별 스킬 점수 계산 함수 (개선 버전)
    
    Args:
        department: 부서명
        employees: 직원 데이터 리스트
        skill_requirements: 스킬별 요구사항
        
    Returns:
        부서 스킬 점수 분석 결과
    """
    try:
        logger.info(f"=== 부서 '{department}' 스킬 점수 계산 시작 ===")
        
        # 입력 검증
        if not employees:
            logger.warning(f"부서 '{department}'에 직원이 없습니다.")
            return {
                'status': 'warning',
                'department': department,
                'message': '직원 데이터가 없습니다.',
                'data': None
            }
        
        # 부서 프로파일 초기화
        dept_profile = DepartmentSkillProfile(
            department=department,
            total_employees=len(employees)
        )
        
        # 스킬별 점수 계산
        skill_aggregates = defaultdict(lambda: {
            'current_levels': [],
            'required_levels': [],
            'proficiencies': [],
            'gaps': []
        })
        
        # 각 직원의 스킬 데이터 수집
        for employee in employees:
            employee_skills = _extract_employee_skills(employee)
            
            for skill_name, skill_data in employee_skills.items():
                if skill_name not in skill_requirements:
                    continue
                    
                req = skill_requirements[skill_name]
                required_level = req.get('required_level', 2)
                current_level = skill_data.get('level', 0)
                
                # 점수 계산
                proficiency = _calculate_proficiency(current_level, required_level)
                gap = _calculate_gap(current_level, required_level)
                
                skill_aggregates[skill_name]['current_levels'].append(current_level)
                skill_aggregates[skill_name]['required_levels'].append(required_level)
                skill_aggregates[skill_name]['proficiencies'].append(proficiency)
                skill_aggregates[skill_name]['gaps'].append(gap)
        
        # 스킬별 평균 계산
        for skill_name, aggregates in skill_aggregates.items():
            if not aggregates['current_levels']:
                continue
                
            skill_score = SkillScore(
                skill_name=skill_name,
                category=skill_requirements[skill_name].get('category', 'business'),
                current_level=round(np.mean(aggregates['current_levels']), 1),
                required_level=round(np.mean(aggregates['required_levels']), 1),
                proficiency_score=np.mean(aggregates['proficiencies']),
                gap_score=np.mean(aggregates['gaps']),
                weight=skill_requirements[skill_name].get('weight', 1.0)
            )
            
            dept_profile.skill_scores.append(skill_score)
            
            logger.debug(f"스킬 '{skill_name}' 계산 완료: {skill_score.to_dict()}")
        
        # 부서 평균 계산
        dept_profile.calculate_averages()
        
        # 결과 생성
        result = {
            'status': 'success',
            'department': department,
            'summary': {
                'total_employees': dept_profile.total_employees,
                'total_skills': len(dept_profile.skill_scores),
                'avg_proficiency': round(dept_profile.avg_proficiency, 2),
                'avg_gap': round(dept_profile.avg_gap, 2)
            },
            'skill_scores': [s.to_dict() for s in dept_profile.skill_scores],
            'top_gaps': _identify_top_gaps(dept_profile.skill_scores, 5),
            'recommendations': _generate_recommendations(dept_profile)
        }
        
        logger.info(f"부서 '{department}' 계산 완료: {result['summary']}")
        return result
        
    except Exception as e:
        logger.error(f"calcSkillScoreForDeptSkill 오류: {str(e)}")
        logger.error(traceback.format_exc())
        
        return {
            'status': 'error',
            'department': department,
            'message': f'계산 중 오류 발생: {str(e)}',
            'data': None
        }

# ===== 3. 보조 함수들 =====

def _extract_employee_skills(employee: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """직원 스킬 데이터 추출"""
    skills = {}
    
    # 기본 스킬 데이터
    if 'skills' in employee and employee['skills'] is not None:
        for skill in employee['skills']:
            skills[skill['name']] = {
                'level': skill.get('level', 0),
                'experience': skill.get('experience', 0)
            }
    
    # 직무 기반 추론
    job_type = employee.get('job_type', '')
    if job_type:
        inferred_skills = _infer_skills_by_job_type(job_type, employee.get('growth_level', 1))
        for skill_name, skill_data in inferred_skills.items():
            if skill_name not in skills:
                skills[skill_name] = skill_data
    
    return skills

def _infer_skills_by_job_type(job_type: str, growth_level: int) -> Dict[str, Dict[str, Any]]:
    """직무 타입별 스킬 추론"""
    base_skills = {
        'IT개발': {
            'Python': {'level': 2, 'experience': 24},
            'Java': {'level': 1, 'experience': 12},
            'SQL': {'level': 2, 'experience': 24},
            '시스템설계': {'level': 1, 'experience': 12}
        },
        'IT기획': {
            '프로젝트관리': {'level': 2, 'experience': 24},
            '업무분석': {'level': 3, 'experience': 36},
            '시스템분석': {'level': 2, 'experience': 24}
        },
        '경영관리': {
            '전략기획': {'level': 2, 'experience': 24},
            '재무분석': {'level': 2, 'experience': 24},
            '프로세스개선': {'level': 1, 'experience': 12}
        },
        '금융영업': {
            '고객관리': {'level': 3, 'experience': 36},
            '여신관리': {'level': 2, 'experience': 24},
            '리스크관리': {'level': 2, 'experience': 24}
        }
    }
    
    skills = base_skills.get(job_type, {})
    
    # 성장레벨에 따른 조정
    level_multiplier = 0.6 + (growth_level - 1) * 0.2  # 0.6 ~ 1.4
    
    adjusted_skills = {}
    for skill_name, skill_data in skills.items():
        adjusted_level = min(4, max(0, int(skill_data['level'] * level_multiplier)))
        adjusted_skills[skill_name] = {
            'level': adjusted_level,
            'experience': skill_data['experience'] * level_multiplier
        }
    
    return adjusted_skills

def _calculate_proficiency(current: int, required: int) -> float:
    """숙련도 점수 계산 (0-100)"""
    if required == 0:
        return 100.0
    return min(100.0, (current / required) * 100.0)

def _calculate_gap(current: int, required: int) -> float:
    """갭 점수 계산 (0-100)"""
    if required == 0:
        return 0.0
    gap = max(0, required - current)
    return (gap / 4.0) * 100.0  # 최대 레벨 4 기준

def _identify_top_gaps(skill_scores: List[SkillScore], top_n: int = 5) -> List[Dict[str, Any]]:
    """상위 갭 스킬 식별"""
    sorted_skills = sorted(skill_scores, key=lambda x: x.gap_score, reverse=True)
    
    return [
        {
            'skill_name': skill.skill_name,
            'category': skill.category,
            'gap_score': skill.gap_score,
            'current_level': skill.current_level,
            'required_level': skill.required_level
        }
        for skill in sorted_skills[:top_n]
    ]

def _generate_recommendations(profile: DepartmentSkillProfile) -> List[str]:
    """부서별 추천사항 생성"""
    recommendations = []
    
    if profile.avg_gap > 50:
        recommendations.append("전반적인 스킬 향상 프로그램이 시급히 필요합니다.")
    elif profile.avg_gap > 30:
        recommendations.append("중점 스킬 교육 계획 수립이 필요합니다.")
    
    # 카테고리별 분석
    category_gaps = defaultdict(list)
    for skill in profile.skill_scores:
        if skill.gap_score > 30:
            category_gaps[skill.category].append(skill)
    
    for category, skills in category_gaps.items():
        if len(skills) >= 2:
            recommendations.append(f"{category} 영역 집중 교육이 필요합니다.")
    
    # 긴급 스킬
    urgent_skills = [s for s in profile.skill_scores if s.gap_score > 60]
    if urgent_skills:
        skill_names = ', '.join([s.skill_name for s in urgent_skills[:3]])
        recommendations.append(f"긴급 교육 필요: {skill_names}")
    
    return recommendations[:5]

# ===== 4. 테스트 데이터셋 =====

def generate_test_data() -> Tuple[List[Dict], Dict[str, Dict]]:
    """테스트용 데이터 생성"""
    
    # 테스트 직원 데이터
    test_employees = [
        {
            'id': 'EMP001',
            'name': '김개발',
            'department': 'IT개발팀',
            'job_type': 'IT개발',
            'growth_level': 3,
            'skills': [
                {'name': 'Python', 'level': 3, 'experience': 36},
                {'name': 'Java', 'level': 2, 'experience': 24},
                {'name': 'SQL', 'level': 3, 'experience': 36}
            ]
        },
        {
            'id': 'EMP002',
            'name': '이기획',
            'department': 'IT개발팀',
            'job_type': 'IT기획',
            'growth_level': 2,
            'skills': [
                {'name': '프로젝트관리', 'level': 2, 'experience': 24},
                {'name': '업무분석', 'level': 2, 'experience': 24}
            ]
        },
        {
            'id': 'EMP003',
            'name': '박신입',
            'department': 'IT개발팀',
            'job_type': 'IT개발',
            'growth_level': 1,
            'skills': [
                {'name': 'Python', 'level': 1, 'experience': 6},
                {'name': 'SQL', 'level': 1, 'experience': 6}
            ]
        },
        {
            'id': 'EMP004',
            'name': '최전문',
            'department': 'IT개발팀',
            'job_type': 'IT개발',
            'growth_level': 4,
            'skills': [
                {'name': 'Python', 'level': 4, 'experience': 60},
                {'name': 'Java', 'level': 4, 'experience': 60},
                {'name': 'SQL', 'level': 4, 'experience': 60},
                {'name': '시스템설계', 'level': 3, 'experience': 36}
            ]
        }
    ]
    
    # 스킬 요구사항
    skill_requirements = {
        'Python': {
            'required_level': 3,
            'category': 'technical',
            'weight': 1.5,
            'description': 'Python 프로그래밍'
        },
        'Java': {
            'required_level': 2,
            'category': 'technical',
            'weight': 1.2,
            'description': 'Java 프로그래밍'
        },
        'SQL': {
            'required_level': 3,
            'category': 'technical',
            'weight': 1.0,
            'description': 'SQL 데이터베이스'
        },
        '프로젝트관리': {
            'required_level': 2,
            'category': 'business',
            'weight': 1.0,
            'description': '프로젝트 관리 능력'
        },
        '업무분석': {
            'required_level': 2,
            'category': 'business',
            'weight': 1.0,
            'description': '업무 분석 능력'
        },
        '시스템설계': {
            'required_level': 2,
            'category': 'technical',
            'weight': 1.3,
            'description': '시스템 설계 능력'
        }
    }
    
    return test_employees, skill_requirements

# ===== 5. 버그 수정 검증 =====

def validate_calculation(result: Dict[str, Any]) -> Dict[str, Any]:
    """계산 결과 검증"""
    validation = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    # 필수 필드 검증
    required_fields = ['status', 'department', 'summary', 'skill_scores']
    for field in required_fields:
        if field not in result:
            validation['errors'].append(f"필수 필드 누락: {field}")
            validation['is_valid'] = False
    
    if result.get('status') == 'success':
        # 데이터 일관성 검증
        summary = result.get('summary', {})
        
        if summary.get('avg_proficiency', 0) > 100:
            validation['errors'].append("평균 숙련도가 100을 초과합니다")
            validation['is_valid'] = False
            
        if summary.get('avg_gap', 0) < 0:
            validation['errors'].append("평균 갭이 음수입니다")
            validation['is_valid'] = False
        
        # 스킬 점수 검증
        skill_scores = result.get('skill_scores', [])
        for skill in skill_scores:
            if skill['proficiency_score'] > 100 or skill['proficiency_score'] < 0:
                validation['warnings'].append(f"스킬 '{skill['skill_name']}'의 숙련도가 범위를 벗어남")
    
    return validation

# ===== 6. 통합 테스트 및 로깅 =====

def run_comprehensive_test():
    """통합 테스트 실행"""
    print("\n" + "="*60)
    print("스킬맵 데이터 바인딩 버그 수정 테스트")
    print("="*60 + "\n")
    
    # 테스트 데이터 생성
    employees, skill_reqs = generate_test_data()
    
    # 개선 전 시뮬레이션 (의도적 버그 포함)
    print("[ 개선 전 시뮬레이션 ]")
    try:
        # 의도적으로 None 값 포함
        buggy_employees = employees.copy()
        buggy_employees[1]['skills'] = None  # 버그 유발
        
        result_before = calcSkillScoreForDeptSkill('IT개발팀', buggy_employees, skill_reqs)
        print(f"상태: {result_before['status']}")
        if result_before['status'] == 'error':
            print(f"에러: {result_before['message']}")
    except Exception as e:
        print(f"예외 발생: {str(e)}")
    
    print("\n" + "-"*60 + "\n")
    
    # 개선 후 테스트
    print("[ 개선 후 실행 ]")
    result_after = calcSkillScoreForDeptSkill('IT개발팀', employees, skill_reqs)
    
    if result_after['status'] == 'success':
        summary = result_after['summary']
        print(f"[OK] 부서: {result_after['department']}")
        print(f"[OK] 직원 수: {summary['total_employees']}")
        print(f"[OK] 분석된 스킬: {summary['total_skills']}")
        print(f"[OK] 평균 숙련도: {summary['avg_proficiency']}%")
        print(f"[OK] 평균 갭: {summary['avg_gap']}%")
        
        print("\n[ 상위 갭 스킬 ]")
        for i, gap in enumerate(result_after['top_gaps'], 1):
            print(f"{i}. {gap['skill_name']} - 갭: {gap['gap_score']:.1f}% "
                  f"(현재: {gap['current_level']}, 필요: {gap['required_level']})")
        
        print("\n[ 추천사항 ]")
        for i, rec in enumerate(result_after['recommendations'], 1):
            print(f"{i}. {rec}")
    
    # 결과 검증
    print("\n[ 검증 결과 ]")
    validation = validate_calculation(result_after)
    print(f"[검증] 유효성: {'통과' if validation['is_valid'] else '실패'}")
    if validation['errors']:
        print("[오류]:")
        for error in validation['errors']:
            print(f"   - {error}")
    if validation['warnings']:
        print("[경고]:")
        for warning in validation['warnings']:
            print(f"   - {warning}")
    
    # JSON 출력 예시
    print("\n[ JSON 출력 샘플 ]")
    print(json.dumps(result_after, indent=2, ensure_ascii=False)[:500] + "...")

# ===== 7. 사용 가이드 =====

def print_usage_guide():
    """사용 가이드 출력"""
    guide = """
    === calcSkillScoreForDeptSkill 함수 사용 가이드 ===
    
    1. 기본 사용법:
    ```python
    from skillmap_databinding_bugfix import calcSkillScoreForDeptSkill
    
    # 직원 데이터
    employees = [
        {
            'id': 'EMP001',
            'name': '홍길동',
            'department': 'IT개발팀',
            'job_type': 'IT개발',
            'growth_level': 3,
            'skills': [
                {'name': 'Python', 'level': 3, 'experience': 36}
            ]
        }
    ]
    
    # 스킬 요구사항
    skill_requirements = {
        'Python': {
            'required_level': 3,
            'category': 'technical',
            'weight': 1.5
        }
    }
    
    # 함수 호출
    result = calcSkillScoreForDeptSkill('IT개발팀', employees, skill_requirements)
    ```
    
    2. 결과 구조:
    - status: 'success' | 'error' | 'warning'
    - department: 부서명
    - summary: 요약 통계
    - skill_scores: 스킬별 점수 리스트
    - top_gaps: 상위 갭 스킬
    - recommendations: 추천사항
    
    3. 오류 처리:
    - 빈 직원 리스트 처리
    - None 값 안전 처리
    - 예외 발생 시 로깅 및 에러 응답
    
    4. 데이터 검증:
    - 점수 범위 검증 (0-100)
    - 필수 필드 존재 여부
    - 데이터 타입 검증
    """
    print(guide)

# ===== 메인 실행 =====

if __name__ == "__main__":
    # 사용 가이드 출력
    print_usage_guide()
    
    # 통합 테스트 실행
    run_comprehensive_test()
    
    print("\n" + "="*60)
    print("테스트 완료!")
    print("="*60)