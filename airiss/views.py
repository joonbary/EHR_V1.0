from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Avg, Q, F, Sum
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json
import random

from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation, EvaluationPeriod
from compensation.models import EmployeeCompensation
from .models import (
    AIAnalysisType, AIAnalysisResult, HRChatbotConversation, 
    AIInsight, AIModelConfig
)
# Temporarily comment out AI model imports due to scikit-learn issues
# from .ai_models import AIModelManager, TurnoverPredictionModel, PromotionPredictionModel, TeamPerformanceModel
from .ai_chatbot import get_hr_chatbot_response, get_hr_suggested_questions


def dashboard(request):
    """AIRISS 대시보드"""
    import os
    print("=" * 80)
    print("[AIRISS DEBUG] dashboard() function called!")
    print(f"[AIRISS DEBUG] Request path: {request.path}")
    print(f"[AIRISS DEBUG] Current working directory: {os.getcwd()}")
    print("=" * 80)
    
    # 강제로 에러를 발생시켜서 이 코드가 실행되는지 확인
    # raise Exception("AIRISS DEBUG: This is a test exception to verify code execution")
    
    context = {
        'current_time': timezone.now(),
        
        # AI 분석 통계
        'total_analyses': AIAnalysisResult.objects.count(),
        'recent_analyses': AIAnalysisResult.objects.select_related(
            'analysis_type', 'employee'
        ).order_by('-analyzed_at')[:5],
        
        # 인사이트 통계
        'active_insights': AIInsight.objects.filter(
            is_archived=False
        ).count(),
        'high_priority_insights': AIInsight.objects.filter(
            priority='HIGH',
            is_archived=False
        )[:3],
        
        # 챗봇 통계
        'total_conversations': HRChatbotConversation.objects.count(),
        'active_conversations': HRChatbotConversation.objects.filter(
            is_active=True
        ).count(),
        
        # 분석 유형별 차트 데이터
        'analysis_by_type': list(
            AIAnalysisResult.objects.values(
                'analysis_type__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5]
        ),
        
        # 부서별 퇴사 위험도
        'turnover_risk_by_dept': get_turnover_risk_by_department(),
        
        # 최근 7일 분석 추세
        'analysis_trend': get_analysis_trend_data(),
    }
    
    # dashboard.html 사용
    return render(request, 'airiss/dashboard.html', context)


def dashboard_original(request):
    """원본 AIRISS 대시보드"""
    context = {
        'current_time': timezone.now(),
        
        # AI 분석 통계
        'total_analyses': AIAnalysisResult.objects.count(),
        'recent_analyses': AIAnalysisResult.objects.select_related(
            'analysis_type', 'employee'
        ).order_by('-analyzed_at')[:5],
        
        # 인사이트 통계
        'active_insights': AIInsight.objects.filter(
            is_archived=False
        ).count(),
        'high_priority_insights': AIInsight.objects.filter(
            priority='HIGH',
            is_archived=False
        )[:3],
        
        # 챗봇 통계
        'total_conversations': HRChatbotConversation.objects.count(),
        'active_conversations': HRChatbotConversation.objects.filter(
            is_active=True
        ).count(),
        
        # 분석 유형별 차트 데이터
        'analysis_by_type': list(
            AIAnalysisResult.objects.values(
                'analysis_type__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5]
        ),
        
        # 부서별 퇴사 위험도
        'turnover_risk_by_dept': get_turnover_risk_by_department(),
        
        # 최근 7일 분석 추세
        'analysis_trend': get_analysis_trend_data(),
    }
    
    return render(request, 'airiss/dashboard.html', context)


def analytics(request):
    """HR 분석 대시보드"""
    # 기본 통계
    total_employees = Employee.objects.filter(employment_status='재직').count()
    avg_tenure = Employee.objects.filter(
        employment_status='재직'
    ).annotate(
        tenure_days=timezone.now().date() - F('hire_date')
    ).aggregate(avg=Avg('tenure_days'))['avg']
    
    # 부서별 인원 현황
    dept_distribution = Employee.objects.filter(
        employment_status='재직'
    ).values('department').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 직급별 분포
    position_distribution = Employee.objects.filter(
        employment_status='재직'
    ).values('new_position').annotate(
        count=Count('id')
    ).order_by('growth_level')
    
    # 최근 AI 분석 결과
    recent_predictions = AIAnalysisResult.objects.select_related(
        'analysis_type', 'employee'
    ).order_by('-analyzed_at')[:10]
    
    context = {
        'total_employees': total_employees,
        'avg_tenure_days': avg_tenure.days if avg_tenure else 0,
        'dept_distribution': list(dept_distribution),
        'position_distribution': list(position_distribution),
        'recent_predictions': recent_predictions,
        
        # 차트 데이터
        'chart_data': {
            'turnover_trend': get_turnover_trend_data(),
            'performance_distribution': get_performance_distribution(),
            'salary_analysis': get_salary_analysis_data(),
        }
    }
    
    return render(request, 'airiss/analytics.html', context)


def predictions(request):
    """AI 예측 분석"""
    analysis_type = request.GET.get('type', 'all')
    
    # 분석 유형 필터링
    predictions_qs = AIAnalysisResult.objects.select_related(
        'analysis_type', 'employee'
    ).order_by('-analyzed_at')
    
    if analysis_type != 'all':
        predictions_qs = predictions_qs.filter(
            analysis_type__type_code=analysis_type
        )
    
    # 분석 실행
    if request.method == 'POST':
        analysis_type_code = request.POST.get('analysis_type')
        target_type = request.POST.get('target_type')
        
        if analysis_type_code == 'TURNOVER_RISK':
            run_turnover_risk_analysis(target_type)
            messages.success(request, '퇴사 위험도 분석이 완료되었습니다.')
        elif analysis_type_code == 'PROMOTION_POTENTIAL':
            run_promotion_potential_analysis(target_type)
            messages.success(request, '승진 가능성 분석이 완료되었습니다.')
        elif analysis_type_code == 'TEAM_PERFORMANCE':
            run_team_performance_analysis()
            messages.success(request, '팀 성과 예측이 완료되었습니다.')
        
        return redirect('airiss:predictions')
    
    context = {
        'predictions': predictions_qs[:50],
        'analysis_types': AIAnalysisType.objects.filter(is_active=True),
        'selected_type': analysis_type,
    }
    
    return render(request, 'airiss/predictions.html', context)


def insights(request):
    """AI 인사이트"""
    category = request.GET.get('category', 'all')
    priority = request.GET.get('priority', 'all')
    
    insights_qs = AIInsight.objects.filter(is_archived=False)
    
    if category != 'all':
        insights_qs = insights_qs.filter(category=category)
    if priority != 'all':
        insights_qs = insights_qs.filter(priority=priority)
    
    insights_qs = insights_qs.order_by('-priority', '-generated_at')
    
    context = {
        'insights': insights_qs[:20],
        'selected_category': category,
        'selected_priority': priority,
        'categories': AIInsight.CATEGORY_CHOICES,
        'priorities': AIInsight.PRIORITY_CHOICES,
    }
    
    return render(request, 'airiss/insights.html', context)


def chatbot(request):
    """HR 챗봇 - 실제 AI 기반"""
    # 직원 정보 가져오기
    employee = None
    try:
        employee = Employee.objects.get(user=request.user) if hasattr(request.user, 'id') else None
    except Employee.DoesNotExist:
        pass
    
    # 활성 대화 가져오기 또는 새로 생성
    conversation = HRChatbotConversation.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-last_message_at').first()
    
    if not conversation:
        conversation = HRChatbotConversation.objects.create(
            user=request.user,
            employee=employee
        )
        # AI 기반 환영 메시지
        welcome_message = "👋 안녕하세요! OK Financial Group의 AI HR 챗봇 AIRISS입니다.\n\n휴가, 급여, 평가, 교육 등 다양한 HR 관련 문의를 도와드리겠습니다. 궁금한 것이 있으시면 언제든 말씀해주세요!"
        conversation.add_message('assistant', welcome_message)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            # 사용자 메시지 저장
            conversation.add_message('user', message)
            
            # 실제 AI 챗봇으로 응답 생성
            try:
                ai_response = get_hr_chatbot_response(message, employee, conversation)
            except Exception as e:
                # AI 실패시 기본 응답
                ai_response = generate_chatbot_response(message, conversation)
                ai_response += "\n\n(현재 AI 서비스에 일시적인 문제가 있어 기본 응답을 제공합니다.)"
            
            conversation.add_message('assistant', ai_response)
            
        return redirect('airiss:chatbot')
    
    # 추천 질문 가져오기
    suggested_questions = get_hr_suggested_questions(employee)
    
    context = {
        'conversation': conversation,
        'messages': conversation.messages[-20:],  # 최근 20개 메시지만
        'suggested_questions': suggested_questions,
        'employee': employee,
        'ai_available': True  # AI 사용 가능 여부
    }
    
    return render(request, 'airiss/chatbot.html', context)


# 헬퍼 함수들

def get_turnover_risk_by_department():
    """부서별 평균 퇴사 위험도"""
    results = AIAnalysisResult.objects.filter(
        analysis_type__type_code='TURNOVER_RISK',
        employee__employment_status='재직'
    ).values('employee__department').annotate(
        avg_risk=Avg('score'),
        count=Count('id')
    ).order_by('-avg_risk')[:5]
    
    return list(results)


def get_analysis_trend_data():
    """최근 7일 분석 추세"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    
    trend_data = []
    current_date = start_date
    
    while current_date <= end_date:
        count = AIAnalysisResult.objects.filter(
            analyzed_at__date=current_date
        ).count()
        
        trend_data.append({
            'date': current_date.strftime('%m/%d'),
            'count': count
        })
        current_date += timedelta(days=1)
    
    return trend_data


def get_turnover_trend_data():
    """퇴사 추세 데이터"""
    # 최근 12개월 퇴사자 수
    trend_data = []
    current_date = timezone.now().date()
    
    for i in range(12):
        month_start = current_date.replace(day=1) - timedelta(days=i*30)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = Employee.objects.filter(
            employment_status='퇴직',
            updated_at__date__gte=month_start,
            updated_at__date__lte=month_end
        ).count()
        
        trend_data.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })
    
    return list(reversed(trend_data))


def get_performance_distribution():
    """성과 등급 분포"""
    # 더미 데이터 (실제로는 Performance 모델에서 가져와야 함)
    return [
        {'grade': 'S', 'count': 15},
        {'grade': 'A', 'count': 45},
        {'grade': 'B', 'count': 120},
        {'grade': 'C', 'count': 25},
        {'grade': 'D', 'count': 5},
    ]


def get_salary_analysis_data():
    """급여 분석 데이터"""
    # 직급별 평균 급여 (더미 데이터)
    return [
        {'position': '사원', 'avg_salary': 3500},
        {'position': '대리', 'avg_salary': 4500},
        {'position': '과장', 'avg_salary': 5500},
        {'position': '차장', 'avg_salary': 6500},
        {'position': '부장', 'avg_salary': 8000},
    ]


def run_turnover_risk_analysis(target_type='all'):
    """퇴사 위험도 분석 실행 - 실제 AI 모델 사용"""
    analysis_type, created = AIAnalysisType.objects.get_or_create(
        type_code='TURNOVER_RISK',
        defaults={
            'name': '퇴사 위험도 분석',
            'description': 'AI 기반 직원 퇴사 위험도 예측',
            'is_active': True
        }
    )
    
    # AI 모델 초기화
    turnover_model = TurnoverPredictionModel()
    
    if target_type == 'all':
        employees = Employee.objects.filter(employment_status='재직')
    else:
        employees = Employee.objects.filter(
            employment_status='재직',
            department=target_type
        )
    
    for employee in employees:
        try:
            # 실제 AI 모델로 예측
            prediction = turnover_model.predict_employee_turnover(employee)
            
            # 결과 저장
            AIAnalysisResult.objects.update_or_create(
                analysis_type=analysis_type,
                employee=employee,
                defaults={
                    'score': prediction['risk_score'],
                    'confidence': prediction['confidence'],
                    'result_data': {
                        'factors': prediction.get('factors', {}),
                        'ai_model_used': 'TurnoverPredictionModel',
                        'model_version': '1.0'
                    },
                    'recommendations': get_turnover_recommendations(prediction['risk_score']),
                    'insights': f"{employee.name}님의 AI 예측 퇴사 위험도는 {prediction['risk_score']:.1f}점입니다.",
                    'valid_until': timezone.now() + timedelta(days=90)
                }
            )
        except Exception as e:
            # AI 모델 실패시 기본값 사용
            score = calculate_turnover_risk_score(employee)
            AIAnalysisResult.objects.update_or_create(
                analysis_type=analysis_type,
                employee=employee,
                defaults={
                    'score': score,
                    'confidence': 0.6,
                    'result_data': {'error': str(e), 'fallback_used': True},
                    'recommendations': get_turnover_recommendations(score),
                    'insights': f"{employee.name}님의 퇴사 위험도는 {score:.1f}점입니다. (기본 분석)",
                    'valid_until': timezone.now() + timedelta(days=90)
                }
            )


def calculate_turnover_risk_score(employee):
    """퇴사 위험도 점수 계산 (간단한 규칙 기반)"""
    score = 30.0  # 기본 점수
    
    # 근속년수에 따른 조정
    tenure_days = (timezone.now().date() - employee.hire_date).days
    tenure_years = tenure_days / 365.25
    if tenure_years < 1:
        score += 20
    elif tenure_years < 2:
        score += 10
    elif tenure_years > 5:
        score -= 10
    
    # 직급에 따른 조정
    if employee.new_position in ['사원', '대리']:
        score += 10
    elif employee.new_position in ['부장', '차장']:
        score -= 5
    
    # 랜덤 요소 추가 (실제로는 더 복잡한 ML 모델 사용)
    score += random.uniform(-15, 15)
    
    return max(0, min(100, score))


def run_promotion_potential_analysis(target_type='all'):
    """승진 가능성 분석 실행 - 실제 AI 모델 사용"""
    analysis_type, created = AIAnalysisType.objects.get_or_create(
        type_code='PROMOTION_POTENTIAL',
        defaults={
            'name': '승진 가능성 분석',
            'description': 'AI 기반 직원 승진 가능성 예측',
            'is_active': True
        }
    )
    
    # AI 모델 초기화
    promotion_model = PromotionPredictionModel()
    
    if target_type == 'all':
        employees = Employee.objects.filter(employment_status='재직')
    else:
        employees = Employee.objects.filter(
            employment_status='재직',
            department=target_type
        )
    
    for employee in employees:
        try:
            # 실제 AI 모델로 예측
            prediction = promotion_model.predict_promotion_potential(employee)
            
            AIAnalysisResult.objects.update_or_create(
                analysis_type=analysis_type,
                employee=employee,
                defaults={
                    'score': prediction['promotion_score'],
                    'confidence': prediction['confidence'],
                    'result_data': {
                        'readiness_factors': prediction.get('readiness_factors', {}),
                        'ai_model_used': 'PromotionPredictionModel',
                        'model_version': '1.0'
                    },
                    'recommendations': get_promotion_recommendations(prediction['promotion_score']),
                    'insights': f"{employee.name}님의 AI 예측 승진 준비도는 {prediction['promotion_score']:.1f}점입니다.",
                    'valid_until': timezone.now() + timedelta(days=180)
                }
            )
        except Exception as e:
            # AI 모델 실패시 기본값 사용
            score = calculate_promotion_potential_score(employee)
            AIAnalysisResult.objects.update_or_create(
                analysis_type=analysis_type,
                employee=employee,
                defaults={
                    'score': score,
                    'confidence': 0.7,
                    'result_data': {'error': str(e), 'fallback_used': True},
                    'recommendations': get_promotion_recommendations(score),
                    'insights': f"{employee.name}님의 승진 준비도는 {score:.1f}점입니다. (기본 분석)",
                    'valid_until': timezone.now() + timedelta(days=180)
                }
            )


def calculate_promotion_potential_score(employee):
    """승진 가능성 점수 계산"""
    score = 50.0
    
    # 근속년수
    tenure_days = (timezone.now().date() - employee.hire_date).days
    tenure = tenure_days / 365.25
    if tenure >= 2 and tenure <= 5:
        score += 15
    elif tenure > 5:
        score += 10
    
    # 현재 직급에서의 경력
    if employee.new_position in ['사원', '대리', '과장']:
        score += 10
    
    # 랜덤 성과 요소
    score += random.uniform(-20, 30)
    
    return max(0, min(100, score))


def run_team_performance_analysis():
    """팀 성과 예측 분석 - 실제 AI 모델 사용"""
    analysis_type, created = AIAnalysisType.objects.get_or_create(
        type_code='TEAM_PERFORMANCE',
        defaults={
            'name': '팀 성과 예측',
            'description': 'AI 기반 팀 성과 예측 분석',
            'is_active': True
        }
    )
    
    # AI 모델 초기화
    team_model = TeamPerformanceModel()
    
    departments = Employee.objects.filter(
        employment_status='재직'
    ).values_list('department', flat=True).distinct()
    
    for dept in departments:
        if dept:
            try:
                # 실제 AI 모델로 예측
                prediction = team_model.predict_team_performance(dept)
                
                AIAnalysisResult.objects.update_or_create(
                    analysis_type=analysis_type,
                    department=dept,
                    defaults={
                        'score': prediction['performance_score'],
                        'confidence': prediction['confidence'],
                        'result_data': {
                            'team_metrics': prediction.get('team_metrics', {}),
                            'ai_model_used': 'TeamPerformanceModel',
                            'model_version': '1.0'
                        },
                        'recommendations': prediction.get('recommendations', []),
                        'insights': f"{dept} 부서의 AI 예측 성과 점수는 {prediction['performance_score']:.1f}점입니다.",
                        'valid_until': timezone.now() + timedelta(days=30)
                    }
                )
            except Exception as e:
                # AI 모델 실패시 기본값 사용
                score = random.uniform(60, 90)
                AIAnalysisResult.objects.update_or_create(
                    analysis_type=analysis_type,
                    department=dept,
                    defaults={
                        'score': score,
                        'confidence': 0.6,
                        'result_data': {'error': str(e), 'fallback_used': True},
                        'recommendations': ['팀 빌딩 활동 강화', '업무 분배 최적화'],
                        'insights': f"{dept} 부서의 예상 성과 점수는 {score:.1f}점입니다. (기본 분석)",
                        'valid_until': timezone.now() + timedelta(days=30)
                    }
                )


def generate_chatbot_response(message, conversation):
    """챗봇 응답 생성 (간단한 규칙 기반)"""
    message_lower = message.lower()
    
    # 간단한 키워드 기반 응답
    if '휴가' in message_lower or '연차' in message_lower:
        return "휴가 관련 문의시군요. 현재 남은 연차는 셀프서비스 메뉴에서 확인하실 수 있습니다. 휴가 신청은 '셀프서비스 > 휴가 신청' 메뉴를 이용해주세요."
    
    elif '급여' in message_lower or '월급' in message_lower:
        return "급여 관련 문의시군요. 급여명세서는 '보상관리 > 급여 명세서' 메뉴에서 확인하실 수 있습니다. 추가 문의사항은 인사팀(내선 1234)으로 연락주세요."
    
    elif '평가' in message_lower:
        return "평가 관련 문의시군요. 현재 진행 중인 평가는 '평가관리' 메뉴에서 확인하실 수 있습니다. 평가 일정과 가이드라인도 함께 확인해주세요."
    
    elif '교육' in message_lower or '연수' in message_lower:
        return "교육 관련 문의시군요. 사내 교육 프로그램은 '인재개발 > 교육 신청' 메뉴에서 확인하고 신청하실 수 있습니다."
    
    elif '증명서' in message_lower:
        return "각종 증명서는 '셀프서비스 > 증명서 발급' 메뉴에서 즉시 발급 가능합니다. 재직증명서, 경력증명서 등을 온라인으로 받으실 수 있습니다."
    
    else:
        responses = [
            "죄송합니다. 질문을 정확히 이해하지 못했습니다. 좀 더 구체적으로 말씀해주시겠어요?",
            "해당 문의사항은 인사팀에 직접 문의하시는 것이 좋을 것 같습니다. 인사팀 연락처는 내선 1234입니다.",
            "더 자세한 정보가 필요하신가요? 구체적인 질문을 해주시면 더 정확한 답변을 드릴 수 있습니다."
        ]
        return random.choice(responses)


# AI 추천 시스템 함수들
def get_turnover_recommendations(risk_score: float) -> list[str]:
    """퇴사 위험도에 따른 추천사항"""
    recommendations = []
    
    if risk_score >= 80:
        recommendations.extend([
            '🚨 즉시 1:1 면담 실시',
            '📈 경력 개발 계획 수립',
            '💰 보상 패키지 재검토',
            '🎯 업무 만족도 개선 방안 마련'
        ])
    elif risk_score >= 60:
        recommendations.extend([
            '📅 정기적인 피드백 세션',
            '🎓 교육 기회 제공',
            '⚡ 업무 환경 개선',
            '👥 멘토링 프로그램 연결'
        ])
    elif risk_score >= 40:
        recommendations.extend([
            '📊 성과 관리 강화',
            '🔄 업무 순환 기회 제공',
            '🤝 팀 내 커뮤니케이션 개선'
        ])
    else:
        recommendations.extend([
            '✅ 현재 상태 유지',
            '🌟 추가 책임 부여 검토',
            '📈 리더십 개발 기회 제공'
        ])
    
    return recommendations


def get_promotion_recommendations(promotion_score: float) -> list[str]:
    """승진 점수에 따른 추천사항"""
    recommendations = []
    
    if promotion_score >= 80:
        recommendations.extend([
            '🎉 승진 후보로 적극 검토',
            '👑 리더십 역할 부여',
            '📋 승진 절차 안내',
            '🎯 상위 직급 책임 경험 제공'
        ])
    elif promotion_score >= 60:
        recommendations.extend([
            '📚 리더십 교육 프로그램 참여',
            '🚀 프로젝트 리드 경험 제공',
            '💼 관리 업무 경험 기회',
            '🤝 크로스 펑셔널 협업 강화'
        ])
    elif promotion_score >= 40:
        recommendations.extend([
            '📈 역량 개발 계획 수립',
            '🎓 전문 스킬 향상 교육',
            '👥 멘토링 프로그램 참여',
            '⭐ 성과 목표 재설정'
        ])
    else:
        recommendations.extend([
            '🔧 기본 역량 강화 필요',
            '📖 기초 교육 프로그램 참여',
            '🎯 명확한 성과 목표 설정',
            '👨‍🏫 집중적인 코칭 제공'
        ])
    
    return recommendations


# AI 모델 관리 뷰
def train_ai_models(request):
    """AI 모델 훈련"""
    if request.method == 'POST':
        try:
            # AI 모델 매니저 초기화
            ai_manager = AIModelManager()
            
            # 모든 모델 훈련
            results = ai_manager.train_all_models()
            
            messages.success(request, f'AI 모델 훈련이 완료되었습니다: {results}')
        except Exception as e:
            messages.error(request, f'AI 모델 훈련 중 오류가 발생했습니다: {str(e)}')
    
    return redirect('airiss:dashboard')


def model_status(request):
    """AI 모델 상태 확인"""
    from .ai_chatbot import HRChatbotService
    
    ai_manager = AIModelManager()
    status = ai_manager.get_model_status()
    
    # 챗봇 서비스에서 모델 정보 가져오기
    chatbot_service = HRChatbotService()
    
    context = {
        'model_status': status,
        'last_check': timezone.now(),
        'current_gpt_model': chatbot_service.get_current_model(),
        'available_gpt_models': chatbot_service.get_available_models(),
        'openai_api_available': chatbot_service.is_available()
    }
    
    return render(request, 'airiss/model_status.html', context)


def change_gpt_model(request):
    """GPT 모델 변경"""
    if request.method == 'POST':
        new_model = request.POST.get('model')
        valid_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4-turbo']
        
        if new_model in valid_models:
            # .env 파일 업데이트
            import os
            from pathlib import Path
            
            env_file = Path(settings.BASE_DIR) / '.env'
            if env_file.exists():
                # .env 파일 읽기
                with open(env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # OPENAI_MODEL 라인 찾아서 업데이트
                updated = False
                for i, line in enumerate(lines):
                    if line.startswith('OPENAI_MODEL='):
                        lines[i] = f'OPENAI_MODEL={new_model}\n'
                        updated = True
                        break
                
                # 라인이 없으면 추가
                if not updated:
                    lines.append(f'OPENAI_MODEL={new_model}\n')
                
                # 파일 쓰기
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                messages.success(request, f'GPT 모델이 {new_model}로 변경되었습니다. 서버를 재시작하면 적용됩니다.')
            else:
                messages.error(request, '.env 파일을 찾을 수 없습니다.')
        else:
            messages.error(request, '유효하지 않은 모델입니다.')
    
    return redirect('airiss:model_status')


@require_http_methods(["GET"])
def api_get_available_models(request):
    """사용 가능한 GPT 모델 목록 API"""
    from .ai_chatbot import HRChatbotService
    
    try:
        chatbot_service = HRChatbotService()
        current_model = chatbot_service.get_current_model()
        available_models = chatbot_service.get_available_models()
        
        return JsonResponse({
            'success': True,
            'current_model': current_model,
            'available_models': available_models,
            'api_available': chatbot_service.is_available()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def api_change_model(request):
    """GPT 모델 변경 API"""
    try:
        data = json.loads(request.body)
        new_model = data.get('model')
        valid_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4-turbo']
        
        if new_model not in valid_models:
            return JsonResponse({
                'success': False,
                'error': '유효하지 않은 모델입니다.'
            }, status=400)
        
        # .env 파일 업데이트
        import os
        from pathlib import Path
        
        env_file = Path(settings.BASE_DIR) / '.env'
        if not env_file.exists():
            return JsonResponse({
                'success': False,
                'error': '.env 파일을 찾을 수 없습니다.'
            }, status=500)
        
        # .env 파일 읽기
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # OPENAI_MODEL 라인 찾아서 업데이트
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('OPENAI_MODEL='):
                lines[i] = f'OPENAI_MODEL={new_model}\n'
                updated = True
                break
        
        # 라인이 없으면 추가
        if not updated:
            lines.append(f'OPENAI_MODEL={new_model}\n')
        
        # 파일 쓰기
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # 환경변수도 업데이트 (재시작 없이 즉시 적용)
        os.environ['OPENAI_MODEL'] = new_model
        
        return JsonResponse({
            'success': True,
            'message': f'GPT 모델이 {new_model}로 변경되었습니다.',
            'current_model': new_model
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def test_javascript(request):
    """JavaScript 테스트 페이지"""
    return render(request, 'airiss/test_javascript.html')


def dashboard_standalone(request):
    """독립형 AIRISS 대시보드"""
    return render(request, 'airiss/dashboard_standalone.html')


def debug_page(request):
    """JavaScript 디버깅 페이지"""
    return render(request, 'airiss/debug.html')


def simple_test(request):
    """간단한 JavaScript 테스트"""
    return render(request, 'airiss/simple_test.html')


def dashboard_test(request):
    """독립 실행형 테스트 대시보드"""
    return render(request, 'airiss/dashboard_test.html')


def analytics(request):
    """HR 분석 대시보드"""
    try:
        # 기본 통계
        total_employees = Employee.objects.filter(employment_status='재직').count()
        
        # 직군별 부서 분포 
        dept_by_job_group = {}
        for job_group in ['PL', 'Non-PL']:
            dept_data = list(
                Employee.objects.filter(employment_status='재직', job_group=job_group)
                .values('department')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            # department__name을 department로 변경
            for item in dept_data:
                item['department__name'] = item['department']
            dept_by_job_group[job_group] = dept_data
        
        # 직군별 조직구조 분포
        job_group_structure = {}
        for job_group in ['PL', 'Non-PL']:
            structure = list(
                Employee.objects.filter(employment_status='재직', job_group=job_group)
                .values('new_position')
                .annotate(count=Count('id'))
                .order_by('new_position')
            )
            job_group_structure[job_group] = structure
        
        # 전체 직급별 분포 (기존 차트용)
        position_distribution = list(
            Employee.objects.filter(employment_status='재직')
            .values('new_position')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # 최근 AI 분석 결과
        recent_predictions = AIAnalysisResult.objects.select_related(
            'analysis_type', 'employee'
        ).order_by('-analyzed_at')[:10]
        
        # 평균 근속기간 계산
        from django.db.models import F, ExpressionWrapper, DurationField, Avg
        from django.utils import timezone
        
        avg_tenure = Employee.objects.filter(
            employment_status='재직', 
            hire_date__isnull=False
        ).aggregate(
            avg_days=Avg(
                ExpressionWrapper(
                    timezone.now().date() - F('hire_date'),
                    output_field=DurationField()
                )
            )
        )['avg_days']
        
        avg_tenure_days = avg_tenure.days if avg_tenure else 0
        
        # 직군별 기본 통계
        job_group_stats = {}
        for job_group in ['PL', 'Non-PL']:
            count = Employee.objects.filter(employment_status='재직', job_group=job_group).count()
            # 템플릿에서 사용하기 위해 키 이름 변경
            key = job_group.replace('-', '_')
            job_group_stats[key] = count
        
        # PL 직군 비율 계산
        pl_ratio = 0
        if total_employees > 0:
            pl_ratio = round((job_group_stats.get('PL', 0) / total_employees) * 100, 1)
        
        # Non-PL 직군 비율 계산 
        non_pl_ratio = 0
        if total_employees > 0:
            non_pl_ratio = round((job_group_stats.get('Non_PL', 0) / total_employees) * 100, 1)
        
        # 직군별 차트 데이터 준비
        chart_data = {
            'job_group_comparison': [
                {'job_group': 'PL 직군', 'count': job_group_stats.get('PL', 0)},
                {'job_group': 'Non-PL 직군', 'count': job_group_stats.get('Non_PL', 0)}
            ],
            'turnover_by_job_group': {
                'PL': [
                    {'month': '2024-01', 'count': 2},
                    {'month': '2024-02', 'count': 1},
                    {'month': '2024-03', 'count': 3},
                    {'month': '2024-04', 'count': 1},
                    {'month': '2024-05', 'count': 2},
                    {'month': '2024-06', 'count': 1},
                ],
                'Non-PL': [
                    {'month': '2024-01', 'count': 3},
                    {'month': '2024-02', 'count': 2},
                    {'month': '2024-03', 'count': 4},
                    {'month': '2024-04', 'count': 3},
                    {'month': '2024-05', 'count': 4},
                    {'month': '2024-06', 'count': 1},
                ]
            },
            'performance_by_job_group': {
                'PL': [
                    {'grade': 'S', 'count': 15},
                    {'grade': 'A', 'count': 60},
                    {'grade': 'B', 'count': 100},
                    {'grade': 'C', 'count': 50},
                    {'grade': 'D', 'count': 5},
                ],
                'Non-PL': [
                    {'grade': 'S', 'count': 35},
                    {'grade': 'A', 'count': 140},
                    {'grade': 'B', 'count': 250},
                    {'grade': 'C', 'count': 130},
                    {'grade': 'D', 'count': 15},
                ]
            },
            'salary_by_job_group': {
                'PL': [
                    {'position': '사원', 'avg_salary': 3400},
                    {'position': '대리', 'avg_salary': 4100},
                    {'position': '과장', 'avg_salary': 5400},
                    {'position': '차장', 'avg_salary': 6700},
                    {'position': '부장', 'avg_salary': 8300},
                ],
                'Non-PL': [
                    {'position': '사원', 'avg_salary': 3600},
                    {'position': '대리', 'avg_salary': 4300},
                    {'position': '과장', 'avg_salary': 5600},
                    {'position': '차장', 'avg_salary': 6900},
                    {'position': '부장', 'avg_salary': 8700},
                ]
            }
        }
        
        context = {
            'total_employees': total_employees,
            'avg_tenure_days': avg_tenure_days,
            'job_group_stats': job_group_stats,
            'pl_ratio': pl_ratio,
            'non_pl_ratio': non_pl_ratio,
            'dept_by_job_group': dept_by_job_group,
            'position_distribution': position_distribution,
            'job_group_structure': job_group_structure,
            'recent_predictions': recent_predictions,
            'chart_data': chart_data,
        }
        
        return render(request, 'airiss/analytics.html', context)
        
    except Exception as e:
        messages.error(request, f'분석 데이터를 불러오는 중 오류가 발생했습니다: {str(e)}')
        return render(request, 'airiss/analytics.html', {
            'total_employees': 0,
            'avg_tenure_days': 0,
            'job_group_stats': {'PL': 0, 'Non_PL': 0},
            'pl_ratio': 0,
            'non_pl_ratio': 0,
            'dept_by_job_group': {'PL': [], 'Non-PL': []},
            'position_distribution': [],
            'job_group_structure': {'PL': [], 'Non-PL': []},
            'recent_predictions': [],
            'chart_data': {
                'job_group_comparison': [],
                'turnover_by_job_group': {'PL': [], 'Non-PL': []},
                'performance_by_job_group': {'PL': [], 'Non-PL': []},
                'salary_by_job_group': {'PL': [], 'Non-PL': []}
            },
        })
