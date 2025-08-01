import React, { useState } from 'react';
import MainLayout from '../layouts/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { 
  Building2,
  Users,
  ChevronRight,
  ChevronDown,
  Search,
  Plus,
  Edit,
  UserPlus,
  Move,
  Download,
  Upload,
  Layers,
  Building,
  User
} from 'lucide-react';

interface Department {
  id: string;
  name: string;
  managerId: string;
  managerName: string;
  memberCount: number;
  subDepartments?: Department[];
  expanded?: boolean;
}

interface Employee {
  id: string;
  name: string;
  position: string;
  email: string;
  department: string;
}

const OrganizationPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState<Department | null>(null);
  const [showAddDeptDialog, setShowAddDeptDialog] = useState(false);
  const [showMoveDialog, setShowMoveDialog] = useState(false);
  const [viewMode, setViewMode] = useState<'tree' | 'chart'>('tree');

  // 더미 조직도 데이터
  const [organization, setOrganization] = useState<Department[]>([
    {
      id: '1',
      name: 'OK금융그룹',
      managerId: 'ceo',
      managerName: '최고경영자',
      memberCount: 1234,
      expanded: true,
      subDepartments: [
        {
          id: '2',
          name: '경영지원본부',
          managerId: 'exec1',
          managerName: '김본부장',
          memberCount: 150,
          expanded: false,
          subDepartments: [
            {
              id: '3',
              name: '인사팀',
              managerId: 'hr_manager',
              managerName: '이팀장',
              memberCount: 25,
            },
            {
              id: '4',
              name: '재무팀',
              managerId: 'finance_manager',
              managerName: '박팀장',
              memberCount: 30,
            },
          ],
        },
        {
          id: '5',
          name: 'IT본부',
          managerId: 'it_exec',
          managerName: '정본부장',
          memberCount: 200,
          expanded: true,
          subDepartments: [
            {
              id: '6',
              name: 'IT개발팀',
              managerId: 'dev_manager',
              managerName: '최팀장',
              memberCount: 80,
            },
            {
              id: '7',
              name: 'IT인프라팀',
              managerId: 'infra_manager',
              managerName: '강팀장',
              memberCount: 40,
            },
          ],
        },
      ],
    },
  ]);

  // 더미 직원 데이터
  const employees: Employee[] = [
    { id: '1', name: '홍길동', position: '선임 개발자', email: 'hong@okfn.co.kr', department: 'IT개발팀' },
    { id: '2', name: '김철수', position: '대리', email: 'kim@okfn.co.kr', department: 'IT개발팀' },
    { id: '3', name: '이영희', position: '과장', email: 'lee@okfn.co.kr', department: '인사팀' },
    { id: '4', name: '박민수', position: '사원', email: 'park@okfn.co.kr', department: '재무팀' },
  ];

  const toggleDepartment = (deptId: string) => {
    const updateDepartments = (departments: Department[]): Department[] => {
      return departments.map(dept => {
        if (dept.id === deptId) {
          return { ...dept, expanded: !dept.expanded };
        }
        if (dept.subDepartments) {
          return { ...dept, subDepartments: updateDepartments(dept.subDepartments) };
        }
        return dept;
      });
    };
    setOrganization(updateDepartments(organization));
  };

  const renderDepartmentTree = (departments: Department[], level = 0) => {
    return departments.map(dept => (
      <div key={dept.id} className={`${level > 0 ? 'ml-6' : ''}`}>
        <div
          className={`flex items-center gap-2 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer ${
            selectedDepartment?.id === dept.id ? 'bg-primary/10' : ''
          }`}
          onClick={() => setSelectedDepartment(dept)}
        >
          {dept.subDepartments && dept.subDepartments.length > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleDepartment(dept.id);
              }}
              className="p-1"
            >
              {dept.expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>
          )}
          {!dept.subDepartments && <div className="w-6" />}
          
          <Building2 className="w-5 h-5 text-gray-400" />
          <div className="flex-1">
            <div className="font-medium">{dept.name}</div>
            <div className="text-sm text-gray-500">{dept.managerName} · {dept.memberCount}명</div>
          </div>
        </div>
        
        {dept.expanded && dept.subDepartments && (
          <div className="mt-1">
            {renderDepartmentTree(dept.subDepartments, level + 1)}
          </div>
        )}
      </div>
    ));
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            조직도 관리
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            회사 조직 구조를 확인하고 관리합니다
          </p>
        </div>

        {/* 액션 바 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="부서 또는 직원 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-[300px]"
                />
              </div>
              
              <Select value={viewMode} onValueChange={(value: 'tree' | 'chart') => setViewMode(value)}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tree">트리 보기</SelectItem>
                  <SelectItem value="chart">차트 보기</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex gap-2">
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                내보내기
              </Button>
              <Button variant="outline">
                <Upload className="w-4 h-4 mr-2" />
                가져오기
              </Button>
              <Button onClick={() => setShowAddDeptDialog(true)}>
                <Plus className="w-4 h-4 mr-2" />
                부서 추가
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 조직도 트리 */}
          <div className="lg:col-span-2">
            <Card className="h-[600px]">
              <CardHeader>
                <CardTitle>조직 구조</CardTitle>
                <CardDescription>
                  부서를 클릭하여 상세 정보를 확인하세요
                </CardDescription>
              </CardHeader>
              <CardContent className="overflow-auto" style={{ maxHeight: '500px' }}>
                {viewMode === 'tree' ? (
                  renderDepartmentTree(organization)
                ) : (
                  <div className="flex items-center justify-center h-[400px] text-gray-500">
                    차트 뷰는 준비 중입니다
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* 상세 정보 패널 */}
          <div className="space-y-6">
            {/* 선택된 부서 정보 */}
            {selectedDepartment && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    {selectedDepartment.name}
                    <Button size="sm" variant="ghost">
                      <Edit className="w-4 h-4" />
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm text-gray-500">부서장</label>
                      <div className="flex items-center gap-2 mt-1">
                        <User className="w-4 h-4 text-gray-400" />
                        <span>{selectedDepartment.managerName}</span>
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm text-gray-500">구성원</label>
                      <div className="flex items-center gap-2 mt-1">
                        <Users className="w-4 h-4 text-gray-400" />
                        <span>{selectedDepartment.memberCount}명</span>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 pt-4">
                      <Button size="sm" variant="outline" className="flex-1">
                        <UserPlus className="w-4 h-4 mr-1" />
                        직원 추가
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="flex-1"
                        onClick={() => setShowMoveDialog(true)}
                      >
                        <Move className="w-4 h-4 mr-1" />
                        이동
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 부서 구성원 목록 */}
            {selectedDepartment && (
              <Card>
                <CardHeader>
                  <CardTitle>부서 구성원</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {employees
                      .filter(emp => emp.department === selectedDepartment.name)
                      .map(emp => (
                        <div key={emp.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <div>
                            <div className="font-medium">{emp.name}</div>
                            <div className="text-sm text-gray-500">{emp.position}</div>
                          </div>
                          <Button size="sm" variant="ghost">
                            <ChevronRight className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 조직 통계 */}
            <Card>
              <CardHeader>
                <CardTitle>조직 통계</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">전체 부서</span>
                    <span className="font-medium">7개</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">전체 직원</span>
                    <span className="font-medium">1,234명</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">평균 부서 인원</span>
                    <span className="font-medium">176명</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">조직 계층</span>
                    <span className="font-medium">3단계</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* 부서 추가 다이얼로그 */}
        <Dialog open={showAddDeptDialog} onOpenChange={setShowAddDeptDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>새 부서 추가</DialogTitle>
              <DialogDescription>
                새로운 부서를 생성합니다.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <label className="text-sm font-medium">부서명</label>
                <Input placeholder="예: 마케팅팀" className="mt-1" />
              </div>
              <div>
                <label className="text-sm font-medium">상위 부서</label>
                <Select>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">OK금융그룹</SelectItem>
                    <SelectItem value="2">경영지원본부</SelectItem>
                    <SelectItem value="5">IT본부</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium">부서장</label>
                <Select>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="emp1">김부장</SelectItem>
                    <SelectItem value="emp2">이부장</SelectItem>
                    <SelectItem value="emp3">박부장</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowAddDeptDialog(false)}>
                취소
              </Button>
              <Button onClick={() => setShowAddDeptDialog(false)}>
                추가
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* 부서 이동 다이얼로그 */}
        <Dialog open={showMoveDialog} onOpenChange={setShowMoveDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>부서 이동</DialogTitle>
              <DialogDescription>
                {selectedDepartment?.name}을(를) 다른 상위 부서로 이동합니다.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <label className="text-sm font-medium">새 상위 부서</label>
                <Select>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">OK금융그룹</SelectItem>
                    <SelectItem value="2">경영지원본부</SelectItem>
                    <SelectItem value="5">IT본부</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowMoveDialog(false)}>
                취소
              </Button>
              <Button onClick={() => setShowMoveDialog(false)}>
                이동
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </MainLayout>
  );
};

export default OrganizationPage;