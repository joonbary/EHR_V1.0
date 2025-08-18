"""
AI Interviewer Services - AI 채용 면접관 서비스
"""
import json
import logging

# OpenAI import 처리
try:
    import openai
except ImportError:
    openai = None
    
# Anthropic import 처리
try:
    import anthropic
except ImportError:
    anthropic = None
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Avg

from .models import (
    InterviewSession, InterviewQuestion, InterviewResponse,
    InterviewFeedback, InterviewTemplate, InterviewMetrics
)
from job_profiles.models import JobProfile
from employees.models import Employee

logger = logging.getLogger(__name__)


class AIInterviewer:
    """AI 면접관 클래스"""
    
    def __init__(self, session: InterviewSession):
        self.session = session
        self.job_profile = session.job_profile
        self.ai_client = self._get_ai_client()
        self.personality = session.ai_personality
        self.language = session.interview_language
        
    def _get_ai_client(self):
        """AI 클라이언트 초기화"""
        try:
            # OpenAI API 우선 사용
            if openai and hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                return 'openai'
            # Anthropic Claude 사용
            elif anthropic and hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
                try:
                    # 새 버전 시도
                    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                except (TypeError, AttributeError):
                    # 구버전 Anthropic 라이브러리 처리
                    try:
                        return anthropic.Client(settings.ANTHROPIC_API_KEY)
                    except:
                        logger.warning("Anthropic client initialization failed")
                        return None
            else:
                logger.warning("AI API 키가 설정되지 않았습니다. 시뮬레이션 모드로 동작합니다.")
                return None
        except Exception as e:
            logger.error(f"AI 클라이언트 초기화 오류: {e}")
            return None
    
    def start_interview(self) -> Dict[str, Any]:
        """면접 시작"""
        try:
            # 세션 상태 업데이트
            self.session.status = 'IN_PROGRESS'
            self.session.started_at = timezone.now()
            self.session.save()
            
            # 첫 번째 질문 생성
            first_question = self.generate_next_question()
            
            return {
                'success': True,
                'session_id': str(self.session.session_id),
                'status': 'STARTED',
                'first_question': self._format_question(first_question),
                'message': f"안녕하세요! {self.session.candidate_name}님, {self.job_profile.title} 면접을 시작하겠습니다."
            }
            
        except Exception as e:
            logger.error(f"면접 시작 오류: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_next_question(self, previous_response: Optional[InterviewResponse] = None) -> InterviewQuestion:
        """다음 질문 생성"""
        try:
            question_number = self.session.questions.count() + 1
            
            # 질문 생성 컨텍스트 구성
            context = self._build_question_context(previous_response)
            
            # AI로 질문 생성
            question_data = self._generate_question_with_ai(context, question_number)
            
            # 질문 저장
            question = InterviewQuestion.objects.create(
                session=self.session,
                question_number=question_number,
                question_type=question_data.get('type', 'BEHAVIORAL'),
                question_text=question_data['text'],
                question_context=question_data.get('context', ''),
                expected_answer_points=question_data.get('expected_points', []),
                evaluation_criteria=question_data.get('criteria', 'COMMUNICATION'),
                difficulty_score=question_data.get('difficulty', 5.0),
                estimated_response_time=question_data.get('time_limit', 120),
                ai_reasoning=question_data.get('reasoning', ''),
                adapted_from_previous=bool(previous_response),
                tags=question_data.get('tags', [])
            )
            
            return question
            
        except Exception as e:
            logger.error(f"질문 생성 오류: {e}")
            # 폴백: 기본 질문 생성
            return self._generate_fallback_question(question_number)
    
    def _build_question_context(self, previous_response: Optional[InterviewResponse] = None) -> Dict[str, Any]:
        """질문 생성 컨텍스트 구성"""
        context = {
            'job_profile': {
                'title': self.job_profile.title,
                'department': self.job_profile.department,
                'required_skills': self.job_profile.required_skills,
                'job_level': self.job_profile.job_level
            },
            'session_info': {
                'type': self.session.session_type,
                'difficulty': self.session.difficulty_level,
                'current_question': self.session.questions.count() + 1,
                'max_questions': self.session.max_questions
            },
            'candidate_info': {
                'name': self.session.candidate_name,
                'previous_responses': []
            }
        }
        
        # 이전 응답 정보 추가
        if previous_response:
            context['candidate_info']['previous_responses'] = [
                {
                    'question': previous_response.question.question_text,
                    'response': previous_response.response_text,
                    'score': previous_response.ai_score,
                    'analysis': previous_response.ai_analysis
                }
            ]
        
        return context
    
    def _generate_question_with_ai(self, context: Dict[str, Any], question_number: int) -> Dict[str, Any]:
        """AI를 사용해 질문 생성"""
        if not self.ai_client:
            return self._generate_simulated_question(question_number)
        
        try:
            # 프롬프트 구성
            system_prompt = self._build_interviewer_prompt()
            user_prompt = f"""
다음 맥락을 바탕으로 면접 질문을 생성해주세요:

채용 공고: {context['job_profile']['title']} ({context['job_profile']['department']})
면접 유형: {context['session_info']['type']}
난이도: {context['session_info']['difficulty']}
질문 순서: {question_number}/{context['session_info']['max_questions']}

{f"이전 응답 분석: {context['candidate_info']['previous_responses']}" if context['candidate_info']['previous_responses'] else "첫 번째 질문입니다."}

다음 JSON 형식으로 응답해주세요:
{{
    "text": "질문 내용",
    "type": "질문 유형 (BEHAVIORAL/TECHNICAL/SITUATIONAL 등)",
    "context": "질문 배경 설명",
    "expected_points": ["기대하는 답변 요소들"],
    "criteria": "평가 기준 (COMMUNICATION/PROBLEM_SOLVING 등)",
    "difficulty": 난이도 점수 (1-10),
    "time_limit": 예상 응답 시간(초),
    "reasoning": "이 질문을 선택한 이유",
    "tags": ["관련 태그들"]
}}
"""
            
            if self.ai_client == 'openai':
                response = openai.ChatCompletion.create(
                    model=self.session.ai_model_version,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                content = response.choices[0].message.content
                
            else:  # Anthropic Claude
                response = self.ai_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                content = response.content[0].text
            
            # JSON 파싱
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"AI 질문 생성 오류: {e}")
            return self._generate_simulated_question(question_number)
    
    def _build_interviewer_prompt(self) -> str:
        """면접관 AI 프롬프트 구성"""
        personality_traits = {
            'PROFESSIONAL': '전문적이고 객관적인',
            'FRIENDLY': '친근하고 따뜻한',
            'CHALLENGING': '도전적이고 분석적인',
            'SUPPORTIVE': '지원적이고 격려하는'
        }
        
        personality = personality_traits.get(self.personality, '전문적이고 객관적인')
        
        return f"""당신은 {personality} AI 면접관입니다.

핵심 역할:
1. 지원자의 역량을 정확히 평가할 수 있는 질문 생성
2. 이전 응답을 바탕으로 한 적응형 후속 질문 개발
3. 채용 공고와 직무에 특화된 맞춤형 질문 구성

질문 원칙:
- 구체적이고 실무 중심적
- 지원자의 경험과 역량을 파악 가능
- 차별 없이 공정한 평가 기준
- 명확하고 이해하기 쉬운 표현
- 적절한 난이도와 시간 배분

면접 언어: {self.language}
항상 JSON 형식으로 정확히 응답하세요."""
    
    def _generate_simulated_question(self, question_number: int) -> Dict[str, Any]:
        """시뮬레이션 질문 생성 (AI 사용 불가시 폴백)"""
        question_templates = [
            {
                "text": f"{self.job_profile.title} 직무에 지원하신 이유와 본인이 이 역할에 적합한 이유를 말씀해 주세요.",
                "type": "BEHAVIORAL",
                "criteria": "COMMUNICATION",
                "difficulty": 3
            },
            {
                "text": "이전 경험에서 어려운 문제를 해결했던 사례를 구체적으로 설명해 주세요.",
                "type": "SITUATIONAL",
                "criteria": "PROBLEM_SOLVING",
                "difficulty": 5
            },
            {
                "text": "팀 프로젝트에서 갈등이 생겼을 때 어떻게 해결하시나요?",
                "type": "BEHAVIORAL",
                "criteria": "TEAMWORK",
                "difficulty": 4
            },
            {
                "text": f"{self.job_profile.department}에서 가장 중요하게 생각하는 가치나 원칙은 무엇인가요?",
                "type": "CULTURAL_FIT",
                "criteria": "CULTURAL_FIT",
                "difficulty": 3
            }
        ]
        
        template = question_templates[(question_number - 1) % len(question_templates)]
        
        return {
            "text": template["text"],
            "type": template["type"],
            "context": "AI 시뮬레이션으로 생성된 질문입니다.",
            "expected_points": ["구체적 사례", "논리적 설명", "결과 및 학습점"],
            "criteria": template["criteria"],
            "difficulty": template["difficulty"],
            "time_limit": 120,
            "reasoning": "기본 템플릿 기반 질문",
            "tags": ["기본질문", "시뮬레이션"]
        }
    
    def _generate_fallback_question(self, question_number: int) -> InterviewQuestion:
        """폴백 질문 생성"""
        question_data = self._generate_simulated_question(question_number)
        
        return InterviewQuestion.objects.create(
            session=self.session,
            question_number=question_number,
            question_type=question_data['type'],
            question_text=question_data['text'],
            question_context=question_data['context'],
            evaluation_criteria=question_data['criteria'],
            difficulty_score=question_data['difficulty'],
            estimated_response_time=120,
            generated_by_ai=False
        )
    
    def evaluate_response(self, response: InterviewResponse) -> Dict[str, Any]:
        """응답 평가"""
        try:
            if not self.ai_client:
                return self._evaluate_response_simulated(response)
            
            # AI 평가 수행
            evaluation = self._evaluate_with_ai(response)
            
            # 응답 업데이트
            response.ai_score = evaluation['score']
            response.ai_feedback = evaluation['feedback']
            response.ai_analysis = evaluation['analysis']
            response.quality_rating = evaluation['quality_rating']
            response.sentiment_score = evaluation.get('sentiment_score', 0.0)
            response.confidence_level = evaluation.get('confidence_level', 0.0)
            response.clarity_score = evaluation.get('clarity_score', 0.0)
            response.relevance_score = evaluation.get('relevance_score', 0.0)
            response.keyword_matches = evaluation.get('keyword_matches', [])
            response.word_count = len(response.response_text.split())
            response.save()
            
            return {
                'success': True,
                'evaluation': evaluation,
                'next_question_ready': self._should_continue_interview()
            }
            
        except Exception as e:
            logger.error(f"응답 평가 오류: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _evaluate_with_ai(self, response: InterviewResponse) -> Dict[str, Any]:
        """AI를 사용한 응답 평가"""
        try:
            question = response.question
            
            evaluation_prompt = f"""
다음 면접 응답을 평가해주세요:

질문: {question.question_text}
평가 기준: {question.get_evaluation_criteria_display()}
예상 답변 포인트: {question.expected_answer_points}

응답자 답변:
{response.response_text}

응답 시간: {response.response_time_seconds:.1f}초
예상 시간: {question.estimated_response_time}초

다음 JSON 형식으로 평가 결과를 제공해주세요:
{{
    "score": 0-10 점수,
    "feedback": "상세한 피드백",
    "analysis": {{
        "strengths": ["강점들"],
        "weaknesses": ["약점들"],
        "key_insights": ["핵심 인사이트"]
    }},
    "quality_rating": "EXCELLENT/GOOD/AVERAGE/BELOW_AVERAGE/POOR",
    "sentiment_score": -1.0 ~ 1.0 감정 점수,
    "confidence_level": 0.0 ~ 1.0 자신감 수준,
    "clarity_score": 0.0 ~ 1.0 명확성 점수,
    "relevance_score": 0.0 ~ 1.0 관련성 점수,
    "keyword_matches": ["일치하는 키워드들"]
}}
"""
            
            if self.ai_client == 'openai':
                response = openai.ChatCompletion.create(
                    model=self.session.ai_model_version,
                    messages=[
                        {"role": "system", "content": "당신은 공정하고 전문적인 면접관입니다."},
                        {"role": "user", "content": evaluation_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )
                content = response.choices[0].message.content
                
            else:  # Anthropic Claude
                response = self.ai_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=800,
                    temperature=0.3,
                    system="당신은 공정하고 전문적인 면접관입니다.",
                    messages=[{"role": "user", "content": evaluation_prompt}]
                )
                content = response.content[0].text
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"AI 평가 오류: {e}")
            return self._evaluate_response_simulated(response)
    
    def _evaluate_response_simulated(self, response: InterviewResponse) -> Dict[str, Any]:
        """시뮬레이션 응답 평가"""
        word_count = len(response.response_text.split())
        time_factor = min(1.0, response.response_time_seconds / response.question.estimated_response_time)
        
        # 기본 점수 계산 (단어 수와 시간 기반)
        base_score = min(10.0, (word_count / 50) * 5 + time_factor * 3)
        
        return {
            'score': base_score,
            'feedback': '시뮬레이션 모드에서 생성된 평가입니다.',
            'analysis': {
                'strengths': ['응답을 제공함'],
                'weaknesses': [],
                'key_insights': ['기본적인 의사소통 능력']
            },
            'quality_rating': 'AVERAGE',
            'sentiment_score': 0.0,
            'confidence_level': 0.5,
            'clarity_score': 0.6,
            'relevance_score': 0.7,
            'keyword_matches': []
        }
    
    def _should_continue_interview(self) -> bool:
        """면접 계속 진행 여부 판단"""
        current_questions = self.session.questions.count()
        return current_questions < self.session.max_questions
    
    def complete_interview(self) -> Dict[str, Any]:
        """면접 완료"""
        try:
            self.session.status = 'COMPLETED'
            self.session.completed_at = timezone.now()
            self.session.total_questions_asked = self.session.questions.count()
            self.session.total_responses = self.session.questions.filter(
                response__isnull=False
            ).count()
            
            # 평균 응답 시간 계산
            responses = InterviewResponse.objects.filter(
                question__session=self.session
            )
            if responses.exists():
                avg_time = responses.aggregate(
                    avg=Avg('response_time_seconds')
                )['avg']
                self.session.average_response_time = avg_time or 0.0
                
                # 종합 점수 계산
                avg_score = responses.aggregate(
                    avg=Avg('ai_score')
                )['avg']
                self.session.overall_score = avg_score or 0.0
            
            self.session.save()
            
            # 최종 AI 평가 생성
            final_assessment = self._generate_final_assessment()
            self.session.ai_assessment = final_assessment
            self.session.save()
            
            # 면접 지표 계산
            metrics = self._calculate_metrics()
            
            # 피드백 생성
            feedback = self._generate_comprehensive_feedback()
            
            return {
                'success': True,
                'session_id': str(self.session.session_id),
                'status': 'COMPLETED',
                'final_score': self.session.overall_score,
                'duration_minutes': self.session.get_duration_minutes(),
                'assessment': final_assessment,
                'metrics': metrics,
                'feedback': feedback
            }
            
        except Exception as e:
            logger.error(f"면접 완료 처리 오류: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_final_assessment(self) -> Dict[str, Any]:
        """최종 AI 평가 생성"""
        responses = InterviewResponse.objects.filter(
            question__session=self.session
        )
        
        if not responses.exists():
            return {"message": "응답이 없어 평가할 수 없습니다."}
        
        # 기본 통계
        scores = [r.ai_score for r in responses if r.ai_score > 0]
        
        assessment = {
            'overall_performance': 'AVERAGE',
            'total_questions': self.session.questions.count(),
            'completed_responses': len(scores),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'score_distribution': {
                'excellent': len([s for s in scores if s >= 8]),
                'good': len([s for s in scores if 6 <= s < 8]),
                'average': len([s for s in scores if 4 <= s < 6]),
                'below_average': len([s for s in scores if s < 4])
            },
            'key_strengths': [],
            'areas_for_improvement': [],
            'recommendation': 'NEUTRAL',
            'confidence': 0.7
        }
        
        # 성과 등급 결정
        avg_score = assessment['average_score']
        if avg_score >= 8:
            assessment['overall_performance'] = 'EXCELLENT'
            assessment['recommendation'] = 'STRONGLY_RECOMMEND'
        elif avg_score >= 6:
            assessment['overall_performance'] = 'GOOD'
            assessment['recommendation'] = 'RECOMMEND'
        elif avg_score >= 4:
            assessment['overall_performance'] = 'AVERAGE'
            assessment['recommendation'] = 'NEUTRAL'
        else:
            assessment['overall_performance'] = 'BELOW_AVERAGE'
            assessment['recommendation'] = 'NOT_RECOMMEND'
        
        return assessment
    
    def _calculate_metrics(self) -> InterviewMetrics:
        """면접 지표 계산"""
        responses = InterviewResponse.objects.filter(
            question__session=self.session
        )
        
        metrics_data = {
            'total_duration_minutes': self.session.get_duration_minutes(),
            'average_question_time': 0.0,
            'response_completeness': 0.0,
            'average_response_length': 0,
            'communication_score': 0.0,
            'problem_solving_score': 0.0,
            'technical_competence': 0.0,
            'cultural_fit_score': 0.0
        }
        
        if responses.exists():
            # 시간 지표
            total_time = sum(r.response_time_seconds for r in responses)
            metrics_data['average_question_time'] = total_time / (responses.count() * 60)
            
            # 응답 품질 지표
            response_lengths = [len(r.response_text.split()) for r in responses]
            metrics_data['average_response_length'] = sum(response_lengths) / len(response_lengths)
            metrics_data['response_completeness'] = min(1.0, metrics_data['average_response_length'] / 100)
            
            # 역량별 점수 (평가 기준별로 집계)
            criteria_scores = {}
            for response in responses:
                criteria = response.question.evaluation_criteria
                if criteria not in criteria_scores:
                    criteria_scores[criteria] = []
                criteria_scores[criteria].append(response.ai_score)
            
            # 평균 점수 계산
            for criteria, scores in criteria_scores.items():
                avg_score = sum(scores) / len(scores) / 10  # 0-1 스케일로 변환
                if criteria == 'COMMUNICATION':
                    metrics_data['communication_score'] = avg_score
                elif criteria == 'PROBLEM_SOLVING':
                    metrics_data['problem_solving_score'] = avg_score
                elif criteria == 'TECHNICAL_SKILLS':
                    metrics_data['technical_competence'] = avg_score
                elif criteria == 'CULTURAL_FIT':
                    metrics_data['cultural_fit_score'] = avg_score
        
        # 종합 추천도 결정
        overall_score = sum([
            metrics_data['communication_score'],
            metrics_data['problem_solving_score'],
            metrics_data['technical_competence'],
            metrics_data['cultural_fit_score']
        ]) / 4
        
        if overall_score >= 0.8:
            recommendation = 'STRONGLY_RECOMMEND'
        elif overall_score >= 0.6:
            recommendation = 'RECOMMEND'
        elif overall_score >= 0.4:
            recommendation = 'NEUTRAL'
        elif overall_score >= 0.2:
            recommendation = 'NOT_RECOMMEND'
        else:
            recommendation = 'STRONGLY_NOT_RECOMMEND'
        
        metrics_data['overall_recommendation'] = recommendation
        
        # 메트릭스 저장
        metrics, created = InterviewMetrics.objects.update_or_create(
            session=self.session,
            defaults=metrics_data
        )
        
        return metrics
    
    def _generate_comprehensive_feedback(self) -> List[InterviewFeedback]:
        """종합 피드백 생성"""
        feedback_list = []
        
        # 종합 평가 피드백
        overall_feedback = InterviewFeedback.objects.create(
            session=self.session,
            feedback_type='OVERALL',
            title='종합 면접 평가',
            content=f"""
{self.session.candidate_name}님의 면접이 완료되었습니다.

📊 면접 결과 요약:
• 총 질문 수: {self.session.total_questions_asked}개
• 평균 점수: {self.session.overall_score:.1f}/10점  
• 소요 시간: {self.session.get_duration_minutes()}분
• 완료율: {self.session.get_completion_rate():.1f}%

전반적으로 성실하게 면접에 임하셨으며, 각 질문에 대해 진솔한 답변을 해주셨습니다.
""",
            rating=max(1, min(5, int(self.session.overall_score / 2))),
            priority_level=5
        )
        feedback_list.append(overall_feedback)
        
        return feedback_list
    
    def _format_question(self, question: InterviewQuestion) -> Dict[str, Any]:
        """질문 포맷팅"""
        return {
            'id': question.id,
            'number': question.question_number,
            'type': question.get_question_type_display(),
            'text': question.question_text,
            'context': question.question_context,
            'time_limit': question.estimated_response_time,
            'difficulty': question.difficulty_score
        }


class InterviewTemplateManager:
    """면접 템플릿 관리자"""
    
    @staticmethod
    def create_default_templates():
        """기본 템플릿 생성"""
        default_templates = [
            {
                'name': '일반 신입사원 면접',
                'category': 'ENTRY_LEVEL',
                'description': '신입 사원을 위한 기본 면접 템플릿',
                'target_duration': 20,
                'question_count': 6,
                'difficulty_level': 'BEGINNER',
                'question_templates': [
                    {
                        'type': 'BEHAVIORAL',
                        'text': '자기소개를 해주세요.',
                        'criteria': 'COMMUNICATION'
                    },
                    {
                        'type': 'BEHAVIORAL', 
                        'text': '우리 회사에 지원한 이유는 무엇인가요?',
                        'criteria': 'CULTURAL_FIT'
                    }
                ]
            },
            {
                'name': '기술직 면접',
                'category': 'TECHNICAL',
                'description': '개발자 및 기술직을 위한 면접 템플릿',
                'target_duration': 45,
                'question_count': 10,
                'difficulty_level': 'INTERMEDIATE',
                'question_templates': [
                    {
                        'type': 'TECHNICAL',
                        'text': '최근 진행한 프로젝트에 대해 설명해 주세요.',
                        'criteria': 'TECHNICAL_SKILLS'
                    }
                ]
            }
        ]
        
        for template_data in default_templates:
            InterviewTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )


class InterviewAnalyzer:
    """면접 분석기"""
    
    @staticmethod
    def get_session_statistics(days: int = 30) -> Dict[str, Any]:
        """면접 세션 통계"""
        from django.db.models import Count, Avg
        from datetime import timedelta
        
        cutoff_date = timezone.now().date() - timedelta(days=days)
        sessions = InterviewSession.objects.filter(
            created_at__date__gte=cutoff_date
        )
        
        stats = {
            'total_sessions': sessions.count(),
            'completed_sessions': sessions.filter(status='COMPLETED').count(),
            'in_progress_sessions': sessions.filter(status='IN_PROGRESS').count(),
            'average_score': sessions.aggregate(avg=Avg('overall_score'))['avg'] or 0,
            'average_duration': sessions.aggregate(avg=Avg('average_response_time'))['avg'] or 0,
            'by_type': dict(sessions.values('session_type').annotate(count=Count('id')).values_list('session_type', 'count')),
            'by_status': dict(sessions.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'completion_rate': 0
        }
        
        if stats['total_sessions'] > 0:
            stats['completion_rate'] = (stats['completed_sessions'] / stats['total_sessions']) * 100
        
        return stats
    
    @staticmethod
    def get_candidate_insights(session_id: str) -> Dict[str, Any]:
        """후보자 인사이트 분석"""
        try:
            session = InterviewSession.objects.get(session_id=session_id)
            responses = InterviewResponse.objects.filter(question__session=session)
            
            insights = {
                'performance_trend': [],
                'strength_areas': [],
                'improvement_areas': [],
                'response_patterns': {},
                'recommendations': []
            }
            
            # 성과 트렌드 분석
            for response in responses.order_by('question__question_number'):
                insights['performance_trend'].append({
                    'question': response.question.question_number,
                    'score': response.ai_score,
                    'time': response.response_time_seconds
                })
            
            # 강점/약점 분석
            high_scores = responses.filter(ai_score__gte=7.0)
            low_scores = responses.filter(ai_score__lt=5.0)
            
            insights['strength_areas'] = [
                response.question.get_evaluation_criteria_display() 
                for response in high_scores
            ]
            
            insights['improvement_areas'] = [
                response.question.get_evaluation_criteria_display() 
                for response in low_scores
            ]
            
            return insights
            
        except InterviewSession.DoesNotExist:
            return {'error': '세션을 찾을 수 없습니다.'}