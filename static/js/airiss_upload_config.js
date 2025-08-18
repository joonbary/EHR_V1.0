// AIRISS Upload Configuration
// This file intercepts and redirects AIRISS upload requests to the correct endpoint

(function() {
    'use strict';
    
    // Get the correct AIRISS URL from environment or settings
    const AIRISS_URL = window.AIRISS_SERVICE_URL || 'https://web-production-4066.up.railway.app';
    const PROXY_URL = '/airiss/api/upload-proxy/';
    
    // Override XMLHttpRequest to intercept AIRISS upload requests
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;
    
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        // Check if this is an AIRISS upload request
        if (url && (url.includes('localhost:8003') || url.includes('api/v1/upload'))) {
            console.log('[AIRISS] Intercepting upload request:', url);
            
            // Redirect to our proxy endpoint
            if (url.includes('localhost:8003')) {
                url = url.replace('http://localhost:8003', '');
                url = PROXY_URL;
            } else if (!url.startsWith('http') && url.includes('api/v1/upload')) {
                url = PROXY_URL;
            }
            
            console.log('[AIRISS] Redirected to:', url);
        }
        
        this._interceptedURL = url;
        return originalXHROpen.apply(this, [method, url, async, user, password]);
    };
    
    // Override fetch API as well for modern requests
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        // Convert URL to string if it's a Request object
        const urlString = typeof url === 'string' ? url : url.url;
        
        // Check if this is an AIRISS upload request
        if (urlString && (urlString.includes('localhost:8003') || urlString.includes('api/v1/upload'))) {
            console.log('[AIRISS] Intercepting fetch request:', urlString);
            
            // Redirect to our proxy endpoint
            let newUrl = urlString;
            if (urlString.includes('localhost:8003')) {
                newUrl = urlString.replace('http://localhost:8003', '');
                newUrl = PROXY_URL;
            } else if (!urlString.startsWith('http') && urlString.includes('api/v1/upload')) {
                newUrl = PROXY_URL;
            }
            
            console.log('[AIRISS] Redirected fetch to:', newUrl);
            
            // Update the URL
            if (typeof url === 'string') {
                url = newUrl;
            } else {
                url = new Request(newUrl, url);
            }
        }
        
        return originalFetch.apply(this, [url, options]);
    };
    
    // Also handle any iframe messages from AIRISS
    window.addEventListener('message', function(event) {
        // Check if message is from AIRISS iframe
        if (event.origin === AIRISS_URL || event.origin === 'http://localhost:3000') {
            console.log('[AIRISS] Received message from iframe:', event.data);
            
            // Handle upload requests from iframe
            if (event.data && event.data.type === 'upload') {
                // Forward the upload request to our proxy
                const formData = new FormData();
                if (event.data.file) {
                    formData.append('file', event.data.file);
                }
                if (event.data.employee_id) {
                    formData.append('employee_id', event.data.employee_id);
                }
                if (event.data.analysis_type) {
                    formData.append('analysis_type', event.data.analysis_type);
                }
                
                fetch(PROXY_URL, {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    // Send response back to iframe
                    event.source.postMessage({
                        type: 'upload_response',
                        success: true,
                        data: data
                    }, event.origin);
                })
                .catch(error => {
                    // Send error back to iframe
                    event.source.postMessage({
                        type: 'upload_response',
                        success: false,
                        error: error.message
                    }, event.origin);
                });
            }
        }
    });
    
    // Log that the interceptor is active
    console.log('[AIRISS] Upload interceptor initialized');
    console.log('[AIRISS] Proxy URL:', PROXY_URL);
    console.log('[AIRISS] AIRISS Service URL:', AIRISS_URL);
})();