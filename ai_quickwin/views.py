"""
AI Quick Win 통합 뷰
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import random

# AI Quick Win 오케스트레이터
from .services import AIQuickWinOrchestrator


class AIQuickWinDashboardView(TemplateView):
    """AI Quick Win 메인 대시보드"""
    template_name = 'ai/quickwin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # AI 모듈 상태 정보
        context['modules'] = [
            {
                'name': '팀 조합 최적화',
                'status': 'active',
                'completion': 85,
                'url': 'ai_team_optimizer:dashboard',
                'icon': 'users',
                'color': 'purple'
            },
            {
                'name': '실시간 코칭 어시스턴트',
                'status': 'active',
                'completion': 70,
                'url': 'ai_coaching:dashboard',
                'icon': 'message-circle',
                'color': 'pink'
            },
            {
                'name': 'AI 인사이트 대시보드',
                'status': 'beta',
                'completion': 60,
                'url': 'ai_insights:dashboard',
                'icon': 'trending-up',
                'color': 'yellow'
            },
            {
                'name': '이직 예측 분석',
                'status': 'beta',
                'completion': 55,
                'url': 'ai_predictions:dashboard',
                'icon': 'user-check',
                'color': 'cyan'
            },
            {
                'name': 'AI 면접 도우미',
                'status': 'beta',
                'completion': 50,
                'url': 'ai_interviewer:dashboard',
                'icon': 'video',
                'color': 'orange'
            }
        ]
        
        # 통계 데이터
        context['stats'] = {
            'active_modules': 7,
            'daily_analysis': 1234,
            'accuracy': 89,
            'response_time': 2.5
        }
        
        return context


class AIQuickWinAPIView(TemplateView):
    """AI Quick Win API 엔드포인트"""
    
    def get(self, request, *args, **kwargs):
        """AI 모듈 상태 및 통계 반환"""
        
        # 더미 데이터 생성
        data = {
            'timestamp': timezone.now().isoformat(),
            'modules': {
                'team_optimizer': {
                    'status': 'active',
                    'usage_today': random.randint(50, 200),
                    'accuracy': random.uniform(85, 95)
                },
                'coaching_assistant': {
                    'status': 'active',
                    'sessions_today': random.randint(20, 100),
                    'satisfaction': random.uniform(4.0, 5.0)
                },
                'insights_dashboard': {
                    'status': 'beta',
                    'reports_generated': random.randint(10, 50),
                    'insights_found': random.randint(100, 500)
                },
                'turnover_prediction': {
                    'status': 'beta',
                    'predictions_today': random.randint(5, 30),
                    'risk_identified': random.randint(10, 50)
                },
                'interview_assistant': {
                    'status': 'beta',
                    'interviews_conducted': random.randint(5, 20),
                    'questions_generated': random.randint(50, 200)
                }
            },
            'overall_stats': {
                'total_api_calls': random.randint(1000, 5000),
                'average_response_time': random.uniform(1.5, 3.5),
                'system_health': 'healthy',
                'uptime_percentage': 99.9
            }
        }
        
        return JsonResponse(data)


def ai_chatbot_view(request):
    """AI 챗봇 뷰"""
    return render(request, 'ai/chatbot.html')


def ai_leader_assistant_view(request):
    """리더 AI 어시스턴트 뷰"""
    return render(request, 'ai/leader_assistant.html')


def ai_settings_view(request):
    """AI 설정 관리 뷰"""
    from .ai_config import ai_config_manager
    import os
    
    # 현재 설정 정보 가져오기
    context = {
        'active_providers': ai_config_manager.get_available_providers(),
        'openai_configured': bool(os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your-openai-api-key-here'),
        'anthropic_configured': bool(os.getenv('ANTHROPIC_API_KEY') and os.getenv('ANTHROPIC_API_KEY') != 'your-anthropic-api-key-here'),
        'google_configured': bool(os.getenv('GOOGLE_AI_API_KEY') and os.getenv('GOOGLE_AI_API_KEY') != 'your-google-api-key-here'),
        'monthly_budget': os.getenv('AI_MONTHLY_BUDGET_USD', '100'),
        'usage': ai_config_manager.usage_tracker.get_current_usage(),
        'modules': [
            {
                'id': 'insights',
                'name': 'AI 인사이트',
                'description': '조직 전반의 인사이트 분석',
                'icon': 'trending-up',
                'enabled': ai_config_manager.is_module_enabled('insights')
            },
            {
                'id': 'predictions',
                'name': '이직 예측',
                'description': '이직 리스크 분석 및 예측',
                'icon': 'user-check',
                'enabled': ai_config_manager.is_module_enabled('predictions')
            },
            {
                'id': 'interviewer',
                'name': 'AI 면접관',
                'description': 'AI 기반 면접 질문 생성',
                'icon': 'video',
                'enabled': ai_config_manager.is_module_enabled('interviewer')
            },
            {
                'id': 'team_optimizer',
                'name': '팀 최적화',
                'description': '최적의 팀 구성 추천',
                'icon': 'users',
                'enabled': ai_config_manager.is_module_enabled('team_optimizer')
            },
            {
                'id': 'coaching',
                'name': '코칭 어시스턴트',
                'description': '개인별 맞춤 코칭',
                'icon': 'message-circle',
                'enabled': ai_config_manager.is_module_enabled('coaching')
            },
            {
                'id': 'airiss',
                'name': 'AIRISS Core',
                'description': '통합 AI 분석 엔진',
                'icon': 'cpu',
                'enabled': ai_config_manager.is_module_enabled('airiss')
            }
        ]
    }
    
    # 예산 사용률 계산
    total_cost = context['usage'].get('total_cost', 0)
    monthly_budget = float(context['monthly_budget'])
    context['budget_usage_percent'] = int((total_cost / monthly_budget) * 100) if monthly_budget > 0 else 0
    
    return render(request, 'ai/ai_settings.html', context)


class EmployeeSyncAPIView(View):
    """직원 프로파일 동기화 API"""
    
    def __init__(self):
        super().__init__()
        self.orchestrator = AIQuickWinOrchestrator()
    
    def post(self, request, employee_id):
        """직원 프로파일을 모든 AI 모듈에 동기화"""
        try:
            result = self.orchestrator.sync_employee_profile(employee_id)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class InterviewToCoachingAPIView(View):
    """면접 결과를 코칭 계획으로 변환하는 API"""
    
    def __init__(self):
        super().__init__()
        self.orchestrator = AIQuickWinOrchestrator()
    
    def post(self, request):
        """면접 세션을 코칭 계획으로 변환"""
        try:
            data = json.loads(request.body)
            interview_session_id = data.get('interview_session_id')
            
            if not interview_session_id:
                return JsonResponse({
                    'success': False,
                    'error': 'interview_session_id is required'
                }, status=400)
            
            result = self.orchestrator.orchestrate_interview_to_coaching(interview_session_id)
            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class ComprehensiveReportAPIView(View):
    """직원 종합 AI 분석 리포트 API"""
    
    def __init__(self):
        super().__init__()
        self.orchestrator = AIQuickWinOrchestrator()
    
    def get(self, request, employee_id):
        """직원에 대한 종합 AI 분석 리포트 생성"""
        try:
            report = self.orchestrator.generate_comprehensive_report(employee_id)
            
            if 'error' in report:
                return JsonResponse({
                    'success': False,
                    'error': report['error']
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'report': report
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class ModuleIntegrationStatusAPIView(View):
    """AI 모듈 통합 상태 API"""
    
    def __init__(self):
        super().__init__()
        self.orchestrator = AIQuickWinOrchestrator()
    
    def get(self, request):
        """모든 AI 모듈의 통합 상태 확인"""
        try:
            status = self.orchestrator.get_module_integration_status()
            return JsonResponse(status)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'integration_health': 'ERROR'
            }, status=500)


@csrf_exempt
def batch_sync_employees(request):
    """다수 직원 일괄 동기화 API"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        employee_ids = data.get('employee_ids', [])
        
        if not employee_ids:
            return JsonResponse({
                'success': False,
                'error': 'employee_ids list is required'
            }, status=400)
        
        orchestrator = AIQuickWinOrchestrator()
        results = []
        
        for emp_id in employee_ids:
            try:
                result = orchestrator.sync_employee_profile(emp_id)
                results.append({
                    'employee_id': emp_id,
                    'success': result.get('success', False),
                    'message': result.get('message', '')
                })
            except Exception as e:
                results.append({
                    'employee_id': emp_id,
                    'success': False,
                    'error': str(e)
                })
        
        success_count = sum(1 for r in results if r['success'])
        
        return JsonResponse({
            'success': True,
            'total_processed': len(employee_ids),
            'success_count': success_count,
            'failed_count': len(employee_ids) - success_count,
            'results': results
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AIProviderTestAPIView(View):
    """AI 프로바이더 연결 테스트 API"""
    
    def post(self, request):
        """AI 프로바이더 연결 및 API 키 테스트"""
        try:
            data = json.loads(request.body)
            provider = data.get('provider')
            api_key = data.get('api_key')
            model_name = data.get('model_name')
            endpoint = data.get('endpoint')
            
            if not provider or not api_key:
                return JsonResponse({
                    'success': False,
                    'error': 'provider와 api_key는 필수입니다'
                }, status=400)
            
            # AI 설정 임시 생성하여 테스트
            from .ai_config import AIModelConfig, AIProvider, AIServiceClient
            
            # 프로바이더 enum 변환
            provider_enum = None
            if provider.lower() == 'openai':
                provider_enum = AIProvider.OPENAI
                model_name = model_name or 'gpt-3.5-turbo'
            elif provider.lower() == 'anthropic':
                provider_enum = AIProvider.ANTHROPIC  
                model_name = model_name or 'claude-3-haiku-20240307'
            elif provider.lower() == 'google':
                provider_enum = AIProvider.GOOGLE
                model_name = model_name or 'gemini-pro'
            elif provider.lower() == 'azure':
                provider_enum = AIProvider.AZURE
                model_name = model_name or 'gpt-4'
            elif provider.lower() == 'local':
                provider_enum = AIProvider.LOCAL
                model_name = model_name or 'llama2'
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'지원하지 않는 프로바이더: {provider}'
                }, status=400)
            
            # 테스트 구성 생성
            test_config = AIModelConfig(
                provider=provider_enum,
                model_name=model_name,
                api_key=api_key,
                endpoint=endpoint,
                max_tokens=100,
                timeout=10
            )
            
            # 테스트 클라이언트 생성 및 테스트 호출
            client = AIServiceClient(test_config)
            test_prompt = "안녕하세요! 연결 테스트입니다."
            
            try:
                response = client.generate_completion(test_prompt)
                
                if response and len(response.strip()) > 0:
                    return JsonResponse({
                        'success': True,
                        'message': f'{provider} 연결 성공!',
                        'test_response': response[:100] + '...' if len(response) > 100 else response
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'API 응답이 비어있습니다'
                    })
                    
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'API 호출 실패: {str(e)}'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'테스트 중 오류 발생: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AIProviderSaveAPIView(View):
    """AI 프로바이더 설정 저장 API"""
    
    def post(self, request):
        """AI 프로바이더 설정을 환경 변수로 저장"""
        try:
            data = json.loads(request.body)
            provider = data.get('provider')
            settings = data.get('settings', {})
            
            if not provider:
                return JsonResponse({
                    'success': False,
                    'error': 'provider는 필수입니다'
                }, status=400)
            
            # 설정을 세션에 임시 저장 (실제로는 환경 변수나 DB에 저장해야 함)
            if not hasattr(request, 'session'):
                return JsonResponse({
                    'success': False,
                    'error': '세션이 활성화되지 않았습니다'
                }, status=500)
            
            session_key = f'ai_config_{provider}'
            request.session[session_key] = settings
            request.session.modified = True
            
            # 기본 프로바이더 설정도 저장
            if data.get('is_default'):
                request.session['default_ai_provider'] = provider
                request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': f'{provider} 설정이 저장되었습니다',
                'saved_settings': {
                    'provider': provider,
                    'model_name': settings.get('model_name'),
                    'is_default': data.get('is_default', False)
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'설정 저장 중 오류: {str(e)}'
            }, status=500)


class AISettingsLoadAPIView(View):
    """AI 설정 로드 API"""
    
    def get(self, request):
        """현재 AI 설정 불러오기"""
        try:
            from .ai_config import ai_config_manager
            
            # 사용 가능한 프로바이더 목록
            available_providers = ai_config_manager.get_available_providers()
            
            # 세션에서 저장된 설정 불러오기
            saved_settings = {}
            default_provider = None
            
            if hasattr(request, 'session'):
                # 각 프로바이더별 저장된 설정 확인
                for provider in ['openai', 'anthropic', 'google', 'azure', 'local']:
                    session_key = f'ai_config_{provider}'
                    if session_key in request.session:
                        saved_settings[provider] = request.session[session_key]
                
                # 기본 프로바이더 확인
                default_provider = request.session.get('default_ai_provider')
            
            return JsonResponse({
                'success': True,
                'available_providers': available_providers,
                'default_provider': default_provider or ai_config_manager.default_provider,
                'saved_settings': saved_settings,
                'environment_config': {
                    'openai_configured': bool(ai_config_manager.configs.get('openai')),
                    'anthropic_configured': bool(ai_config_manager.configs.get('anthropic')),
                    'google_configured': bool(ai_config_manager.configs.get('google')),
                    'azure_configured': bool(ai_config_manager.configs.get('azure')),
                    'local_configured': bool(ai_config_manager.configs.get('local'))
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'설정 로드 중 오류: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AIChatAPIView(View):
    """AI 챗봇 실제 응답 API"""
    
    def post(self, request):
        """사용자 질문에 대한 AI 응답 생성"""
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({
                    'success': False,
                    'error': '메시지가 비어있습니다'
                }, status=400)
            
            # AI 클라이언트 가져오기
            from .ai_config import get_ai_client
            
            # 세션에서 저장된 설정 사용 또는 환경변수 설정 사용
            ai_client = self._get_ai_client_for_session(request, 'chatbot')
            
            if not ai_client:
                return JsonResponse({
                    'success': False,
                    'error': 'AI 서비스가 설정되지 않았습니다. 설정 페이지에서 API 키를 구성해주세요.'
                })
            
            # HR 전용 시스템 프롬프트
            system_prompt = """당신은 OK금융그룹의 전문 HR AI 어시스턴트입니다. 
            다음과 같은 역할을 수행합니다:

            - 인사 정책, 복리후생, 평가 제도에 대한 정확한 정보 제공
            - 직원들의 경력 개발과 교육에 대한 조언
            - 조직 문화와 업무 프로세스에 대한 안내
            - 근무 환경과 제도 관련 질문 답변

            답변 시 다음 원칙을 지켜주세요:
            1. 정확하고 도움이 되는 정보 제공
            2. 친근하고 전문적인 톤 사용
            3. 불확실한 정보는 HR 담당자 문의 안내
            4. 개인정보나 기밀 정보는 절대 요구하지 않음
            5. 한국어로 자연스럽게 응답"""
            
            try:
                # AI 응답 생성
                response = ai_client.generate_completion(
                    prompt=user_message,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=500
                )
                
                if response:
                    return JsonResponse({
                        'success': True,
                        'response': response,
                        'timestamp': timezone.now().isoformat()
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'AI 서비스에서 응답을 받지 못했습니다'
                    })
                    
            except Exception as e:
                # AI 호출 실패 시 폴백 응답
                fallback_response = self._get_fallback_response(user_message)
                return JsonResponse({
                    'success': True,
                    'response': fallback_response,
                    'fallback': True,
                    'timestamp': timezone.now().isoformat()
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'오류가 발생했습니다: {str(e)}'
            }, status=500)
    
    def _get_ai_client_for_session(self, request, module_name):
        """세션 또는 환경변수 기반 AI 클라이언트 가져오기"""
        from .ai_config import get_ai_client, AIServiceClient, AIModelConfig, AIProvider
        
        # 먼저 환경변수 기반 클라이언트 시도
        ai_client = get_ai_client(module_name)
        if ai_client:
            return ai_client
        
        # 세션에서 저장된 설정 사용
        if hasattr(request, 'session'):
            # 기본 프로바이더 확인
            default_provider = request.session.get('default_ai_provider', 'openai')
            session_key = f'ai_config_{default_provider}'
            
            if session_key in request.session:
                settings = request.session[session_key]
                
                try:
                    # 세션 기반 설정으로 클라이언트 생성
                    provider_enum = AIProvider.OPENAI  # 기본값
                    if default_provider.lower() == 'anthropic':
                        provider_enum = AIProvider.ANTHROPIC
                    elif default_provider.lower() == 'google':
                        provider_enum = AIProvider.GOOGLE
                    
                    config = AIModelConfig(
                        provider=provider_enum,
                        model_name=settings.get('model_name', 'gpt-3.5-turbo'),
                        api_key=settings.get('api_key'),
                        temperature=0.7,
                        max_tokens=500
                    )
                    
                    return AIServiceClient(config)
                    
                except Exception:
                    pass
        
        return None
    
    def _get_fallback_response(self, message):
        """AI 호출 실패 시 폴백 응답"""
        responses = {
            '연차': 'HR 정책에 따르면 연차휴가는 근속기간에 따라 차등 지급됩니다. 자세한 내용은 HR 담당자에게 문의해주세요.',
            '평가': '성과평가는 정기적으로 실시되며 다양한 지표를 종합 평가합니다. 구체적인 평가 기준은 HR포털에서 확인 가능합니다.',
            '교육': '직원 교육 프로그램은 HR포털을 통해 신청하실 수 있습니다. 다양한 교육 과정이 준비되어 있습니다.',
            '재택': '재택근무 정책에 대한 자세한 내용은 최신 정책을 HR 담당자에게 확인해주시기 바랍니다.',
            '급여': '급여 관련 문의사항은 HR 담당자 또는 급여 담당자에게 직접 문의해주세요.',
            '복리후생': '복리후생 제도에 대한 상세 정보는 직원 핸드북이나 HR포털에서 확인하실 수 있습니다.'
        }
        
        # 키워드 매칭
        for key, response in responses.items():
            if key in message:
                return response
        
        return '죄송합니다. 현재 AI 서비스 연결에 문제가 있어 정확한 답변을 드리기 어렵습니다. HR 담당자에게 직접 문의해주시거나, 잠시 후 다시 시도해주세요.'


@method_decorator(csrf_exempt, name='dispatch')  
class AILeaderAssistantAPIView(View):
    """AI 리더 어시스턴트 응답 API"""
    
    def post(self, request):
        """리더십 관련 질문에 대한 AI 응답 생성"""
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({
                    'success': False,
                    'error': '메시지가 비어있습니다'
                }, status=400)
            
            # AI 클라이언트 가져오기 (챗봇과 동일한 로직)
            ai_client = AIChatAPIView()._get_ai_client_for_session(request, 'leader_assistant')
            
            if not ai_client:
                return JsonResponse({
                    'success': False,
                    'error': 'AI 서비스가 설정되지 않았습니다. 설정 페이지에서 API 키를 구성해주세요.'
                })
            
            # 리더십 전용 시스템 프롬프트
            system_prompt = """당신은 OK금융그룹의 전문 리더십 AI 어시스턴트입니다. 
            관리자와 리더들을 위한 전문적인 조언을 제공합니다.

            전문 분야:
            - 팀 관리 및 리더십 스킬
            - 성과 관리 및 평가
            - 조직 운영 및 의사결정
            - 직원 동기부여 및 개발
            - 갈등 해결 및 커뮤니케이션
            - 전략적 사고 및 비전 수립

            답변 원칙:
            1. 실용적이고 구체적인 리더십 조언 제공
            2. 경험과 이론을 바탕으로 한 전문적 답변
            3. 상황별 맞춤 솔루션 제시
            4. 윤리적이고 건설적인 관점 유지
            5. 한국 기업 문화에 적합한 조언"""
            
            try:
                # AI 응답 생성
                response = ai_client.generate_completion(
                    prompt=user_message,
                    system_prompt=system_prompt,
                    temperature=0.6,  # 리더십 조언은 조금 더 일관성 있게
                    max_tokens=600
                )
                
                if response:
                    return JsonResponse({
                        'success': True,
                        'response': response,
                        'timestamp': timezone.now().isoformat()
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'AI 서비스에서 응답을 받지 못했습니다'
                    })
                    
            except Exception as e:
                # AI 호출 실패 시 폴백 응답
                fallback_response = self._get_leadership_fallback_response(user_message)
                return JsonResponse({
                    'success': True,
                    'response': fallback_response,
                    'fallback': True,
                    'timestamp': timezone.now().isoformat()
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'오류가 발생했습니다: {str(e)}'
            }, status=500)
    
    def _get_leadership_fallback_response(self, message):
        """리더십 관련 폴백 응답"""
        responses = {
            '팀': '효과적인 팀 관리를 위해서는 명확한 목표 설정, 정기적인 소통, 그리고 팀원들의 강점을 파악하여 활용하는 것이 중요합니다.',
            '성과': '성과 관리는 목표 설정, 진행 상황 모니터링, 피드백 제공, 그리고 결과 평가의 순환 과정으로 이루어집니다.',
            '소통': '리더의 효과적인 소통을 위해서는 경청, 명확한 전달, 그리고 상황에 맞는 커뮤니케이션 방식 선택이 핵심입니다.',
            '동기': '직원 동기부여를 위해서는 개인의 성장 기회 제공, 성과 인정, 그리고 의미 있는 업무 부여가 효과적입니다.',
            '의사결정': '좋은 의사결정을 위해서는 충분한 정보 수집, 다양한 관점 고려, 그리고 리스크와 기회의 균형을 맞추는 것이 중요합니다.',
            '갈등': '갈등 해결 시에는 양측의 입장을 이해하고, 공통의 목표를 찾아 Win-Win 해결책을 모색하는 것이 바람직합니다.'
        }
        
        # 키워드 매칭
        for key, response in responses.items():
            if key in message:
                return response
        
        return '리더십은 지속적인 학습과 실践의 과정입니다. 구체적인 상황에 대해 더 자세히 말씀해 주시면 더 정확한 조언을 드릴 수 있습니다. 현재 AI 서비스 연결에 일시적인 문제가 있어 제한적인 답변을 드리고 있습니다.'