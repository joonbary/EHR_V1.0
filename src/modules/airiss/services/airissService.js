/**
 * AIRISS LLM Service Integration Layer
 * EHR 시스템과 AIRISS 마이크로서비스 간 통신 관리
 */

class AirissService {
  constructor(config = {}) {
    this.baseUrl = config.baseUrl || process.env.REACT_APP_AIRISS_URL || 'http://localhost:8080';
    this.apiKey = config.apiKey || process.env.AIRISS_API_KEY;
    this.timeout = config.timeout || 30000;
    this.retryAttempts = config.retryAttempts || 3;
    this.cache = new Map();
    this.cacheTimeout = config.cacheTimeout || 300000; // 5분
  }

  /**
   * API 요청 헤더 생성
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    const token = this.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * EHR 시스템에서 인증 토큰 가져오기
   */
  getAuthToken() {
    // EHR 시스템의 인증 토큰 로직
    return localStorage.getItem('ehr_auth_token') || sessionStorage.getItem('ehr_auth_token');
  }

  /**
   * 재시도 로직이 포함된 fetch 래퍼
   */
  async fetchWithRetry(url, options, attempt = 1) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response;
    } catch (error) {
      if (attempt < this.retryAttempts) {
        console.warn(`요청 실패, 재시도 ${attempt}/${this.retryAttempts}:`, error.message);
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        return this.fetchWithRetry(url, options, attempt + 1);
      }
      throw error;
    }
  }

  /**
   * 단일 직원 AI 분석
   */
  async analyzeEmployee(employeeData) {
    const cacheKey = `analyze_${employeeData.employee_id}`;
    
    // 캐시 확인
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        console.log('캐시된 분석 결과 반환');
        return cached.data;
      }
    }

    try {
      const response = await this.fetchWithRetry(
        `${this.baseUrl}/api/v1/llm/analyze`,
        {
          method: 'POST',
          headers: this.getHeaders(),
          body: JSON.stringify({
            employee_data: this.transformEmployeeData(employeeData),
            analysis_type: 'comprehensive',
            include_recommendations: true,
          }),
        }
      );

      const result = await response.json();

      // 캐시 저장
      this.cache.set(cacheKey, {
        data: result,
        timestamp: Date.now(),
      });

      return this.transformAnalysisResult(result);
    } catch (error) {
      console.error('직원 분석 실패:', error);
      throw new Error(`AI 분석 실패: ${error.message}`);
    }
  }

  /**
   * 배치 직원 분석
   */
  async batchAnalyzeEmployees(employeeList) {
    try {
      const response = await this.fetchWithRetry(
        `${this.baseUrl}/api/v1/llm/batch-analyze`,
        {
          method: 'POST',
          headers: this.getHeaders(),
          body: JSON.stringify({
            employees: employeeList.map(emp => this.transformEmployeeData(emp)),
            analysis_type: 'comprehensive',
            include_recommendations: false,
          }),
        }
      );

      const result = await response.json();
      return this.transformBatchResults(result);
    } catch (error) {
      console.error('배치 분석 실패:', error);
      throw new Error(`배치 AI 분석 실패: ${error.message}`);
    }
  }

  /**
   * EHR 형식을 AIRISS 형식으로 변환
   */
  transformEmployeeData(ehrEmployee) {
    return {
      employee_id: ehrEmployee.id || ehrEmployee.employeeId,
      name: ehrEmployee.name || `${ehrEmployee.firstName} ${ehrEmployee.lastName}`,
      department: ehrEmployee.department || ehrEmployee.dept,
      position: ehrEmployee.position || ehrEmployee.jobTitle,
      performance_data: {
        목표달성률: ehrEmployee.performanceScore || 0,
        프로젝트성공률: ehrEmployee.projectSuccessRate || 0,
        고객만족도: ehrEmployee.customerSatisfaction || 0,
        출근율: ehrEmployee.attendanceRate || 0,
      },
      competencies: {
        리더십: ehrEmployee.leadershipScore || 0,
        기술력: ehrEmployee.technicalSkill || 0,
        커뮤니케이션: ehrEmployee.communicationScore || 0,
        문제해결: ehrEmployee.problemSolving || 0,
        팀워크: ehrEmployee.teamwork || 0,
        창의성: ehrEmployee.creativity || 0,
        적응력: ehrEmployee.adaptability || 0,
        성실성: ehrEmployee.reliability || 0,
      },
      additional_info: {
        경력년수: ehrEmployee.yearsOfExperience || 0,
        교육수준: ehrEmployee.educationLevel || '',
        자격증: ehrEmployee.certifications || [],
      },
    };
  }

  /**
   * AIRISS 분석 결과를 EHR 형식으로 변환
   */
  transformAnalysisResult(airissResult) {
    return {
      employeeId: airissResult.employee_id,
      aiScore: airissResult.ai_score,
      grade: airissResult.grade,
      strengths: airissResult.strengths || [],
      improvements: airissResult.improvements || [],
      feedback: airissResult.ai_feedback,
      recommendations: airissResult.recommendations || {},
      analyzedAt: airissResult.timestamp,
      processingTime: airissResult.processing_time,
      
      // EHR 시스템 특화 필드
      riskLevel: this.calculateRiskLevel(airissResult.ai_score),
      promotionReady: airissResult.ai_score >= 85,
      trainingNeeded: airissResult.improvements?.length > 3,
      retentionPriority: airissResult.grade === 'S' || airissResult.grade === 'A+',
    };
  }

  /**
   * 배치 결과 변환
   */
  transformBatchResults(batchResult) {
    return {
      results: batchResult.results.map(r => this.transformAnalysisResult(r)),
      summary: {
        total: batchResult.total_count,
        successful: batchResult.success_count,
        failed: batchResult.failed_count,
        processingTime: batchResult.total_processing_time,
        averageScore: this.calculateAverageScore(batchResult.results),
      },
    };
  }

  /**
   * 위험 수준 계산
   */
  calculateRiskLevel(aiScore) {
    if (aiScore < 60) return 'high';
    if (aiScore < 75) return 'medium';
    return 'low';
  }

  /**
   * 평균 점수 계산
   */
  calculateAverageScore(results) {
    const validScores = results
      .filter(r => r.ai_score > 0)
      .map(r => r.ai_score);
    
    if (validScores.length === 0) return 0;
    
    return validScores.reduce((sum, score) => sum + score, 0) / validScores.length;
  }

  /**
   * 서비스 상태 확인
   */
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        headers: this.getHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      
      const health = await response.json();
      return {
        status: health.status === 'healthy',
        details: health,
      };
    } catch (error) {
      console.error('Health check 실패:', error);
      return {
        status: false,
        error: error.message,
      };
    }
  }

  /**
   * 캐시 초기화
   */
  clearCache() {
    this.cache.clear();
    console.log('AIRISS 서비스 캐시 초기화됨');
  }

  /**
   * 특정 직원의 캐시 제거
   */
  invalidateEmployeeCache(employeeId) {
    const cacheKey = `analyze_${employeeId}`;
    this.cache.delete(cacheKey);
  }
}

// 싱글톤 인스턴스 생성
const airissService = new AirissService();

export default airissService;
export { AirissService };