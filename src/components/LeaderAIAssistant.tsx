import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  Brain,
  TrendingUp,
  Users,
  Target,
  AlertCircle,
  CheckCircle,
  Lightbulb,
  FileText,
  Download,
  RefreshCw,
  Sparkles
} from 'lucide-react';

interface InsightCard {
  id: string;
  title: string;
  category: 'performance' | 'talent' | 'risk' | 'opportunity';
  priority: 'high' | 'medium' | 'low';
  description: string;
  recommendation: string;
  metrics?: {
    label: string;
    value: string;
    trend?: 'up' | 'down' | 'stable';
  }[];
}

const LeaderAIAssistant: React.FC = () => {
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [selectedPeriod, setSelectedPeriod] = useState('current');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // 더미 인사이트 데이터
  const insights: InsightCard[] = [
    {
      id: '1',
      title: '핵심 인재 이탈 위험 감지',
      category: 'risk',
      priority: 'high',
      description: 'IT개발팀의 선임급 개발자 3명이 최근 3개월간 성과 하락 및 참여도 감소를 보이고 있습니다.',
      recommendation: '1:1 면담을 통한 동기부여 요인 파악 및 경력 개발 계획 수립을 권장합니다.',
      metrics: [
        { label: '위험도', value: '78%', trend: 'up' },
        { label: '영향 범위', value: '3명', trend: 'stable' },
      ],
    },
    {
      id: '2',
      title: '팀 성과 개선 기회',
      category: 'opportunity',
      priority: 'medium',
      description: '마케팅팀의 협업 지수가 전사 평균 대비 15% 높으며, 프로젝트 완료율이 지속적으로 상승하고 있습니다.',
      recommendation: '우수 사례를 전사에 공유하고, 팀 리더에게 인센티브 제공을 고려하세요.',
      metrics: [
        { label: '협업 지수', value: '85점', trend: 'up' },
        { label: '프로젝트 완료율', value: '92%', trend: 'up' },
      ],
    },
    {
      id: '3',
      title: '승진 후보자 분석 완료',
      category: 'talent',
      priority: 'medium',
      description: '2024년 하반기 승진 심사 대상자 중 5명이 뛰어난 리더십과 성과를 보여주고 있습니다.',
      recommendation: '해당 인원들에 대한 멘토링 프로그램 배정 및 리더십 교육을 준비하세요.',
      metrics: [
        { label: '적합도', value: '88%', trend: 'stable' },
        { label: '준비도', value: '75%', trend: 'up' },
      ],
    },
    {
      id: '4',
      title: '부서별 성과 격차 확대',
      category: 'performance',
      priority: 'high',
      description: '영업팀과 기획팀 간의 목표 달성률 격차가 30% 이상으로 벌어지고 있습니다.',
      recommendation: '저성과 부서에 대한 원인 분석 및 맞춤형 개선 계획 수립이 필요합니다.',
      metrics: [
        { label: '격차', value: '32%', trend: 'up' },
        { label: '영향 인원', value: '45명', trend: 'stable' },
      ],
    },
  ];

  const getCategoryIcon = (category: InsightCard['category']) => {
    switch (category) {
      case 'performance':
        return <TrendingUp className="w-5 h-5" />;
      case 'talent':
        return <Users className="w-5 h-5" />;
      case 'risk':
        return <AlertCircle className="w-5 h-5" />;
      case 'opportunity':
        return <Lightbulb className="w-5 h-5" />;
    }
  };

  const getCategoryColor = (category: InsightCard['category']) => {
    switch (category) {
      case 'performance':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20';
      case 'talent':
        return 'text-purple-600 bg-purple-100 dark:bg-purple-900/20';
      case 'risk':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      case 'opportunity':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
    }
  };

  const getPriorityBadge = (priority: InsightCard['priority']) => {
    const colors = {
      high: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
      medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      low: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    };

    const labels = {
      high: '높음',
      medium: '보통',
      low: '낮음',
    };

    return (
      <span className={`px-2 py-1 text-xs rounded-full font-medium ${colors[priority]}`}>
        {labels[priority]}
      </span>
    );
  };

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 2000);
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          리더 AI 어시스턴트
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          AI 기반 인사 인사이트와 의사결정 지원
        </p>
      </div>

      {/* 필터 및 액션 */}
      <Card>
        <CardHeader>
          <CardTitle>인사이트 분석</CardTitle>
          <CardDescription>
            부서와 기간을 선택하여 맞춤형 인사이트를 확인하세요
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
              <SelectTrigger className="sm:w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 부서</SelectItem>
                <SelectItem value="it">IT개발팀</SelectItem>
                <SelectItem value="hr">인사팀</SelectItem>
                <SelectItem value="finance">재무팀</SelectItem>
                <SelectItem value="marketing">마케팅팀</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
              <SelectTrigger className="sm:w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="current">현재</SelectItem>
                <SelectItem value="month">최근 1개월</SelectItem>
                <SelectItem value="quarter">최근 분기</SelectItem>
                <SelectItem value="year">최근 1년</SelectItem>
              </SelectContent>
            </Select>
            
            <div className="flex gap-2 ml-auto">
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                리포트 다운로드
              </Button>
              <Button onClick={handleAnalyze} disabled={isAnalyzing}>
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    분석 중...
                  </>
                ) : (
                  <>
                    <Brain className="w-4 h-4 mr-2" />
                    AI 분석 실행
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI 인사이트 카드 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {insights.map((insight) => (
          <Card key={insight.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getCategoryColor(insight.category)}`}>
                    {getCategoryIcon(insight.category)}
                  </div>
                  <div>
                    <CardTitle className="text-lg">{insight.title}</CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      {getPriorityBadge(insight.priority)}
                      <span className="text-sm text-gray-500">우선순위</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {insight.description}
              </p>
              
              {insight.metrics && (
                <div className="flex gap-4">
                  {insight.metrics.map((metric, index) => (
                    <div key={index} className="flex-1 bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                      <p className="text-xs text-gray-500 dark:text-gray-400">{metric.label}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-lg font-semibold">{metric.value}</span>
                        {metric.trend && (
                          <span className={`text-xs ${
                            metric.trend === 'up' ? 'text-red-600' : 
                            metric.trend === 'down' ? 'text-green-600' : 
                            'text-gray-500'
                          }`}>
                            {metric.trend === 'up' ? '↑' : 
                             metric.trend === 'down' ? '↓' : '→'}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <div className="border-t pt-4">
                <div className="flex items-start gap-2">
                  <Sparkles className="w-4 h-4 text-primary mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">AI 추천</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {insight.recommendation}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 실행 가능한 액션 */}
      <Card>
        <CardHeader>
          <CardTitle>즉시 실행 가능한 액션</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium">고위험 이탈 직원 3명과 1:1 면담 일정 잡기</span>
              </div>
              <Button size="sm">실행</Button>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium">마케팅팀 우수 사례 전사 공유회 개최</span>
              </div>
              <Button size="sm">실행</Button>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium">저성과 부서 개선 TF 구성</span>
              </div>
              <Button size="sm">실행</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LeaderAIAssistant;