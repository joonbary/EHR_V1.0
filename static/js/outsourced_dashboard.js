// 외주인력 현황관리 Dashboard JavaScript
const API_BASE = '/employees/hr/api/outsourced';

// 전역 변수
let trendChart = null;
let currentBaseType = 'week';
let currentPeriod = '3months';

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 현재 월로 초기화
    const now = new Date();
    const currentMonth = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0');
    document.getElementById('selectedMonth').value = currentMonth;
    
    loadCurrentStatus();
    setupFilters();
});

// 필터 설정
function setupFilters() {
    document.getElementById('companyFilter').addEventListener('change', loadCurrentStatus);
    document.getElementById('staffTypeFilter').addEventListener('change', loadCurrentStatus);
}

// 현재 현황 로드
async function loadCurrentStatus() {
    const company = document.getElementById('companyFilter').value;
    const staffType = document.getElementById('staffTypeFilter').value;
    const selectedMonth = document.getElementById('selectedMonth').value;
    
    let url = `${API_BASE}/current/?`;
    if (selectedMonth) url += `month=${selectedMonth}&`;
    if (company) url += `company=${encodeURIComponent(company)}&`;
    if (staffType) url += `staff_type=${staffType}`;
    
    try {
        console.log('Fetching data from:', url); // 디버깅용
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Received data:', data); // 디버깅용
        
        // 요약 정보 업데이트
        updateSummary(data.summary);
        
        // 테이블 업데이트
        updateCurrentTable(data.data);
        
    } catch (error) {
        console.error('Error loading current status:', error);
        // 에러 메시지를 테이블에 표시
        const tbody = document.getElementById('currentTableBody');
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-red-500">데이터 로드 중 오류가 발생했습니다: ${error.message}</td></tr>`;
    }
}

// 외부에서 호출 가능하도록 전역 함수로 설정
window.loadOutsourcedData = loadCurrentStatus;

// 요약 정보 업데이트
function updateSummary(summary) {
    document.getElementById('totalCount').textContent = summary.total_headcount || 0;
    document.getElementById('residentCount').textContent = summary.total_resident || 0;
    document.getElementById('nonResidentCount').textContent = summary.total_non_resident || 0;
    document.getElementById('projectCount').textContent = summary.total_project || 0;
}

// 전주 대비 증감 로드
async function loadWeekChange() {
    try {
        const response = await fetch(`${API_BASE}/diff/?base_type=week`);
        const data = await response.json();
        
        const totalChange = (data.summary.total_increase || 0) + (data.summary.total_decrease || 0);
        const weekChangeEl = document.getElementById('weekChange');
        const iconEl = document.getElementById('weekChangeIcon');
        
        weekChangeEl.textContent = totalChange > 0 ? `+${totalChange}` : totalChange.toString();
        
        if (totalChange > 0) {
            weekChangeEl.classList.add('text-danger');
            iconEl.innerHTML = '<i class="fas fa-arrow-up fa-2x text-danger opacity-50"></i>';
        } else if (totalChange < 0) {
            weekChangeEl.classList.add('text-success');
            iconEl.innerHTML = '<i class="fas fa-arrow-down fa-2x text-success opacity-50"></i>';
        } else {
            iconEl.innerHTML = '<i class="fas fa-equals fa-2x text-muted opacity-50"></i>';
        }
        
    } catch (error) {
        console.error('Error loading week change:', error);
    }
}

// 현재 현황 테이블 업데이트
function updateCurrentTable(data) {
    console.log('updateCurrentTable called with data:', data); // 디버깅용
    const tbody = document.getElementById('currentTableBody');
    tbody.innerHTML = '';
    
    if (!data || data.length === 0) {
        console.log('No data to display');
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-gray-500">데이터가 없습니다.</td></tr>';
        return;
    }
    
    data.forEach(item => {
        const row = tbody.insertRow();
        row.className = 'hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors';
        
        // 회사별 색상 클래스
        let companyClass = '';
        if (item.company_name.includes('홀딩스')) companyClass = 'company-ok-holdings';
        else if (item.company_name.includes('저축은행')) companyClass = 'company-ok-savings';
        else if (item.company_name.includes('캐피탈')) companyClass = 'company-ok-capital';
        else if (item.company_name.includes('투자증권')) companyClass = 'company-ok-securities';
        else if (item.company_name.includes('신용정보')) companyClass = 'company-ok-credit';
        else if (item.company_name.includes('데이터')) companyClass = 'company-ok-data';
        
        row.className += ' ' + companyClass;
        
        // 구분에 따른 배지 클래스와 텍스트
        let badgeClass = '';
        let badgeText = '';
        if (item.staff_type === 'resident') {
            badgeClass = 'resident-badge';
            badgeText = '상주';
        } else if (item.staff_type === 'non_resident') {
            badgeClass = 'non-resident-badge';
            badgeText = '비상주';
        } else if (item.staff_type === 'project') {
            badgeClass = 'project-badge';
            badgeText = '프로젝트';
        }
        
        // 전월 대비 변화량
        const monthChange = item.month_change || 0;
        const monthChangeClass = monthChange > 0 ? 'text-red-600 font-semibold' : monthChange < 0 ? 'text-green-600 font-semibold' : 'text-gray-400';
        const monthChangeIcon = monthChange > 0 ? '↑' : monthChange < 0 ? '↓' : '';
        const monthChangeDisplay = monthChange !== 0 ? `${monthChangeIcon} ${Math.abs(monthChange)}` : '-';
        
        // 전년말 대비 변화량
        const yearEndChange = item.year_end_change || 0;
        const yearEndChangeClass = yearEndChange > 0 ? 'text-red-600 font-semibold' : yearEndChange < 0 ? 'text-green-600 font-semibold' : 'text-gray-400';
        const yearEndChangeIcon = yearEndChange > 0 ? '↑' : yearEndChange < 0 ? '↓' : '';
        const yearEndChangeDisplay = yearEndChange !== 0 ? `${yearEndChangeIcon} ${Math.abs(yearEndChange)}` : '-';
        
        // 날짜 포맷
        const reportDate = item.report_date ? new Date(item.report_date).toLocaleDateString('ko-KR') : '-';
        
        row.innerHTML = `
            <td class="table-row-spacing font-medium text-gray-900 dark:text-gray-100">
                ${item.company_name}
            </td>
            <td class="table-row-spacing text-gray-700 dark:text-gray-300">
                ${item.project_name || '-'}
            </td>
            <td class="table-row-spacing text-center">
                <span class="${badgeClass}">
                    ${badgeText}
                </span>
            </td>
            <td class="table-row-spacing text-center font-semibold text-gray-900 dark:text-gray-100">
                ${item.headcount}명
            </td>
            <td class="table-row-spacing text-center ${monthChangeClass}">
                ${monthChangeDisplay}
            </td>
            <td class="table-row-spacing text-center ${yearEndChangeClass}">
                ${yearEndChangeDisplay}
            </td>
            <td class="table-row-spacing text-center text-gray-500 dark:text-gray-400 text-xs">
                ${reportDate}
            </td>
        `;
    });
    
    // Lucide 아이콘 초기화
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// 추이 데이터 로드
async function loadTrendData(period) {
    currentPeriod = period;
    const company = document.getElementById('companyFilter').value;
    
    let url = `${API_BASE}/trend/?period=${period}`;
    if (company) url += `&company=${encodeURIComponent(company)}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        updateTrendChart(data);
        
    } catch (error) {
        console.error('Error loading trend data:', error);
    }
}

// 추이 차트 업데이트
function updateTrendChart(data) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (trendChart) {
        trendChart.destroy();
    }
    
    const labels = data.total.map(item => item.date);
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '전체',
                data: data.total.map(item => item.count),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.3
            }, {
                label: '상주',
                data: data.resident.map(item => item.count),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.3
            }, {
                label: '비상주',
                data: data.non_resident.map(item => item.count),
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.3
            }, {
                label: '프로젝트',
                data: data.project.map(item => item.count),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// 증감 비교 데이터 로드
async function loadComparisonData(baseType) {
    currentBaseType = baseType;
    const company = document.getElementById('companyFilter').value;
    
    let url = `${API_BASE}/diff/?base_type=${baseType}`;
    if (company) url += `&company=${encodeURIComponent(company)}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        updateComparisonLists(data.details);
        
    } catch (error) {
        console.error('Error loading comparison data:', error);
    }
}

// 증감 비교 리스트 업데이트
function updateComparisonLists(details) {
    const increaseList = document.getElementById('increaseList');
    const decreaseList = document.getElementById('decreaseList');
    
    increaseList.innerHTML = '';
    decreaseList.innerHTML = '';
    
    details.forEach(item => {
        const listItem = document.createElement('div');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        if (item.change > 0) {
            listItem.innerHTML = `
                <div>
                    <h6 class="mb-0">${item.company_name} - ${item.project_name}</h6>
                    <small class="text-muted">${item.previous} → ${item.current}</small>
                </div>
                <span class="badge bg-danger rounded-pill">+${item.change} (${item.change_rate.toFixed(1)}%)</span>
            `;
            increaseList.appendChild(listItem);
        } else if (item.change < 0) {
            listItem.innerHTML = `
                <div>
                    <h6 class="mb-0">${item.company_name} - ${item.project_name}</h6>
                    <small class="text-muted">${item.previous} → ${item.current}</small>
                </div>
                <span class="badge bg-success rounded-pill">${item.change} (${item.change_rate.toFixed(1)}%)</span>
            `;
            decreaseList.appendChild(listItem);
        }
    });
}

// 파일 업로드 모달 표시
function showUploadModal() {
    const modalElement = document.getElementById('uploadModal');
    
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        // Bootstrap 5 방식
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    } else if (typeof $ !== 'undefined') {
        // jQuery/Bootstrap 4 방식
        $('#uploadModal').modal('show');
    } else {
        // 대체 방법: 직접 표시
        modalElement.classList.add('show');
        modalElement.style.display = 'block';
        document.body.classList.add('modal-open');
        
        // 배경 추가
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        document.body.appendChild(backdrop);
    }
}

// 파일 업로드
async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('파일을 선택해주세요.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Upload failed:', response.status, errorText);
            throw new Error(`업로드 실패: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            // 모달 닫기
            const modalElement = document.getElementById('uploadModal');
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                // Bootstrap 5 방식
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
            } else if (typeof $ !== 'undefined') {
                // jQuery/Bootstrap 4 방식
                $('#uploadModal').modal('hide');
            } else {
                // 대체 방법: 모달 배경과 display 직접 제어
                modalElement.classList.remove('show');
                modalElement.style.display = 'none';
                document.body.classList.remove('modal-open');
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
            }
            // 파일 입력 초기화
            document.getElementById('fileInput').value = '';
            loadCurrentStatus();
        } else {
            alert(data.error || '업로드 중 오류가 발생했습니다.');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        alert('파일 업로드 중 오류가 발생했습니다.');
    }
}

// 추이 차트 기간 변경
function updateTrendChart(period) {
    document.querySelectorAll('#trend .btn-group button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    loadTrendData(period);
}

// 증감 비교 기준 변경
function updateComparisonChart(baseType) {
    document.querySelectorAll('#comparison .btn-group button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    loadComparisonData(baseType);
}

// 유틸리티 함수들
function getChangeClass(change) {
    if (change > 0) return 'status-increase';
    if (change < 0) return 'status-decrease';
    return 'status-maintain';
}

function formatChange(change) {
    if (change > 0) return `+${change}`;
    if (change < 0) return `${change}`;
    return '0';
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

// 인력 구분 배지 클래스
function getStaffTypeBadgeClass(staffType) {
    switch(staffType) {
        case 'resident':
            return 'resident-badge';
        case 'non_resident':
            return 'non-resident-badge';
        case 'project':
            return 'project-badge';
        default:
            return 'badge bg-secondary';
    }
}

// 인력 구분 라벨
function getStaffTypeLabel(staffType) {
    switch(staffType) {
        case 'resident':
            return '상주';
        case 'non_resident':
            return '비상주';
        case 'project':
            return '프로젝트';
        default:
            return '미분류';
    }
}