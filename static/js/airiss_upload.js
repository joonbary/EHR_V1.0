// AIRISS File Upload Handler
class AirissFileUploader {
    constructor() {
        this.apiUrl = window.AIRISS_CONFIG ? window.AIRISS_CONFIG.getApiUrl('UPLOAD') : 'https://web-production-4066.up.railway.app/api/v1/upload';
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File input handler
        const fileInput = document.getElementById('airiss-file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        // Upload button handler
        const uploadBtn = document.getElementById('airiss-upload-btn');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.uploadFile());
        }
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.selectedFile = file;
            this.updateFileInfo(file);
        }
    }

    updateFileInfo(file) {
        const fileInfo = document.getElementById('file-info');
        if (fileInfo) {
            fileInfo.innerHTML = `
                <div class="alert alert-info">
                    <strong>선택된 파일:</strong> ${file.name}<br>
                    <strong>크기:</strong> ${this.formatFileSize(file.size)}<br>
                    <strong>타입:</strong> ${file.type || 'Unknown'}
                </div>
            `;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    async uploadFile() {
        if (!this.selectedFile) {
            this.showMessage('파일을 선택해주세요.', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', this.selectedFile);

        // Get additional metadata if available
        const employeeId = document.getElementById('employee-id')?.value;
        if (employeeId) {
            formData.append('employee_id', employeeId);
        }

        this.showProgress(true);
        
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                body: formData,
                // Don't set Content-Type header, let browser set it with boundary for multipart/form-data
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: 'Upload failed' }));
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.handleUploadSuccess(result);
            
        } catch (error) {
            console.error('Upload error:', error);
            this.handleUploadError(error);
        } finally {
            this.showProgress(false);
        }
    }

    handleUploadSuccess(result) {
        this.showMessage('파일이 성공적으로 업로드되었습니다!', 'success');
        
        // Clear file selection
        const fileInput = document.getElementById('airiss-file-input');
        if (fileInput) {
            fileInput.value = '';
        }
        
        // Clear file info
        const fileInfo = document.getElementById('file-info');
        if (fileInfo) {
            fileInfo.innerHTML = '';
        }
        
        this.selectedFile = null;
        
        // Show analysis results if available
        if (result.analysis_id) {
            this.showAnalysisLink(result.analysis_id);
        }
    }

    handleUploadError(error) {
        let message = '파일 업로드에 실패했습니다.';
        
        if (error.message.includes('ERR_CONNECTION_REFUSED')) {
            message = 'AIRISS 서비스에 연결할 수 없습니다. 서비스 상태를 확인해주세요.';
        } else if (error.message.includes('502')) {
            message = 'AIRISS 서비스가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.';
        } else if (error.message) {
            message += ' ' + error.message;
        }
        
        this.showMessage(message, 'danger');
    }

    showAnalysisLink(analysisId) {
        const resultContainer = document.getElementById('upload-result');
        if (resultContainer) {
            resultContainer.innerHTML = `
                <div class="alert alert-success mt-3">
                    <h5>업로드 완료!</h5>
                    <p>분석 ID: ${analysisId}</p>
                    <a href="/airiss/analysis/${analysisId}" class="btn btn-primary btn-sm">
                        분석 결과 보기
                    </a>
                </div>
            `;
        }
    }

    showMessage(message, type = 'info') {
        const messageContainer = document.getElementById('upload-message');
        if (messageContainer) {
            messageContainer.innerHTML = `
                <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    }

    showProgress(show) {
        const progressContainer = document.getElementById('upload-progress');
        if (progressContainer) {
            if (show) {
                progressContainer.innerHTML = `
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 100%">
                            업로드 중...
                        </div>
                    </div>
                `;
            } else {
                progressContainer.innerHTML = '';
            }
        }
        
        // Disable/enable upload button
        const uploadBtn = document.getElementById('airiss-upload-btn');
        if (uploadBtn) {
            uploadBtn.disabled = show;
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    window.airissUploader = new AirissFileUploader();
});