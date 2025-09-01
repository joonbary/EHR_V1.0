// 간격 테스트 스크립트
// 브라우저 콘솔에서 실행하여 계층 기반 간격이 제대로 적용되는지 확인

console.clear();
console.log('%c🧪 계층 기반 간격 시스템 테스트', 'color: #00d4ff; font-size: 16px; font-weight: bold');

// 테스트 1: CONFIG 확인
const testConfig = () => {
    if (typeof CONFIG !== 'undefined') {
        console.log('✅ CONFIG 설정 확인:');
        console.log(`   - NODE_WIDTH_DENSE: ${CONFIG.NODE_WIDTH_DENSE}px (목표: 60px)`);
        console.log(`   - SIBLING_SPACING_DENSE: ${CONFIG.SIBLING_SPACING_DENSE}px`);
        console.log(`   - GROUP_SPACING_MULTIPLIER:`, CONFIG.GROUP_SPACING_MULTIPLIER);
        
        if (CONFIG.NODE_WIDTH_DENSE === 60) {
            console.log('   ✅ 노드 너비가 60px로 설정됨');
        } else {
            console.warn(`   ⚠️ 노드 너비가 ${CONFIG.NODE_WIDTH_DENSE}px로 설정됨 (60px 필요)`);
        }
    } else {
        console.error('❌ CONFIG를 찾을 수 없음');
    }
};

// 테스트 2: 노드 간격 측정
const testNodeSpacing = () => {
    const nodes = document.querySelectorAll('.org-node, .dense-node');
    console.log(`\n📊 노드 간격 분석 (총 ${nodes.length}개 노드):`);
    
    // 레벨별로 노드 그룹화
    const nodesByLevel = new Map();
    nodes.forEach(node => {
        const level = parseInt(node.dataset.level || '0');
        if (!nodesByLevel.has(level)) {
            nodesByLevel.set(level, []);
        }
        nodesByLevel.get(level).push(node);
    });
    
    // 각 레벨에서 간격 측정
    nodesByLevel.forEach((levelNodes, level) => {
        if (levelNodes.length > 1) {
            const spacings = [];
            for (let i = 1; i < levelNodes.length; i++) {
                const prevRect = levelNodes[i-1].getBoundingClientRect();
                const currRect = levelNodes[i].getBoundingClientRect();
                const spacing = currRect.left - (prevRect.left + prevRect.width);
                spacings.push(spacing);
            }
            
            const avgSpacing = spacings.reduce((a, b) => a + b, 0) / spacings.length;
            const minSpacing = Math.min(...spacings);
            const maxSpacing = Math.max(...spacings);
            
            console.log(`   레벨 ${level}: 평균 ${avgSpacing.toFixed(1)}px (최소: ${minSpacing.toFixed(1)}px, 최대: ${maxSpacing.toFixed(1)}px)`);
        }
    });
};

// 테스트 3: 계층 구조 확인
const testHierarchy = () => {
    console.log('\n🏗️ 계층 구조 분석:');
    
    // 본부 노드들 찾기
    const divisions = Array.from(document.querySelectorAll('[data-type="division"]'));
    console.log(`   - 본부: ${divisions.length}개`);
    
    // 각 본부의 부서 수 확인
    divisions.forEach(div => {
        const divName = div.querySelector('.node-name')?.textContent || '알 수 없음';
        const departments = document.querySelectorAll(`[data-parent="${div.id}"][data-type="department"]`);
        console.log(`     ${divName}: ${departments.length}개 부서`);
    });
    
    // 부서 간격 확인
    const departments = Array.from(document.querySelectorAll('[data-type="department"]'));
    if (departments.length > 1) {
        const deptSpacings = [];
        for (let i = 1; i < departments.length; i++) {
            const prevRect = departments[i-1].getBoundingClientRect();
            const currRect = departments[i].getBoundingClientRect();
            const spacing = currRect.left - (prevRect.left + prevRect.width);
            
            // 같은 본부인지 확인
            const prevParent = departments[i-1].dataset.parent;
            const currParent = departments[i].dataset.parent;
            const sameParent = prevParent === currParent;
            
            deptSpacings.push({
                spacing: spacing,
                sameParent: sameParent
            });
        }
        
        const sameParentSpacings = deptSpacings.filter(s => s.sameParent).map(s => s.spacing);
        const diffParentSpacings = deptSpacings.filter(s => !s.sameParent).map(s => s.spacing);
        
        if (sameParentSpacings.length > 0) {
            const avgSame = sameParentSpacings.reduce((a, b) => a + b, 0) / sameParentSpacings.length;
            console.log(`   - 같은 본부 내 부서 간격: 평균 ${avgSame.toFixed(1)}px`);
        }
        
        if (diffParentSpacings.length > 0) {
            const avgDiff = diffParentSpacings.reduce((a, b) => a + b, 0) / diffParentSpacings.length;
            console.log(`   - 다른 본부 부서 간격: 평균 ${avgDiff.toFixed(1)}px`);
            
            // 간격 비율 확인
            if (sameParentSpacings.length > 0 && diffParentSpacings.length > 0) {
                const avgSame = sameParentSpacings.reduce((a, b) => a + b, 0) / sameParentSpacings.length;
                const ratio = avgDiff / avgSame;
                console.log(`   - 간격 비율: ${ratio.toFixed(2)}배 (목표: 2.0배)`);
                
                if (ratio >= 1.5) {
                    console.log('   ✅ 계층별 간격 차별화 성공');
                } else {
                    console.warn('   ⚠️ 계층별 간격 차별화 개선 필요');
                }
            }
        }
    }
};

// 테스트 4: Dense 모드 확인
const testDenseMode = () => {
    console.log('\n🔍 Dense 모드 상태:');
    
    const isDense = OrgChartState.zoomLevel < CONFIG.ZOOM_DENSE_THRESHOLD;
    console.log(`   - 현재 줌: ${OrgChartState.zoomLevel}%`);
    console.log(`   - Dense 모드: ${isDense ? '활성' : '비활성'}`);
    
    const denseNodes = document.querySelectorAll('.dense-node');
    const normalNodes = document.querySelectorAll('.org-node:not(.dense-node)');
    
    console.log(`   - Dense 노드: ${denseNodes.length}개`);
    console.log(`   - Normal 노드: ${normalNodes.length}개`);
    
    // 노드 너비 실제 측정
    if (denseNodes.length > 0) {
        const sampleNode = denseNodes[0];
        const rect = sampleNode.getBoundingClientRect();
        console.log(`   - 실제 Dense 노드 너비: ${rect.width.toFixed(1)}px (목표: 60px)`);
        
        if (Math.abs(rect.width - 60) < 5) {
            console.log('   ✅ Dense 노드 너비 최적화 성공');
        } else {
            console.warn(`   ⚠️ Dense 노드 너비 조정 필요 (현재: ${rect.width.toFixed(1)}px)`);
        }
    }
};

// 모든 테스트 실행
testConfig();
testNodeSpacing();
testHierarchy();
testDenseMode();

console.log('\n%c📊 테스트 완료!', 'color: #10b981; font-size: 14px; font-weight: bold');
console.log('💡 Tip: updateZoom(30)으로 Dense 모드를 활성화하여 60px 노드를 확인하세요');