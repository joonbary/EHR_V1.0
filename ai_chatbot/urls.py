from django.urls import path
from .views import (
    AIChatbotView, ChatAPIView, ChatSessionListView, 
    ChatSessionDetailView, QuickActionAPIView,
    LeadershipAIView, LeadershipInsightAPIView
)

app_name = 'ai_chatbot'

urlpatterns = [
    # AI 챗봇
    path('', AIChatbotView.as_view(), name='chatbot'),
    path('api/chat/', ChatAPIView.as_view(), name='chat_api'),
    path('api/sessions/', ChatSessionListView.as_view(), name='session_list'),
    path('api/sessions/<uuid:session_id>/', ChatSessionDetailView.as_view(), name='session_detail'),
    path('api/quick-actions/', QuickActionAPIView.as_view(), name='quick_actions'),
    
    # 리더십 AI 파트너
    path('leadership/', LeadershipAIView.as_view(), name='leadership'),
    path('api/leadership/insight/', LeadershipInsightAPIView.as_view(), name='leadership_insight'),
]