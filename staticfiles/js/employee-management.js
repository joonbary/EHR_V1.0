// 직원 관리 JavaScript 모듈

// 전역 변수
let currentEmployees = [];
let currentPage = 1;
let totalPages = 1;
let isGridView = true;
let currentFilters = {};
let editingEmployeeId = null;

// DOM이 로드되면 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DOM Content Loaded ===');
    console.log('Current URL:', window.location.href);
    console.log('Document ready state:', document.readyState);
    initializeEmployeeManagement();
});

// 초기화 함수
function initializeEmployeeManagement() {
    console.log('=== Initializing employee management ===');
    console.log('isGridView:', isGridView);
    console.log('Checking required elements...');
    
    // 필수 DOM 요소 확인
    const requiredElements = [
        'viewToggle', 'searchInput', 'departmentFilter', 'positionFilter', 
        'statusFilter', 'clearFiltersBtn', 'refreshBtn', 'addEmployeeBtn',
        'loadingState', 'employeeGrid', 'employeeTable', 'emptyState'
    ];
    
    for (const id of requiredElements) {
        const element = document.getElementById(id);
        if (!element) {
            console.error(`Required element missing: ${id}`);
            return;
        }
        console.log(`✓ Found element: ${id}`);
    }
    
    // Lucide 아이콘 초기화
    if (typeof lucide !== 'undefined') {
        console.log('✓ Lucide library found, initializing icons');
        lucide.createIcons();
    } else {
        console.warn('⚠ Lucide library not found');
    }
    
    // 초기 뷰 상태 설정
    const viewToggleBtn = document.getElementById('viewToggle');
    if (!viewToggleBtn) {
        console.error('viewToggle button not found during initialization');
        return;
    }
    
    let icon = viewToggleBtn.querySelector('i');
    if (!icon) {
        console.warn('Icon not found in viewToggle button, creating new icon element');
        icon = document.createElement('i');
        viewToggleBtn.appendChild(icon);
    }
    
    if (isGridView) {
        icon.setAttribute('data-lucide', 'grid');
        viewToggleBtn.title = '테이블 보기로 변경';
        console.log('Initialized with grid view');
    } else {
        icon.setAttribute('data-lucide', 'list');
        viewToggleBtn.title = '카드 보기로 변경';
        console.log('Initialized with table view');
    }
    
    // 아이콘 재생성
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // 이벤트 리스너 등록
    console.log('=== Setting up event listeners ===');
    setupEventListeners();
    
    // 초기 뷰 상태 설정 (HTML에서 둘 다 hidden이므로 올바른 뷰를 표시)
    const grid = document.getElementById('employeeGrid');
    const table = document.getElementById('employeeTable');
    
    if (grid && table) {
        if (isGridView) {
            grid.classList.remove('hidden');
            table.classList.add('hidden');
            console.log('Initial view set to grid');
        } else {
            grid.classList.add('hidden');
            table.classList.remove('hidden');
            console.log('Initial view set to table');
        }
    }
    
    // 초기 데이터 로드
    console.log('=== Starting initial data load ===');
    loadEmployees();
}

// 이벤트 리스너 설정
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // 검색 및 필터 - 안전한 처리
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
        console.log('✓ Search input listener added');
    }
    
    const departmentFilter = document.getElementById('departmentFilter');
    if (departmentFilter) {
        departmentFilter.addEventListener('change', handleFilter);
        console.log('✓ Department filter listener added');
    }
    
    const positionFilter = document.getElementById('positionFilter');
    if (positionFilter) {
        positionFilter.addEventListener('change', handleFilter);
        console.log('✓ Position filter listener added');
    }
    
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', handleFilter);
        console.log('✓ Status filter listener added');
    }
    
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearFilters);
        console.log('✓ Clear filters button listener added');
    }
    
    // 버튼 이벤트 - 안전한 처리
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadEmployees);
        console.log('✓ Refresh button listener added');
    }
    
    const addEmployeeBtn = document.getElementById('addEmployeeBtn');
    if (addEmployeeBtn) {
        addEmployeeBtn.addEventListener('click', openAddEmployeeModal);
        console.log('✓ Add employee button listener added');
    }
    
    const addFirstEmployeeBtn = document.getElementById('addFirstEmployeeBtn');
    if (addFirstEmployeeBtn) {
        addFirstEmployeeBtn.addEventListener('click', openAddEmployeeModal);
        console.log('✓ Add first employee button listener added');
    }
    
    const viewToggle = document.getElementById('viewToggle');
    if (viewToggle) {
        viewToggle.addEventListener('click', toggleView);
        console.log('✓ View toggle button listener added');
    }
    
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportEmployees);
        console.log('✓ Export button listener added');
    }
    
    // 모달 이벤트 - 안전한 처리
    const closeDetailModalBtn = document.getElementById('closeDetailModal');
    if (closeDetailModalBtn) {
        closeDetailModalBtn.addEventListener('click', closeDetailModal);
        console.log('✓ Close detail modal listener added');
    }
    
    const closeFormModalBtn = document.getElementById('closeFormModal');
    if (closeFormModalBtn) {
        closeFormModalBtn.addEventListener('click', closeFormModal);
        console.log('✓ Close form modal listener added');
    }
    
    const cancelFormBtn = document.getElementById('cancelFormBtn');
    if (cancelFormBtn) {
        cancelFormBtn.addEventListener('click', closeFormModal);
        console.log('✓ Cancel form button listener added');
    }
    
    const employeeForm = document.getElementById('employeeForm');
    if (employeeForm) {
        employeeForm.addEventListener('submit', handleFormSubmit);
        console.log('✓ Employee form submit listener added');
    }
    
    // 모달 외부 클릭 시 닫기
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModals();
        }
    });
    
    // ESC 키로 모달 닫기
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModals();
        }
    });
}

// 직원 목록 로드
async function loadEmployees() {
    console.log('=== loadEmployees 함수 시작 ===');
    showLoading();
    
    try {
        const params = new URLSearchParams({
            page: currentPage,
            ...currentFilters
        });
        
        // 10초 타임아웃 설정
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);
        
        const url = `/employees/api/employees/?${params}`;
        console.log('API 요청 URL:', url);
        
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json'
            },
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        console.log('API 응답 상태:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || '직원 목록을 불러오는데 실패했습니다.');
        }
        
        const data = await response.json();
        console.log('API 응답 데이터:', data);
        
        currentEmployees = data.results || data;
        console.log('파싱된 직원 수:', currentEmployees.length);
        
        // 페이지네이션 정보 업데이트
        if (data.count !== undefined) {
            totalPages = Math.ceil(data.count / 20);
            updateResultCount(data.count);
            console.log('총 직원 수:', data.count, '총 페이지:', totalPages);
        } else {
            updateResultCount(currentEmployees.length);
        }
        
        renderEmployees();
        renderPagination();
        hideLoading();
        console.log('=== loadEmployees 함수 완료 ===');
        
    } catch (error) {
        console.error('=== API 호출 실패 ===');
        console.error('Error type:', error.name);
        console.error('Error message:', error.message);
        console.error('Full error:', error);
        
        if (error.name === 'AbortError') {
            showError('요청 시간이 초과되었습니다. 네트워크 연결을 확인해주세요.');
        } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
            console.error('네트워크 연결 문제 또는 CORS 오류일 수 있습니다');
            showError('네트워크 연결을 확인해주세요. 서버가 실행 중인지 확인하세요.');
        } else {
            showError(error.message || '직원 목록을 불러오는데 실패했습니다.');
        }
        
        hideLoading();
        
        // 디버깅용 임시 데이터로 테스트
        console.log('=== 디버깅: 임시 데이터 사용 ===');
        currentEmployees = [{
            id: 1,
            name: "테스트 직원",
            email: "test@example.com",
            department: "IT",
            new_position: "사원",
            job_type: "IT개발",
            growth_level: 1,
            employment_status: "재직",
            hire_date: "2024-01-01"
        }];
        
        renderEmployees();
        updateResultCount(1);
    }
}

// 직원 목록 렌더링
function renderEmployees() {
    console.log('Rendering employees:', currentEmployees.length, 'items, gridView:', isGridView);
    
    if (currentEmployees.length === 0) {
        showEmptyState();
        return;
    }
    
    hideEmptyState();
    
    if (isGridView) {
        console.log('Rendering grid view');
        renderEmployeeGrid();
    } else {
        console.log('Rendering table view');
        renderEmployeeTable();
    }
}

// 직원 카드 그리드 렌더링
function renderEmployeeGrid() {
    const grid = document.getElementById('employeeGrid');
    const table = document.getElementById('employeeTable');
    
    console.log('renderEmployeeGrid - showing grid, hiding table');
    grid.classList.remove('hidden');
    table.classList.add('hidden');
    
    grid.innerHTML = currentEmployees.map(employee => `
        <div class="employee-card glass dark:glass-dark rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-sm" 
             onclick="openEmployeeDetail(${employee.id})"
             data-employee-id="${employee.id}">
            <div class="flex items-start justify-between mb-4">
                <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-xl flex items-center justify-center text-white font-bold text-lg">
                        ${employee.name.charAt(0)}
                    </div>
                    <div>
                        <h3 class="font-semibold text-gray-900 dark:text-white">${employee.name}</h3>
                        <p class="text-sm text-gray-500 dark:text-gray-400">${employee.email}</p>
                    </div>
                </div>
                <span class="status-badge ${getStatusClass(employee.employment_status)}">
                    ${employee.employment_status}
                </span>
            </div>
            
            <div class="space-y-2 mb-4">
                <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <i data-lucide="building" class="w-4 h-4 mr-2"></i>
                    ${employee.department}
                </div>
                <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <i data-lucide="user" class="w-4 h-4 mr-2"></i>
                    ${employee.new_position} (Level ${employee.growth_level})
                </div>
                <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <i data-lucide="briefcase" class="w-4 h-4 mr-2"></i>
                    ${employee.job_type}
                </div>
            </div>
            
            <div class="flex items-center justify-between pt-4 border-t border-gray-200/30 dark:border-gray-700/30">
                <div class="text-xs text-gray-500 dark:text-gray-400">
                    입사일: ${formatDate(employee.hire_date)}
                </div>
                <div class="flex items-center space-x-2">
                    <button onclick="event.stopPropagation(); editEmployee(${employee.id})" 
                            class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="수정">
                        <i data-lucide="edit" class="w-4 h-4"></i>
                    </button>
                    <button onclick="event.stopPropagation(); deleteEmployee(${employee.id})" 
                            class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="퇴사처리">
                        <i data-lucide="user-x" class="w-4 h-4"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    // 아이콘 다시 초기화 (그리드 영역만)
    if (typeof lucide !== 'undefined') {
        try {
            lucide.createIcons({
                nameAttr: 'data-lucide'
            });
            console.log('✓ Grid icons initialized');
        } catch (error) {
            console.warn('Lucide grid icon initialization failed:', error);
        }
    }
}

// 직원 테이블 렌더링
function renderEmployeeTable() {
    const grid = document.getElementById('employeeGrid');
    const table = document.getElementById('employeeTable');
    const tbody = document.getElementById('employeeTableBody');
    
    console.log('renderEmployeeTable - hiding grid, showing table');
    grid.classList.add('hidden');
    table.classList.remove('hidden');
    
    tbody.innerHTML = currentEmployees.map(employee => `
        <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer" 
            onclick="openEmployeeDetail(${employee.id})"
            data-employee-id="${employee.id}">
            <td class="px-6 py-4">
                <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center text-white font-bold text-sm">
                        ${employee.name.charAt(0)}
                    </div>
                    <div>
                        <div class="font-medium text-gray-900 dark:text-white">${employee.name}</div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">${employee.email}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">${employee.department}</td>
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">${employee.new_position}</td>
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">${employee.job_type}</td>
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">Level ${employee.growth_level}</td>
            <td class="px-6 py-4">
                <span class="status-badge ${getStatusClass(employee.employment_status)}">
                    ${employee.employment_status}
                </span>
            </td>
            <td class="px-6 py-4">
                <div class="flex items-center space-x-2">
                    <button onclick="event.stopPropagation(); editEmployee(${employee.id})" 
                            class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="수정">
                        <i data-lucide="edit" class="w-4 h-4"></i>
                    </button>
                    <button onclick="event.stopPropagation(); deleteEmployee(${employee.id})" 
                            class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="퇴사처리">
                        <i data-lucide="user-x" class="w-4 h-4"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    // 아이콘 다시 초기화 (테이블 영역만)
    if (typeof lucide !== 'undefined') {
        try {
            lucide.createIcons({
                nameAttr: 'data-lucide'
            });
            console.log('✓ Table icons initialized');
        } catch (error) {
            console.warn('Lucide table icon initialization failed:', error);
        }
    }
}

// 유틸리티 함수들
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}


function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR');
}

function getStatusClass(status) {
    switch(status) {
        case '재직': return 'status-active';
        case '퇴직': return 'status-inactive';
        case '휴직': case '파견': return 'status-leave';
        default: return 'status-active';
    }
}

// 검색 및 필터 함수들
function handleSearch() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    if (searchTerm) {
        currentFilters.search = searchTerm;
    } else {
        delete currentFilters.search;
    }
    currentPage = 1;
    updateActiveFilters();
    loadEmployees();
}

function handleFilter() {
    const department = document.getElementById('departmentFilter').value;
    const position = document.getElementById('positionFilter').value;
    const status = document.getElementById('statusFilter').value;
    
    // 필터 값 설정
    if (department) currentFilters.department = department;
    else delete currentFilters.department;
    
    if (position) currentFilters.new_position = position;
    else delete currentFilters.new_position;
    
    if (status) currentFilters.employment_status = status;
    else delete currentFilters.employment_status;
    
    currentPage = 1;
    updateActiveFilters();
    loadEmployees();
}

function clearFilters() {
    currentFilters = {};
    currentPage = 1;
    
    // 필터 UI 초기화
    document.getElementById('searchInput').value = '';
    document.getElementById('departmentFilter').value = '';
    document.getElementById('positionFilter').value = '';
    document.getElementById('statusFilter').value = '';
    
    updateActiveFilters();
    loadEmployees();
}

function updateActiveFilters() {
    const container = document.getElementById('activeFilters');
    const filters = [];
    
    if (currentFilters.search) {
        filters.push({ key: 'search', label: `검색: "${currentFilters.search}"`, value: currentFilters.search });
    }
    if (currentFilters.department) {
        filters.push({ key: 'department', label: `부서: ${currentFilters.department}`, value: currentFilters.department });
    }
    if (currentFilters.new_position) {
        filters.push({ key: 'new_position', label: `직급: ${currentFilters.new_position}`, value: currentFilters.new_position });
    }
    if (currentFilters.employment_status) {
        filters.push({ key: 'employment_status', label: `상태: ${currentFilters.employment_status}`, value: currentFilters.employment_status });
    }
    
    if (filters.length > 0) {
        container.innerHTML = `
            <div class="flex items-center mb-2">
                <span class="text-sm text-gray-600 dark:text-gray-400 mr-2">활성 필터:</span>
                ${filters.map(filter => `
                    <div class="filter-tag">
                        ${filter.label}
                        <button onclick="removeFilter('${filter.key}')" aria-label="필터 제거">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        container.innerHTML = '';
    }
}

function removeFilter(key) {
    delete currentFilters[key];
    
    // UI 업데이트
    switch(key) {
        case 'search':
            document.getElementById('searchInput').value = '';
            break;
        case 'department':
            document.getElementById('departmentFilter').value = '';
            break;
        case 'new_position':
            document.getElementById('positionFilter').value = '';
            break;
        case 'employment_status':
            document.getElementById('statusFilter').value = '';
            break;
    }
    
    currentPage = 1;
    updateActiveFilters();
    loadEmployees();
}

// UI 상태 관리 함수들
function showLoading() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('employeeGrid').classList.add('hidden');
    document.getElementById('employeeTable').classList.add('hidden');
    document.getElementById('emptyState').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loadingState').classList.add('hidden');
}

function showEmptyState() {
    document.getElementById('emptyState').classList.remove('hidden');
    document.getElementById('employeeGrid').classList.add('hidden');
    document.getElementById('employeeTable').classList.add('hidden');
}

function hideEmptyState() {
    document.getElementById('emptyState').classList.add('hidden');
}

function updateResultCount(count) {
    document.getElementById('resultCount').textContent = `${count}명`;
}

// 페이지네이션 렌더링
function renderPagination() {
    const container = document.getElementById('pagination');
    if (!container) return;
    
    if (totalPages <= 1) {
        container.classList.add('hidden');
        return;
    }
    
    container.classList.remove('hidden');
    
    let paginationHTML = '';
    
    // 이전 페이지 버튼
    if (currentPage > 1) {
        paginationHTML += `
            <button onclick="goToPage(${currentPage - 1})" 
                    class="px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700">
                이전
            </button>
        `;
    }
    
    // 페이지 번호들
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const isCurrentPage = i === currentPage;
        paginationHTML += `
            <button onclick="goToPage(${i})" 
                    class="px-3 py-2 text-sm ${isCurrentPage 
                        ? 'bg-primary text-white' 
                        : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    } border border-gray-300 dark:border-gray-600 rounded-lg">
                ${i}
            </button>
        `;
    }
    
    // 다음 페이지 버튼
    if (currentPage < totalPages) {
        paginationHTML += `
            <button onclick="goToPage(${currentPage + 1})" 
                    class="px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700">
                다음
            </button>
        `;
    }
    
    container.innerHTML = paginationHTML;
    console.log(`✓ Pagination rendered: page ${currentPage}/${totalPages}`);
}

// 페이지 이동
function goToPage(page) {
    if (page < 1 || page > totalPages || page === currentPage) return;
    
    console.log(`Going to page ${page}`);
    currentPage = page;
    loadEmployees();
}

// 뷰 토글 함수
function toggleView() {
    console.log('Toggle view clicked, current isGridView:', isGridView);
    isGridView = !isGridView;
    console.log('New isGridView:', isGridView);
    
    const button = document.getElementById('viewToggle');
    if (!button) {
        console.error('viewToggle button not found');
        return;
    }
    
    let icon = button.querySelector('i');
    if (!icon) {
        console.warn('Icon element not found in viewToggle button, creating new one');
        icon = document.createElement('i');
        icon.className = 'w-5 h-5';
        button.appendChild(icon);
    }
    
    if (isGridView) {
        icon.setAttribute('data-lucide', 'grid');
        button.title = '테이블 보기로 변경';
        console.log('Switched to grid view');
    } else {
        icon.setAttribute('data-lucide', 'list');
        button.title = '카드 보기로 변경';
        console.log('Switched to table view');
    }
    
    // 아이콘 재생성
    if (typeof lucide !== 'undefined') {
        try {
            lucide.createIcons({
                nameAttr: 'data-lucide'
            });
            console.log('✓ Toggle button icon updated');
        } catch (error) {
            console.warn('Lucide toggle icon update failed:', error);
        }
    }
    
    // 뷰 렌더링 - 직원 데이터가 있을 때만
    if (currentEmployees && currentEmployees.length > 0) {
        renderEmployees();
    } else {
        console.log('No employee data to render');
        // 데이터가 없어도 뷰 전환 상태만 표시
        const grid = document.getElementById('employeeGrid');
        const table = document.getElementById('employeeTable');
        
        if (grid && table) {
            if (isGridView) {
                grid.classList.remove('hidden');
                table.classList.add('hidden');
            } else {
                grid.classList.add('hidden');
                table.classList.remove('hidden');
            }
        }
    }
}

// 모달 관리 함수들
function openEmployeeDetail(employeeId) {
    loadEmployeeDetail(employeeId);
}

async function loadEmployeeDetail(employeeId) {
    try {
        const response = await fetch(`/employees/api/employees/${employeeId}/`, {
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('직원 정보를 불러오는데 실패했습니다.');
        }
        
        const employee = await response.json();
        renderEmployeeDetail(employee);
        
        const modal = document.getElementById('employeeDetailModal');
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
        
    } catch (error) {
        console.error('Error loading employee detail:', error);
        showError('직원 정보를 불러오는데 실패했습니다.');
    }
}

function renderEmployeeDetail(employee) {
    const content = document.getElementById('employeeDetailContent');
    content.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- 기본 정보 -->
            <div class="space-y-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">
                    기본 정보
                </h3>
                
                <div class="space-y-4">
                    <div class="flex items-center space-x-4">
                        <div class="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center text-white font-bold text-2xl">
                            ${employee.name.charAt(0)}
                        </div>
                        <div>
                            <h4 class="text-xl font-bold text-gray-900 dark:text-white">${employee.name}</h4>
                            <p class="text-gray-600 dark:text-gray-400">${employee.email}</p>
                            <span class="status-badge ${getStatusClass(employee.employment_status)} mt-1">
                                ${employee.employment_status}
                            </span>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">부서</label>
                            <p class="mt-1 text-gray-900 dark:text-white">${employee.department}</p>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">직급</label>
                            <p class="mt-1 text-gray-900 dark:text-white">${employee.new_position}</p>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">성장레벨</label>
                            <p class="mt-1 text-gray-900 dark:text-white">Level ${employee.growth_level}</p>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">급호</label>
                            <p class="mt-1 text-gray-900 dark:text-white">${employee.grade_level}호</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 직무 정보 -->
            <div class="space-y-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">
                    직무 정보
                </h3>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">직군</label>
                        <p class="mt-1 text-gray-900 dark:text-white">${employee.job_group}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">직종</label>
                        <p class="mt-1 text-gray-900 dark:text-white">${employee.job_type}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">구체적 직무</label>
                        <p class="mt-1 text-gray-900 dark:text-white">${employee.job_role || '-'}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">고용형태</label>
                        <p class="mt-1 text-gray-900 dark:text-white">${employee.employment_type}</p>
                    </div>
                </div>
            </div>
            
            <!-- 연락처 정보 -->
            <div class="space-y-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">
                    연락처 정보
                </h3>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">전화번호</label>
                        <p class="mt-1 text-gray-900 dark:text-white">${employee.phone || '-'}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">주소</label>
                        <p class="mt-1 text-gray-900 dark:text-white">${employee.address || '-'}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">비상연락처</label>
                        <p class="mt-1 text-gray-900 dark:text-white">
                            ${employee.emergency_contact || '-'} 
                            ${employee.emergency_phone ? `(${employee.emergency_phone})` : ''}
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- 근무 정보 -->
            <div class="space-y-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">
                    근무 정보
                </h3>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">입사일</label>
                        <p class="mt-1 text-gray-900 dark:text-white">${formatDate(employee.hire_date)}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">직속상사</label>
                        <p class="mt-1 text-gray-900 dark:text-white">
                            ${employee.manager ? employee.manager.name : '없음'}
                        </p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">부하직원</label>
                        <p class="mt-1 text-gray-900 dark:text-white">
                            ${employee.subordinates && employee.subordinates.length > 0 
                                ? `${employee.subordinates.length}명` 
                                : '없음'}
                        </p>
                    </div>
                </div>
            </div>
        </div>
        
        ${employee.subordinates && employee.subordinates.length > 0 ? `
            <div class="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">부하직원 목록</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    ${employee.subordinates.map(sub => `
                        <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <div class="flex items-center space-x-3">
                                <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                                    ${sub.name.charAt(0)}
                                </div>
                                <div>
                                    <p class="font-medium text-gray-900 dark:text-white">${sub.name}</p>
                                    <p class="text-sm text-gray-500 dark:text-gray-400">${sub.new_position}</p>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
    
    // 수정 버튼 이벤트 업데이트
    document.getElementById('editEmployeeBtn').onclick = () => editEmployee(employee.id);
}

function closeDetailModal() {
    const modal = document.getElementById('employeeDetailModal');
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
}

function closeFormModal() {
    const modal = document.getElementById('employeeFormModal');
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
    editingEmployeeId = null;
    document.getElementById('employeeForm').reset();
}

function closeModals() {
    closeDetailModal();
    closeFormModal();
}

// 직원 등록/수정 함수들
function openAddEmployeeModal() {
    editingEmployeeId = null;
    document.getElementById('employeeFormTitle').textContent = '새 직원 등록';
    document.querySelector('#submitFormBtn .btn-text').textContent = '등록';
    
    renderEmployeeForm();
    
    const modal = document.getElementById('employeeFormModal');
    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
}

async function editEmployee(employeeId) {
    editingEmployeeId = employeeId;
    document.getElementById('employeeFormTitle').textContent = '직원 정보 수정';
    document.querySelector('#submitFormBtn .btn-text').textContent = '수정';
    
    try {
        const response = await fetch(`/employees/api/employees/${employeeId}/`, {
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('직원 정보를 불러오는데 실패했습니다.');
        }
        
        const employee = await response.json();
        renderEmployeeForm(employee);
        
        // 상세 모달 닫기
        closeDetailModal();
        
        const modal = document.getElementById('employeeFormModal');
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
        
    } catch (error) {
        console.error('Error loading employee for edit:', error);
        showError('직원 정보를 불러오는데 실패했습니다.');
    }
}

function renderEmployeeForm(employee = null) {
    const content = document.getElementById('employeeFormContent');
    content.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 기본 정보 -->
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">이름 *</label>
                <input type="text" name="name" required 
                       value="${employee?.name || ''}"
                       class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">이메일 *</label>
                <input type="email" name="email" required 
                       value="${employee?.email || ''}"
                       class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">부서 *</label>
                <select name="department" required 
                        class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
                    <option value="">부서 선택</option>
                    <option value="IT" ${employee?.department === 'IT' ? 'selected' : ''}>IT</option>
                    <option value="HR" ${employee?.department === 'HR' ? 'selected' : ''}>인사</option>
                    <option value="FINANCE" ${employee?.department === 'FINANCE' ? 'selected' : ''}>재무</option>
                    <option value="MARKETING" ${employee?.department === 'MARKETING' ? 'selected' : ''}>마케팅</option>
                    <option value="SALES" ${employee?.department === 'SALES' ? 'selected' : ''}>영업</option>
                    <option value="OPERATIONS" ${employee?.department === 'OPERATIONS' ? 'selected' : ''}>운영</option>
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">직급 *</label>
                <select name="new_position" required 
                        class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
                    <option value="">직급 선택</option>
                    <option value="사원" ${employee?.new_position === '사원' ? 'selected' : ''}>사원</option>
                    <option value="선임" ${employee?.new_position === '선임' ? 'selected' : ''}>선임</option>
                    <option value="주임" ${employee?.new_position === '주임' ? 'selected' : ''}>주임</option>
                    <option value="대리" ${employee?.new_position === '대리' ? 'selected' : ''}>대리</option>
                    <option value="과장" ${employee?.new_position === '과장' ? 'selected' : ''}>과장</option>
                    <option value="차장" ${employee?.new_position === '차장' ? 'selected' : ''}>차장</option>
                    <option value="부장" ${employee?.new_position === '부장' ? 'selected' : ''}>부장</option>
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">직군 *</label>
                <select name="job_group" required 
                        class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
                    <option value="Non-PL" ${employee?.job_group === 'Non-PL' ? 'selected' : ''}>Non-PL직군</option>
                    <option value="PL" ${employee?.job_group === 'PL' ? 'selected' : ''}>PL직군</option>
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">직종 *</label>
                <select name="job_type" required 
                        class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
                    <option value="">직종 선택</option>
                    <option value="고객지원" ${employee?.job_type === '고객지원' ? 'selected' : ''}>고객지원</option>
                    <option value="IT기획" ${employee?.job_type === 'IT기획' ? 'selected' : ''}>IT기획</option>
                    <option value="IT개발" ${employee?.job_type === 'IT개발' ? 'selected' : ''}>IT개발</option>
                    <option value="IT운영" ${employee?.job_type === 'IT운영' ? 'selected' : ''}>IT운영</option>
                    <option value="경영관리" ${employee?.job_type === '경영관리' ? 'selected' : ''}>경영관리</option>
                    <option value="기업영업" ${employee?.job_type === '기업영업' ? 'selected' : ''}>기업영업</option>
                    <option value="기업금융" ${employee?.job_type === '기업금융' ? 'selected' : ''}>기업금융</option>
                    <option value="리테일금융" ${employee?.job_type === '리테일금융' ? 'selected' : ''}>리테일금융</option>
                    <option value="투자금융" ${employee?.job_type === '투자금융' ? 'selected' : ''}>투자금융</option>
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">성장레벨 *</label>
                <select name="growth_level" required 
                        class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
                    <option value="1" ${employee?.growth_level === 1 ? 'selected' : ''}>Level 1</option>
                    <option value="2" ${employee?.growth_level === 2 ? 'selected' : ''}>Level 2</option>
                    <option value="3" ${employee?.growth_level === 3 ? 'selected' : ''}>Level 3</option>
                    <option value="4" ${employee?.growth_level === 4 ? 'selected' : ''}>Level 4</option>
                    <option value="5" ${employee?.growth_level === 5 ? 'selected' : ''}>Level 5</option>
                    <option value="6" ${employee?.growth_level === 6 ? 'selected' : ''}>Level 6</option>
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">급호</label>
                <input type="number" name="grade_level" min="1" 
                       value="${employee?.grade_level || 1}"
                       class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">전화번호</label>
                <input type="tel" name="phone" 
                       value="${employee?.phone || ''}"
                       class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">고용형태</label>
                <select name="employment_type" 
                        class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
                    <option value="정규직" ${employee?.employment_type === '정규직' ? 'selected' : ''}>정규직</option>
                    <option value="계약직" ${employee?.employment_type === '계약직' ? 'selected' : ''}>계약직</option>
                    <option value="파견" ${employee?.employment_type === '파견' ? 'selected' : ''}>파견</option>
                    <option value="인턴" ${employee?.employment_type === '인턴' ? 'selected' : ''}>인턴</option>
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">재직상태</label>
                <select name="employment_status" 
                        class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
                    <option value="재직" ${employee?.employment_status === '재직' ? 'selected' : ''}>재직</option>
                    <option value="휴직" ${employee?.employment_status === '휴직' ? 'selected' : ''}>휴직</option>
                    <option value="파견" ${employee?.employment_status === '파견' ? 'selected' : ''}>파견</option>
                    <option value="퇴직" ${employee?.employment_status === '퇴직' ? 'selected' : ''}>퇴직</option>
                </select>
            </div>
            
            <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">구체적 직무</label>
                <input type="text" name="job_role" 
                       value="${employee?.job_role || ''}"
                       placeholder="예: 수신고객지원, 시스템기획, HRM 등"
                       class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
            </div>
            
            <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">주소</label>
                <textarea name="address" rows="2" 
                          class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">${employee?.address || ''}</textarea>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">비상연락처 이름</label>
                <input type="text" name="emergency_contact" 
                       value="${employee?.emergency_contact || ''}"
                       class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">비상연락처 번호</label>
                <input type="tel" name="emergency_phone" 
                       value="${employee?.emergency_phone || ''}"
                       class="w-full px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-primary focus:outline-none">
            </div>
        </div>
    `;
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitFormBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loading = submitBtn.querySelector('.loading');
    
    // 로딩 상태 설정
    btnText.classList.add('hidden');
    loading.classList.remove('hidden');
    submitBtn.disabled = true;
    
    try {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        // 숫자 필드 변환
        data.growth_level = parseInt(data.growth_level);
        data.grade_level = parseInt(data.grade_level);
        
        const url = editingEmployeeId 
            ? `/employees/api/employees/${editingEmployeeId}/`
            : '/employees/api/employees/';
        
        const method = editingEmployeeId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || '저장에 실패했습니다.');
        }
        
        showSuccess(result.message || '성공적으로 저장되었습니다.');
        closeFormModal();
        loadEmployees();
        
    } catch (error) {
        console.error('Error saving employee:', error);
        showError(error.message || '저장에 실패했습니다.');
    } finally {
        // 로딩 상태 해제
        btnText.classList.remove('hidden');
        loading.classList.add('hidden');
        submitBtn.disabled = false;
    }
}

// 직원 삭제 (퇴사 처리)
async function deleteEmployee(employeeId) {
    if (!confirm('정말로 이 직원을 퇴사 처리하시겠습니까?')) {
        return;
    }
    
    try {
        const response = await fetch(`/employees/api/employees/${employeeId}/retire/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                employment_status: '퇴직'
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || '퇴사 처리에 실패했습니다.');
        }
        
        showSuccess(result.message);
        loadEmployees();
        
    } catch (error) {
        console.error('Error retiring employee:', error);
        showError(error.message || '퇴사 처리에 실패했습니다.');
    }
}

// 직원 데이터 내보내기
async function exportEmployees() {
    try {
        const params = new URLSearchParams(currentFilters);
        const response = await fetch(`/employees/api/employees/?${params}&export=true`, {
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('데이터 내보내기에 실패했습니다.');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `employees_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showSuccess('직원 데이터가 성공적으로 내보내졌습니다.');
        
    } catch (error) {
        console.error('Error exporting employees:', error);
        showError('데이터 내보내기에 실패했습니다.');
    }
}

// 알림 메시지 함수들
function showSuccess(message) {
    // Toast 알림 구현 (간단한 버전)
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function showError(message) {
    // Toast 알림 구현 (간단한 버전)
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}