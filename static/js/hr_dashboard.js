// HR Dashboard JavaScript
const API_BASE = '/employees/hr/api';

// CSRF 토큰 가져오기
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 전역 변수
let currentDomesticPage = 1;
let currentOverseasPage = 1;
let currentContractorPage = 1;
const pageSize = 20;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeUpload();
    loadDashboardSummary();
    loadDomesticEmployees();
    
    // 탭 변경 이벤트
    document.querySelectorAll('#hrTabs a[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            const target = e.target.getAttribute('href');
            switch(target) {
                case '#domestic':
                    loadDomesticEmployees();
                    break;
                case '#overseas':
                    loadOverseasEmployees();
                    break;
                case '#contractor':
                    loadContractors();
                    break;
                case '#visualization':
                    loadCharts();
                    break;
            }
        });
    });
});

// 파일 업로드 초기화
function initializeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    // 클릭 이벤트
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // 드래그 앤 드롭 이벤트
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragging');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragging');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragging');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
    
    // 파일 선택 이벤트
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

// 파일 업로드 처리
async function handleFileUpload(file) {
    // 파일 유효성 검사
    const validTypes = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    if (!validTypes.includes(file.type)) {
        alert('엑셀 파일만 업로드 가능합니다.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    // 프로그레스 표시
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = uploadProgress ? uploadProgress.querySelector('.gradient-bg') : null;
    const uploadStatus = document.getElementById('uploadStatus');
    
    if (uploadProgress) {
        uploadProgress.classList.remove('hidden');
    }
    if (progressBar) {
        progressBar.style.width = '0%';
    }
    
    try {
        const response = await fetch(`${API_BASE}/upload/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (!response.ok) {
            let errorMessage = `업로드 실패: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.json();
                console.error('Server error details:', errorData);
                errorMessage = errorData.error || errorMessage;
                if (errorData.traceback) {
                    console.error('Server traceback:', errorData.traceback);
                }
            } catch (e) {
                const errorText = await response.text();
                console.error('Server response text:', errorText);
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        if (progressBar) progressBar.style.width = '50%';
        if (uploadStatus) uploadStatus.textContent = `${data.file_type} 파일 처리 중...`;
        
        // 처리 상태 확인
        await checkProcessingStatus(data.task_id);
        
    } catch (error) {
        console.error('Upload error:', error);
        alert('파일 업로드 중 오류가 발생했습니다.');
        if (uploadProgress) uploadProgress.classList.add('hidden');
    }
}

// 파일 처리 상태 확인
async function checkProcessingStatus(taskId) {
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = uploadProgress ? uploadProgress.querySelector('.gradient-bg') : null;
    const uploadStatus = document.getElementById('uploadStatus');
    
    const checkInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/task/${taskId}/status/`);
            const data = await response.json();
            
            if (data.completed) {
                clearInterval(checkInterval);
                if (progressBar) progressBar.style.width = '100%';
                
                if (data.status === 'completed') {
                    if (uploadStatus) uploadStatus.textContent = '처리 완료!';
                    setTimeout(() => {
                        const uploadProgress = document.getElementById('uploadProgress');
                        if (uploadProgress) uploadProgress.classList.add('hidden');
                        loadDashboardSummary();
                        loadDomesticEmployees();
                        loadOverseasEmployees();
                        loadContractors();
                    }, 1500);
                } else {
                    if (uploadStatus) uploadStatus.textContent = '처리 실패';
                    alert('파일 처리 중 오류가 발생했습니다.');
                }
            } else {
                // 진행률 업데이트
                const progress = 50 + (data.success_records / data.total_records * 50);
                if (progressBar) progressBar.style.width = `${progress}%`;
            }
        } catch (error) {
            clearInterval(checkInterval);
            console.error('Status check error:', error);
        }
    }, 2000);
}

// 대시보드 요약 데이터 로드
async function loadDashboardSummary() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/summary/`);
        const data = await response.json();
        
        // 요약 카드 업데이트
        document.getElementById('totalCount').textContent = 
            (data.summary.domestic_count + data.summary.overseas_count).toLocaleString();
        document.getElementById('overseasCount').textContent = 
            data.summary.overseas_count.toLocaleString();
        document.getElementById('contractorCount').textContent = 
            data.summary.total_contractors.toLocaleString();
        document.getElementById('monthlyCost').textContent = 
            formatCurrency(data.summary.total_monthly_cost);
            
    } catch (error) {
        console.error('Summary load error:', error);
    }
}

// 국내 직원 목록 로드
async function loadDomesticEmployees(page = 1) {
    try {
        const company = document.getElementById('domesticCompanyFilter').value;
        const search = document.getElementById('domesticSearchInput').value;
        
        let url = `${API_BASE}/employees/?location_type=domestic&page=${page}&limit=${pageSize}`;
        if (company) url += `&company=${encodeURIComponent(company)}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        // 테이블 업데이트
        const tbody = document.getElementById('domesticTableBody');
        tbody.innerHTML = data.data.map(emp => `
            <tr>
                <td>${emp.employee_no || '-'}</td>
                <td>${emp.name}</td>
                <td>${emp.company}</td>
                <td>${emp.department || '-'}</td>
                <td>${emp.job_level || '-'}</td>
                <td>${emp.position || '-'}</td>
                <td>${emp.hire_date || '-'}</td>
                <td>
                    <span class="badge ${getStatusBadgeClass(emp.status_label)}">
                        ${emp.status_label}
                    </span>
                </td>
            </tr>
        `).join('');
        
        // 페이지네이션 업데이트
        updatePagination('domesticPagination', page, data.total_pages, loadDomesticEmployees);
        currentDomesticPage = page;
        
    } catch (error) {
        console.error('Domestic employees load error:', error);
    }
}

// 해외 직원 목록 로드
async function loadOverseasEmployees(page = 1) {
    try {
        const country = document.getElementById('overseasCountryFilter').value;
        
        let url = `${API_BASE}/employees/?location_type=overseas&page=${page}&limit=${pageSize}`;
        if (country) url += `&country=${encodeURIComponent(country)}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        // 테이블 업데이트
        const tbody = document.getElementById('overseasTableBody');
        tbody.innerHTML = data.data.map(emp => `
            <tr>
                <td>${emp.name}</td>
                <td>${emp.company}</td>
                <td>${emp.country || '-'}</td>
                <td>${emp.position || '-'}</td>
                <td>${emp.job_level || '-'}</td>
                <td>
                    <span class="badge bg-success">재직</span>
                </td>
            </tr>
        `).join('');
        
        // 페이지네이션 업데이트
        updatePagination('overseasPagination', page, data.total_pages, loadOverseasEmployees);
        currentOverseasPage = page;
        
    } catch (error) {
        console.error('Overseas employees load error:', error);
    }
}

// 외주 인력 목록 로드
async function loadContractors(page = 1) {
    try {
        const vendor = document.getElementById('vendorFilter').value;
        const project = document.getElementById('projectFilter').value;
        const status = document.getElementById('contractorStatusFilter').value;
        
        let url = `${API_BASE}/contractors/?page=${page}&limit=${pageSize}`;
        if (status) url += `&status=${status}`;
        if (vendor) url += `&vendor=${encodeURIComponent(vendor)}`;
        if (project) url += `&project=${encodeURIComponent(project)}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        // 테이블 업데이트
        const tbody = document.getElementById('contractorTableBody');
        tbody.innerHTML = data.data.map(contractor => `
            <tr>
                <td>${contractor.contractor_name}</td>
                <td>${contractor.vendor_company}</td>
                <td>${contractor.project_name}</td>
                <td>${contractor.department || '-'}</td>
                <td>${contractor.role || '-'}</td>
                <td>${contractor.start_date || '-'}</td>
                <td>${contractor.end_date || '-'}</td>
                <td>${formatCurrency(contractor.monthly_rate)}</td>
                <td>
                    <span class="badge ${getProjectStatusBadgeClass(contractor.project_status)}">
                        ${contractor.project_status}
                    </span>
                </td>
            </tr>
        `).join('');
        
        // 페이지네이션 업데이트
        updatePagination('contractorPagination', page, data.total_pages, loadContractors);
        currentContractorPage = page;
        
    } catch (error) {
        console.error('Contractors load error:', error);
    }
}

// 차트 로드
async function loadCharts() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/summary/`);
        const data = await response.json();
        
        // 회사별 인원 분포 차트
        const companyCtx = document.getElementById('companyChart').getContext('2d');
        new Chart(companyCtx, {
            type: 'pie',
            data: {
                labels: data.company_distribution.map(item => item.company),
                datasets: [{
                    data: data.company_distribution.map(item => item.count),
                    backgroundColor: [
                        '#1443FF',
                        '#FFD700',
                        '#FF6B6B',
                        '#4ECDC4',
                        '#45B7D1'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        // 월별 인력 변동 추이 차트
        const trendResponse = await fetch(`${API_BASE}/dashboard/trend/`);
        const trendData = await trendResponse.json();
        
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: getLast12Months(),
                datasets: [{
                    label: '입사',
                    data: [5, 8, 12, 7, 9, 6, 10, 8, 11, 7, 9, 8],
                    borderColor: '#1443FF',
                    backgroundColor: 'rgba(20, 67, 255, 0.1)',
                    tension: 0.3
                }, {
                    label: '퇴사',
                    data: [3, 4, 2, 5, 3, 4, 2, 3, 4, 2, 3, 4],
                    borderColor: '#FF6B6B',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Charts load error:', error);
    }
}

// 검색 함수들
function searchDomesticEmployees() {
    loadDomesticEmployees(1);
}

function searchOverseasEmployees() {
    loadOverseasEmployees(1);
}

function searchContractors() {
    loadContractors(1);
}

// 유틸리티 함수들
function formatCurrency(amount) {
    return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW',
        maximumFractionDigits: 0
    }).format(amount);
}

function getStatusBadgeClass(status) {
    const statusClasses = {
        '재직': 'bg-success',
        '신규': 'bg-primary',
        '퇴직': 'bg-secondary'
    };
    return statusClasses[status] || 'bg-secondary';
}

function getProjectStatusBadgeClass(status) {
    const statusClasses = {
        '진행중': 'bg-success',
        '예정': 'bg-warning',
        '종료': 'bg-secondary'
    };
    return statusClasses[status] || 'bg-secondary';
}

function updatePagination(elementId, currentPage, totalPages, loadFunction) {
    const pagination = document.getElementById(elementId);
    let html = '';
    
    // Previous button
    html += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="event.preventDefault(); ${loadFunction.name}(${currentPage - 1})">이전</a>
        </li>
    `;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="event.preventDefault(); ${loadFunction.name}(${i})">${i}</a>
                </li>
            `;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    // Next button
    html += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="event.preventDefault(); ${loadFunction.name}(${currentPage + 1})">다음</a>
        </li>
    `;
    
    pagination.innerHTML = html;
}

function getLast12Months() {
    const months = [];
    const now = new Date();
    
    for (let i = 11; i >= 0; i--) {
        const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
        months.push(date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'short' }));
    }
    
    return months;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}