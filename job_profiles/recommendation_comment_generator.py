"""
리더 추천 자연어 코멘트 생성기
평가 결과와 직무 매칭 정보를 기반으로 자연스러운 추천 문장 생성
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class CommentTemplate:
    """코멘트 템플릿"""
    template: str
    required_conditions: Dict[str, any]
    priority: int = 0


class RecommendationCommentGenerator:
    """추천 코멘트 생성기"""
    
    def __init__(self):
        self._initialize_templates()
    
    def _initialize_templates(self):
        """템플릿 초기화"""
        # 한국어 템플릿
        self.ko_templates = {
            'evaluation_excellence': [
                CommentTemplate(
                    template="최근 {eval_period} 연속 {grade}등급을 받은 고성과자로, {key_strength}이(가) 검증되었습니다.",
                    required_conditions={'consecutive_high_grade': True},
                    priority=10
                ),
                CommentTemplate(
                    template="평가 결과 {professionalism} 전문성과 {contribution} 기여도를 보여주며, {impact} 수준의 영향력을 발휘하고 있습니다.",
                    required_conditions={'has_evaluation': True},
                    priority=8
                ),
                CommentTemplate(
                    template="탁월한 {grade}등급 성과와 함께 {key_achievement}을(를) 달성한 우수 인재입니다.",
                    required_conditions={'grade': ['S', 'A+']},
                    priority=9
                )
            ],
            
            'skill_match': [
                CommentTemplate(
                    template="{matched_skills} 등 핵심 역량을 보유하여 {target_job} 직무에 {match_score}% 적합합니다.",
                    required_conditions={'high_match': True},
                    priority=7
                ),
                CommentTemplate(
                    template="{target_job} 직무에 필요한 {required_count}개 역량 중 {matched_count}개를 충족하며, 특히 {top_skill} 분야에서 강점을 보입니다.",
                    required_conditions={'skill_match': True},
                    priority=6
                )
            ],
            
            'growth_level': [
                CommentTemplate(
                    template="현재 성장레벨 {current_level}을(를) 달성하여 {target_job} 보임 조건을 충족하였습니다.",
                    required_conditions={'level_satisfied': True},
                    priority=5
                ),
                CommentTemplate(
                    template="성장레벨 {current_level}으로 목표 직무 요구사항을 {level_status}하고 있습니다.",
                    required_conditions={'has_level': True},
                    priority=4
                )
            ],
            
            'experience': [
                CommentTemplate(
                    template="{career_years}년의 경력과 {key_experience}을(를) 바탕으로 리더십 역량이 입증되었습니다.",
                    required_conditions={'senior_experience': True},
                    priority=6
                ),
                CommentTemplate(
                    template="{department} 부서에서 {career_years}년간 쌓은 전문성과 {achievement}이(가) 주목됩니다.",
                    required_conditions={'has_experience': True},
                    priority=5
                )
            ],
            
            'development_needed': [
                CommentTemplate(
                    template="{skill_gap} 역량 보완이 필요하나, {potential_reason}으로 성장 가능성이 높습니다.",
                    required_conditions={'has_gap': True, 'has_potential': True},
                    priority=3
                ),
                CommentTemplate(
                    template="현재 {match_score}%의 적합도를 보이며, {development_area} 개발 시 우수한 {target_job}이(가) 될 것으로 기대됩니다.",
                    required_conditions={'needs_development': True},
                    priority=2
                )
            ],
            
            'promotion_ready': [
                CommentTemplate(
                    template="모든 보임 조건을 충족하여 즉시 {target_job} 직책 수행이 가능합니다.",
                    required_conditions={'promotion_ready': True},
                    priority=10
                ),
                CommentTemplate(
                    template="{readiness_score}%의 준비도로 {target_job} 승진 적격자입니다.",
                    required_conditions={'high_readiness': True},
                    priority=9
                )
            ]
        }
        
        # 영어 템플릿
        self.en_templates = {
            'evaluation_excellence': [
                CommentTemplate(
                    template="A high performer with {eval_period} consecutive {grade} grades, demonstrating proven {key_strength}.",
                    required_conditions={'consecutive_high_grade': True},
                    priority=10
                ),
                CommentTemplate(
                    template="Shows {professionalism} professionalism and {contribution} contribution with {impact}-level impact.",
                    required_conditions={'has_evaluation': True},
                    priority=8
                )
            ],
            
            'skill_match': [
                CommentTemplate(
                    template="Possesses key competencies including {matched_skills}, showing {match_score}% fit for {target_job} position.",
                    required_conditions={'high_match': True},
                    priority=7
                ),
                CommentTemplate(
                    template="Meets {matched_count} out of {required_count} required competencies for {target_job}, with particular strength in {top_skill}.",
                    required_conditions={'skill_match': True},
                    priority=6
                )
            ],
            
            'growth_level': [
                CommentTemplate(
                    template="Has achieved growth level {current_level}, meeting requirements for {target_job} appointment.",
                    required_conditions={'level_satisfied': True},
                    priority=5
                )
            ],
            
            'experience': [
                CommentTemplate(
                    template="With {career_years} years of experience and {key_experience}, leadership capability is well demonstrated.",
                    required_conditions={'senior_experience': True},
                    priority=6
                )
            ],
            
            'promotion_ready': [
                CommentTemplate(
                    template="Meets all appointment criteria and is ready for immediate {target_job} role.",
                    required_conditions={'promotion_ready': True},
                    priority=10
                )
            ]
        }
    
    def generate_recommendation_comment(
        self,
        employee_profile: dict,
        target_job_profile: dict,
        match_score: float,
        skill_gap: List[str],
        promotion_ready: bool,
        language: str = "ko"
    ) -> str:
        """
        추천 코멘트 생성
        
        Args:
            employee_profile: 직원 프로파일
            target_job_profile: 목표 직무 프로파일
            match_score: 매칭 점수
            skill_gap: 스킬 갭
            promotion_ready: 승진 준비 여부
            language: 언어 ('ko' 또는 'en')
        
        Returns:
            생성된 추천 코멘트
        """
        # 컨텍스트 생성
        context = self._build_context(
            employee_profile,
            target_job_profile,
            match_score,
            skill_gap,
            promotion_ready
        )
        
        # 언어별 템플릿 선택
        templates = self.ko_templates if language == "ko" else self.en_templates
        
        # 적용 가능한 템플릿 찾기
        applicable_templates = []
        
        for category, template_list in templates.items():
            for template in template_list:
                if self._check_conditions(template.required_conditions, context):
                    applicable_templates.append((category, template))
        
        # 우선순위로 정렬
        applicable_templates.sort(key=lambda x: x[1].priority, reverse=True)
        
        # 상위 템플릿 선택 및 조합
        selected_comments = []
        used_categories = set()
        
        for category, template in applicable_templates[:3]:  # 최대 3개 문장
            if category not in used_categories or len(selected_comments) < 2:
                comment = self._fill_template(template.template, context, language)
                selected_comments.append(comment)
                used_categories.add(category)
        
        # 문장 조합
        if language == "ko":
            return " ".join(selected_comments)
        else:
            return " ".join(selected_comments)
    
    def _build_context(
        self,
        employee_profile: dict,
        target_job_profile: dict,
        match_score: float,
        skill_gap: List[str],
        promotion_ready: bool
    ) -> dict:
        """컨텍스트 구성"""
        context = {
            # 기본 정보
            'name': employee_profile.get('name', ''),
            'current_level': employee_profile.get('level', 'N/A'),
            'career_years': employee_profile.get('career_years', 0),
            'department': employee_profile.get('department', ''),
            
            # 목표 직무
            'target_job': target_job_profile.get('name', ''),
            'required_skills': target_job_profile.get('required_skills', []),
            
            # 매칭 정보
            'match_score': round(match_score, 1),
            'skill_gap': skill_gap,
            'promotion_ready': promotion_ready,
            
            # 평가 정보
            'has_evaluation': 'recent_evaluation' in employee_profile,
        }
        
        # 평가 정보 추가
        if context['has_evaluation']:
            eval_data = employee_profile['recent_evaluation']
            context.update({
                'grade': eval_data.get('overall_grade', 'N/A'),
                'professionalism': eval_data.get('professionalism', 'N/A'),
                'contribution': eval_data.get('contribution', 'N/A'),
                'impact': eval_data.get('impact', 'N/A'),
            })
            
            # 연속 고성과 체크
            context['consecutive_high_grade'] = self._check_consecutive_high_grade(
                employee_profile
            )
        
        # 스킬 매칭 분석
        context.update(self._analyze_skill_match(
            employee_profile,
            target_job_profile,
            skill_gap
        ))
        
        # 조건 플래그
        context['high_match'] = match_score >= 80
        context['level_satisfied'] = self._check_level_satisfied(
            employee_profile,
            target_job_profile
        )
        context['senior_experience'] = context['career_years'] >= 7
        context['has_gap'] = len(skill_gap) > 0
        context['has_potential'] = match_score >= 60 and context['career_years'] >= 3
        context['needs_development'] = 60 <= match_score < 80
        context['high_readiness'] = match_score >= 85
        
        return context
    
    def _check_conditions(self, required_conditions: dict, context: dict) -> bool:
        """조건 확인"""
        for key, value in required_conditions.items():
            if key not in context:
                return False
            
            if isinstance(value, bool):
                if context[key] != value:
                    return False
            elif isinstance(value, list):
                if context[key] not in value:
                    return False
            else:
                if context[key] != value:
                    return False
        
        return True
    
    def _fill_template(self, template: str, context: dict, language: str) -> str:
        """템플릿 채우기"""
        # 평가 관련
        if '{eval_period}' in template:
            eval_period = self._get_evaluation_period(context, language)
            template = template.replace('{eval_period}', eval_period)
        
        if '{key_strength}' in template:
            key_strength = self._get_key_strength(context, language)
            template = template.replace('{key_strength}', key_strength)
        
        # 스킬 관련
        if '{matched_skills}' in template:
            matched_skills = self._format_skills(
                context.get('matched_skills', [])[:3], 
                language
            )
            template = template.replace('{matched_skills}', matched_skills)
        
        if '{top_skill}' in template:
            top_skill = context.get('matched_skills', ['역량'])[0]
            template = template.replace('{top_skill}', top_skill)
        
        # 경력 관련
        if '{key_experience}' in template:
            key_experience = self._get_key_experience(context, language)
            template = template.replace('{key_experience}', key_experience)
        
        if '{achievement}' in template:
            achievement = self._get_achievement(context, language)
            template = template.replace('{achievement}', achievement)
        
        # 개발 필요 영역
        if '{skill_gap}' in template:
            gap_text = self._format_skills(context.get('skill_gap', [])[:2], language)
            template = template.replace('{skill_gap}', gap_text)
        
        if '{development_area}' in template:
            dev_area = self._format_skills(context.get('skill_gap', [])[:1], language)
            template = template.replace('{development_area}', dev_area)
        
        if '{potential_reason}' in template:
            reason = self._get_potential_reason(context, language)
            template = template.replace('{potential_reason}', reason)
        
        # 레벨 상태
        if '{level_status}' in template:
            status = "충족" if context.get('level_satisfied') else "미달"
            if language == "en":
                status = "satisfy" if context.get('level_satisfied') else "not meet"
            template = template.replace('{level_status}', status)
        
        # 기본 치환
        for key, value in context.items():
            placeholder = f'{{{key}}}'
            if placeholder in template:
                template = template.replace(placeholder, str(value))
        
        return template
    
    def _check_consecutive_high_grade(self, employee_profile: dict) -> bool:
        """연속 고성과 체크"""
        # 평가 이력이 있는 경우
        if 'evaluation_history' in employee_profile:
            history = employee_profile['evaluation_history']
            high_grades = ['S', 'A+', 'A']
            
            consecutive = 0
            for eval in history:
                if eval.get('overall_grade') in high_grades:
                    consecutive += 1
                else:
                    break
            
            return consecutive >= 3
        
        # 단일 평가만 있는 경우
        return employee_profile.get('recent_evaluation', {}).get('overall_grade') in ['S', 'A+', 'A']
    
    def _analyze_skill_match(
        self,
        employee_profile: dict,
        target_job_profile: dict,
        skill_gap: List[str]
    ) -> dict:
        """스킬 매칭 분석"""
        required_skills = set(target_job_profile.get('required_skills', []))
        employee_skills = set(employee_profile.get('skills', []))
        
        matched_skills = list(required_skills & employee_skills)
        
        return {
            'skill_match': len(matched_skills) > 0,
            'matched_skills': matched_skills,
            'matched_count': len(matched_skills),
            'required_count': len(required_skills),
            'has_experience': employee_profile.get('career_years', 0) > 0
        }
    
    def _check_level_satisfied(
        self,
        employee_profile: dict,
        target_job_profile: dict
    ) -> bool:
        """레벨 충족 여부 확인"""
        current_level = employee_profile.get('level', 'Lv.1')
        required_level = target_job_profile.get('min_required_level', 'Lv.3')
        
        # 레벨 숫자 추출
        try:
            current_num = int(current_level.replace('Lv.', ''))
            required_num = int(required_level.replace('Lv.', ''))
            return current_num >= required_num
        except:
            return False
    
    def _get_evaluation_period(self, context: dict, language: str) -> str:
        """평가 기간 텍스트"""
        # 실제로는 평가 이력에서 계산
        if language == "ko":
            return "3개 분기"
        else:
            return "3 quarters"
    
    def _get_key_strength(self, context: dict, language: str) -> str:
        """핵심 강점"""
        if context.get('professionalism') in ['S', 'A+']:
            return "전문성" if language == "ko" else "expertise"
        elif context.get('contribution') in ['Top 10%', 'Top 20%']:
            return "탁월한 기여도" if language == "ko" else "exceptional contribution"
        elif context.get('impact') == '전사':
            return "전사적 영향력" if language == "ko" else "company-wide impact"
        else:
            return "리더십 역량" if language == "ko" else "leadership capability"
    
    def _format_skills(self, skills: List[str], language: str) -> str:
        """스킬 포맷팅"""
        if not skills:
            return ""
        
        if language == "ko":
            if len(skills) == 1:
                return skills[0]
            elif len(skills) == 2:
                return f"{skills[0]}와 {skills[1]}"
            else:
                return f"{', '.join(skills[:-1])}, {skills[-1]}"
        else:
            if len(skills) == 1:
                return skills[0]
            elif len(skills) == 2:
                return f"{skills[0]} and {skills[1]}"
            else:
                return f"{', '.join(skills[:-1])}, and {skills[-1]}"
    
    def _get_key_experience(self, context: dict, language: str) -> str:
        """핵심 경험"""
        career_years = context.get('career_years', 0)
        
        if career_years >= 10:
            return "풍부한 실무 경험" if language == "ko" else "extensive practical experience"
        elif career_years >= 7:
            return "리더십 경험" if language == "ko" else "leadership experience"
        elif career_years >= 5:
            return "전문 분야 경험" if language == "ko" else "domain expertise"
        else:
            return "실무 경험" if language == "ko" else "practical experience"
    
    def _get_achievement(self, context: dict, language: str) -> str:
        """주요 성과"""
        if context.get('grade') in ['S', 'A+']:
            return "우수한 성과" if language == "ko" else "excellent performance"
        elif context.get('contribution') in ['Top 10%', 'Top 20%']:
            return "높은 기여도" if language == "ko" else "high contribution"
        else:
            return "안정적인 성과" if language == "ko" else "consistent performance"
    
    def _get_potential_reason(self, context: dict, language: str) -> str:
        """잠재력 이유"""
        if context.get('career_years', 0) < 5:
            return "빠른 성장세" if language == "ko" else "rapid growth"
        elif context.get('grade') in ['A', 'A+']:
            return "우수한 평가 결과" if language == "ko" else "excellent evaluation"
        else:
            return "지속적인 발전" if language == "ko" else "continuous improvement"


def generate_recommendation_comment(
    employee_profile: dict,
    target_job_profile: dict,
    match_score: float,
    skill_gap: List[str],
    promotion_ready: bool,
    language: str = "ko"
) -> str:
    """
    추천 코멘트 생성 함수
    
    Args:
        employee_profile: 직원 프로파일
        target_job_profile: 목표 직무 프로파일
        match_score: 매칭 점수
        skill_gap: 스킬 갭
        promotion_ready: 승진 준비 여부
        language: 언어 ('ko' 또는 'en')
    
    Returns:
        생성된 추천 코멘트
    """
    generator = RecommendationCommentGenerator()
    return generator.generate_recommendation_comment(
        employee_profile,
        target_job_profile,
        match_score,
        skill_gap,
        promotion_ready,
        language
    )


# 사용 예시
if __name__ == "__main__":
    # 샘플 데이터
    sample_employee = {
        "name": "홍길동",
        "level": "Lv.3",
        "career_years": 7,
        "department": "영업팀",
        "skills": ["성과관리", "전략수립", "리더십", "데이터분석"],
        "recent_evaluation": {
            "professionalism": "A+",
            "contribution": "Top 10%",
            "impact": "전사",
            "overall_grade": "A"
        }
    }
    
    sample_job = {
        "name": "팀장",
        "required_skills": ["성과관리", "전략수립", "조직운영", "예산관리"],
        "min_required_level": "Lv.3"
    }
    
    # 한국어 코멘트 생성
    ko_comment = generate_recommendation_comment(
        employee_profile=sample_employee,
        target_job_profile=sample_job,
        match_score=91.2,
        skill_gap=["조직운영"],
        promotion_ready=True,
        language="ko"
    )
    
    print("한국어 추천 코멘트:")
    print(ko_comment)
    
    # 영어 코멘트 생성
    en_comment = generate_recommendation_comment(
        employee_profile=sample_employee,
        target_job_profile=sample_job,
        match_score=91.2,
        skill_gap=["조직운영"],
        promotion_ready=True,
        language="en"
    )
    
    print("\n영어 추천 코멘트:")
    print(en_comment)