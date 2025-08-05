"""
AI 기능 뷰 함수들
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random


@login_required
def ehr_chatbot(request):
    """AI HR 챗봇 인터페이스"""
    # 초기 환영 메시지
    welcome_messages = [
        {
            'type': 'bot',
            'message': '안녕하세요! OK금융그룹 HR AI 어시스턴트입니다. 무엇을 도와드릴까요?',
            'timestamp': 'now'
        }
    ]
    
    # 빠른 응답 제안
    suggestions = [
        '연차 잔여일수 확인',
        '급여명세서 조회',
        '교육 프로그램 안내',
        '복지 혜택 문의',
        'HR 정책 안내'
    ]
    
    context = {
        'title': 'AI HR Assistant',
        'initial_messages': welcome_messages,
        'suggestions': suggestions
    }
    
    return render(request, 'ai/chatbot.html', context)


@csrf_exempt
@login_required
def chat_api(request):
    """챗봇 API 엔드포인트"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # 간단한 응답 로직 (실제로는 AI 모델 연동)
            response = generate_simple_response(user_message)
            
            # 후속 제안 생성
            follow_up_suggestions = get_contextual_suggestions(user_message)
            
            return JsonResponse({
                'success': True,
                'response': response,
                'suggestions': follow_up_suggestions
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def leader_ai_assistant(request):
    """리더 AI 어시스턴트"""
    # 팀 현황 데이터 (실제로는 DB에서 조회)
    team_insights = [
        {
            'title': '팀 성과 지표',
            'insight': '이번 분기 팀 성과가 전분기 대비 15% 향상되었습니다.',
            'confidence': 0.92,
            'type': 'positive'
        },
        {
            'title': '인력 리스크',
            'insight': '핵심 인재 2명의 이직 가능성이 감지되었습니다.',
            'confidence': 0.78,
            'type': 'warning'
        },
        {
            'title': '교육 필요성',
            'insight': '팀원 중 3명이 신기술 교육이 필요한 것으로 분석됩니다.',
            'confidence': 0.85,
            'type': 'info'
        }
    ]
    
    context = {
        'title': '리더 AI 어시스턴트',
        'team_insights': team_insights
    }
    
    return render(request, 'ai/leader_assistant.html', context)


# 헬퍼 함수들
def generate_simple_response(message):
    """간단한 응답 생성 (실제로는 AI 모델 사용)"""
    message_lower = message.lower()
    
    if '연차' in message_lower:
        return '현재 남은 연차는 12일입니다. 연차 사용 신청은 ESS 시스템에서 가능합니다.'
    elif '급여' in message_lower:
        return '급여명세서는 매월 25일에 발행됩니다. ESS > 급여 메뉴에서 확인하실 수 있습니다.'
    elif '교육' in message_lower:
        return '현재 신청 가능한 교육 프로그램이 5개 있습니다. 자세한 내용은 교육 포털에서 확인해주세요.'
    elif '복지' in message_lower:
        return 'OK금융그룹은 다양한 복지 혜택을 제공합니다. 건강검진, 자녀학자금, 휴양시설 등이 있습니다.'
    else:
        responses = [
            '문의하신 내용을 확인하고 있습니다. 좀 더 구체적으로 말씀해 주시겠어요?',
            '해당 문의는 HR 담당자에게 전달하겠습니다. 추가로 궁금하신 점이 있으신가요?',
            '관련 정보를 찾고 있습니다. 다른 도움이 필요하신가요?'
        ]
        return random.choice(responses)


def get_contextual_suggestions(message):
    """문맥에 따른 추천 질문 생성"""
    message_lower = message.lower()
    
    if '연차' in message_lower:
        return ['연차 사용 신청하기', '공휴일 확인', '연차 사용 규정']
    elif '급여' in message_lower:
        return ['4대보험 공제내역', '연말정산 서류', '급여 이의신청']
    elif '교육' in message_lower:
        return ['필수 교육 확인', '교육 이수증 발급', '외부 교육 신청']
    else:
        return ['자주 묻는 질문', 'HR 담당자 연결', '다른 문의하기']