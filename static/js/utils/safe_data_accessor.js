/**
 * Safe Data Accessor
 * Null/Undefined 안전 데이터 접근
 */

class SafeDataAccessor {
    /**
     * 안전한 중첩 속성 접근
     * @param {Object} obj - 대상 객체
     * @param {string} path - 속성 경로 (예: 'data.employee.salary')
     * @param {*} defaultValue - 기본값
     * @returns {*} 속성값 또는 기본값
     */
    static get(obj, path, defaultValue = null) {
        try {
            const keys = path.split('.');
            let result = obj;
            
            for (const key of keys) {
                if (result === null || result === undefined) {
                    console.warn(`[SafeAccessor] Null/undefined at key: ${key}`);
                    return defaultValue;
                }
                result = result[key];
            }
            
            // NaN, null, undefined 체크
            if (result === null || result === undefined || 
                (typeof result === 'number' && isNaN(result))) {
                console.warn(`[SafeAccessor] Invalid value at path: ${path}`);
                return defaultValue;
            }
            
            return result;
        } catch (error) {
            console.error(`[SafeAccessor] Error accessing ${path}:`, error);
            return defaultValue;
        }
    }
    
    /**
     * 안전한 숫자 파싱
     * @param {*} value - 파싱할 값
     * @param {number} defaultValue - 기본값
     * @returns {number} 파싱된 숫자 또는 기본값
     */
    static parseNumber(value, defaultValue = 0) {
        if (value === null || value === undefined || value === '') {
            return defaultValue;
        }
        
        const parsed = Number(value);
        
        if (isNaN(parsed)) {
            console.warn(`[SafeAccessor] Invalid number: ${value}`);
            return defaultValue;
        }
        
        return parsed;
    }
    
    /**
     * 안전한 배열 접근
     * @param {*} value - 배열 값
     * @param {Array} defaultValue - 기본 배열
     * @returns {Array} 배열 또는 기본값
     */
    static getArray(value, defaultValue = []) {
        if (!Array.isArray(value)) {
            console.warn(`[SafeAccessor] Not an array: ${value}`);
            return defaultValue;
        }
        return value;
    }
    
    /**
     * 안전한 문자열 변환
     * @param {*} value - 변환할 값
     * @param {string} defaultValue - 기본값
     * @returns {string} 문자열 또는 기본값
     */
    static getString(value, defaultValue = '') {
        if (value === null || value === undefined) {
            return defaultValue;
        }
        
        return String(value);
    }
    
    /**
     * 통화 형식 변환
     * @param {number} value - 숫자값
     * @param {string} defaultValue - 기본값
     * @returns {string} 통화 형식 문자열
     */
    static formatCurrency(value, defaultValue = '₩0') {
        const num = this.parseNumber(value, 0);
        
        try {
            return new Intl.NumberFormat('ko-KR', {
                style: 'currency',
                currency: 'KRW'
            }).format(num);
        } catch (error) {
            console.error('[SafeAccessor] Currency format error:', error);
            return defaultValue;
        }
    }
    
    /**
     * 퍼센트 형식 변환
     * @param {number} value - 숫자값
     * @param {number} decimals - 소수점 자리수
     * @returns {string} 퍼센트 형식 문자열
     */
    static formatPercent(value, decimals = 1) {
        const num = this.parseNumber(value, 0);
        return `${num.toFixed(decimals)}%`;
    }
}

// 사용 예시
function updateDashboardSafely(data) {
    // 안전한 데이터 접근
    const totalEmployees = SafeDataAccessor.get(data, 'workforce.totalEmployees', 0);
    const departments = SafeDataAccessor.getArray(data.departments);
    const avgSalary = SafeDataAccessor.get(data, 'compensation.avgSalary', 0);
    
    // UI 업데이트
    document.getElementById('totalEmployees').textContent = totalEmployees;
    document.getElementById('avgSalary').textContent = 
        SafeDataAccessor.formatCurrency(avgSalary);
    
    // 배열 처리
    departments.forEach(dept => {
        const name = SafeDataAccessor.getString(dept.name, 'Unknown');
        const count = SafeDataAccessor.get(dept, 'employeeCount', 0);
        console.log(`Department: ${name}, Count: ${count}`);
    });
}