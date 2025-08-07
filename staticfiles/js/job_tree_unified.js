// 전역 변수
let currentJobId = null;
let jobData = {};
let isFullscreen = false;

// 헬퍼 함수들
function getIcon(iconName) {
    if (iconName && iconName.startsWith('fa-')) {
        return iconName;
    }
    const iconMap = {
        'IT기획': 'fa-laptop-code',
        'IT개발': 'fa-code',
        'IT운영': 'fa-server',
        '경영관리': 'fa-briefcase',
        '투자금융': 'fa-chart-line',
        '기업금융': 'fa-building',
        '기업영업': 'fa-handshake',
        '리테일금융': 'fa-coins',
        '고객지원': 'fa-headset'
    };
    return iconMap[iconName] || 'fa-folder';
}

function getCategoryGradient(categoryName) {
    const gradients = {
        'IT기획': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
        'IT개발': 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
        'IT운영': 'linear-gradient(135deg, #a78bfa 0%, #c4b5fd 100%)',
        '경영관리': 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)',
        '투자금융': 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)',
        '기업금융': 'linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%)',
        '기업영업': 'linear-gradient(135deg, #14b8a6 0%, #2dd4bf 100%)',
        '리테일금융': 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
        '고객지원': 'linear-gradient(135deg, #22d3ee 0%, #67e8f9 100%)'
    };
    return gradients[categoryName] || 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)';
}

function getCategoryColor(categoryName) {
    const colors = {
        'IT기획': '#6366f1',
        'IT개발': '#8b5cf6',
        'IT운영': '#a78bfa',
        '경영관리': '#3b82f6',
        '투자금융': '#0ea5e9',
        '기업금융': '#06b6d4',
        '기업영업': '#14b8a6',
        '리테일금융': '#10b981',
        '고객지원': '#22d3ee'
    };
    return colors[categoryName] || '#6366f1';
}

function countJobs(jobs) {
    if (Array.isArray(jobs)) {
        return jobs.length;
    } else if (typeof jobs === 'object') {
        return Object.values(jobs).reduce((sum, jobList) => {
            return sum + (Array.isArray(jobList) ? jobList.length : 0);
        }, 0);
    }
    return 0;
}

function animateCards() {
    const cards = document.querySelectorAll('.job-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 30);
    });
}

// 페이지 로드시 초기화
document.addEventListener('DOMContentLoaded', function() {
    loadTreeData();
    initializeEventListeners();
});

// 이벤트 리스너 초기화
function initializeEventListeners() {
    // 뷰 모드 탭 삭제됨 - 조직도 보기만 사용
    
    // 검색 기능
    const searchInput = document.getElementById('jobSearch');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
    
    // 필터 칩
    document.querySelectorAll('.filter-chips .chip').forEach(chip => {
        chip.addEventListener('click', handleFilter);
    });
    
    // 모달 외부 클릭시 닫기
    const modal = document.getElementById('jobDetailModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
    }
    
    // ESC 키로 모달/전체화면 닫기
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (isFullscreen) exitFullscreen();
            else closeModal();
        }
    });
}

// 뷰 모드 변경 처리 - 삭제됨 (조직도 보기만 사용)

// 트리 데이터 로드
async function loadTreeData() {
    try {
        const response = await fetch('/job-profiles/api/tree-map-data/');
        const result = await response.json();
        
        if (result.success) {
            jobData = result.data;
            renderTreeMap(result.data);
        } else {
            showError('데이터를 불러올 수 없습니다.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('서버 연결에 실패했습니다.');
    }
}

// 트리맵 렌더링 (조직도 뷰)
function renderTreeMap(data) {
    // Non-PL 렌더링
    const nonPlContent = document.getElementById('non-pl-content');
    nonPlContent.innerHTML = renderGroup(data['Non-PL'], 'Non-PL');
    
    // PL 렌더링
    const plContent = document.getElementById('pl-content');
    plContent.innerHTML = renderGroup(data['PL'], 'PL');
    
    // 애니메이션 적용
    animateCards();
}

// 그리드 뷰 렌더링 - 삭제됨

// 트리맵 뷰 렌더링 - 삭제됨

// 그룹 렌더링
function renderGroup(groupData, groupType) {
    if (!groupData || Object.keys(groupData).length === 0) {
        return '<div class="empty-state">데이터가 없습니다.</div>';
    }
    
    let html = '';
    
    for (const [categoryName, categoryData] of Object.entries(groupData)) {
        // categoryData가 직접 jobs 객체인 경우와 icon/jobs 구조인 경우 모두 처리
        const jobs = categoryData.jobs || categoryData;
        const icon = categoryData.icon || '';
        
        // jobs가 배열인지 객체인지 확인
        const jobCount = Array.isArray(jobs) ? 
            jobs.length : 
            Object.values(jobs).reduce((sum, jobList) => sum + (Array.isArray(jobList) ? jobList.length : 0), 0);
        
        html += `
            <div class="category-section" data-category="${categoryName}">
                <div class="category-header">
                    <div class="category-icon" style="background: ${getCategoryGradient(categoryName)}">
                        <i class="fas ${getIcon(icon || categoryName)}"></i>
                    </div>
                    <div class="category-info">
                        <h3 class="category-title">${categoryName}</h3>
                        <span class="category-stats">
                            ${jobCount}개 직무
                        </span>
                    </div>
                </div>
                
                <div class="job-types-container">
                    ${renderJobTypes(jobs, categoryName)}
                </div>
            </div>
        `;
    }
    
    return html;
}

// 직종별 직무 렌더링
function renderJobTypes(jobTypes, categoryName) {
    let html = '';
    
    // jobTypes가 배열인 경우 직접 렌더링
    if (Array.isArray(jobTypes)) {
        html += `
            <div class="job-type-section">
                <div class="jobs-grid">
                    ${jobTypes.map(job => renderJobCard(job, categoryName)).join('')}
                </div>
            </div>
        `;
    } 
    // jobTypes가 객체인 경우 기존 로직
    else if (typeof jobTypes === 'object') {
        for (const [jobTypeName, jobs] of Object.entries(jobTypes)) {
            // jobs가 배열인지 확인
            if (Array.isArray(jobs)) {
                html += `
                    <div class="job-type-section">
                        <h4 class="job-type-title" style="border-color: ${getCategoryColor(categoryName)}">
                            ${jobTypeName}
                            <span class="job-count">${jobs.length}</span>
                        </h4>
                        <div class="jobs-grid">
                            ${jobs.map(job => renderJobCard(job, categoryName)).join('')}
                        </div>
                    </div>
                `;
            }
        }
    }
    
    return html;
}

// 직무 카드 렌더링
function renderJobCard(job, categoryName) {
    // has_profile이 없으면 기본값을 true로 설정 (모두 작성완료로 표시)
    const hasProfile = job.has_profile !== false;
    const cardClass = hasProfile ? 'has-profile' : 'no-profile';
    const color = getCategoryColor(categoryName);
    
    return `
        <div class="job-card ${cardClass}" 
             data-job-id="${job.id}"
             data-has-profile="${hasProfile}"
             onclick="showJobDetail('${job.id}')"
             style="--card-color: ${color}">
            <div class="job-card-icon">
                <i class="fas ${hasProfile ? 'fa-file-alt' : 'fa-file'}"></i>
            </div>
            <h5 class="job-card-title">${job.name}</h5>
            <span class="job-card-status ${hasProfile ? 'complete' : 'incomplete'}">
                ${hasProfile ? '작성완료' : '미작성'}
            </span>
        </div>
    `;
}

// 직무 상세 표시
async function showJobDetail(jobId) {
    currentJobId = jobId;
    
    try {
        const response = await fetch(`/job-profiles/api/job-detail/${jobId}/`);
        const result = await response.json();
        
        if (result.success) {
            displayJobDetail(result.job);
        } else {
            console.error('Failed to load job detail');
            // 기본 정보 표시
            displayJobDetail({
                id: jobId,
                name: '직무명',
                category: 'Non-PL',
                type: '직종',
                description: '직무 설명이 여기에 표시됩니다.',
                requirements: '필요 역량이 여기에 표시됩니다.',
                skills: '필요 기술이 여기에 표시됩니다.',
                profile_status: '작성완료'
            });
        }
    } catch (error) {
        console.error('Error:', error);
        // 기본 정보 표시
        displayJobDetail({
            id: jobId,
            name: '직무명',
            category: 'Non-PL',
            type: '직종',
            description: '직무 설명이 여기에 표시됩니다.',
            requirements: '필요 역량이 여기에 표시됩니다.',
            skills: '필요 기술이 여기에 표시됩니다.',
            profile_status: '작성완료'
        });
    }
}

// displayJobDetail 함수는 job_detail_modern.js에서 제공됨

// 유틸리티 함수들 - 중복 제거됨
function formatText(text) {
    if (!text) return '';
    return text.split('\n').map(line => `<p>${line}</p>`).join('');
}

// 모달 제어
function openModal() {
    const modal = document.getElementById('jobDetailModal');
    if (modal) {
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-open');
    } else {
        // 모달이 없으면 간단한 알림 표시
        console.log('Job detail modal not found');
    }
}

function closeModal() {
    const modal = document.getElementById('jobDetailModal');
    if (modal) {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    }
    document.body.classList.remove('modal-open');
    currentJobId = null;
}

// 전체화면 제어
function toggleFullscreen() {
    if (!isFullscreen) {
        closeModal();
        const fullscreenDetail = document.getElementById('fullscreenDetail');
        if (fullscreenDetail) {
            fullscreenDetail.style.display = 'flex';
        }
        document.body.classList.add('fullscreen-open');
        isFullscreen = true;
    } else {
        exitFullscreen();
    }
}

function exitFullscreen() {
    const fullscreenDetail = document.getElementById('fullscreenDetail');
    if (fullscreenDetail) {
        fullscreenDetail.style.display = 'none';
    }
    document.body.classList.remove('fullscreen-open');
    isFullscreen = false;
}

// 편집/삭제 기능
function editJobProfile() {
    if (currentJobId) {
        window.location.href = `/job-profiles/${currentJobId}/edit/`;
    }
}

function deleteJobProfile() {
    if (currentJobId && confirm('정말로 이 직무기술서를 삭제하시겠습니까?')) {
        // 삭제 API 호출
        fetch(`/api/job-profiles/${currentJobId}/delete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('삭제되었습니다.');
                closeModal();
                loadTreeData(); // 데이터 새로고침
            } else {
                alert('삭제에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('서버 오류가 발생했습니다.');
        });
    }
}

function createJobProfile(jobId) {
    window.location.href = `/job-profiles/create/?job_role=${jobId}`;
}

// 검색 기능
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    
    document.querySelectorAll('.job-card').forEach(card => {
        const jobName = card.querySelector('.job-card-title').textContent.toLowerCase();
        const shouldShow = jobName.includes(searchTerm);
        card.style.display = shouldShow ? '' : 'none';
    });
    
    // 빈 직종 숨기기
    document.querySelectorAll('.job-type-section').forEach(section => {
        const visibleCards = section.querySelectorAll('.job-card:not([style*="display: none"])');
        section.style.display = visibleCards.length > 0 ? '' : 'none';
    });
    
    // 빈 카테고리 숨기기
    document.querySelectorAll('.category-section').forEach(section => {
        const visibleTypes = section.querySelectorAll('.job-type-section:not([style*="display: none"])');
        section.style.display = visibleTypes.length > 0 ? '' : 'none';
    });
}

// 필터 기능
function handleFilter(e) {
    const chip = e.target;
    const filter = chip.dataset.filter;
    
    // 활성 칩 변경
    document.querySelectorAll('.filter-chips .chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    
    // 필터 적용
    document.querySelectorAll('.job-card').forEach(card => {
        const hasProfile = card.dataset.hasProfile === 'true';
        let shouldShow = true;
        
        if (filter === 'with-profile') shouldShow = hasProfile;
        else if (filter === 'no-profile') shouldShow = !hasProfile;
        
        card.style.display = shouldShow ? '' : 'none';
    });
    
    // 빈 섹션 처리
    handleSearch({ target: document.getElementById('jobSearch') });
}

// 카드 애니메이션
function animateCards() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.job-card').forEach(card => {
        observer.observe(card);
    });
}

// 에러 표시
function showError(message) {
    const errorHTML = `
        <div class="error-state">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
            <button class="btn btn-primary" onclick="loadTreeData()">
                <i class="fas fa-redo"></i> 다시 시도
            </button>
        </div>
    `;
    
    document.getElementById('non-pl-content').innerHTML = errorHTML;
    document.getElementById('pl-content').innerHTML = '';
}