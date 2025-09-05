// 줌 기능 문제 진단 스크립트
console.log('=== 줌 기능 진단 시작 ===');

// 1. 필수 요소 존재 확인
const diagnostics = {
    elements: {
        zoomIn: document.getElementById('zoomIn'),
        zoomOut: document.getElementById('zoomOut'),
        zoomReset: document.getElementById('zoomReset'),
        zoomLevel: document.getElementById('zoomLevel'),
        treeContainer: document.getElementById('treeContainer'),
        chartViewport: document.getElementById('chartViewport')
    },
    functions: {
        updateZoom: typeof updateZoom === 'function',
        windowUpdateZoom: typeof window.updateZoom === 'function',
        OrgChartState: typeof window.OrgChartState !== 'undefined',
        CONFIG: typeof window.CONFIG !== 'undefined'
    },
    config: {
        ZOOM_MIN: window.CONFIG?.ZOOM_MIN,
        ZOOM_MAX: window.CONFIG?.ZOOM_MAX,
        ZOOM_STEP: window.CONFIG?.ZOOM_STEP
    }
};

// 진단 결과 출력
console.log('📊 요소 존재 여부:', diagnostics.elements);
console.log('📊 함수 존재 여부:', diagnostics.functions);
console.log('📊 설정 값:', diagnostics.config);

// 2. 현재 상태 확인
if (window.OrgChartState) {
    console.log('📊 현재 줌 레벨:', window.OrgChartState.zoomLevel);
}

// 3. 이벤트 리스너 확인
const checkEventListeners = () => {
    const zoomIn = document.getElementById('zoomIn');
    if (zoomIn) {
        // 테스트 클릭 이벤트
        const testHandler = (e) => {
            console.log('✅ 줌인 버튼 클릭됨!');
            e.stopPropagation();
        };
        zoomIn.addEventListener('click', testHandler);
        
        // 즉시 클릭 시뮬레이션
        zoomIn.click();
        
        // 핸들러 제거
        zoomIn.removeEventListener('click', testHandler);
    }
};

// 4. updateZoom 함수 패치 (디버깅용)
const originalUpdateZoom = window.updateZoom;
window.updateZoom = function(level) {
    console.log(`🔧 updateZoom 호출됨: ${level}%`);
    
    // 기본 동작 수행
    if (originalUpdateZoom) {
        return originalUpdateZoom.call(this, level);
    }
    
    // 폴백: 직접 구현
    const zoomLevel = Math.max(30, Math.min(200, level));
    
    // 줌 레벨 표시 업데이트
    const zoomDisplay = document.getElementById('zoomLevel');
    if (zoomDisplay) {
        zoomDisplay.textContent = `${zoomLevel}%`;
    }
    
    // CSS transform 적용
    const container = document.getElementById('treeContainer');
    if (container) {
        const scale = zoomLevel / 100;
        container.style.transform = `scale(${scale})`;
        container.style.transformOrigin = '0 0';
        console.log(`✅ Transform 적용: scale(${scale})`);
    }
    
    // 상태 업데이트
    if (window.OrgChartState) {
        window.OrgChartState.zoomLevel = zoomLevel;
    }
};

// 5. 버튼에 직접 이벤트 바인딩 (폴백)
const fixZoomButtons = () => {
    const zoomIn = document.getElementById('zoomIn');
    const zoomOut = document.getElementById('zoomOut');
    const zoomReset = document.getElementById('zoomReset');
    
    if (zoomIn && !zoomIn.hasAttribute('data-fixed')) {
        zoomIn.setAttribute('data-fixed', 'true');
        zoomIn.onclick = () => {
            const current = window.OrgChartState?.zoomLevel || 100;
            const newLevel = Math.min(current + 10, 200);
            console.log(`📍 줌인: ${current}% → ${newLevel}%`);
            window.updateZoom(newLevel);
        };
        console.log('✅ 줌인 버튼 수정됨');
    }
    
    if (zoomOut && !zoomOut.hasAttribute('data-fixed')) {
        zoomOut.setAttribute('data-fixed', 'true');
        zoomOut.onclick = () => {
            const current = window.OrgChartState?.zoomLevel || 100;
            const newLevel = Math.max(current - 10, 30);
            console.log(`📍 줌아웃: ${current}% → ${newLevel}%`);
            window.updateZoom(newLevel);
        };
        console.log('✅ 줌아웃 버튼 수정됨');
    }
    
    if (zoomReset && !zoomReset.hasAttribute('data-fixed')) {
        zoomReset.setAttribute('data-fixed', 'true');
        zoomReset.onclick = () => {
            console.log('📍 줌 리셋: 100%');
            window.updateZoom(100);
        };
        console.log('✅ 줌 리셋 버튼 수정됨');
    }
};

// 6. 실행
setTimeout(() => {
    checkEventListeners();
    fixZoomButtons();
    console.log('=== 줌 기능 진단 및 수정 완료 ===');
    
    // 자동 테스트
    console.log('🧪 자동 테스트: 줌인 시도...');
    const zoomInBtn = document.getElementById('zoomIn');
    if (zoomInBtn) {
        zoomInBtn.click();
    }
}, 1000);