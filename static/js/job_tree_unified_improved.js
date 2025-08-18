// 전역 변수
let currentView = 'org';
let currentFilter = 'all';
let jobData = {};
let currentJobId = null;

// 직무 데이터 구조 (하드코딩)
const jobStructure = {
    'Non-PL': {
        'IT기획': ['시스템기획'],
        'IT개발': ['시스템개발'],
        'IT운영': ['시스템관리', '서비스운영'],
        '경영관리': [
            '감사', 'HRM', 'HRD', '경영지원', '비서', 'PR', '경영기획',
            '디자인', '리스크관리', '마케팅', '스포츠사무관리', '자금',
            '재무회계', '정보보안', '준법지원', '총무'
        ],
        '투자금융': ['IB금융'],
        '기업금융': ['기업영업기획', '기업여신심사', '기업여신관리'],
        '기업영업': ['여신영업'],
        '리테일금융': [
            '데이터/통계', '플랫폼/핀테크', 'NPL영업기획', '리테일심사기획',
            'PL기획', '모기지기획', '수신기획', '수신영업'
        ]
    },
    'PL': {
        '고객지원': ['여신고객지원', '사무지원', '수신고객지원', '채권관리지원']
    }
};

// 페이지 로드시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadJobData();
    updateStatistics();
});

// 이벤트 리스너 초기화
function initializeEventListeners() {
    // 뷰 탭 전환
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.addEventListener('click', handleViewChange);
    });
    
    // 필터 칩
    document.querySelectorAll('.filter-chips .chip').forEach(chip => {
        chip.addEventListener('click', handleFilter);
    });
    
    // 검색 기능
    const searchInput = document.getElementById('jobSearch');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
    
    // 직무 아이템 클릭
    document.querySelectorAll('.job-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.stopPropagation();
            showJobDetail(this.textContent);
        });
    });
    
    // 직종 카드 클릭
    document.querySelectorAll('.job-type-card').forEach(card => {
        card.addEventListener('click', function() {
            const jobType = this.dataset.jobType;
            expandJobType(jobType);
        });
    });
    
    // 모달 외부 클릭시 닫기
    document.getElementById('jobDetailModal').addEventListener('click', function(e) {
        if (e.target === this) closeModal();
    });
    
    // ESC 키로 모달 닫기
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

// 뷰 변경 처리
function handleViewChange(e) {
    const newView = e.currentTarget.dataset.view;
    
    // 탭 활성화 상태 변경
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    e.currentTarget.classList.add('active');
    
    // 뷰 컨텐츠 변경
    document.querySelectorAll('.view-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const viewContent = document.getElementById(`${newView}-view`);
    if (viewContent) {
        viewContent.classList.add('active');
    }
    
    currentView = newView;
    
    // 뷰별 렌더링
    if (newView === 'grid') {
        renderGridView();
    } else if (newView === 'treemap') {
        renderTreeMap();
    }
}

// 필터 처리
function handleFilter(e) {
    const filter = e.currentTarget.dataset.filter;
    
    // 칩 활성화 상태 변경
    document.querySelectorAll('.filter-chips .chip').forEach(chip => {
        chip.classList.remove('active');
    });
    e.currentTarget.classList.add('active');
    
    currentFilter = filter;
    applyFilter();
}

// 검색 처리
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    
    if (currentView === 'org') {
        // 조직도 보기에서 검색
        document.querySelectorAll('.job-item').forEach(item => {
            const jobName = item.textContent.toLowerCase();
            const shouldShow = jobName.includes(searchTerm);
            item.style.display = shouldShow ? 'block' : 'none';
        });
        
        // 빈 직종 카드 숨기기
        document.querySelectorAll('.job-type-card').forEach(card => {
            const visibleItems = card.querySelectorAll('.job-item:not([style*="display: none"])');
            card.style.display = visibleItems.length > 0 ? 'block' : 'none';
        });
    }
}

// 필터 적용
function applyFilter() {
    if (currentView === 'org') {
        document.querySelectorAll('.job-group').forEach(group => {
            if (currentFilter === 'all') {
                group.style.display = 'block';
            } else if (currentFilter === 'non-pl' && group.classList.contains('non-pl-group')) {
                group.style.display = 'block';
            } else if (currentFilter === 'pl' && group.classList.contains('pl-group')) {
                group.style.display = 'block';
            } else if (currentFilter === 'with-profile' || currentFilter === 'no-profile') {
                // 기술서 필터는 API 연동 필요
                group.style.display = 'block';
            } else {
                group.style.display = 'none';
            }
        });
    }
}

// 직무 데이터 로드
async function loadJobData() {
    try {
        const response = await fetch('/api/job-tree-data/');
        const data = await response.json();
        
        if (data) {
            jobData = data;
            console.log('Job data loaded:', jobData);
        }
    } catch (error) {
        console.error('Error loading job data:', error);
        // 에러시 하드코딩된 데이터 사용
        jobData = jobStructure;
    }
}

// 통계 업데이트
function updateStatistics() {
    // 정확한 카운트 설정
    const stats = {
        groups: 2,  // Non-PL, PL
        types: 9,   // 8 Non-PL + 1 PL
        roles: 37,  // 33 Non-PL + 4 PL
        profiles: 37 // 모든 직무에 기술서 있음
    };
    
    // DOM 업데이트
    const statCards = document.querySelectorAll('.stat-card');
    if (statCards.length >= 4) {
        statCards[0].querySelector('.stat-value').textContent = stats.groups;
        statCards[1].querySelector('.stat-value').textContent = stats.types;
        statCards[2].querySelector('.stat-value').textContent = stats.roles;
        statCards[3].querySelector('.stat-value').textContent = stats.profiles;
    }
}

// 그리드 뷰 렌더링
function renderGridView() {
    const gridContent = document.getElementById('grid-content');
    if (!gridContent) return;
    
    let html = '<div class="grid-layout">';
    
    for (const [group, types] of Object.entries(jobStructure)) {
        html += `
            <div class="grid-group">
                <h3 class="grid-group-title">
                    <span class="group-badge ${group === 'Non-PL' ? 'non-pl' : 'pl'}">${group} 직군</span>
                </h3>
                <div class="grid-types">`;
        
        for (const [type, jobs] of Object.entries(types)) {
            html += `
                <div class="grid-type-section">
                    <h4 class="grid-type-title">${type} (${jobs.length})</h4>
                    <div class="grid-jobs">`;
            
            jobs.forEach(job => {
                html += `<div class="grid-job-item" onclick="showJobDetail('${job}')">${job}</div>`;
            });
            
            html += `</div></div>`;
        }
        
        html += `</div></div>`;
    }
    
    html += '</div>';
    gridContent.innerHTML = html;
}

// 트리맵 렌더링 (D3.js 사용)
function renderTreeMap() {
    const container = document.getElementById('treemap-container');
    if (!container) return;
    
    // 기존 내용 제거
    container.innerHTML = '';
    
    // 트리맵 데이터 준비
    const treeData = {
        name: 'OK금융그룹',
        children: []
    };
    
    for (const [group, types] of Object.entries(jobStructure)) {
        const groupNode = {
            name: group,
            children: []
        };
        
        for (const [type, jobs] of Object.entries(types)) {
            const typeNode = {
                name: type,
                children: jobs.map(job => ({
                    name: job,
                    value: 1,
                    category: type
                }))
            };
            groupNode.children.push(typeNode);
        }
        
        treeData.children.push(groupNode);
    }
    
    // D3.js 트리맵 생성
    const width = container.clientWidth;
    const height = 600;
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const root = d3.hierarchy(treeData)
        .sum(d => d.value)
        .sort((a, b) => b.value - a.value);
    
    d3.treemap()
        .size([width, height])
        .padding(2)
        .round(true)(root);
    
    const leaf = svg.selectAll('g')
        .data(root.leaves())
        .enter().append('g')
        .attr('transform', d => `translate(${d.x0},${d.y0})`);
    
    leaf.append('rect')
        .attr('class', 'node')
        .attr('data-category', d => d.data.category)
        .attr('width', d => d.x1 - d.x0)
        .attr('height', d => d.y1 - d.y0)
        .on('click', (event, d) => showJobDetail(d.data.name));
    
    leaf.append('text')
        .attr('x', 4)
        .attr('y', 20)
        .text(d => d.data.name)
        .style('font-size', '12px')
        .style('fill', '#333')
        .style('pointer-events', 'none');
}

// 직종 확장
function expandJobType(jobType) {
    console.log('Expanding job type:', jobType);
    // 직종 카드 확장/축소 토글
    const card = document.querySelector(`.job-type-card[data-job-type="${jobType}"]`);
    if (card) {
        card.classList.toggle('expanded');
    }
}

// 직무 상세 보기
async function showJobDetail(jobName) {
    currentJobId = jobName;
    
    try {
        // API 호출 시도
        const response = await fetch(`/api/job-detail/${jobName}/`);
        if (response.ok) {
            const data = await response.json();
            displayJobDetail(data);
        } else {
            // 기본 정보만 표시
            displayBasicJobDetail(jobName);
        }
    } catch (error) {
        console.error('Error loading job detail:', error);
        displayBasicJobDetail(jobName);
    }
}

// 기본 직무 정보 표시
function displayBasicJobDetail(jobName) {
    const modal = document.getElementById('jobDetailModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = jobName;
    
    // 직무가 속한 직종과 직군 찾기
    let jobGroup = '';
    let jobType = '';
    
    for (const [group, types] of Object.entries(jobStructure)) {
        for (const [type, jobs] of Object.entries(types)) {
            if (jobs.includes(jobName)) {
                jobGroup = group;
                jobType = type;
                break;
            }
        }
        if (jobGroup) break;
    }
    
    modalBody.innerHTML = `
        <div class="job-detail-content">
            <div class="detail-section">
                <h3><i class="fas fa-info-circle"></i> 기본 정보</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>직군</label>
                        <span>${jobGroup} 직군</span>
                    </div>
                    <div class="detail-item">
                        <label>직종</label>
                        <span>${jobType}</span>
                    </div>
                    <div class="detail-item">
                        <label>직무명</label>
                        <span>${jobName}</span>
                    </div>
                </div>
            </div>
            
            <div class="detail-section">
                <h3><i class="fas fa-file-alt"></i> 직무기술서</h3>
                <p class="text-muted">직무기술서 정보를 불러오는 중...</p>
            </div>
        </div>
    `;
    
    modal.classList.add('show');
}

// 직무 상세 정보 표시
function displayJobDetail(data) {
    const modal = document.getElementById('jobDetailModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = data.job_role?.name || currentJobId;
    
    let detailHTML = `
        <div class="job-detail-content">
            <div class="detail-section">
                <h3><i class="fas fa-info-circle"></i> 기본 정보</h3>
                <div class="detail-grid">`;
    
    if (data.job_role) {
        detailHTML += `
                    <div class="detail-item">
                        <label>직군</label>
                        <span>${data.job_role.job_type?.category?.name || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>직종</label>
                        <span>${data.job_role.job_type?.name || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>직무명</label>
                        <span>${data.job_role.name}</span>
                    </div>`;
        
        if (data.job_role.description) {
            detailHTML += `
                    <div class="detail-item full-width">
                        <label>설명</label>
                        <span>${data.job_role.description}</span>
                    </div>`;
        }
    }
    
    detailHTML += `
                </div>
            </div>`;
    
    if (data.profile) {
        detailHTML += `
            <div class="detail-section">
                <h3><i class="fas fa-file-alt"></i> 직무기술서</h3>`;
        
        if (data.profile.role_responsibility) {
            detailHTML += `
                <div class="detail-subsection">
                    <h4>역할과 책임</h4>
                    <p>${data.profile.role_responsibility}</p>
                </div>`;
        }
        
        if (data.profile.qualification) {
            detailHTML += `
                <div class="detail-subsection">
                    <h4>자격 요건</h4>
                    <p>${data.profile.qualification}</p>
                </div>`;
        }
        
        if (data.profile.basic_skills && data.profile.basic_skills.length > 0) {
            detailHTML += `
                <div class="detail-subsection">
                    <h4>기본 역량</h4>
                    <ul>
                        ${data.profile.basic_skills.map(skill => `<li>${skill}</li>`).join('')}
                    </ul>
                </div>`;
        }
        
        if (data.profile.growth_path) {
            detailHTML += `
                <div class="detail-subsection">
                    <h4>성장 경로</h4>
                    <p>${data.profile.growth_path}</p>
                </div>`;
        }
        
        detailHTML += `</div>`;
    } else {
        detailHTML += `
            <div class="detail-section">
                <h3><i class="fas fa-file-alt"></i> 직무기술서</h3>
                <p class="text-muted">직무기술서가 아직 작성되지 않았습니다.</p>
            </div>`;
    }
    
    detailHTML += `</div>`;
    
    modalBody.innerHTML = detailHTML;
    modal.classList.add('show');
}

// 모달 닫기
function closeModal() {
    const modal = document.getElementById('jobDetailModal');
    modal.classList.remove('show');
}

// 직무 프로필 편집
function editJobProfile() {
    if (currentJobId) {
        window.location.href = `/job-profiles/edit/${currentJobId}/`;
    }
}

// 스타일 추가
const style = document.createElement('style');
style.textContent = `
    .grid-layout {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }
    
    .grid-group {
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        background: var(--bg-secondary);
    }
    
    .grid-group-title {
        font-size: 1.25rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .grid-types {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
    }
    
    .grid-type-section {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid var(--border-color);
    }
    
    .grid-type-title {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: var(--primary-color);
    }
    
    .grid-jobs {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .grid-job-item {
        padding: 0.5rem 0.75rem;
        background: var(--bg-secondary);
        border-radius: 6px;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .grid-job-item:hover {
        background: var(--primary-color);
        color: white;
        transform: translateX(4px);
    }
    
    .job-detail-content {
        padding: 1rem;
    }
    
    .detail-section {
        margin-bottom: 1.5rem;
    }
    
    .detail-section h3 {
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .detail-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    
    .detail-item {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .detail-item.full-width {
        grid-column: 1 / -1;
    }
    
    .detail-item label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-secondary);
    }
    
    .detail-item span {
        font-size: 1rem;
        color: var(--text-primary);
    }
    
    .detail-subsection {
        margin-bottom: 1rem;
    }
    
    .detail-subsection h4 {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: var(--text-primary);
    }
    
    .detail-subsection p,
    .detail-subsection ul {
        font-size: 0.95rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    .detail-subsection ul {
        margin-left: 1.5rem;
    }
    
    .text-muted {
        color: var(--text-tertiary);
        font-style: italic;
    }
`;
document.head.appendChild(style);