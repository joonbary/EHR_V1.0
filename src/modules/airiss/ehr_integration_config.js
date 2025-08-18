/**
 * EHR-AIRISS Integration Configuration
 * EHR 시스템에서 AIRISS MSA를 호출하기 위한 설정
 */

const AIRISS_CONFIG = {
  // Railway에 배포된 AIRISS MSA URL
  baseUrl: 'https://web-production-4066.up.railway.app',
  
  // API 엔드포인트
  endpoints: {
    health: '/health',
    analyze: '/api/v1/llm/analyze',
    batchAnalyze: '/api/v1/llm/batch-analyze',
    usage: '/api/v1/llm/usage',
    docs: '/docs'
  },
  
  // 요청 설정
  requestConfig: {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    timeout: 30000, // 30초
    retryAttempts: 3
  }
};

/**
 * AIRISS 서비스 클래스
 */
class AirissIntegrationService {
  constructor(config = AIRISS_CONFIG) {
    this.config = config;
    this.baseUrl = config.baseUrl;
  }

  /**
   * 헬스 체크
   */
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseUrl}${this.config.endpoints.health}`, {
        method: 'GET',
        headers: this.config.requestConfig.headers
      });
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('AIRISS Health Check Error:', error);
      return { status: 'error', error: error.message };
    }
  }

  /**
   * 단일 직원 AI 분석
   */
  async analyzeEmployee(employeeData) {
    try {
      const requestBody = {
        employee_data: {
          employee_id: employeeData.id || employeeData.employeeId,
          name: employeeData.name,
          department: employeeData.department,
          position: employeeData.position,
          performance_data: {
            목표달성률: employeeData.goalAchievement || 0,
            프로젝트성공률: employeeData.projectSuccess || 0,
            고객만족도: employeeData.customerSatisfaction || 0,
            출근율: employeeData.attendance || 0
          },
          competencies: {
            리더십: employeeData.leadership || 0,
            기술력: employeeData.technical || 0,
            커뮤니케이션: employeeData.communication || 0,
            문제해결: employeeData.problemSolving || 0,
            팀워크: employeeData.teamwork || 0,
            창의성: employeeData.creativity || 0,
            적응력: employeeData.adaptability || 0,
            성실성: employeeData.reliability || 0
          }
        },
        analysis_type: 'comprehensive',
        include_recommendations: true
      };

      const response = await fetch(`${this.baseUrl}${this.config.endpoints.analyze}`, {
        method: 'POST',
        headers: this.config.requestConfig.headers,
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Analysis failed: ${response.status}`);
      }

      const result = await response.json();
      
      // EHR 형식으로 변환
      return {
        employeeId: result.employee_id,
        aiScore: result.ai_score,
        grade: result.grade,
        strengths: result.strengths || [],
        improvements: result.improvements || [],
        feedback: result.ai_feedback,
        recommendations: result.recommendations,
        timestamp: result.timestamp,
        processingTime: result.processing_time
      };
    } catch (error) {
      console.error('AIRISS Analysis Error:', error);
      throw error;
    }
  }

  /**
   * 배치 직원 분석
   */
  async batchAnalyzeEmployees(employeeList) {
    try {
      const employees = employeeList.map(emp => ({
        employee_id: emp.id || emp.employeeId,
        name: emp.name,
        department: emp.department,
        position: emp.position,
        performance_data: {
          목표달성률: emp.goalAchievement || 0,
          프로젝트성공률: emp.projectSuccess || 0,
          고객만족도: emp.customerSatisfaction || 0,
          출근율: emp.attendance || 0
        },
        competencies: {
          리더십: emp.leadership || 0,
          기술력: emp.technical || 0,
          커뮤니케이션: emp.communication || 0,
          문제해결: emp.problemSolving || 0,
          팀워크: emp.teamwork || 0,
          창의성: emp.creativity || 0,
          적응력: emp.adaptability || 0,
          성실성: emp.reliability || 0
        }
      }));

      const requestBody = {
        employees,
        analysis_type: 'comprehensive',
        include_recommendations: false
      };

      const response = await fetch(`${this.baseUrl}${this.config.endpoints.batchAnalyze}`, {
        method: 'POST',
        headers: this.config.requestConfig.headers,
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Batch analysis failed: ${response.status}`);
      }

      const result = await response.json();
      
      // EHR 형식으로 변환
      return {
        results: result.results.map(r => ({
          employeeId: r.employee_id,
          aiScore: r.ai_score,
          grade: r.grade,
          strengths: r.strengths || [],
          improvements: r.improvements || [],
          feedback: r.ai_feedback,
          timestamp: r.timestamp
        })),
        summary: {
          total: result.total_count,
          successful: result.success_count,
          failed: result.failed_count,
          processingTime: result.total_processing_time
        }
      };
    } catch (error) {
      console.error('AIRISS Batch Analysis Error:', error);
      throw error;
    }
  }
}

// Export for use in EHR system
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { AirissIntegrationService, AIRISS_CONFIG };
} else {
  window.AirissIntegrationService = AirissIntegrationService;
  window.AIRISS_CONFIG = AIRISS_CONFIG;
}