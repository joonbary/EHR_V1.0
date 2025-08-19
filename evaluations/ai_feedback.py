"""
AI 피드백 생성 시스템
OpenAI API를 활용한 평가 피드백 자동 생성
"""
import os
import json
from typing import Dict, List, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# OpenAI API 설정
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        try:
            # OpenAI 클라이언트 생성 - 새 버전 API만 지원
            client = OpenAI(api_key=api_key)
            logger.info("OpenAI 클라이언트 초기화 성공")
        except Exception as e:
            logger.error(f"OpenAI 클라이언트 초기화 실패: {str(e)}")
            client = None
            OPENAI_AVAILABLE = False
    else:
        client = None
        logger.warning("OpenAI API 키가 설정되지 않았습니다.")
        OPENAI_AVAILABLE = False
except ImportError:
    OPENAI_AVAILABLE = False
    client = None
    logger.warning("OpenAI 패키지가 설치되지 않았습니다. pip install openai를 실행하세요.")
except Exception as e:
    OPENAI_AVAILABLE = False
    client = None
    logger.error(f"OpenAI 초기화 중 예상치 못한 오류: {str(e)}")


class AIFeedbackGenerator:
    """AI 기반 평가 피드백 생성기"""
    
    def __init__(self):
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = 500
        self.temperature = 0.7
        self.client = client
        
    def generate_contribution_feedback(self, evaluation_data: Dict) -> str:
        """기여도 평가에 대한 AI 피드백 생성"""
        
        if not OPENAI_AVAILABLE:
            return self._generate_fallback_feedback(evaluation_data, "contribution")
            
        try:
            # 프롬프트 구성
            prompt = self._build_contribution_prompt(evaluation_data)
            
            if self.client:
                # 새로운 버전 API 사용
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "당신은 전문적인 HR 평가자입니다. 건설적이고 구체적인 피드백을 한국어로 제공하세요."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                feedback = response.choices[0].message.content.strip()
            else:
                # 클라이언트가 없으면 폴백 메시지 반환
                logger.warning("OpenAI 클라이언트를 사용할 수 없습니다.")
                return self._generate_fallback_feedback(evaluation_data, "contribution")
            
            return feedback
            
        except Exception as e:
            logger.error(f"AI 피드백 생성 오류: {str(e)}")
            return self._generate_fallback_feedback(evaluation_data, "contribution")
    
    def generate_expertise_feedback(self, evaluation_data: Dict) -> str:
        """전문성 평가에 대한 AI 피드백 생성"""
        
        if not OPENAI_AVAILABLE:
            return self._generate_fallback_feedback(evaluation_data, "expertise")
            
        try:
            prompt = self._build_expertise_prompt(evaluation_data)
            
            if self.client:
                response = self.client.chat.completions.create(
                    model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 전문성 개발 컨설턴트입니다. 역량 개발을 위한 구체적인 조언을 한국어로 제공하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI 피드백 생성 오류: {str(e)}")
            return self._generate_fallback_feedback(evaluation_data, "expertise")
    
    def generate_impact_feedback(self, evaluation_data: Dict) -> str:
        """영향력 평가에 대한 AI 피드백 생성"""
        
        if not OPENAI_AVAILABLE:
            return self._generate_fallback_feedback(evaluation_data, "impact")
            
        if not self.client:
            return self._generate_fallback_feedback(evaluation_data, "impact")
        
        try:
            prompt = self._build_impact_prompt(evaluation_data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 리더십 코치입니다. 영향력과 리더십 향상을 위한 피드백을 한국어로 제공하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI 피드백 생성 오류: {str(e)}")
            return self._generate_fallback_feedback(evaluation_data, "impact")
    
    def _build_contribution_prompt(self, data: Dict) -> str:
        """기여도 평가 프롬프트 생성"""
        prompt = f"""
        직원 평가 데이터:
        - 이름: {data.get('employee_name', '직원')}
        - 부서: {data.get('department', '부서')}
        - 직급: {data.get('position', '직급')}
        - 기여도 점수: {data.get('contribution_score', 0)}/4.0
        - 완료한 업무 수: {data.get('completed_tasks', 0)}
        - 업무 달성률: {data.get('achievement_rate', 0)}%
        
        주요 업무:
        {self._format_tasks(data.get('tasks', []))}
        
        이 직원의 기여도 평가에 대해 다음을 포함한 피드백을 작성해주세요:
        1. 긍정적인 성과 2-3가지
        2. 개선이 필요한 영역 1-2가지
        3. 향후 발전을 위한 구체적인 제안 2가지
        
        300자 이내로 작성해주세요.
        """
        return prompt
    
    def _build_expertise_prompt(self, data: Dict) -> str:
        """전문성 평가 프롬프트 생성"""
        prompt = f"""
        직원 전문성 평가:
        - 이름: {data.get('employee_name', '직원')}
        - 전문성 점수: {data.get('expertise_score', 0)}/100
        - 강점 역량: {', '.join(data.get('strengths', []))}
        - 개발 필요 역량: {', '.join(data.get('improvements', []))}
        
        체크리스트 결과:
        {self._format_checklist(data.get('checklist', {}))}
        
        이 직원의 전문성 개발을 위한 피드백을 작성해주세요:
        1. 현재 강점과 활용 방안
        2. 우선적으로 개발해야 할 역량
        3. 추천 교육 과정이나 학습 방법
        
        300자 이내로 작성해주세요.
        """
        return prompt
    
    def _build_impact_prompt(self, data: Dict) -> str:
        """영향력 평가 프롬프트 생성"""
        prompt = f"""
        직원 영향력 평가:
        - 이름: {data.get('employee_name', '직원')}
        - 영향력 점수: {data.get('impact_score', 0)}/100
        - 리더십 스타일: {data.get('leadership_style', '미정')}
        - 핵심 가치 실천도: {data.get('value_practice', 0)}%
        
        영향력 지표:
        - 팀 영향력: {data.get('team_impact', 0)}/5
        - 조직 영향력: {data.get('org_impact', 0)}/5
        - 외부 영향력: {data.get('external_impact', 0)}/5
        
        이 직원의 영향력 향상을 위한 피드백을 작성해주세요:
        1. 현재 영향력의 긍정적 측면
        2. 영향력 확대를 위한 기회 영역
        3. 리더십 개발을 위한 구체적 행동 계획
        
        300자 이내로 작성해주세요.
        """
        return prompt
    
    def _format_tasks(self, tasks: List[Dict]) -> str:
        """업무 목록 포맷팅"""
        if not tasks:
            return "- 등록된 업무 없음"
        
        formatted = []
        for task in tasks[:5]:  # 상위 5개만
            formatted.append(f"- {task.get('title', '업무')}: {task.get('achievement', 0)}% 달성")
        return "\n".join(formatted)
    
    def _format_checklist(self, checklist: Dict) -> str:
        """체크리스트 결과 포맷팅"""
        if not checklist:
            return "- 체크리스트 데이터 없음"
        
        formatted = []
        for key, value in list(checklist.items())[:5]:
            status = "✓" if value else "✗"
            formatted.append(f"{status} {key}")
        return "\n".join(formatted)
    
    def _generate_fallback_feedback(self, data: Dict, eval_type: str) -> str:
        """OpenAI API를 사용할 수 없을 때의 대체 피드백"""
        
        employee_name = data.get('employee_name', '직원')
        
        if eval_type == "contribution":
            score = data.get('contribution_score', 0)
            if score >= 3.5:
                level = "매우 우수"
                feedback = f"{employee_name}님은 탁월한 업무 성과를 보여주셨습니다. 목표를 초과 달성하며 팀에 큰 기여를 하고 있습니다."
            elif score >= 2.5:
                level = "우수"
                feedback = f"{employee_name}님은 안정적인 업무 수행 능력을 보여주고 있습니다. 지속적인 성장이 기대됩니다."
            elif score >= 1.5:
                level = "보통"
                feedback = f"{employee_name}님은 기본적인 업무를 수행하고 있습니다. 더 높은 목표에 도전해보시기 바랍니다."
            else:
                level = "개선 필요"
                feedback = f"{employee_name}님은 업무 수행에 개선이 필요합니다. 멘토링과 교육을 통해 역량을 강화하시기 바랍니다."
                
        elif eval_type == "expertise":
            score = data.get('expertise_score', 0)
            if score >= 80:
                feedback = f"{employee_name}님은 높은 전문성을 보유하고 있습니다. 이 전문성을 팀원들과 공유하여 조직 전체의 역량 향상에 기여해주세요."
            elif score >= 60:
                feedback = f"{employee_name}님은 견고한 전문 지식을 갖추고 있습니다. 최신 트렌드 학습과 실무 적용을 통해 더욱 발전하시기 바랍니다."
            else:
                feedback = f"{employee_name}님의 전문성 개발이 필요합니다. 교육 프로그램 참여와 멘토링을 통해 핵심 역량을 강화하세요."
                
        elif eval_type == "impact":
            score = data.get('impact_score', 0)
            if score >= 80:
                feedback = f"{employee_name}님은 조직에 큰 영향력을 발휘하고 있습니다. 리더십을 더욱 발전시켜 차세대 리더로 성장하시기 바랍니다."
            elif score >= 60:
                feedback = f"{employee_name}님은 긍정적인 영향력을 보여주고 있습니다. 더 많은 이니셔티브를 통해 영향력을 확대해보세요."
            else:
                feedback = f"{employee_name}님의 영향력 확대가 필요합니다. 적극적인 소통과 협업을 통해 팀과 조직에 기여도를 높여주세요."
        else:
            feedback = f"{employee_name}님의 평가가 완료되었습니다. 지속적인 성장과 발전을 응원합니다."
        
        # 공통 개선 제안 추가
        feedback += "\n\n[개선 제안]\n"
        feedback += "1. 정기적인 1:1 미팅을 통한 목표 점검\n"
        feedback += "2. 동료 피드백을 통한 다면 평가 활용\n"
        feedback += "3. 개인 개발 계획(IDP) 수립 및 실행"
        
        return feedback


class AIFeedbackValidator:
    """AI 생성 피드백 검증기"""
    
    def validate_feedback(self, feedback: str) -> Dict:
        """피드백 품질 검증"""
        
        validation_result = {
            'is_valid': True,
            'issues': [],
            'score': 100
        }
        
        # 길이 체크
        if len(feedback) < 50:
            validation_result['issues'].append("피드백이 너무 짧습니다")
            validation_result['score'] -= 20
            
        if len(feedback) > 1000:
            validation_result['issues'].append("피드백이 너무 깁니다")
            validation_result['score'] -= 10
        
        # 부적절한 내용 체크
        inappropriate_words = ['차별', '혐오', '비하']
        for word in inappropriate_words:
            if word in feedback:
                validation_result['issues'].append(f"부적절한 표현 포함: {word}")
                validation_result['is_valid'] = False
                validation_result['score'] = 0
                
        # 건설적 피드백 요소 체크
        positive_indicators = ['개선', '발전', '성장', '강점', '기회']
        positive_count = sum(1 for word in positive_indicators if word in feedback)
        
        if positive_count < 2:
            validation_result['issues'].append("건설적인 피드백 요소가 부족합니다")
            validation_result['score'] -= 15
        
        validation_result['is_valid'] = validation_result['score'] >= 50
        
        return validation_result


# 싱글톤 인스턴스
ai_feedback_generator = AIFeedbackGenerator()
ai_feedback_validator = AIFeedbackValidator()