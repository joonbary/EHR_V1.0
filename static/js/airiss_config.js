// AIRISS MSA Service Configuration
window.AIRISS_CONFIG = {
    // Production URL for AIRISS service on Railway
    API_URL: 'https://web-production-4066.up.railway.app',
    
    // API endpoints
    ENDPOINTS: {
        UPLOAD: '/api/v1/upload',
        ANALYZE: '/api/v1/analysis/analyze',
        HEALTH: '/api/v1/health',
        RESULTS: '/api/v1/analysis/results'
    },
    
    // Request configuration
    REQUEST_TIMEOUT: 30000, // 30 seconds
    
    // Helper function to get full API URL
    getApiUrl: function(endpoint) {
        return this.API_URL + this.ENDPOINTS[endpoint];
    }
};

// Override for local development if needed
if (window.location.hostname === 'localhost' && window.location.port === '8000') {
    // When running Django locally, still use Railway API
    console.log('Using Railway AIRISS API for local development');
}