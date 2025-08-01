import React from 'react';
import MainLayout from '../layouts/MainLayout';
import { StatCard } from '../components/ui/card';
import { DataTable } from '../components/ui/data-table';
import { Button } from '../components/ui/button';
import { 
  Users, 
  Building2, 
  Briefcase, 
  FileText, 
  TrendingUp, 
  UserPlus,
  ArrowRight
} from 'lucide-react';

// 더미 데이터
const recentActivities = [
  { id: 1, activity: '김철수 직원 정보 수정', time: '10분 전', type: 'update' },
  { id: 2, activity: '2024년 상반기 평가 시작', time: '1시간 전', type: 'evaluation' },
  { id: 3, activity: '신규 직원 3명 등록', time: '3시간 전', type: 'new' },
  { id: 4, activity: '조직도 업데이트', time: '5시간 전', type: 'organization' },
  { id: 5, activity: '인사팀 권한 변경', time: '1일 전', type: 'permission' },
];

const columns = [
  {
    accessorKey: "activity",
    header: "활동 내역",
  },
  {
    accessorKey: "time",
    header: "시간",
  },
  {
    accessorKey: "type",
    header: "유형",
    cell: ({ row }: any) => {
      const type = row.getValue("type");
      const typeLabels: Record<string, string> = {
        update: '수정',
        evaluation: '평가',
        new: '신규',
        organization: '조직',
        permission: '권한',
      };
      return (
        <span className="px-2 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-700">
          {typeLabels[type as string] || type}
        </span>
      );
    },
  },
];

const DashboardPage: React.FC = () => {
  return (
    <MainLayout>
      {/* 페이지 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          대시보드
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          OK금융그룹 e-HR 시스템에 오신 것을 환영합니다
        </p>
      </div>

      {/* 통계 카드 그리드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
        <StatCard
          title="전체 직원"
          value="1,234"
          description="전월 대비"
          icon={<Users className="w-6 h-6 text-primary" />}
          trend={{ value: 2.5, isPositive: true }}
        />
        <StatCard
          title="부서"
          value="45"
          description="활성 부서"
          icon={<Building2 className="w-6 h-6 text-purple-600" />}
          trend={{ value: 1, isPositive: true }}
        />
        <StatCard
          title="직무"
          value="123"
          description="등록된 직무"
          icon={<Briefcase className="w-6 h-6 text-blue-600" />}
          trend={{ value: 0, isPositive: true }}
        />
        <StatCard
          title="직무기술서"
          value="98"
          description="작성 완료"
          icon={<FileText className="w-6 h-6 text-green-600" />}
          trend={{ value: 12, isPositive: true }}
        />
        <StatCard
          title="진행중 평가"
          value="15"
          description="이번 분기"
          icon={<TrendingUp className="w-6 h-6 text-yellow-600" />}
          trend={{ value: 3, isPositive: false }}
        />
        <StatCard
          title="신규 입사자"
          value="23"
          description="이번 달"
          icon={<UserPlus className="w-6 h-6 text-indigo-600" />}
          trend={{ value: 5, isPositive: true }}
        />
      </div>

      {/* 빠른 작업 및 최근 활동 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 빠른 작업 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            빠른 작업
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <Button 
              variant="outline" 
              className="justify-start h-auto py-4 px-4"
              onClick={() => console.log('직원 등록')}
            >
              <div className="flex flex-col items-start">
                <Users className="w-5 h-5 mb-2 text-primary" />
                <span className="font-medium">직원 등록</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  새 직원 추가
                </span>
              </div>
            </Button>
            
            <Button 
              variant="outline" 
              className="justify-start h-auto py-4 px-4"
              onClick={() => console.log('평가 시작')}
            >
              <div className="flex flex-col items-start">
                <TrendingUp className="w-5 h-5 mb-2 text-green-600" />
                <span className="font-medium">평가 시작</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  새 평가 생성
                </span>
              </div>
            </Button>
            
            <Button 
              variant="outline" 
              className="justify-start h-auto py-4 px-4"
              onClick={() => console.log('조직도 보기')}
            >
              <div className="flex flex-col items-start">
                <Building2 className="w-5 h-5 mb-2 text-purple-600" />
                <span className="font-medium">조직도 보기</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  조직 구조 확인
                </span>
              </div>
            </Button>
            
            <Button 
              variant="outline" 
              className="justify-start h-auto py-4 px-4"
              onClick={() => console.log('리포트 생성')}
            >
              <div className="flex flex-col items-start">
                <FileText className="w-5 h-5 mb-2 text-blue-600" />
                <span className="font-medium">리포트 생성</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  통계 리포트
                </span>
              </div>
            </Button>
          </div>
        </div>

        {/* 최근 활동 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              최근 활동
            </h2>
            <Button variant="ghost" size="sm">
              전체 보기 <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
          <DataTable
            columns={columns}
            data={recentActivities}
          />
        </div>
      </div>
    </MainLayout>
  );
};

export default DashboardPage;