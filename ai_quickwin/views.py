"""
AI Quick Win 통합 뷰
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
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