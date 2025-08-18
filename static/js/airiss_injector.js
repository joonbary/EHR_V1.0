// AIRISS API Injector - iframe 내부에서 실행되어 API 호출을 부모 창으로 전달
// 이 스크립트는 AIRISS React 앱 내부에 주입되어야 함

(function() {
    'use strict';
    
    console.log('[AIRISS Injector] Initializing API interceptor in iframe...');
    
    // 부모 창과 통신 설정
    const parentOrigin = window.parent.location.origin;
    let requestCounter = 0;
    const pendingRequests = new Map();
    
    // 부모 창으로부터 메시지 수신
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'AIRISS_CONFIG') {
            console.log('[AIRISS Injector] Received config from parent:', event.data);
            
            // API 기본 URL 업데이트
            if (window.API_BASE_URL) {
                window.API_BASE_URL = event.data.proxyUrl;
            }
            
            // React 앱의 환경 변수 업데이트 시도
            if (window.process && window.process.env) {
                window.process.env.REACT_APP_API_URL = event.data.proxyUrl;
            }
        } else if (event.data && event.data.type === 'AIRISS_UPLOAD_RESPONSE') {
            // 업로드 응답 처리
            const callback = pendingRequests.get(event.data.requestId);
            if (callback) {
                callback(event.data);
                pendingRequests.delete(event.data.requestId);
            }
        } else if (event.data && event.data.type === 'AIRISS_API_RESPONSE') {
            // API 응답 처리
            const callback = pendingRequests.get(event.data.requestId);
            if (callback) {
                callback(event.data);
                pendingRequests.delete(event.data.requestId);
            }
        }
    });
    
    // XMLHttpRequest 오버라이드
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
        const xhr = new originalXHR();
        const originalOpen = xhr.open;
        const originalSend = xhr.send;
        
        xhr.open = function(method, url, async, user, password) {
            this._method = method;
            this._url = url;
            
            // localhost:8003 요청 감지
            if (url && url.includes('localhost:8003')) {
                console.log('[AIRISS Injector] Intercepting XHR to:', url);
                
                // 부모 창으로 전달할 준비
                this._shouldProxy = true;
                this._originalUrl = url;
                
                // 일단 가짜 URL로 열기 (실제로는 부모 창으로 전송)
                return originalOpen.call(this, method, 'about:blank', async, user, password);
            }
            
            return originalOpen.call(this, method, url, async, user, password);
        };
        
        xhr.send = function(data) {
            if (this._shouldProxy) {
                console.log('[AIRISS Injector] Proxying XHR request through parent');
                
                const requestId = `xhr_${requestCounter++}`;
                
                // FormData 처리
                if (data instanceof FormData) {
                    // FormData를 직렬화
                    const fileEntry = data.get('file');
                    if (fileEntry && fileEntry instanceof File) {
                        const reader = new FileReader();
                        reader.onload = function() {
                            window.parent.postMessage({
                                type: 'AIRISS_UPLOAD_REQUEST',
                                requestId: requestId,
                                method: this._method,
                                endpoint: this._originalUrl,
                                fileData: {
                                    name: fileEntry.name,
                                    type: fileEntry.type,
                                    buffer: reader.result
                                },
                                employee_id: data.get('employee_id'),
                                analysis_type: data.get('analysis_type')
                            }, parentOrigin);
                        }.bind(this);
                        reader.readAsArrayBuffer(fileEntry);
                    }
                } else {
                    // 일반 데이터
                    window.parent.postMessage({
                        type: 'AIRISS_API_REQUEST',
                        requestId: requestId,
                        method: this._method,
                        endpoint: this._originalUrl,
                        body: data
                    }, parentOrigin);
                }
                
                // 응답 대기
                pendingRequests.set(requestId, (response) => {
                    // XHR 응답 시뮬레이션
                    Object.defineProperty(xhr, 'responseText', {
                        value: JSON.stringify(response.data)
                    });
                    Object.defineProperty(xhr, 'response', {
                        value: response.data
                    });
                    Object.defineProperty(xhr, 'status', {
                        value: response.status || (response.success ? 200 : 500)
                    });
                    Object.defineProperty(xhr, 'readyState', {
                        value: 4
                    });
                    
                    // 이벤트 발생
                    if (xhr.onreadystatechange) {
                        xhr.onreadystatechange();
                    }
                    if (response.success && xhr.onload) {
                        xhr.onload();
                    } else if (!response.success && xhr.onerror) {
                        xhr.onerror();
                    }
                });
                
                return;
            }
            
            return originalSend.call(this, data);
        };
        
        return xhr;
    };
    
    // fetch API 오버라이드
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        let urlString = typeof url === 'string' ? url : url.url;
        
        // localhost:8003 요청 감지
        if (urlString && urlString.includes('localhost:8003')) {
            console.log('[AIRISS Injector] Intercepting fetch to:', urlString);
            
            const requestId = `fetch_${requestCounter++}`;
            
            return new Promise((resolve, reject) => {
                // FormData 처리
                if (options.body instanceof FormData) {
                    const fileEntry = options.body.get('file');
                    if (fileEntry && fileEntry instanceof File) {
                        const reader = new FileReader();
                        reader.onload = function() {
                            window.parent.postMessage({
                                type: 'AIRISS_UPLOAD_REQUEST',
                                requestId: requestId,
                                method: options.method || 'POST',
                                endpoint: urlString,
                                fileData: {
                                    name: fileEntry.name,
                                    type: fileEntry.type,
                                    buffer: reader.result
                                },
                                employee_id: options.body.get('employee_id'),
                                analysis_type: options.body.get('analysis_type')
                            }, parentOrigin);
                        };
                        reader.readAsArrayBuffer(fileEntry);
                    }
                } else {
                    // 일반 요청
                    let body = options.body;
                    if (typeof body === 'string') {
                        try {
                            body = JSON.parse(body);
                        } catch (e) {
                            // JSON이 아닌 경우 그대로 사용
                        }
                    }
                    
                    window.parent.postMessage({
                        type: 'AIRISS_API_REQUEST',
                        requestId: requestId,
                        method: options.method || 'GET',
                        endpoint: urlString,
                        body: body,
                        headers: options.headers
                    }, parentOrigin);
                }
                
                // 응답 대기
                pendingRequests.set(requestId, (response) => {
                    if (response.success) {
                        resolve(new Response(JSON.stringify(response.data), {
                            status: response.status || 200,
                            headers: { 'Content-Type': 'application/json' }
                        }));
                    } else {
                        reject(new Error(response.error || 'Request failed'));
                    }
                });
            });
        }
        
        return originalFetch.call(this, url, options);
    };
    
    // 부모 창에 준비 완료 알림
    window.parent.postMessage({
        type: 'AIRISS_INJECTOR_READY'
    }, parentOrigin);
    
    console.log('[AIRISS Injector] API interceptor ready');
})();