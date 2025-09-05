// 조직도 디버깅 스크립트
// 브라우저 콘솔에서 실행하세요

console.log('=== 조직도 디버깅 시작 ===');

// 1. Dense 노드 확인
const denseNodes = document.querySelectorAll('.dense-node');
console.log(`Dense 노드 개수: ${denseNodes.length}`);

if (denseNodes.length > 0) {
    const firstNode = denseNodes[0];
    const rect = firstNode.getBoundingClientRect();
    const styles = window.getComputedStyle(firstNode);
    
    console.log('첫 번째 Dense 노드:');
    console.log('- 실제 크기:', rect.width, 'x', rect.height);
    console.log('- CSS width:', styles.width);
    console.log('- CSS height:', styles.height);
    console.log('- CSS min-height:', styles.minHeight);
    console.log('- 배경색:', styles.backgroundColor);
    console.log('- 테두리:', styles.border);
}

// 2. 일반 노드 확인
const normalNodes = document.querySelectorAll('.org-node:not(.dense-node):not(.ultra-node)');
console.log(`일반 노드 개수: ${normalNodes.length}`);

if (normalNodes.length > 0) {
    const firstNormal = normalNodes[0];
    const rect = firstNormal.getBoundingClientRect();
    console.log('첫 번째 일반 노드 크기:', rect.width, 'x', rect.height);
}

// 3. 줌 레벨 확인
console.log('현재 줌 레벨:', OrgChartState?.zoomLevel || '확인 불가');

// 4. 현재 뷰 모드 확인
console.log('현재 뷰 모드:', getCurrentViewMode ? getCurrentViewMode() : '함수 없음');

// 5. CONFIG 값 확인
if (typeof CONFIG !== 'undefined') {
    console.log('CONFIG 노드 크기:');
    console.log('- NODE_WIDTH_DENSE:', CONFIG.NODE_WIDTH_DENSE);
    console.log('- NODE_HEIGHT_DENSE:', CONFIG.NODE_HEIGHT_DENSE);
    console.log('- LEVEL_SPACING_DENSE:', CONFIG.LEVEL_SPACING_DENSE);
}

// 6. 노드 겹침 체크
const allNodes = document.querySelectorAll('.org-node');
let overlapCount = 0;

for (let i = 0; i < allNodes.length; i++) {
    for (let j = i + 1; j < allNodes.length; j++) {
        const rect1 = allNodes[i].getBoundingClientRect();
        const rect2 = allNodes[j].getBoundingClientRect();
        
        const overlap = !(rect1.right < rect2.left || 
                         rect2.right < rect1.left || 
                         rect1.bottom < rect2.top || 
                         rect2.bottom < rect1.top);
        
        if (overlap) {
            overlapCount++;
            if (overlapCount <= 3) {
                console.log(`겹침 발견: ${allNodes[i].innerText.substring(0,20)} ↔ ${allNodes[j].innerText.substring(0,20)}`);
            }
        }
    }
}
console.log(`총 겹침 횟수: ${overlapCount}`);

console.log('=== 디버깅 완료 ===');