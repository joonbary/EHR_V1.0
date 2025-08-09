from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import openai
import os
from datetime import datetime, timedelta

from .models import ChatSession, ChatMessage, AIPromptTemplate, QuickAction, AIConfiguration
from employees.models import Employee


class AIChatbotView(TemplateView):
    """AI 챗봇 메인 뷰"""
    template_name = 'ai/chatbot_revolutionary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 임시로 첫 번째 직원 사용 (나중에 로그인 기능 구현 시 수정)
        employee = Employee.objects.filter(employment_status='active').first()
        
        # 최근 채팅 세션들
        recent_sessions = ChatSession.objects.filter(
            employee=employee
        ).order_by('-updated_at')[:5] if employee else []
        
        # 빠른 액션 버튼들
        quick_actions = QuickAction.objects.filter(is_active=True)
        
        context.update({
            'employee': employee,
            'recent_sessions': recent_sessions,
            'quick_actions': quick_actions,
        })
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(View):
    """채팅 API 엔드포인트"""
    
    def post(self, request):
        """메시지 전송 및 AI 응답 처리"""
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            session_id = data.get('session_id')
            
            if not message:
                return JsonResponse({'error': '메시지가 비어있습니다.'}, status=400)
            
            # 직원 정보 가져오기
            employee = Employee.objects.filter(employment_status='active').first()
            
            # 세션 가져오기 또는 생성
            if session_id:
                session = get_object_or_404(ChatSession, id=session_id)
            else:
                session = ChatSession.objects.create(
                    employee=employee,
                    title=message[:50] if len(message) > 50 else message
                )
            
            # 사용자 메시지 저장
            user_message = ChatMessage.objects.create(
                session=session,
                role='user',
                content=message
            )
            
            # AI 응답 생성
            ai_response = self.generate_ai_response(message, session)
            
            # AI 메시지 저장
            ai_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=ai_response['content'],
                model_used=ai_response.get('model', 'gpt-3.5-turbo'),
                tokens_used=ai_response.get('tokens', 0),
                response_time=ai_response.get('response_time', 0)
            )
            
            # 세션 업데이트
            session.updated_at = timezone.now()
            session.save()
            
            return JsonResponse({
                'success': True,
                'session_id': str(session.id),
                'message': {
                    'id': str(ai_message.id),
                    'content': ai_message.content,
                    'created_at': ai_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'role': 'assistant'
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def generate_ai_response(self, message, session):
        """AI 응답 생성"""
        start_time = timezone.now()
        
        # OpenAI API 키 설정
        api_key = AIConfiguration.get_config('OPENAI_API_KEY')
        if not api_key:
            # 환경변수에서 가져오기
            api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key:
            # 실제 OpenAI API 호출
            try:
                openai.api_key = api_key
                
                # 컨텍스트 준비
                messages = self.prepare_context(session, message)
                
                # API 호출
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7,
                )
                
                content = response.choices[0].message.content
                tokens = response.usage.total_tokens
                
            except Exception as e:
                # API 오류 시 폴백
                content = self.get_fallback_response(message)
                tokens = 0
        else:
            # API 키가 없을 때 폴백 응답
            content = self.get_fallback_response(message)
            tokens = 0
        
        response_time = (timezone.now() - start_time).total_seconds()
        
        return {
            'content': content,
            'model': 'gpt-3.5-turbo',
            'tokens': tokens,
            'response_time': response_time
        }
    
    def prepare_context(self, session, current_message):
        """대화 컨텍스트 준비"""
        messages = []
        
        # 시스템 프롬프트
        system_prompt = """당신은 OK Financial Group의 HR AI 어시스턴트입니다.
        직원들의 HR 관련 질문에 친절하고 정확하게 답변해주세요.
        한국어로 대화하며, 존댓말을 사용합니다.
        
        주요 역할:
        1. 인사 정책 및 절차 안내
        2. 성과평가 관련 질문 답변
        3. 교육 프로그램 추천
        4. 휴가 및 복지 안내
        5. 조직 문화 및 가치 설명
        """
        
        messages.append({"role": "system", "content": system_prompt})
        
        # 최근 대화 내역 추가 (최대 10개)
        recent_messages = session.messages.order_by('-created_at')[:10]
        for msg in reversed(recent_messages):
            if msg.content != current_message:  # 현재 메시지 제외
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 현재 메시지 추가
        messages.append({"role": "user", "content": current_message})
        
        return messages
    
    def get_fallback_response(self, message):
        """폴백 응답 생성"""
        message_lower = message.lower()
        
        # 키워드 기반 응답
        responses = {
            '휴가': """휴가 신청 관련 안내입니다.

📌 연차 휴가
• 신청 방법: HR 포털 > 근태관리 > 휴가신청
• 잔여 연차: 마이페이지에서 확인 가능
• 신청 기한: 최소 3일 전 신청 권장

필요하신 경우 HR팀(내선 1234)으로 문의 주세요.""",
            
            '평가': """성과평가 관련 정보입니다.

📊 2024년 성과평가 일정
• 자기평가: 3월 15일 ~ 25일
• 1차 평가: 3월 26일 ~ 4월 5일
• 최종 결과: 4월 20일 공개

평가 시스템 접속: HR 포털 > 성과관리""",
            
            '교육': """교육 프로그램 안내입니다.

📚 추천 교육 과정
• 리더십 에센셜: 차세대 리더 양성
• AI/ML 기초: 디지털 역량 강화
• 글로벌 비즈니스: 어학 및 문화

신청: HR 포털 > 교육/훈련 > 과정 신청""",
            
            '채용': """채용 관련 정보입니다.

👥 채용 프로세스
• 서류 전형 → 1차 면접 → 2차 면접 → 최종 합격
• 추천 채용: 내부 추천 시 가점 부여
• 수시 채용: 각 부서별 필요 시 진행

자세한 내용은 채용 포털을 확인해주세요.""",
        }
        
        # 키워드 매칭
        for keyword, response in responses.items():
            if keyword in message_lower:
                return response
        
        # 기본 응답
        return """문의하신 내용을 확인했습니다.

더 정확한 답변을 위해 다음 정보를 확인해주시거나, HR팀에 직접 문의 부탁드립니다:
• HR 포털: 각종 신청 및 조회
• HR 헬프데스크: 내선 1234
• 이메일: hr@okfgroup.com

다른 도움이 필요하시면 말씀해주세요!"""


class ChatSessionListView(View):
    """채팅 세션 목록 API"""
    
    def get(self, request):
        """세션 목록 조회"""
        employee = Employee.objects.filter(employment_status='active').first()
        
        sessions = ChatSession.objects.filter(
            employee=employee
        ).order_by('-updated_at')[:20] if employee else []
        
        sessions_data = []
        for session in sessions:
            last_message = session.get_last_message()
            sessions_data.append({
                'id': str(session.id),
                'title': session.title,
                'created_at': session.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': session.updated_at.strftime('%Y-%m-%d %H:%M'),
                'message_count': session.get_message_count(),
                'last_message': last_message.content[:50] if last_message else None
            })
        
        return JsonResponse({
            'success': True,
            'sessions': sessions_data
        })


class ChatSessionDetailView(View):
    """채팅 세션 상세 API"""
    
    def get(self, request, session_id):
        """세션의 모든 메시지 조회"""
        session = get_object_or_404(ChatSession, id=session_id)
        
        messages = []
        for msg in session.messages.all():
            messages.append({
                'id': str(msg.id),
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'session': {
                'id': str(session.id),
                'title': session.title,
                'created_at': session.created_at.strftime('%Y-%m-%d %H:%M'),
            },
            'messages': messages
        })
    
    def delete(self, request, session_id):
        """세션 삭제"""
        session = get_object_or_404(ChatSession, id=session_id)
        session.delete()
        
        return JsonResponse({'success': True})


class QuickActionAPIView(View):
    """빠른 액션 API"""
    
    def get(self, request):
        """빠른 액션 목록"""
        actions = QuickAction.objects.filter(is_active=True)
        
        actions_data = []
        for action in actions:
            actions_data.append({
                'id': action.id,
                'title': action.title,
                'prompt': action.prompt,
                'icon': action.icon,
                'category': action.category
            })
        
        return JsonResponse({
            'success': True,
            'actions': actions_data
        })


# 리더십 AI 파트너 뷰
class LeadershipAIView(TemplateView):
    """리더십 AI 파트너 메인 뷰"""
    template_name = 'ai/leader_assistant_revolutionary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 임시 데이터 (실제로는 데이터베이스에서 가져옴)
        context.update({
            'insights': self.get_leadership_insights(),
            'team_metrics': self.get_team_metrics(),
            'decisions': self.get_pending_decisions(),
        })
        
        return context
    
    def get_leadership_insights(self):
        """리더십 인사이트 생성"""
        return [
            {
                'type': 'critical',
                'icon': '⚠️',
                'title': '핵심 인재 이탈 위험',
                'description': '개발팀 시니어 개발자 2명이 높은 이탈 위험을 보이고 있습니다.',
                'action': '대응 방안 보기'
            },
            {
                'type': 'warning',
                'icon': '📊',
                'title': '팀 성과 하락 추세',
                'description': '마케팅팀의 KPI 달성률이 3개월 연속 하락 중입니다.',
                'action': '상세 분석 보기'
            },
            {
                'type': 'success',
                'icon': '🎯',
                'title': '영업팀 목표 초과 달성',
                'description': '영업팀이 분기 목표를 115% 달성했습니다.',
                'action': '인센티브 계획'
            }
        ]
    
    def get_team_metrics(self):
        """팀 성과 메트릭"""
        return {
            'goal_achievement': 87,
            'goal_change': 5,
            'team_satisfaction': 4.2,
            'satisfaction_change': 0.3,
            'project_completion': 92,
            'completion_change': -2,
            'efficiency_index': 78,
            'efficiency_change': 8
        }
    
    def get_pending_decisions(self):
        """대기 중인 의사결정 사항"""
        return [
            {
                'title': '신규 프로젝트 팀 구성',
                'priority': 'high',
                'content': 'AI 분석 결과, 개발팀 A와 디자인팀 B의 조합이 최적의 시너지를 낼 것으로 예측됩니다.'
            },
            {
                'title': '교육 예산 배분',
                'priority': 'medium',
                'content': 'AI/ML 교육에 40%, 리더십 교육에 30%, 기술 역량에 30% 배분을 추천합니다.'
            }
        ]


@method_decorator(csrf_exempt, name='dispatch')
class LeadershipInsightAPIView(View):
    """리더십 인사이트 API"""
    
    def post(self, request):
        """리더십 관련 AI 분석 요청"""
        try:
            data = json.loads(request.body)
            query_type = data.get('type', 'general')
            context = data.get('context', {})
            
            # 분석 유형에 따른 처리
            if query_type == 'team_analysis':
                result = self.analyze_team_performance(context)
            elif query_type == 'talent_risk':
                result = self.analyze_talent_risk(context)
            elif query_type == 'decision_support':
                result = self.provide_decision_support(context)
            else:
                result = self.general_leadership_advice(context)
            
            return JsonResponse({
                'success': True,
                'analysis': result
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def analyze_team_performance(self, context):
        """팀 성과 분석"""
        # 실제로는 데이터베이스에서 데이터를 가져와 분석
        return {
            'summary': '팀 성과가 전반적으로 향상되고 있습니다.',
            'key_metrics': {
                'productivity': 85,
                'quality': 90,
                'collaboration': 88
            },
            'recommendations': [
                '주간 1:1 미팅 강화',
                '팀 빌딩 활동 증가',
                '성과 인센티브 재설계'
            ]
        }
    
    def analyze_talent_risk(self, context):
        """인재 이탈 위험 분석"""
        return {
            'high_risk_employees': 3,
            'risk_factors': [
                '경력 정체',
                '보상 불만족',
                '워라밸 이슈'
            ],
            'retention_strategies': [
                '경력 개발 계획 수립',
                '유연 근무제 확대',
                '성과 보상 강화'
            ]
        }
    
    def provide_decision_support(self, context):
        """의사결정 지원"""
        return {
            'recommendation': '옵션 A를 추천합니다.',
            'confidence': 0.85,
            'reasoning': [
                'ROI가 가장 높음',
                '리스크가 관리 가능한 수준',
                '팀 역량과 잘 맞음'
            ],
            'risks': [
                '초기 투자 비용',
                '구현 기간 3개월'
            ]
        }
    
    def general_leadership_advice(self, context):
        """일반 리더십 조언"""
        return {
            'advice': '현재 상황에서는 팀원들과의 소통을 강화하는 것이 중요합니다.',
            'action_items': [
                '주간 팀 미팅 정례화',
                '익명 피드백 채널 구축',
                '성과 인정 프로그램 도입'
            ]
        }