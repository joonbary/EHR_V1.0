// 조직도 문제 진단 및 수정 스크립트
console.log('=== 조직도 문제 진단 시작 ===');

// 1. updateZoom 함수 확인
console.log('1. updateZoom 함수 위치:', {
    'window.updateZoom': typeof window.updateZoom,
    'window.orgChart?.updateZoom': window.orgChart ? typeof window.orgChart.updateZoom : 'orgChart 없음',
    'AdvancedOrgChart.prototype.updateZoom': typeof AdvancedOrgChart?.prototype?.updateZoom
});

// 2. 현재 줌 동작 확인
const container = document.getElementById('treeContainer');
if (container) {
    console.log('2. 컨테이너 transform:', {
        transform: container.style.transform,
        transformOrigin: container.style.transformOrigin
    });
}

// 3. Dense 노드 확인
const denseNodes = document.querySelectorAll('.dense-node');
console.log('3. Dense 노드 상태:', {
    개수: denseNodes.length,
    첫번째_노드: denseNodes[0] ? {
        width: denseNodes[0].style.width,
        height: denseNodes[0].style.height,
        computedWidth: window.getComputedStyle(denseNodes[0]).width,
        computedHeight: window.getComputedStyle(denseNodes[0]).height,
        innerHTML: denseNodes[0].innerHTML.substring(0, 100)
    } : null
});

// 4. updateZoom 함수 패치 - transform 사용 강제
window.updateZoom = function(level) {
    console.log(`✅ Patched updateZoom called with level: ${level}`);
    
    // 줌 레벨 업데이트
    if (window.OrgChartState) {
        window.OrgChartState.zoomLevel = level;
    }
    
    // 줌 표시 업데이트
    const zoomDisplay = document.getElementById('zoomLevel');
    if (zoomDisplay) {
        zoomDisplay.textContent = level + '%';
    }
    
    // CSS transform만 사용 (노드 크기 변경하지 않음)
    const container = document.getElementById('treeContainer');
    if (container) {
        const scale = level / 100;
        container.style.transform = `scale(${scale})`;
        container.style.transformOrigin = '0 0';
        console.log(`✅ Applied transform: scale(${scale})`);
    }
    
    // 미니맵 업데이트
    if (typeof updateMinimap === 'function') {
        updateMinimap();
    }
};

// 5. 노드 생성 함수 패치 - 동적 높이 적용 강제
if (window.NodeRenderer) {
    const originalCreateDenseNode = NodeRenderer.createDenseNode;
    NodeRenderer.createDenseNode = function(node) {
        console.log(`✅ Creating dense node for: ${node.name}`);
        
        const div = document.createElement('div');
        div.className = 'dense-node org-node';
        div.id = `node-${node.id}`;
        
        // 글자 수에 따른 높이 동적 조정
        const nameLength = node.name.length;
        const minHeight = 45;
        const charHeight = 12;
        const padding = 20;
        const nodeHeight = Math.max(minHeight, nameLength * charHeight + padding);
        
        // 스타일 직접 적용 (고정 폭, 동적 높이)
        div.style.cssText = `
            position: absolute;
            width: 35px !important;
            height: ${nodeHeight}px !important;
            background: white;
            border: 1px solid #333;
            border-radius: 2px;
            padding: 3px;
            cursor: pointer;
            color: black;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        `;
        
        // 글자 수에 따른 폰트 크기 조정
        let fontSize = 10;
        if (nameLength <= 4) {
            fontSize = 11;
        } else if (nameLength >= 8) {
            fontSize = 8;
        }
        
        div.innerHTML = `
            <div class="vertical-cjk" style="
                font-size: ${fontSize}px; 
                text-align: center; 
                height: 100%; 
                padding: 2px; 
                line-height: 1.1;
                writing-mode: vertical-rl;
                text-orientation: upright;
            ">${node.name}</div>
        `;
        
        // 이벤트 리스너
        div.addEventListener('click', () => {
            window.orgChart?.focusNode(node.id);
        });
        
        console.log(`✅ Dense node created: width=35px, height=${nodeHeight}px`);
        return div;
    };
}

// 6. 즉시 수정 적용
setTimeout(() => {
    console.log('=== 수정 사항 적용 중 ===');
    
    // 모든 Dense 노드 스타일 강제 수정
    document.querySelectorAll('.dense-node').forEach((node, index) => {
        const name = node.textContent || node.innerText;
        const nameLength = name.length;
        const nodeHeight = Math.max(45, nameLength * 12 + 20);
        
        node.style.width = '35px';
        node.style.height = `${nodeHeight}px`;
        
        if (index < 3) {
            console.log(`노드 ${name} 수정: width=35px, height=${nodeHeight}px`);
        }
    });
    
    console.log('=== 수정 완료 ===');
}, 1000);

console.log('=== 진단 스크립트 로드 완료 ===');