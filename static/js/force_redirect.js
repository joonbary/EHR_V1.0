// Force redirect localhost:8003 requests to local proxy
(function() {
    'use strict';
    
    console.log('[Force Redirect] Initializing...');
    
    // Override fetch
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        let urlString = typeof url === 'string' ? url : url.url;
        
        if (urlString && urlString.includes('localhost:8003')) {
            const newUrl = urlString.replace('http://localhost:8003', '/airiss');
            console.log('[Force Redirect] Redirecting fetch:', urlString, '→', newUrl);
            
            if (typeof url === 'string') {
                url = newUrl;
            } else {
                url = new Request(newUrl, url);
            }
        }
        
        return originalFetch.call(this, url, options);
    };
    
    // Override XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        if (url && url.includes('localhost:8003')) {
            url = url.replace('http://localhost:8003', '/airiss');
            console.log('[Force Redirect] Redirecting XHR:', url);
        }
        return originalXHROpen.call(this, method, url, async, user, password);
    };
    
    console.log('[Force Redirect] Ready');
})();