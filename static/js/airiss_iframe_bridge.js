// AIRISS iframe Bridge - iframe 내부의 API 호출을 가로채서 프록시로 리다이렉트
(function() {
    'use strict';
    
    console.log('[AIRISS Bridge] Initializing iframe bridge...');
    
    // AIRISS iframe 찾기
    function setupIframeBridge() {
        const iframe = document.getElementById('airissFrame');
        if (!iframe) {
            console.log('[AIRISS Bridge] iframe not found, retrying...');
            setTimeout(setupIframeBridge, 1000);
            return;
        }
        
        console.log('[AIRISS Bridge] iframe found, setting up bridge...');
        
        // iframe이 로드된 후 스크립트 주입
        iframe.addEventListener('load', function() {
            console.log('[AIRISS Bridge] iframe loaded, injecting script...');
            
            try {
                // iframe의 window 객체에 접근 시도
                const iframeWindow = iframe.contentWindow;
                
                // 같은 도메인이 아니면 postMessage 사용
                if (iframe.src.includes('railway.app') || iframe.src.includes('localhost:3000')) {
                    console.log('[AIRISS Bridge] Cross-origin iframe detected, using postMessage...');
                    
                    // iframe에 설정 메시지 보내기
                    iframeWindow.postMessage({
                        type: 'AIRISS_CONFIG',
                        apiBaseUrl: '/airiss/api/upload-proxy/',
                        proxyUrl: window.location.origin + '/airiss/api/upload-proxy/'
                    }, '*');
                    
                    // iframe으로부터 업로드 요청 받기
                    window.addEventListener('message', handleIframeMessage);
                }
            } catch (e) {
                console.log('[AIRISS Bridge] Cannot access iframe directly (cross-origin), using postMessage only');
                
                // postMessage로만 통신
                iframe.contentWindow.postMessage({
                    type: 'AIRISS_CONFIG',
                    apiBaseUrl: '/airiss/api/upload-proxy/',
                    proxyUrl: window.location.origin + '/airiss/api/upload-proxy/'
                }, '*');
            }
        });
    }
    
    // iframe으로부터 메시지 처리
    function handleIframeMessage(event) {
        // AIRISS iframe에서 온 메시지인지 확인
        if (!event.data || !event.data.type) return;
        
        console.log('[AIRISS Bridge] Received message from iframe:', event.data.type);
        
        if (event.data.type === 'AIRISS_UPLOAD_REQUEST') {
            // 업로드 요청 처리
            handleUploadRequest(event.data, event.source, event.origin);
        } else if (event.data.type === 'AIRISS_API_REQUEST') {
            // 일반 API 요청 처리
            handleApiRequest(event.data, event.source, event.origin);
        }
    }
    
    // 업로드 요청 처리
    async function handleUploadRequest(data, source, origin) {
        console.log('[AIRISS Bridge] Processing upload request...');
        
        const formData = new FormData();
        
        // File 객체 재구성이 필요한 경우
        if (data.fileData) {
            const blob = new Blob([data.fileData.buffer], { type: data.fileData.type });
            const file = new File([blob], data.fileData.name, { type: data.fileData.type });
            formData.append('file', file);
        } else if (data.file) {
            formData.append('file', data.file);
        }
        
        // 추가 데이터
        if (data.employee_id) formData.append('employee_id', data.employee_id);
        if (data.analysis_type) formData.append('analysis_type', data.analysis_type);
        
        try {
            const response = await fetch('/airiss/api/upload-proxy/', {
                method: 'POST',
                body: formData,
                credentials: 'same-origin'
            });
            
            const result = await response.json();
            
            // 결과를 iframe으로 전송
            source.postMessage({
                type: 'AIRISS_UPLOAD_RESPONSE',
                requestId: data.requestId,
                success: response.ok,
                data: result,
                status: response.status
            }, origin);
            
            console.log('[AIRISS Bridge] Upload response sent to iframe');
            
        } catch (error) {
            console.error('[AIRISS Bridge] Upload error:', error);
            source.postMessage({
                type: 'AIRISS_UPLOAD_RESPONSE',
                requestId: data.requestId,
                success: false,
                error: error.message
            }, origin);
        }
    }
    
    // 일반 API 요청 처리
    async function handleApiRequest(data, source, origin) {
        console.log('[AIRISS Bridge] Processing API request:', data.endpoint);
        
        try {
            // localhost:8003 요청을 프록시로 변환
            let url = data.endpoint;
            if (url.includes('localhost:8003')) {
                url = url.replace('http://localhost:8003', window.location.origin + '/airiss');
            }
            
            const options = {
                method: data.method || 'GET',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    ...data.headers
                }
            };
            
            if (data.body && data.method !== 'GET') {
                options.body = JSON.stringify(data.body);
            }
            
            const response = await fetch(url, options);
            const result = await response.json();
            
            source.postMessage({
                type: 'AIRISS_API_RESPONSE',
                requestId: data.requestId,
                success: response.ok,
                data: result,
                status: response.status
            }, origin);
            
        } catch (error) {
            console.error('[AIRISS Bridge] API error:', error);
            source.postMessage({
                type: 'AIRISS_API_RESPONSE',
                requestId: data.requestId,
                success: false,
                error: error.message
            }, origin);
        }
    }
    
    // 전역 fetch 오버라이드 (현재 페이지용)
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        let urlString = typeof url === 'string' ? url : url.url;
        
        // localhost:8003 요청 감지
        if (urlString && urlString.includes('localhost:8003')) {
            console.log('[AIRISS Bridge] Intercepting fetch to:', urlString);
            urlString = urlString.replace('http://localhost:8003', window.location.origin + '/airiss');
            console.log('[AIRISS Bridge] Redirected to:', urlString);
            
            if (typeof url === 'string') {
                url = urlString;
            } else {
                url = new Request(urlString, url);
            }
        }
        
        return originalFetch.call(this, url, options);
    };
    
    // 초기화
    setupIframeBridge();
    
    console.log('[AIRISS Bridge] Bridge initialized');
})();