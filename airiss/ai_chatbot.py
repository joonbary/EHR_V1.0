"""
AIRISS AI 챗봇 구현
OpenAI GPT 기반 실제 HR 챗봇
"""
import openai
import json
import os
from typing import Dict, List, Optional
from django.conf import settings
from django.utils import timezone
from datetime import datetime

from employees.models import Employee
from .models import HRChatbotConversation


class HRChatbotService:
    """HR 챗봇 서비스 클래스"""
    
    def __init__(self):
        # OpenAI API 키 설정 (환경변수에서 가져오기)
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        
        # GPT 모델 설정 (환경변수에서 가져오기)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # HR 컨텍스트 정의
        self.hr_context = self._build_hr_context()
        self.conversation_history = []
    
    def _build_hr_context(self) -> str:
        """HR 전용 컨텍스트 구축"""
        context = """
        당신은 OK Financial Group의 전문 HR 챗봇 'AIRISS'입니다. 
        다음 역할과 규칙을 따라주세요:

        ## 역할
        - 직원들의 HR 관련 문의에 친절하고 정확하게 답변
        - 회사 정책과 절차에 대한 안내 제공
        - 개인정보 보호 및 기밀성 유지
        - 전문적이면서도 따뜻한 톤으로 소통

        ## 주요 업무 영역
        1. 휴가 및 연차 관련 문의
        2. 급여 및 보상 관련 안내
        3. 평가 및 승진 관련 정보
        4. 교육 및 개발 프로그램 안내
        5. 복리후생 및 제도 설명
        6. 각종 증명서 발급 안내
        7. 근태 및 출퇴근 관련 문의
        8. 조직 구조 및 연락처 정보

        ## 응답 규칙
        - 간결하고 명확한 답변 제공
        - 관련 메뉴나 절차를 구체적으로 안내
        - 확실하지 않은 정보는 인사팀 문의 안내
        - 개인정보는 절대 노출하지 않음
        - 한국어로 정중하게 응답

        ## 회사 정보
        - 회사명: OK Financial Group
        - 주요 시스템: eHR 시스템
        - 인사팀 연락처: 내선 1234
        - 근무시간: 09:00 - 18:00

        ## 주요 메뉴 경로
        - 직원 관리: 직원관리 > 직원 목록/등록
        - 휴가 신청: 셀프서비스 > 휴가 신청
        - 급여 명세서: 보상관리 > 급여 명세서
        - 평가 관리: 평가관리 > 현재 평가
        - 교육 신청: 인재개발 > 교육 프로그램
        - 증명서 발급: 셀프서비스 > 증명서 발급
        - 조직도: 조직관리 > 조직도
        """
        return context
    
    def is_available(self) -> bool:
        """AI 챗봇 사용 가능 여부 확인"""
        return bool(self.api_key)
    
    def generate_response(self, user_message: str, employee: Optional[Employee] = None, 
                         conversation: Optional[HRChatbotConversation] = None) -> str:
        """AI 기반 응답 생성"""
        if not self.is_available():
            return self._fallback_response(user_message)
        
        try:
            # 대화 히스토리 구성
            messages = self._build_conversation_messages(user_message, employee, conversation)
            
            # 모델별 최적화된 설정
            model_config = self._get_model_config(self.model)
            
            # OpenAI API 호출
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                **model_config
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # 응답 후처리
            return self._post_process_response(ai_response)
            
        except Exception as e:
            print(f"AI 챗봇 오류: {str(e)}")
            return self._fallback_response(user_message)
    
    def _build_conversation_messages(self, user_message: str, employee: Optional[Employee], 
                                   conversation: Optional[HRChatbotConversation]) -> List[Dict]:
        """대화 메시지 구성"""
        messages = [
            {"role": "system", "content": self.hr_context}
        ]
        
        # 직원 정보 추가 (개인정보 제외)
        if employee:
            employee_context = f"""
            현재 대화 중인 직원 정보:
            - 부서: {employee.department or '미지정'}
            - 직위: {employee.new_position or '미지정'}
            - 근속년수: {self._calculate_tenure(employee)}년
            (개인정보 보호를 위해 이름 등은 사용하지 마세요)
            """
            messages.append({"role": "system", "content": employee_context})
        
        # 최근 대화 히스토리 추가 (최대 10개)
        if conversation and hasattr(conversation, 'messages'):
            recent_messages = conversation.messages[-10:] if len(conversation.messages) > 10 else conversation.messages
            
            for msg in recent_messages:
                role = "user" if msg.get('sender') == 'user' else "assistant"
                messages.append({
                    "role": role,
                    "content": msg.get('message', '')
                })
        
        # 현재 사용자 메시지 추가
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _calculate_tenure(self, employee: Employee) -> float:
        """근속년수 계산"""
        if employee.hire_date:
            today = timezone.now().date()
            tenure_days = (today - employee.hire_date).days
            return round(tenure_days / 365.25, 1)
        return 0.0
    
    def _post_process_response(self, response: str) -> str:
        """응답 후처리"""
        # 불필요한 정보 제거
        response = response.replace("OK Financial Group", "저희 회사")
        
        # 이모지 추가로 친근감 향상
        if "안녕" in response:
            response = "👋 " + response
        elif "감사" in response:
            response = response + " 😊"
        elif "문의" in response or "연락" in response:
            response = "📞 " + response
        elif "도움" in response:
            response = "🤝 " + response
        
        return response
    
    def _fallback_response(self, user_message: str) -> str:
        """AI가 사용 불가능할 때 대체 응답"""
        message_lower = user_message.lower()
        
        # 키워드 기반 기본 응답
        if '휴가' in message_lower or '연차' in message_lower:
            return """📅 휴가 관련 문의시군요!
            
• 남은 연차 확인: 셀프서비스 > 내 정보
• 휴가 신청: 셀프서비스 > 휴가 신청
• 휴가 내역: 셀프서비스 > 신청 내역

추가 문의사항은 인사팀(내선 1234)으로 연락주세요."""

        elif '급여' in message_lower or '월급' in message_lower:
            return """💰 급여 관련 문의시군요!
            
• 급여명세서: 보상관리 > 급여 명세서
• 급여 내역: 보상관리 > 급여 내역
• 소득증명서: 셀프서비스 > 증명서 발급

자세한 문의는 인사팀(내선 1234)으로 연락주세요."""

        elif '평가' in message_lower:
            return """📊 평가 관련 문의시군요!
            
• 현재 평가: 평가관리 > 내 평가
• 평가 일정: 평가관리 > 평가 일정
• 평가 가이드: 평가관리 > 평가 가이드

평가 관련 문의는 인사팀(내선 1234)으로 연락주세요."""

        elif '교육' in message_lower or '연수' in message_lower:
            return """🎓 교육 관련 문의시군요!
            
• 교육 프로그램: 인재개발 > 교육 프로그램
• 교육 신청: 인재개발 > 교육 신청
• 교육 이력: 인재개발 > 내 교육 이력

교육 문의는 인사팀(내선 1234)으로 연락주세요."""

        elif '증명서' in message_lower:
            return """📋 증명서 관련 문의시군요!
            
• 재직증명서: 셀프서비스 > 증명서 발급
• 경력증명서: 셀프서비스 > 증명서 발급
• 소득증명서: 셀프서비스 > 증명서 발급

즉시 발급 가능하며, 문의사항은 인사팀(내선 1234)으로 연락주세요."""

        else:
            return """🤝 안녕하세요! OK Financial Group HR 챗봇입니다.
            
다음과 같은 문의를 도와드릴 수 있습니다:
• 휴가/연차 관련 문의
• 급여/보상 관련 안내  
• 평가 관련 정보
• 교육 프로그램 안내
• 증명서 발급 안내
• 복리후생 정보

구체적인 질문을 해주시면 더 정확한 답변을 드릴 수 있습니다.
자세한 문의는 인사팀(내선 1234)으로 연락주세요."""

    def analyze_user_intent(self, message: str) -> Dict[str, float]:
        """사용자 의도 분석"""
        intents = {
            'vacation': 0.0,
            'salary': 0.0,
            'evaluation': 0.0,
            'education': 0.0,
            'certificate': 0.0,
            'organization': 0.0,
            'general': 0.0
        }
        
        message_lower = message.lower()
        
        # 키워드 기반 의도 분석
        vacation_keywords = ['휴가', '연차', '병가', '특별휴가', '휴직']
        salary_keywords = ['급여', '월급', '보너스', '상여금', '연봉', '임금']
        evaluation_keywords = ['평가', '고과', '성과', '목표', 'kpi']
        education_keywords = ['교육', '연수', '교육과정', '강의', '세미나']
        certificate_keywords = ['증명서', '재직증명', '경력증명', '소득증명']
        org_keywords = ['조직도', '부서', '연락처', '직원', '담당자']
        
        for keyword in vacation_keywords:
            if keyword in message_lower:
                intents['vacation'] += 0.2
        
        for keyword in salary_keywords:
            if keyword in message_lower:
                intents['salary'] += 0.2
                
        for keyword in evaluation_keywords:
            if keyword in message_lower:
                intents['evaluation'] += 0.2
                
        for keyword in education_keywords:
            if keyword in message_lower:
                intents['education'] += 0.2
                
        for keyword in certificate_keywords:
            if keyword in message_lower:
                intents['certificate'] += 0.2
                
        for keyword in org_keywords:
            if keyword in message_lower:
                intents['organization'] += 0.2
        
        # 일반 문의가 가장 높으면 general로 설정
        if max(intents.values()) == 0:
            intents['general'] = 1.0
        
        return intents
    
    def _get_model_config(self, model: str) -> Dict:
        """모델별 최적화된 설정 반환"""
        configs = {
            "gpt-3.5-turbo": {
                "max_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            },
            "gpt-4": {
                "max_tokens": 800,
                "temperature": 0.6,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            },
            "gpt-4o": {
                "max_tokens": 1000,
                "temperature": 0.6,
                "top_p": 0.9,
                "frequency_penalty": 0.05,
                "presence_penalty": 0.05
            },
            "gpt-4-turbo": {
                "max_tokens": 1200,
                "temperature": 0.6,
                "top_p": 0.95,
                "frequency_penalty": 0.05,
                "presence_penalty": 0.05
            }
        }
        
        # 기본값은 gpt-3.5-turbo 설정
        return configs.get(model, configs["gpt-3.5-turbo"])
    
    def get_current_model(self) -> str:
        """현재 사용 중인 모델 반환"""
        return self.model
    
    def get_available_models(self) -> List[Dict]:
        """사용 가능한 모델 목록 반환"""
        return [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "빠르고 경제적인 모델 (기본)",
                "cost": "저렴",
                "speed": "빠름"
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "더 정확하고 창의적인 응답",
                "cost": "보통",
                "speed": "보통"
            },
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "description": "최신 멀티모달 모델",
                "cost": "높음",
                "speed": "빠름"
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "GPT-4의 빠른 버전",
                "cost": "높음",
                "speed": "빠름"
            }
        ]
    
    def get_suggested_questions(self, employee: Optional[Employee] = None) -> List[str]:
        """추천 질문 생성"""
        base_questions = [
            "남은 연차가 얼마나 되나요?",
            "이번 달 급여명세서는 어떻게 확인하나요?",
            "재직증명서 발급 방법을 알려주세요",
            "교육 프로그램은 어떤 것들이 있나요?",
            "평가 일정을 확인하고 싶어요",
            "조직도에서 담당자를 찾고 싶어요"
        ]
        
        # 직원 정보에 따라 맞춤형 질문 추가
        if employee:
            if employee.department:
                base_questions.append(f"{employee.department} 부서 관련 정보를 알려주세요")
            
            # 근속년수에 따른 질문
            tenure = self._calculate_tenure(employee)
            if tenure >= 1:
                base_questions.append("승진 관련 정보를 알고 싶어요")
            if tenure >= 3:
                base_questions.append("장기근속 혜택에 대해 알려주세요")
        
        return base_questions[:6]  # 최대 6개만 반환


# 편의 함수
def get_hr_chatbot_response(message: str, employee: Optional[Employee] = None, 
                           conversation: Optional[HRChatbotConversation] = None) -> str:
    """HR 챗봇 응답 생성 편의 함수"""
    chatbot = HRChatbotService()
    return chatbot.generate_response(message, employee, conversation)


def analyze_hr_message_intent(message: str) -> Dict[str, float]:
    """HR 메시지 의도 분석 편의 함수"""
    chatbot = HRChatbotService()
    return chatbot.analyze_user_intent(message)


def get_hr_suggested_questions(employee: Optional[Employee] = None) -> List[str]:
    """HR 추천 질문 생성 편의 함수"""
    chatbot = HRChatbotService()
    return chatbot.get_suggested_questions(employee)