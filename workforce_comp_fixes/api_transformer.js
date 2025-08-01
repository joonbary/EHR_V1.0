
/**
 * API Response Transformer
 * 백엔드 응답을 프론트엔드 형식으로 변환
 */

class APIResponseTransformer {
    // 필드명 매핑 테이블
    static fieldMappings = {
        // Backend (snake_case) -> Frontend (camelCase)
        'employee_count': 'employeeCount',
        'total_employees': 'totalEmployees',
        'active_employees': 'activeEmployees',
        'total_salary': 'totalSalary',
        'avg_salary': 'avgSalary',
        'department_name': 'departmentName',
        'job_title': 'jobTitle',
        'hire_date': 'hireDate',
        'employment_status': 'employmentStatus',
        'salary_range': 'salaryRange',
        'benefits_cost': 'benefitsCost',
        'bonus_pool': 'bonusPool',
        'new_hires_month': 'newHiresMonth',
        'terminations_month': 'terminationsMonth',
        
        // 한글 필드명 처리
        '직원수': 'employeeCount',
        '평균급여': 'avgSalary',
        '총급여': 'totalSalary',
        '부서명': 'departmentName',
        '직급': 'jobTitle',
        '입사일': 'hireDate',
        '재직상태': 'employmentStatus'
    };
    
    /**
     * API 응답 변환
     * @param {Object} response - 백엔드 응답
     * @returns {Object} 변환된 응답
     */
    static transform(response) {
        console.log('[APITransformer] Original response:', response);
        
        if (!response) {
            console.warn('[APITransformer] Null or undefined response');
            return this.getDefaultResponse();
        }
        
        try {
            const transformed = this.transformObject(response);
            console.log('[APITransformer] Transformed response:', transformed);
            return transformed;
        } catch (error) {
            console.error('[APITransformer] Transformation error:', error);
            return this.getDefaultResponse();
        }
    }
    
    /**
     * 객체 변환 (재귀적)
     */
    static transformObject(obj) {
        if (obj === null || obj === undefined) {
            return null;
        }
        
        if (Array.isArray(obj)) {
            return obj.map(item => this.transformObject(item));
        }
        
        if (typeof obj !== 'object') {
            return obj;
        }
        
        const transformed = {};
        
        for (const [key, value] of Object.entries(obj)) {
            const newKey = this.fieldMappings[key] || this.toCamelCase(key);
            transformed[newKey] = this.transformObject(value);
        }
        
        return transformed;
    }
    
    /**
     * snake_case를 camelCase로 변환
     */
    static toCamelCase(str) {
        return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    }
    
    /**
     * 기본 응답 구조
     */
    static getDefaultResponse() {
        return {
            success: false,
            data: {
                totalEmployees: 0,
                activeEmployees: 0,
                departments: [],
                totalSalary: 0,
                avgSalary: 0
            },
            message: 'No data available'
        };
    }
}

// 사용 예시
async function fetchWorkforceData() {
    try {
        const response = await fetch('/api/workforce/summary/');
        const data = await response.json();
        
        // 응답 변환
        const transformedData = APIResponseTransformer.transform(data);
        
        // UI 업데이트
        updateDashboard(transformedData);
        
    } catch (error) {
        console.error('API fetch error:', error);
        const defaultData = APIResponseTransformer.getDefaultResponse();
        updateDashboard(defaultData);
    }
}
