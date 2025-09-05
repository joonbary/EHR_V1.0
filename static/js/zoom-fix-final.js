// 최종 줌 문제 해결 스크립트
console.log('=== 최종 줌 수정 시작 ===');

// 1. 기존 transform 제거
const container = document.getElementById('treeContainer');
if (container) {
    // 기존 transform 스타일 초기화
    container.style.transform = '';
    container.style.transformOrigin = '';
    console.log('✅ 기존 transform 제거됨');
}

// 2. 줌 함수 완전 재정의
window.updateZoom = function(level) {
    console.log(`🔧 Fixed updateZoom 호출: ${level}%`);
    
    // 줌 레벨 범위 제한
    const zoomLevel = Math.max(30, Math.min(200, level));
    
    // 상태 업데이트
    if (window.OrgChartState) {
        window.OrgChartState.zoomLevel = zoomLevel;
    }
    
    // 줌 레벨 표시
    const zoomDisplay = document.getElementById('zoomLevel');
    if (zoomDisplay) {
        zoomDisplay.textContent = `${zoomLevel}%`;
    }
    
    // CSS transform으로 줌 적용
    const container = document.getElementById('treeContainer');
    if (container) {
        const scale = zoomLevel / 100;
        container.style.transform = `scale(${scale})`;
        container.style.transformOrigin = '0 0';
        console.log(`✅ Transform 적용됨: scale(${scale})`);
        
        // 실제 렌더링 크기 확인
        const firstNode = document.querySelector('.dense-node');
        if (firstNode) {
            const rect = firstNode.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(firstNode);
            console.log(`📏 첫 번째 노드 실제 크기:`, {
                설정된_width: computedStyle.width,
                설정된_height: computedStyle.height,
                렌더링_width: rect.width,
                렌더링_height: rect.height,
                scale: scale
            });
        }
    }
};

// 3. Dense 모드 강제 유지
window.getCurrentViewMode = function() {
    return 'dense'; // 항상 dense 모드 반환
};

// 4. 노드 크기 검증 및 수정
function fixNodeSizes() {
    const nodes = document.querySelectorAll('.dense-node');
    let fixedCount = 0;
    
    nodes.forEach(node => {
        const currentWidth = node.style.width;
        const currentHeight = node.style.height;
        
        // 35px 폭이 아닌 경우 수정
        if (currentWidth !== '35px' && currentWidth !== '35px !important') {
            node.style.width = '35px !important';
            fixedCount++;
        }
        
        // 최소 높이 보장
        const minHeight = 45;
        const heightValue = parseInt(currentHeight);
        if (!currentHeight || heightValue < minHeight) {
            const nameLength = (node.textContent || '').length;
            const dynamicHeight = Math.max(minHeight, nameLength * 12 + 20);
            node.style.height = `${dynamicHeight}px !important`;
            fixedCount++;
        }
    });
    
    if (fixedCount > 0) {
        console.log(`✅ ${fixedCount}개 노드 크기 수정됨`);
    }
    
    return nodes.length;
}

// 5. 줌 버튼 이벤트 재바인딩
function rebindZoomButtons() {
    const zoomIn = document.getElementById('zoomIn');
    const zoomOut = document.getElementById('zoomOut');
    const zoomReset = document.getElementById('zoomReset');
    
    if (zoomIn) {
        // 기존 이벤트 제거하고 새로 바인딩
        const newZoomIn = zoomIn.cloneNode(true);
        zoomIn.parentNode.replaceChild(newZoomIn, zoomIn);
        newZoomIn.onclick = function() {
            const current = window.OrgChartState?.zoomLevel || 100;
            const newLevel = Math.min(current + 10, 200);
            console.log(`📍 줌인: ${current}% → ${newLevel}%`);
            window.updateZoom(newLevel);
            setTimeout(fixNodeSizes, 100); // 줌 후 노드 크기 재검증
        };
    }
    
    if (zoomOut) {
        const newZoomOut = zoomOut.cloneNode(true);
        zoomOut.parentNode.replaceChild(newZoomOut, zoomOut);
        newZoomOut.onclick = function() {
            const current = window.OrgChartState?.zoomLevel || 100;
            const newLevel = Math.max(current - 10, 30);
            console.log(`📍 줌아웃: ${current}% → ${newLevel}%`);
            window.updateZoom(newLevel);
            setTimeout(fixNodeSizes, 100);
        };
    }
    
    if (zoomReset) {
        const newZoomReset = zoomReset.cloneNode(true);
        zoomReset.parentNode.replaceChild(newZoomReset, zoomReset);
        newZoomReset.onclick = function() {
            console.log('📍 줌 리셋: 100%');
            window.updateZoom(100);
            setTimeout(fixNodeSizes, 100);
        };
    }
}

// 6. 초기화 실행
setTimeout(() => {
    console.log('🔄 최종 수정 적용 중...');
    
    // Dense 모드 강제 적용
    if (window.OrgChartUtils) {
        window.OrgChartUtils.getCurrentViewMode = () => 'dense';
    }
    
    // 노드 크기 수정
    const nodeCount = fixNodeSizes();
    console.log(`📊 총 ${nodeCount}개 노드 확인됨`);
    
    // 줌 버튼 재바인딩
    rebindZoomButtons();
    
    // 현재 줌 레벨로 재적용
    const currentZoom = window.OrgChartState?.zoomLevel || 100;
    window.updateZoom(currentZoom);
    
    console.log('=== 최종 줌 수정 완료 ===');
}, 1500);

// 7. 주기적 검증 (5초마다)
setInterval(() => {
    const nodes = document.querySelectorAll('.dense-node');
    if (nodes.length > 0) {
        const firstNode = nodes[0];
        const rect = firstNode.getBoundingClientRect();
        const expectedWidth = 35;
        const currentScale = window.OrgChartState?.zoomLevel ? window.OrgChartState.zoomLevel / 100 : 1;
        const expectedRenderedWidth = expectedWidth * currentScale;
        
        if (Math.abs(rect.width - expectedRenderedWidth) > 5) {
            console.warn(`⚠️ 노드 크기 불일치 감지: 예상 ${expectedRenderedWidth}px, 실제 ${rect.width}px`);
            fixNodeSizes();
        }
    }
}, 5000);