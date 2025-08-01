import React, { useState } from 'react';
import MainLayout from '../layouts/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { DataTable } from '../components/ui/data-table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { 
  ClipboardCheck,
  Calendar,
  User,
  FileText,
  TrendingUp,
  Edit,
  Eye,
  Plus,
  Filter,
  Download,
  Award
} from 'lucide-react';

interface Evaluation {
  id: string;
  period: string;
  evaluator: string;
  evaluatee: string;
  department: string;
  status: 'pending' | 'in_progress' | 'completed' | 'approved';
  score?: number;
  dueDate: string;
  completedDate?: string;
}

const evaluations: Evaluation[] = [
  {
    id: '1',
    period: '2024년 상반기',
    evaluator: '김부장',
    evaluatee: '홍길동',
    department: 'IT개발팀',
    status: 'completed',
    score: 92,
    dueDate: '2024-06-30',
    completedDate: '2024-06-25',
  },
  {
    id: '2',
    period: '2024년 상반기',
    evaluator: '이부장',
    evaluatee: '김철수',
    department: '인사팀',
    status: 'in_progress',
    dueDate: '2024-06-30',
  },
  {
    id: '3',
    period: '2024년 상반기',
    evaluator: '박부장',
    evaluatee: '이영희',
    department: '재무팀',
    status: 'pending',
    dueDate: '2024-06-30',
  },
];

const columns = [
  {
    accessorKey: "period",
    header: "평가 기간",
  },
  {
    accessorKey: "evaluatee",
    header: "피평가자",
  },
  {
    accessorKey: "department",
    header: "부서",
  },
  {
    accessorKey: "status",
    header: "상태",
    cell: ({ row }: any) => {
      const status = row.getValue("status");
      const statusConfig = {
        pending: { label: '대기중', class: 'bg-gray-100 text-gray-800' },
        in_progress: { label: '진행중', class: 'bg-blue-100 text-blue-800' },
        completed: { label: '완료', class: 'bg-green-100 text-green-800' },
        approved: { label: '승인됨', class: 'bg-purple-100 text-purple-800' },
      };
      const config = statusConfig[status as keyof typeof statusConfig];
      return (
        <span className={`px-2 py-1 text-xs rounded-full ${config.class}`}>
          {config.label}
        </span>
      );
    },
  },
  {
    accessorKey: "score",
    header: "점수",
    cell: ({ row }: any) => {
      const score = row.getValue("score");
      return score ? (
        <span className="font-semibold">{score}점</span>
      ) : (
        <span className="text-gray-400">-</span>
      );
    },
  },
  {
    accessorKey: "dueDate",
    header: "마감일",
    cell: ({ row }: any) => {
      const date = row.getValue("dueDate");
      return new Date(date).toLocaleDateString('ko-KR');
    },
  },
  {
    id: "actions",
    cell: ({ row }: any) => {
      const evaluation = row.original;
      return (
        <div className="flex items-center gap-2">
          {evaluation.status === 'pending' || evaluation.status === 'in_progress' ? (
            <Button size="sm" variant="default">
              <Edit className="w-3 h-3 mr-1" />
              평가하기
            </Button>
          ) : (
            <Button size="sm" variant="outline">
              <Eye className="w-3 h-3 mr-1" />
              보기
            </Button>
          )}
        </div>
      );
    },
  },
];

const EvaluationPage: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('2024년 상반기');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewEvalDialog, setShowNewEvalDialog] = useState(false);

  // 평가 통계
  const stats = {
    total: evaluations.length,
    completed: evaluations.filter(e => e.status === 'completed' || e.status === 'approved').length,
    inProgress: evaluations.filter(e => e.status === 'in_progress').length,
    pending: evaluations.filter(e => e.status === 'pending').length,
    averageScore: Math.round(
      evaluations
        .filter(e => e.score)
        .reduce((sum, e) => sum + (e.score || 0), 0) / 
      evaluations.filter(e => e.score).length || 0
    ),
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            평가 관리
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            직원 평가를 조회하고 관리합니다
          </p>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-500">
                전체 평가
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-500">
                완료됨
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-500">
                진행중
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.inProgress}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-500">
                대기중
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-600">{stats.pending}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-500">
                평균 점수
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{stats.averageScore}점</div>
            </CardContent>
          </Card>
        </div>

        {/* 필터 및 액션 바 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger className="w-full sm:w-[180px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2024년 상반기">2024년 상반기</SelectItem>
                  <SelectItem value="2023년 하반기">2023년 하반기</SelectItem>
                  <SelectItem value="2023년 상반기">2023년 상반기</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger className="w-full sm:w-[140px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체 상태</SelectItem>
                  <SelectItem value="pending">대기중</SelectItem>
                  <SelectItem value="in_progress">진행중</SelectItem>
                  <SelectItem value="completed">완료</SelectItem>
                  <SelectItem value="approved">승인됨</SelectItem>
                </SelectContent>
              </Select>
              
              <Input
                placeholder="검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full sm:w-[200px]"
              />
            </div>
            
            <div className="flex gap-2">
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                내보내기
              </Button>
              <Dialog open={showNewEvalDialog} onOpenChange={setShowNewEvalDialog}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    새 평가 시작
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>새 평가 시작</DialogTitle>
                    <DialogDescription>
                      새로운 평가 기간을 설정하고 평가를 시작합니다.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div>
                      <label className="text-sm font-medium">평가 기간</label>
                      <Input placeholder="예: 2024년 하반기" className="mt-1" />
                    </div>
                    <div>
                      <label className="text-sm font-medium">평가 대상</label>
                      <Select>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="선택하세요" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">전체 직원</SelectItem>
                          <SelectItem value="department">특정 부서</SelectItem>
                          <SelectItem value="position">특정 직급</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <label className="text-sm font-medium">마감일</label>
                      <Input type="date" className="mt-1" />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setShowNewEvalDialog(false)}>
                      취소
                    </Button>
                    <Button onClick={() => setShowNewEvalDialog(false)}>
                      평가 시작
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>

        {/* 평가 목록 테이블 */}
        <Card>
          <CardHeader>
            <CardTitle>평가 목록</CardTitle>
            <CardDescription>
              진행 중인 평가와 완료된 평가를 확인할 수 있습니다
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable
              columns={columns}
              data={evaluations}
            />
          </CardContent>
        </Card>

        {/* 추가 정보 카드들 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* 평가 진행률 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                평가 진행률
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm">전체 진행률</span>
                    <span className="text-sm font-medium">
                      {Math.round((stats.completed / stats.total) * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full"
                      style={{ width: `${(stats.completed / stats.total) * 100}%` }}
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>IT개발팀</span>
                    <span className="font-medium">80%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>인사팀</span>
                    <span className="font-medium">65%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>재무팀</span>
                    <span className="font-medium">90%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 우수 평가자 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                우수 평가자
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center text-white font-bold">
                    1
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">홍길동</div>
                    <div className="text-sm text-gray-500">IT개발팀 · 92점</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-gray-400 to-gray-600 rounded-full flex items-center justify-center text-white font-bold">
                    2
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">김영희</div>
                    <div className="text-sm text-gray-500">마케팅팀 · 90점</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center text-white font-bold">
                    3
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">박철수</div>
                    <div className="text-sm text-gray-500">재무팀 · 88점</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default EvaluationPage;