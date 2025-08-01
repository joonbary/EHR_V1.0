import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { 
  Send, 
  Bot, 
  User, 
  Loader2,
  Sparkles,
  HelpCircle,
  FileText,
  Users,
  TrendingUp,
  DollarSign
} from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
}

interface SuggestedQuestion {
  icon: React.ElementType;
  question: string;
  category: string;
}

const AIChatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: '안녕하세요! OK금융그룹 AI 어시스턴트입니다. 인사 관련 궁금한 점을 물어보세요.',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions: SuggestedQuestion[] = [
    {
      icon: Users,
      question: '우리 부서의 현재 인원 현황은?',
      category: '인원 관리',
    },
    {
      icon: TrendingUp,
      question: '올해 승진 대상자 명단을 보여줘',
      category: '승진 관리',
    },
    {
      icon: FileText,
      question: '직무기술서 작성 가이드라인이 있나요?',
      category: '문서 관리',
    },
    {
      icon: DollarSign,
      question: '부서별 평균 보상 수준은?',
      category: '보상 관리',
    },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const simulateBotResponse = (userMessage: string) => {
    // 간단한 응답 시뮬레이션
    const responses: { [key: string]: string } = {
      '인원': '현재 IT개발팀에는 총 80명의 직원이 근무하고 있습니다. 개발자 60명, QA 15명, 기타 5명으로 구성되어 있습니다.',
      '승진': '2024년 하반기 승진 대상자는 총 12명입니다. 부서별로는 IT개발팀 4명, 인사팀 3명, 재무팀 3명, 마케팅팀 2명입니다.',
      '직무기술서': '직무기술서 작성 시 다음 항목들을 포함해야 합니다:\n1. 직무 개요\n2. 주요 책임과 역할\n3. 필요 역량 및 자격요건\n4. 성과 지표\n\n템플릿은 인사팀 공유 폴더에서 다운로드할 수 있습니다.',
      '보상': '2024년 기준 부서별 평균 연봉은 다음과 같습니다:\n- IT개발팀: 6,500만원\n- 인사팀: 5,800만원\n- 재무팀: 6,200만원\n- 마케팅팀: 5,500만원',
    };

    // 키워드 매칭
    for (const [keyword, response] of Object.entries(responses)) {
      if (userMessage.includes(keyword)) {
        return response;
      }
    }

    return '해당 질문에 대한 정보를 찾고 있습니다. 더 구체적으로 질문해 주시거나, 인사팀에 직접 문의해 주세요.';
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // 봇 응답 시뮬레이션
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: simulateBotResponse(input),
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const handleSuggestedQuestion = (question: string) => {
    setInput(question);
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader className="border-b">
        <CardTitle className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-hover rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          AI 인사 어시스턴트
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        {/* 메시지 영역 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex gap-3 max-w-[70%] ${message.type === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.type === 'user' 
                    ? 'bg-primary text-white' 
                    : 'bg-gray-100 dark:bg-gray-700'
                }`}>
                  {message.type === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                <div className={`rounded-lg p-3 ${
                  message.type === 'user'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 dark:bg-gray-700'
                }`}>
                  <p className="text-sm whitespace-pre-line">{message.content}</p>
                  <p className={`text-xs mt-1 ${
                    message.type === 'user' ? 'text-primary-foreground/70' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString('ko-KR', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="flex gap-3 max-w-[70%]">
                <div className="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center gap-1">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">입력 중...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* 추천 질문 */}
        {messages.length === 1 && (
          <div className="p-4 border-t">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              추천 질문
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {suggestedQuestions.map((sq, index) => {
                const Icon = sq.icon;
                return (
                  <button
                    key={index}
                    onClick={() => handleSuggestedQuestion(sq.question)}
                    className="text-left p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <Icon className="w-5 h-5 text-primary mt-0.5" />
                      <div>
                        <p className="text-sm font-medium">{sq.category}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {sq.question}
                        </p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* 입력 영역 */}
        <div className="p-4 border-t">
          <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="메시지를 입력하세요..."
              disabled={isTyping}
              className="flex-1"
            />
            <Button type="submit" disabled={!input.trim() || isTyping}>
              <Send className="w-4 h-4" />
            </Button>
          </form>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 flex items-center gap-1">
            <HelpCircle className="w-3 h-3" />
            AI 어시스턴트는 일반적인 정보를 제공합니다. 중요한 결정은 담당자와 상의하세요.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default AIChatbot;