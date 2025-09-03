/**
 * API Utilities - 표준화된 에러 처리 및 API 호출
 * 리팩토링: 중복 API 코드 제거
 * Version: 1.0
 * Date: 2025-01-21
 */

class ApiUtils {
    /**
     * 기본 API 설정
     */
    static config = {
        baseUrl: '/api',
        timeout: 30000,
        retryCount: 3,
        retryDelay: 1000
    };

    /**
     * CSRF 토큰 가져오기
     */
    static getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    /**
     * 표준화된 API 호출
     */
    static async request(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            credentials: 'same-origin'
        };

        const finalOptions = { ...defaultOptions, ...options };
        
        // Body가 있으면 JSON 문자열로 변환
        if (finalOptions.body && typeof finalOptions.body === 'object') {
            finalOptions.body = JSON.stringify(finalOptions.body);
        }

        let lastError = null;
        
        // 재시도 로직
        for (let i = 0; i < this.config.retryCount; i++) {
            try {
                const response = await this.fetchWithTimeout(url, finalOptions);
                
                // 응답 상태 확인
                if (!response.ok) {
                    throw new ApiError(
                        response.status,
                        response.statusText,
                        await this.parseErrorResponse(response)
                    );
                }
                
                // 성공적인 응답 파싱
                return await this.parseResponse(response);
                
            } catch (error) {
                lastError = error;
                
                // 503 에러 또는 네트워크 에러인 경우 재시도
                if (this.shouldRetry(error, i)) {
                    await this.delay(this.config.retryDelay * (i + 1));
                    continue;
                }
                
                // 재시도 불가능한 에러
                throw error;
            }
        }
        
        throw lastError;
    }

    /**
     * 타임아웃이 있는 fetch
     */
    static async fetchWithTimeout(url, options) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), this.config.timeout);
        
        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            return response;
        } finally {
            clearTimeout(timeout);
        }
    }

    /**
     * 재시도 여부 판단
     */
    static shouldRetry(error, attemptNumber) {
        // 마지막 시도인 경우 재시도 안함
        if (attemptNumber >= this.config.retryCount - 1) {
            return false;
        }
        
        // 503 Service Unavailable
        if (error instanceof ApiError && error.status === 503) {
            console.log(`🔄 Retrying due to 503 error (attempt ${attemptNumber + 2}/${this.config.retryCount})`);
            return true;
        }
        
        // 네트워크 에러
        if (error.name === 'AbortError' || error.name === 'NetworkError') {
            console.log(`🔄 Retrying due to network error (attempt ${attemptNumber + 2}/${this.config.retryCount})`);
            return true;
        }
        
        return false;
    }

    /**
     * 응답 파싱
     */
    static async parseResponse(response) {
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
    }

    /**
     * 에러 응답 파싱
     */
    static async parseErrorResponse(response) {
        try {
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch {
            return 'Unknown error occurred';
        }
    }

    /**
     * 지연 함수
     */
    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * GET 요청
     */
    static get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        
        return this.request(fullUrl, {
            method: 'GET'
        });
    }

    /**
     * POST 요청
     */
    static post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: data
        });
    }

    /**
     * PUT 요청
     */
    static put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: data
        });
    }

    /**
     * DELETE 요청
     */
    static delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }

    /**
     * 파일 업로드
     */
    static async upload(url, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        // 추가 데이터 append
        Object.entries(additionalData).forEach(([key, value]) => {
            formData.append(key, value);
        });
        
        return this.request(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCsrfToken()
                // Content-Type은 자동으로 설정됨
            },
            body: formData
        });
    }
}

/**
 * 커스텀 API 에러 클래스
 */
class ApiError extends Error {
    constructor(status, statusText, response) {
        super(`API Error: ${status} ${statusText}`);
        this.name = 'ApiError';
        this.status = status;
        this.statusText = statusText;
        this.response = response;
    }

    /**
     * 사용자 친화적인 에러 메시지 생성
     */
    getUserMessage() {
        switch (this.status) {
            case 400:
                return '잘못된 요청입니다. 입력 값을 확인해주세요.';
            case 401:
                return '인증이 필요합니다. 다시 로그인해주세요.';
            case 403:
                return '권한이 없습니다.';
            case 404:
                return '요청한 리소스를 찾을 수 없습니다.';
            case 500:
                return '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
            case 503:
                return '서비스를 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.';
            default:
                return '오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        }
    }
}

/**
 * 토스트 알림 헬퍼
 */
class Toast {
    static show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    
    static error(message) {
        this.show(message, 'error');
    }
    
    static success(message) {
        this.show(message, 'success');
    }
    
    static info(message) {
        this.show(message, 'info');
    }
}

// 전역 스타일 추가
if (!document.getElementById('api-utils-styles')) {
    const style = document.createElement('style');
    style.id = 'api-utils-styles';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiUtils, ApiError, Toast };
}

// 전역으로도 노출 (브라우저 환경)
if (typeof window !== 'undefined') {
    window.ApiUtils = ApiUtils;
    window.ApiError = ApiError;
    window.Toast = Toast;
}