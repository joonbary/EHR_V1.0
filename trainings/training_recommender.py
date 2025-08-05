"""
교육 추천 엔진
스킬 갭 기반으로 최적의 교육과정을 추천하는 핵심 로직
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TrainingRecommender:
    """교육 추천 엔진"""
    
    def __init__(self):
        self.skill_weight = 0.4
        self.level_weight = 0.2
        self.priority_weight = 0.2
        self.completion_weight = 0.2
    
    def recommend_trainings(
        self,
        missing_skills: List[str],
        current_level: str,
        target_job: str,
        available_courses: List[Dict],
        completed_courses: List[str] = None,
        max_recommendations: int = 10
    ) -> List[Dict]:
        """
        부족한 스킬 기반 교육 추천
        
        Args:
            missing_skills: 부족한 스킬 목록
            current_level: 현재 성장레벨
            target_job: 목표 직무
            available_courses: 가능한 교육과정 목록
            completed_courses: 이수 완료 과정 ID 목록
            max_recommendations: 최대 추천 수
        
        Returns:
            추천 교육과정 목록 (우선순위 정렬)
        """
        if not missing_skills:
            return []
        
        completed_courses = completed_courses or []
        recommendations = []
        
        for course in available_courses:
            # 이미 이수한 과정 제외
            if course['id'] in completed_courses:
                continue
            
            # 추천 점수 계산
            score_data = self._calculate_recommendation_score(
                course=course,
                missing_skills=missing_skills,
                current_level=current_level,
                target_job=target_job
            )
            
            if score_data['total_score'] > 0:
                recommendations.append({
                    'course_id': course['id'],
                    'course_code': course['course_code'],
                    'title': course['title'],
                    'category': course.get('category', '일반'),
                    'related_skills': course.get('related_skills', []),
                    'skill_level': course.get('skill_level', 'INTERMEDIATE'),
                    'duration_hours': course.get('duration_hours', 8),
                    'course_type': course.get('course_type', 'ONLINE'),
                    'provider': course.get('provider', '내부'),
                    'cost': course.get('cost', 0),
                    'is_mandatory': course.get('is_mandatory', False),
                    'certification_eligible': course.get('certification_eligible', False),
                    'match_score': score_data['total_score'],
                    'skill_coverage': score_data['skill_coverage'],
                    'matched_skills': score_data['matched_skills'],
                    'priority': self._calculate_priority(score_data),
                    'recommendation_type': self._determine_recommendation_type(
                        course, score_data
                    ),
                    'recommendation_reason': self._generate_recommendation_reason(
                        course, score_data, missing_skills, target_job
                    ),
                    'expected_completion_time': self._estimate_completion_time(course),
                    'growth_impact': self._calculate_growth_impact(
                        course, current_level
                    )
                })
        
        # 우선순위 및 점수로 정렬
        recommendations.sort(
            key=lambda x: (x['priority'], x['match_score']),
            reverse=True
        )
        
        return recommendations[:max_recommendations]
    
    def _calculate_recommendation_score(
        self,
        course: Dict,
        missing_skills: List[str],
        current_level: str,
        target_job: str
    ) -> Dict:
        """추천 점수 계산"""
        score_data = {
            'skill_score': 0,
            'level_score': 0,
            'priority_score': 0,
            'completion_score': 0,
            'matched_skills': [],
            'skill_coverage': 0,
            'total_score': 0
        }
        
        # 1. 스킬 매칭 점수
        course_skills = [s.lower() for s in course.get('related_skills', [])]
        missing_skills_lower = [s.lower() for s in missing_skills]
        
        matched_skills = []
        for skill in missing_skills:
            if skill.lower() in course_skills:
                matched_skills.append(skill)
        
        if matched_skills:
            score_data['matched_skills'] = matched_skills
            score_data['skill_coverage'] = len(matched_skills) / len(missing_skills)
            score_data['skill_score'] = score_data['skill_coverage'] * 100
        
        # 2. 레벨 적합도 점수
        score_data['level_score'] = self._calculate_level_score(
            course, current_level
        )
        
        # 3. 우선순위 점수 (필수교육, 인증교육 등)
        if course.get('is_mandatory'):
            score_data['priority_score'] = 100
        elif course.get('certification_eligible'):
            score_data['priority_score'] = 80
        else:
            score_data['priority_score'] = 50
        
        # 4. 이수 용이성 점수
        score_data['completion_score'] = self._calculate_completion_score(course)
        
        # 총점 계산
        score_data['total_score'] = (
            score_data['skill_score'] * self.skill_weight +
            score_data['level_score'] * self.level_weight +
            score_data['priority_score'] * self.priority_weight +
            score_data['completion_score'] * self.completion_weight
        )
        
        return score_data
    
    def _calculate_level_score(self, course: Dict, current_level: str) -> float:
        """레벨 적합도 점수 계산"""
        level_map = {
            'Lv.1': 1, 'Lv.2': 2, 'Lv.3': 3,
            'Lv.4': 4, 'Lv.5': 5
        }
        
        current_level_num = level_map.get(current_level, 2)
        
        # 스킬 레벨과 현재 레벨 비교
        skill_level = course.get('skill_level', 'INTERMEDIATE')
        
        if skill_level == 'BASIC' and current_level_num <= 2:
            return 100
        elif skill_level == 'INTERMEDIATE' and 2 <= current_level_num <= 3:
            return 100
        elif skill_level == 'ADVANCED' and current_level_num >= 3:
            return 100
        elif skill_level == 'EXPERT' and current_level_num >= 4:
            return 100
        else:
            # 레벨 차이에 따른 점수 감소
            return max(50 - abs(current_level_num - 3) * 10, 20)
    
    def _calculate_completion_score(self, course: Dict) -> float:
        """이수 용이성 점수"""
        score = 100
        
        # 교육 시간에 따른 감점
        duration = course.get('duration_hours', 8)
        if duration > 40:
            score -= 30
        elif duration > 20:
            score -= 20
        elif duration > 10:
            score -= 10
        
        # 교육 유형에 따른 조정
        course_type = course.get('course_type', 'ONLINE')
        if course_type == 'ONLINE':
            score += 10  # 온라인 가산점
        elif course_type == 'SELF_STUDY':
            score += 15  # 자율학습 가산점
        
        # 비용에 따른 감점
        cost = course.get('cost', 0)
        if cost > 1000000:
            score -= 20
        elif cost > 500000:
            score -= 10
        
        return max(score, 20)
    
    def _calculate_priority(self, score_data: Dict) -> int:
        """우선순위 계산 (1-100, 높을수록 우선)"""
        priority = 50  # 기본값
        
        # 스킬 커버리지에 따른 조정
        if score_data['skill_coverage'] >= 0.8:
            priority += 30
        elif score_data['skill_coverage'] >= 0.5:
            priority += 20
        elif score_data['skill_coverage'] >= 0.3:
            priority += 10
        
        # 총점에 따른 조정
        if score_data['total_score'] >= 80:
            priority += 20
        elif score_data['total_score'] >= 60:
            priority += 10
        
        return min(priority, 100)
    
    def _determine_recommendation_type(
        self, 
        course: Dict, 
        score_data: Dict
    ) -> str:
        """추천 유형 결정"""
        if course.get('is_mandatory'):
            return 'MANDATORY'
        elif score_data['skill_coverage'] >= 0.5:
            return 'SKILL_GAP'
        elif course.get('certification_eligible'):
            return 'GROWTH_LEVEL'
        else:
            return 'CAREER_PATH'
    
    def _generate_recommendation_reason(
        self,
        course: Dict,
        score_data: Dict,
        missing_skills: List[str],
        target_job: str
    ) -> str:
        """추천 사유 생성"""
        reasons = []
        
        # 스킬 매칭 사유
        if score_data['matched_skills']:
            matched_str = ", ".join(score_data['matched_skills'][:3])
            reasons.append(
                f"{target_job} 직무에 필요한 {matched_str} 스킬을 습득할 수 있습니다"
            )
        
        # 필수교육 사유
        if course.get('is_mandatory'):
            reasons.append("이 과정은 필수 이수 교육입니다")
        
        # 인증교육 사유
        if course.get('certification_eligible'):
            reasons.append("성장레벨 인증에 도움이 되는 교육입니다")
        
        # 커버리지 사유
        if score_data['skill_coverage'] >= 0.7:
            percentage = int(score_data['skill_coverage'] * 100)
            reasons.append(f"부족한 스킬의 {percentage}%를 커버합니다")
        
        # 교육 유형 사유
        if course.get('course_type') == 'ONLINE':
            reasons.append("온라인으로 편리하게 수강 가능합니다")
        
        return ". ".join(reasons) if reasons else "경력 개발에 도움이 되는 교육입니다"
    
    def _estimate_completion_time(self, course: Dict) -> str:
        """예상 이수 기간"""
        duration = course.get('duration_hours', 8)
        course_type = course.get('course_type', 'ONLINE')
        
        if course_type == 'SELF_STUDY':
            # 자율학습은 2배 기간
            weeks = (duration * 2) / 20  # 주당 20시간 기준
        elif course_type == 'ONLINE':
            # 온라인은 1.5배 기간
            weeks = (duration * 1.5) / 20
        else:
            # 오프라인은 실제 시간
            weeks = duration / 40  # 주당 40시간 기준
        
        if weeks < 1:
            return f"{int(duration)}시간"
        elif weeks < 4:
            return f"{int(weeks)}주"
        else:
            return f"{int(weeks/4)}개월"
    
    def _calculate_growth_impact(
        self, 
        course: Dict, 
        current_level: str
    ) -> Dict:
        """성장 영향도 계산"""
        impact = {
            'level_progress': 0,
            'certification_eligible': course.get('certification_eligible', False),
            'next_level_contribution': 0
        }
        
        # 성장레벨 영향도
        growth_impact = course.get('growth_level_impact', {})
        if current_level in growth_impact:
            impact['level_progress'] = growth_impact[current_level]
        
        # 다음 레벨 기여도
        level_map = {
            'Lv.1': 'Lv.2', 'Lv.2': 'Lv.3', 
            'Lv.3': 'Lv.4', 'Lv.4': 'Lv.5'
        }
        next_level = level_map.get(current_level)
        if next_level and next_level in growth_impact:
            impact['next_level_contribution'] = growth_impact[next_level]
        
        return impact


def filter_courses_by_criteria(
    courses: List[Dict],
    criteria: Dict
) -> List[Dict]:
    """
    조건에 따른 교육과정 필터링
    
    Args:
        courses: 전체 교육과정 목록
        criteria: 필터 조건
            - categories: 카테고리 목록
            - min_level: 최소 레벨
            - max_duration: 최대 시간
            - course_types: 교육 유형 목록
            - max_cost: 최대 비용
    """
    filtered = courses
    
    # 카테고리 필터
    if criteria.get('categories'):
        filtered = [
            c for c in filtered 
            if c.get('category') in criteria['categories']
        ]
    
    # 레벨 필터
    if criteria.get('min_level'):
        level_order = ['BASIC', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']
        min_idx = level_order.index(criteria['min_level'])
        filtered = [
            c for c in filtered
            if level_order.index(c.get('skill_level', 'INTERMEDIATE')) >= min_idx
        ]
    
    # 시간 필터
    if criteria.get('max_duration'):
        filtered = [
            c for c in filtered
            if c.get('duration_hours', 0) <= criteria['max_duration']
        ]
    
    # 교육 유형 필터
    if criteria.get('course_types'):
        filtered = [
            c for c in filtered
            if c.get('course_type') in criteria['course_types']
        ]
    
    # 비용 필터
    if criteria.get('max_cost') is not None:
        filtered = [
            c for c in filtered
            if c.get('cost', 0) <= criteria['max_cost']
        ]
    
    return filtered


def generate_training_roadmap(
    recommendations: List[Dict],
    available_time_per_month: int = 20
) -> List[Dict]:
    """
    추천 교육과정으로 학습 로드맵 생성
    
    Args:
        recommendations: 추천 교육 목록
        available_time_per_month: 월 가용 학습시간
    
    Returns:
        월별 학습 계획
    """
    roadmap = []
    current_month = 1
    monthly_hours = 0
    month_courses = []
    
    for course in recommendations:
        duration = course.get('duration_hours', 8)
        
        # 현재 월에 추가 가능한지 확인
        if monthly_hours + duration <= available_time_per_month:
            monthly_hours += duration
            month_courses.append(course)
        else:
            # 현재 월 마감하고 다음 월로
            if month_courses:
                roadmap.append({
                    'month': current_month,
                    'courses': month_courses,
                    'total_hours': monthly_hours,
                    'skills_covered': list(set(
                        skill for c in month_courses 
                        for skill in c.get('matched_skills', [])
                    ))
                })
            
            # 다음 월 시작
            current_month += 1
            monthly_hours = duration
            month_courses = [course]
    
    # 마지막 월 추가
    if month_courses:
        roadmap.append({
            'month': current_month,
            'courses': month_courses,
            'total_hours': monthly_hours,
            'skills_covered': list(set(
                skill for c in month_courses 
                for skill in c.get('matched_skills', [])
            ))
        })
    
    return roadmap