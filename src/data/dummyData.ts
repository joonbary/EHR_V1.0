// 테스트용 더미 데이터

export interface Employee {
  id: string;
  employeeId: string;
  name: string;
  email: string;
  phone: string;
  department: string;
  position: string;
  joinDate: string;
  status: 'active' | 'inactive' | 'leave';
  manager?: string;
  location: string;
  skills?: string[];
  profileImage?: string;
}

export interface Department {
  id: string;
  name: string;
  managerId: string;
  managerName: string;
  memberCount: number;
  parentId?: string;
}

export interface Evaluation {
  id: string;
  period: string;
  evaluatorId: string;
  evaluatorName: string;
  evaluateeId: string;
  evaluateeName: string;
  department: string;
  status: 'pending' | 'in_progress' | 'completed' | 'approved';
  score?: number;
  dueDate: string;
  completedDate?: string;
  comments?: string;
}

export interface Compensation {
  id: string;
  employeeId: string;
  employeeName: string;
  baseSalary: number;
  bonus: number;
  totalCompensation: number;
  effectiveDate: string;
  currency: string;
}

export interface Promotion {
  id: string;
  employeeId: string;
  employeeName: string;
  currentPosition: string;
  proposedPosition: string;
  department: string;
  status: 'pending' | 'approved' | 'rejected';
  requestDate: string;
  approvalDate?: string;
  approvedBy?: string;
}

// 직원 더미 데이터
export const dummyEmployees: Employee[] = [
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
    manager: '김부장',
    location: '서울 본사',
    skills: ['React', 'TypeScript', 'Node.js', 'AWS'],
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
    manager: '이부장',
    location: '서울 본사',
    skills: ['인사관리', '채용', '교육기획'],
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
    manager: '박부장',
    location: '서울 본사',
    skills: ['재무분석', 'Excel', 'SAP'],
  },
  {
    id: '4',
    employeeId: 'EMP-2018-0601',
    name: '박민수',
    email: 'park.minsu@okfn.co.kr',
    phone: '010-4567-8901',
    department: '마케팅팀',
    position: '차장',
    joinDate: '2018-06-01',
    status: 'active',
    manager: '정부장',
    location: '서울 본사',
    skills: ['디지털마케팅', '브랜드전략', 'SNS마케팅'],
  },
  {
    id: '5',
    employeeId: 'EMP-2022-0215',
    name: '정수진',
    email: 'jung.sujin@okfn.co.kr',
    phone: '010-5678-9012',
    department: 'IT개발팀',
    position: '주임',
    joinDate: '2022-02-15',
    status: 'active',
    manager: '김부장',
    location: '서울 본사',
    skills: ['Java', 'Spring', 'MySQL'],
  },
  {
    id: '6',
    employeeId: 'EMP-2020-0910',
    name: '최지혜',
    email: 'choi.jihye@okfn.co.kr',
    phone: '010-6789-0123',
    department: '기획팀',
    position: '과장',
    joinDate: '2020-09-10',
    status: 'active',
    manager: '송부장',
    location: '서울 본사',
    skills: ['전략기획', '사업분석', 'PPT'],
  },
];

// 부서 더미 데이터
export const dummyDepartments: Department[] = [
  {
    id: '1',
    name: 'OK금융그룹',
    managerId: 'ceo',
    managerName: '최고경영자',
    memberCount: 1234,
  },
  {
    id: '2',
    name: '경영지원본부',
    managerId: 'exec1',
    managerName: '김본부장',
    memberCount: 150,
    parentId: '1',
  },
  {
    id: '3',
    name: '인사팀',
    managerId: 'hr_manager',
    managerName: '이팀장',
    memberCount: 25,
    parentId: '2',
  },
  {
    id: '4',
    name: '재무팀',
    managerId: 'finance_manager',
    managerName: '박팀장',
    memberCount: 30,
    parentId: '2',
  },
  {
    id: '5',
    name: 'IT본부',
    managerId: 'it_exec',
    managerName: '정본부장',
    memberCount: 200,
    parentId: '1',
  },
  {
    id: '6',
    name: 'IT개발팀',
    managerId: 'dev_manager',
    managerName: '최팀장',
    memberCount: 80,
    parentId: '5',
  },
  {
    id: '7',
    name: 'IT인프라팀',
    managerId: 'infra_manager',
    managerName: '강팀장',
    memberCount: 40,
    parentId: '5',
  },
];

// 평가 더미 데이터
export const dummyEvaluations: Evaluation[] = [
  {
    id: '1',
    period: '2024년 상반기',
    evaluatorId: 'manager1',
    evaluatorName: '김부장',
    evaluateeId: '1',
    evaluateeName: '홍길동',
    department: 'IT개발팀',
    status: 'completed',
    score: 92,
    dueDate: '2024-06-30',
    completedDate: '2024-06-25',
    comments: '우수한 성과를 보였으며, 팀 내 리더십을 발휘함',
  },
  {
    id: '2',
    period: '2024년 상반기',
    evaluatorId: 'manager2',
    evaluatorName: '이부장',
    evaluateeId: '2',
    evaluateeName: '김철수',
    department: '인사팀',
    status: 'in_progress',
    dueDate: '2024-06-30',
  },
  {
    id: '3',
    period: '2024년 상반기',
    evaluatorId: 'manager3',
    evaluatorName: '박부장',
    evaluateeId: '3',
    evaluateeName: '이영희',
    department: '재무팀',
    status: 'pending',
    dueDate: '2024-06-30',
  },
  {
    id: '4',
    period: '2023년 하반기',
    evaluatorId: 'manager1',
    evaluatorName: '김부장',
    evaluateeId: '1',
    evaluateeName: '홍길동',
    department: 'IT개발팀',
    status: 'approved',
    score: 88,
    dueDate: '2023-12-31',
    completedDate: '2023-12-20',
  },
];

// 보상 더미 데이터
export const dummyCompensations: Compensation[] = [
  {
    id: '1',
    employeeId: '1',
    employeeName: '홍길동',
    baseSalary: 65000000,
    bonus: 13000000,
    totalCompensation: 78000000,
    effectiveDate: '2024-01-01',
    currency: 'KRW',
  },
  {
    id: '2',
    employeeId: '2',
    employeeName: '김철수',
    baseSalary: 58000000,
    bonus: 8700000,
    totalCompensation: 66700000,
    effectiveDate: '2024-01-01',
    currency: 'KRW',
  },
  {
    id: '3',
    employeeId: '3',
    employeeName: '이영희',
    baseSalary: 48000000,
    bonus: 4800000,
    totalCompensation: 52800000,
    effectiveDate: '2024-01-01',
    currency: 'KRW',
  },
];

// 승진 더미 데이터
export const dummyPromotions: Promotion[] = [
  {
    id: '1',
    employeeId: '1',
    employeeName: '홍길동',
    currentPosition: '선임 개발자',
    proposedPosition: '책임 개발자',
    department: 'IT개발팀',
    status: 'pending',
    requestDate: '2024-06-01',
  },
  {
    id: '2',
    employeeId: '5',
    employeeName: '정수진',
    currentPosition: '주임',
    proposedPosition: '대리',
    department: 'IT개발팀',
    status: 'approved',
    requestDate: '2024-05-15',
    approvalDate: '2024-05-30',
    approvedBy: '김부장',
  },
  {
    id: '3',
    employeeId: '6',
    employeeName: '최지혜',
    currentPosition: '과장',
    proposedPosition: '차장',
    department: '기획팀',
    status: 'rejected',
    requestDate: '2024-04-01',
    approvalDate: '2024-04-15',
    approvedBy: '송부장',
  },
];

// 통계 데이터 생성 함수
export const generateStatistics = () => {
  return {
    totalEmployees: dummyEmployees.length,
    activeEmployees: dummyEmployees.filter(e => e.status === 'active').length,
    departments: dummyDepartments.length,
    pendingEvaluations: dummyEvaluations.filter(e => e.status === 'pending' || e.status === 'in_progress').length,
    averageCompensation: Math.round(
      dummyCompensations.reduce((sum, c) => sum + c.totalCompensation, 0) / dummyCompensations.length
    ),
    pendingPromotions: dummyPromotions.filter(p => p.status === 'pending').length,
  };
};

// 최근 활동 데이터 생성 함수
export const generateRecentActivities = () => {
  return [
    {
      id: 1,
      type: 'employee_added',
      description: '신규 직원 등록',
      details: '정수진 님이 IT개발팀에 합류했습니다',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2시간 전
      icon: 'user-plus',
      color: 'green',
    },
    {
      id: 2,
      type: 'evaluation_completed',
      description: '평가 완료',
      details: '2024년 상반기 평가가 완료되었습니다',
      timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000), // 5시간 전
      icon: 'clipboard-check',
      color: 'blue',
    },
    {
      id: 3,
      type: 'promotion_approved',
      description: '승진 승인',
      details: '정수진 님의 대리 승진이 승인되었습니다',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1일 전
      icon: 'trending-up',
      color: 'purple',
    },
    {
      id: 4,
      type: 'department_update',
      description: '조직 변경',
      details: 'IT인프라팀이 새로 구성되었습니다',
      timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3일 전
      icon: 'building-2',
      color: 'orange',
    },
  ];
};