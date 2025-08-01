// Mock API 서비스 - 실제 API 연동 전 테스트용

import {
  dummyEmployees,
  dummyDepartments,
  dummyEvaluations,
  dummyCompensations,
  dummyPromotions,
  generateStatistics,
  generateRecentActivities,
  Employee,
  Department,
  Evaluation,
  Compensation,
  Promotion,
} from '../data/dummyData';

// 지연 시뮬레이션
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// API 응답 타입
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// 페이지네이션 응답 타입
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Mock API 클래스
class MockApi {
  // 직원 관련 API
  async getEmployees(page = 1, pageSize = 10, search?: string): Promise<ApiResponse<PaginatedResponse<Employee>>> {
    await delay(500);
    
    let filteredEmployees = [...dummyEmployees];
    
    if (search) {
      const searchLower = search.toLowerCase();
      filteredEmployees = filteredEmployees.filter(emp => 
        emp.name.toLowerCase().includes(searchLower) ||
        emp.email.toLowerCase().includes(searchLower) ||
        emp.department.toLowerCase().includes(searchLower) ||
        emp.position.toLowerCase().includes(searchLower)
      );
    }
    
    const total = filteredEmployees.length;
    const totalPages = Math.ceil(total / pageSize);
    const start = (page - 1) * pageSize;
    const items = filteredEmployees.slice(start, start + pageSize);
    
    return {
      success: true,
      data: {
        items,
        total,
        page,
        pageSize,
        totalPages,
      },
    };
  }
  
  async getEmployeeById(id: string): Promise<ApiResponse<Employee>> {
    await delay(300);
    
    const employee = dummyEmployees.find(emp => emp.id === id);
    
    if (!employee) {
      return {
        success: false,
        error: '직원을 찾을 수 없습니다',
      };
    }
    
    return {
      success: true,
      data: employee,
    };
  }
  
  async createEmployee(employee: Partial<Employee>): Promise<ApiResponse<Employee>> {
    await delay(800);
    
    const newEmployee: Employee = {
      id: String(dummyEmployees.length + 1),
      employeeId: `EMP-${new Date().getFullYear()}-${String(Date.now()).slice(-4)}`,
      status: 'active',
      joinDate: new Date().toISOString().split('T')[0],
      ...employee,
    } as Employee;
    
    dummyEmployees.push(newEmployee);
    
    return {
      success: true,
      data: newEmployee,
      message: '직원이 성공적으로 등록되었습니다',
    };
  }
  
  async updateEmployee(id: string, updates: Partial<Employee>): Promise<ApiResponse<Employee>> {
    await delay(600);
    
    const index = dummyEmployees.findIndex(emp => emp.id === id);
    
    if (index === -1) {
      return {
        success: false,
        error: '직원을 찾을 수 없습니다',
      };
    }
    
    dummyEmployees[index] = { ...dummyEmployees[index], ...updates };
    
    return {
      success: true,
      data: dummyEmployees[index],
      message: '직원 정보가 업데이트되었습니다',
    };
  }
  
  // 부서 관련 API
  async getDepartments(): Promise<ApiResponse<Department[]>> {
    await delay(400);
    
    return {
      success: true,
      data: dummyDepartments,
    };
  }
  
  async getDepartmentById(id: string): Promise<ApiResponse<Department>> {
    await delay(300);
    
    const department = dummyDepartments.find(dept => dept.id === id);
    
    if (!department) {
      return {
        success: false,
        error: '부서를 찾을 수 없습니다',
      };
    }
    
    return {
      success: true,
      data: department,
    };
  }
  
  // 평가 관련 API
  async getEvaluations(employeeId?: string): Promise<ApiResponse<Evaluation[]>> {
    await delay(500);
    
    let evaluations = [...dummyEvaluations];
    
    if (employeeId) {
      evaluations = evaluations.filter(eval => 
        eval.evaluateeId === employeeId || eval.evaluatorId === employeeId
      );
    }
    
    return {
      success: true,
      data: evaluations,
    };
  }
  
  async createEvaluation(evaluation: Partial<Evaluation>): Promise<ApiResponse<Evaluation>> {
    await delay(700);
    
    const newEvaluation: Evaluation = {
      id: String(dummyEvaluations.length + 1),
      status: 'pending',
      dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      ...evaluation,
    } as Evaluation;
    
    dummyEvaluations.push(newEvaluation);
    
    return {
      success: true,
      data: newEvaluation,
      message: '평가가 생성되었습니다',
    };
  }
  
  async updateEvaluation(id: string, updates: Partial<Evaluation>): Promise<ApiResponse<Evaluation>> {
    await delay(600);
    
    const index = dummyEvaluations.findIndex(eval => eval.id === id);
    
    if (index === -1) {
      return {
        success: false,
        error: '평가를 찾을 수 없습니다',
      };
    }
    
    dummyEvaluations[index] = { ...dummyEvaluations[index], ...updates };
    
    return {
      success: true,
      data: dummyEvaluations[index],
      message: '평가가 업데이트되었습니다',
    };
  }
  
  // 보상 관련 API
  async getCompensations(employeeId?: string): Promise<ApiResponse<Compensation[]>> {
    await delay(400);
    
    let compensations = [...dummyCompensations];
    
    if (employeeId) {
      compensations = compensations.filter(comp => comp.employeeId === employeeId);
    }
    
    return {
      success: true,
      data: compensations,
    };
  }
  
  // 승진 관련 API
  async getPromotions(status?: string): Promise<ApiResponse<Promotion[]>> {
    await delay(400);
    
    let promotions = [...dummyPromotions];
    
    if (status) {
      promotions = promotions.filter(promo => promo.status === status);
    }
    
    return {
      success: true,
      data: promotions,
    };
  }
  
  async createPromotion(promotion: Partial<Promotion>): Promise<ApiResponse<Promotion>> {
    await delay(600);
    
    const newPromotion: Promotion = {
      id: String(dummyPromotions.length + 1),
      status: 'pending',
      requestDate: new Date().toISOString().split('T')[0],
      ...promotion,
    } as Promotion;
    
    dummyPromotions.push(newPromotion);
    
    return {
      success: true,
      data: newPromotion,
      message: '승진 요청이 생성되었습니다',
    };
  }
  
  async updatePromotion(id: string, updates: Partial<Promotion>): Promise<ApiResponse<Promotion>> {
    await delay(500);
    
    const index = dummyPromotions.findIndex(promo => promo.id === id);
    
    if (index === -1) {
      return {
        success: false,
        error: '승진 요청을 찾을 수 없습니다',
      };
    }
    
    dummyPromotions[index] = { ...dummyPromotions[index], ...updates };
    
    return {
      success: true,
      data: dummyPromotions[index],
      message: '승진 요청이 업데이트되었습니다',
    };
  }
  
  // 통계 API
  async getStatistics(): Promise<ApiResponse<ReturnType<typeof generateStatistics>>> {
    await delay(300);
    
    return {
      success: true,
      data: generateStatistics(),
    };
  }
  
  // 최근 활동 API
  async getRecentActivities(): Promise<ApiResponse<ReturnType<typeof generateRecentActivities>>> {
    await delay(200);
    
    return {
      success: true,
      data: generateRecentActivities(),
    };
  }
  
  // 인증 관련 API
  async login(email: string, password: string): Promise<ApiResponse<{ token: string; user: Employee }>> {
    await delay(1000);
    
    const user = dummyEmployees.find(emp => emp.email === email);
    
    if (!user || password !== 'password123') {
      return {
        success: false,
        error: '이메일 또는 비밀번호가 올바르지 않습니다',
      };
    }
    
    return {
      success: true,
      data: {
        token: 'mock-jwt-token-' + Date.now(),
        user,
      },
      message: '로그인 성공',
    };
  }
  
  async logout(): Promise<ApiResponse<null>> {
    await delay(200);
    
    return {
      success: true,
      message: '로그아웃되었습니다',
    };
  }
}

// 싱글톤 인스턴스 export
export const mockApi = new MockApi();