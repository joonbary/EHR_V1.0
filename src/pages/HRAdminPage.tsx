import React, { useState } from 'react';
import MainLayout from '../layouts/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { DataTable } from '../components/ui/data-table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { 
  Users,
  UserPlus,
  Shield,
  Settings,
  Download,
  Upload,
  Filter,
  Search,
  Edit,
  Trash2,
  Eye,
  AlertCircle,
  CheckCircle,
  Clock,
  Building2,
  Mail,
  Phone,
  MoreVertical
} from 'lucide-react';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';

interface Employee {
  id: string;
  employeeId: string;
  name: string;
  email: string;
  phone: string;
  department: string;
  position: string;
  joinDate: string;
  status: 'active' | 'inactive' | 'leave';
  lastModified: string;
}

const employees: Employee[] = [
  {
    id: '1',
    employeeId: 'EMP-2020-0315',
    name: '홍길동',
    email: 'hong.gildong@okfn.co.kr',
    phone: '010-1234-5678',
    department: 'IT개발팀',
    position: '선임 개발자',
    joinDate: '2020-03-15',
    status: 'active',
    lastModified: '2024-01-15',
  },
  {
    id: '2',
    employeeId: 'EMP-2019-0820',
    name: '김철수',
    email: 'kim.cheolsu@okfn.co.kr',
    phone: '010-2345-6789',
    department: '인사팀',
    position: '과장',
    joinDate: '2019-08-20',
    status: 'active',
    lastModified: '2024-01-10',
  },
  {
    id: '3',
    employeeId: 'EMP-2021-0105',
    name: '이영희',
    email: 'lee.younghee@okfn.co.kr',
    phone: '010-3456-7890',
    department: '재무팀',
    position: '대리',
    joinDate: '2021-01-05',
    status: 'leave',
    lastModified: '2024-01-05',
  },
];

const columns = [
  {
    id: "select",
    header: ({ table }: any) => (
      <input
        type="checkbox"
        checked={table.getIsAllPageRowsSelected()}
        onChange={(e) => table.toggleAllPageRowsSelected(!!e.target.checked)}
        className="rounded border-gray-300"
      />
    ),
    cell: ({ row }: any) => (
      <input
        type="checkbox"
        checked={row.getIsSelected()}
        onChange={(e) => row.toggleSelected(!!e.target.checked)}
        className="rounded border-gray-300"
      />
    ),
  },
  {
    accessorKey: "employeeId",
    header: "사번",
  },
  {
    accessorKey: "name",
    header: "이름",
    cell: ({ row }: any) => {
      return (
        <div className="font-medium">{row.getValue("name")}</div>
      );
    },
  },
  {
    accessorKey: "department",
    header: "부서",
  },
  {
    accessorKey: "position",
    header: "직급",
  },
  {
    accessorKey: "email",
    header: "이메일",
  },
  {
    accessorKey: "phone",
    header: "전화번호",
  },
  {
    accessorKey: "status",
    header: "상태",
    cell: ({ row }: any) => {
      const status = row.getValue("status");
      const statusConfig = {
        active: { label: '재직', icon: CheckCircle, class: 'text-green-600' },
        inactive: { label: '퇴직', icon: AlertCircle, class: 'text-red-600' },
        leave: { label: '휴직', icon: Clock, class: 'text-yellow-600' },
      };
      const config = statusConfig[status as keyof typeof statusConfig];
      const Icon = config.icon;
      return (
        <div className={`flex items-center gap-1 ${config.class}`}>
          <Icon className="w-4 h-4" />
          <span className="text-sm">{config.label}</span>
        </div>
      );
    },
  },
  {
    id: "actions",
    cell: ({ row }: any) => {
      const employee = row.original;
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">메뉴 열기</span>
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>작업</DropdownMenuLabel>
            <DropdownMenuItem>
              <Eye className="mr-2 h-4 w-4" />
              상세 보기
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Edit className="mr-2 h-4 w-4" />
              수정
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-red-600">
              <Trash2 className="mr-2 h-4 w-4" />
              삭제
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];

const HRAdminPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showAddEmployeeDialog, setShowAddEmployeeDialog] = useState(false);

  // 통계 데이터
  const stats = {
    totalEmployees: 1234,
    activeEmployees: 1180,
    newThisMonth: 23,
    departments: 45,
  };

  // 최근 활동
  const recentActivities = [
    { id: 1, activity: '홍길동 직원 정보 수정', time: '10분 전', type: 'update' },
    { id: 2, activity: '신규 직원 3명 등록', time: '1시간 전', type: 'new' },
    { id: 3, activity: '인사 데이터 백업 완료', time: '3시간 전', type: 'backup' },
    { id: 4, activity: '권한 그룹 설정 변경', time: '5시간 전', type: 'permission' },
  ];

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            HR 관리자 대시보드
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            전체 인사 정보를 관리하고 분석합니다
          </p>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalEmployees.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                전월 대비 +2.5%
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">재직 중</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeEmployees.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                전체의 95.7%
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">신규 입사</CardTitle>
              <UserPlus className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.newThisMonth}</div>
              <p className="text-xs text-muted-foreground">
                이번 달 입사자
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">부서</CardTitle>
              <Building2 className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.departments}</div>
              <p className="text-xs text-muted-foreground">
                활성 부서 수
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 필터 및 액션 바 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="직원 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-full sm:w-[300px]"
                />
              </div>
              
              <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                <SelectTrigger className="w-full sm:w-[180px]">
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
              
              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger className="w-full sm:w-[140px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체 상태</SelectItem>
                  <SelectItem value="active">재직</SelectItem>
                  <SelectItem value="inactive">퇴직</SelectItem>
                  <SelectItem value="leave">휴직</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex gap-2">
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                내보내기
              </Button>
              <Button variant="outline" onClick={() => setShowImportDialog(true)}>
                <Upload className="w-4 h-4 mr-2" />
                가져오기
              </Button>
              <Button onClick={() => setShowAddEmployeeDialog(true)}>
                <UserPlus className="w-4 h-4 mr-2" />
                직원 추가
              </Button>
            </div>
          </div>
        </div>

        {/* 직원 목록 테이블 */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>직원 목록</CardTitle>
            <CardDescription>
              전체 직원 정보를 조회하고 관리할 수 있습니다
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable
              columns={columns}
              data={employees}
            />
          </CardContent>
        </Card>

        {/* 하단 정보 카드들 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 최근 활동 */}
          <Card>
            <CardHeader>
              <CardTitle>최근 활동</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">{activity.activity}</p>
                      <p className="text-xs text-gray-500">{activity.time}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      activity.type === 'new' ? 'bg-green-100 text-green-800' :
                      activity.type === 'update' ? 'bg-blue-100 text-blue-800' :
                      activity.type === 'backup' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {activity.type === 'new' ? '신규' :
                       activity.type === 'update' ? '수정' :
                       activity.type === 'backup' ? '백업' :
                       '권한'}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 빠른 작업 */}
          <Card>
            <CardHeader>
              <CardTitle>빠른 작업</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <Button variant="outline" className="justify-start h-auto py-4">
                  <div className="flex flex-col items-start">
                    <Shield className="w-5 h-5 mb-2 text-purple-600" />
                    <span className="font-medium">권한 관리</span>
                    <span className="text-xs text-gray-500">사용자 권한 설정</span>
                  </div>
                </Button>
                
                <Button variant="outline" className="justify-start h-auto py-4">
                  <div className="flex flex-col items-start">
                    <Settings className="w-5 h-5 mb-2 text-gray-600" />
                    <span className="font-medium">시스템 설정</span>
                    <span className="text-xs text-gray-500">전역 설정 관리</span>
                  </div>
                </Button>
                
                <Button variant="outline" className="justify-start h-auto py-4">
                  <div className="flex flex-col items-start">
                    <Download className="w-5 h-5 mb-2 text-blue-600" />
                    <span className="font-medium">백업</span>
                    <span className="text-xs text-gray-500">데이터 백업</span>
                  </div>
                </Button>
                
                <Button variant="outline" className="justify-start h-auto py-4">
                  <div className="flex flex-col items-start">
                    <Users className="w-5 h-5 mb-2 text-green-600" />
                    <span className="font-medium">일괄 수정</span>
                    <span className="text-xs text-gray-500">대량 데이터 수정</span>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 직원 추가 다이얼로그 */}
        <Dialog open={showAddEmployeeDialog} onOpenChange={setShowAddEmployeeDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>신규 직원 등록</DialogTitle>
              <DialogDescription>
                새로운 직원 정보를 입력합니다.
              </DialogDescription>
            </DialogHeader>
            <div className="grid grid-cols-2 gap-4 py-4">
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">이름 *</label>
                  <Input placeholder="홍길동" className="mt-1" />
                </div>
                <div>
                  <label className="text-sm font-medium">이메일 *</label>
                  <Input type="email" placeholder="hong@okfn.co.kr" className="mt-1" />
                </div>
                <div>
                  <label className="text-sm font-medium">전화번호</label>
                  <Input type="tel" placeholder="010-1234-5678" className="mt-1" />
                </div>
                <div>
                  <label className="text-sm font-medium">입사일 *</label>
                  <Input type="date" className="mt-1" />
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">부서 *</label>
                  <Select>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="it">IT개발팀</SelectItem>
                      <SelectItem value="hr">인사팀</SelectItem>
                      <SelectItem value="finance">재무팀</SelectItem>
                      <SelectItem value="marketing">마케팅팀</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">직급 *</label>
                  <Select>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="staff">사원</SelectItem>
                      <SelectItem value="senior">주임</SelectItem>
                      <SelectItem value="assistant">대리</SelectItem>
                      <SelectItem value="manager">과장</SelectItem>
                      <SelectItem value="deputy">차장</SelectItem>
                      <SelectItem value="general">부장</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">상급자</label>
                  <Select>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="manager1">김부장</SelectItem>
                      <SelectItem value="manager2">이부장</SelectItem>
                      <SelectItem value="manager3">박부장</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">근무지</label>
                  <Select>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="seoul">서울 본사</SelectItem>
                      <SelectItem value="busan">부산 지점</SelectItem>
                      <SelectItem value="daegu">대구 지점</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowAddEmployeeDialog(false)}>
                취소
              </Button>
              <Button onClick={() => setShowAddEmployeeDialog(false)}>
                등록
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* 데이터 가져오기 다이얼로그 */}
        <Dialog open={showImportDialog} onOpenChange={setShowImportDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>직원 데이터 가져오기</DialogTitle>
              <DialogDescription>
                CSV 또는 Excel 파일로 직원 정보를 일괄 등록합니다.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <p className="text-sm text-gray-600 mb-2">
                  파일을 드래그하거나 클릭하여 업로드하세요
                </p>
                <p className="text-xs text-gray-500">
                  CSV, XLSX 파일 지원 (최대 10MB)
                </p>
                <Button variant="outline" className="mt-4">
                  파일 선택
                </Button>
              </div>
              <div className="text-sm text-gray-500">
                <p className="font-medium mb-1">템플릿 다운로드:</p>
                <div className="flex gap-2">
                  <Button size="sm" variant="link" className="p-0">
                    CSV 템플릿
                  </Button>
                  <Button size="sm" variant="link" className="p-0">
                    Excel 템플릿
                  </Button>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowImportDialog(false)}>
                취소
              </Button>
              <Button onClick={() => setShowImportDialog(false)}>
                가져오기
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </MainLayout>
  );
};

export default HRAdminPage;