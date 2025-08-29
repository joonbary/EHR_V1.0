// 조직도 테스트 스크립트
// F12 콘솔에 복사해서 실행하세요

console.clear();
console.log('%c🧪 차세대 조직도 테스트 시작', 'color: #00d4ff; font-size: 16px; font-weight: bold');

// 테스트 1: vertical-cjk 클래스 확인
const test1 = () => {
    const hasCJK = document.querySelector('.vertical-cjk');
    const denseNodes = document.querySelectorAll('.dense-node');
    
    if (hasCJK) {
        console.log('✅ TEST 1: vertical-cjk 클래스 적용됨');
        console.log(`   - Dense 노드 수: ${denseNodes.length}개`);
    } else {
        console.error('❌ TEST 1: vertical-cjk 클래스를 찾을 수 없음');
    }
};

// 테스트 2: validateGraph 함수 확인
const test2 = () => {
    if (typeof validateGraph === 'function') {
        console.log('✅ TEST 2: validateGraph 함수 존재');
        
        // 테스트 실행
        const testEdges = [
            { source: { id: 'A' }, target: { id: 'B' } },
            { source: { id: 'A' }, target: { id: 'C' } },
            { source: { id: 'B' }, target: { id: 'D' } }
        ];
        const result = validateGraph(testEdges);
        console.log('   - 체인 검증 결과:', result);
    } else {
        console.error('❌ TEST 2: validateGraph 함수를 찾을 수 없음');
    }
};

// 테스트 3: expandToDepth BFS 최적화 확인
const test3 = () => {
    if (typeof expandToDepth === 'function') {
        const funcStr = expandToDepth.toString();
        const hasBFS = funcStr.includes('BFS') || funcStr.includes('queue');
        const hasPromiseAll = funcStr.includes('Promise.all');
        
        console.log('✅ TEST 3: expandToDepth 함수 존재');
        console.log(`   - BFS 구현: ${hasBFS ? '✓' : '✗'}`);
        console.log(`   - 병렬 로딩: ${hasPromiseAll ? '✓' : '✗'}`);
    } else {
        console.error('❌ TEST 3: expandToDepth 함수를 찾을 수 없음');
    }
};

// 테스트 4: Dense 모드 설정 확인
const test4 = () => {
    if (typeof CONFIG !== 'undefined') {
        console.log('✅ TEST 4: CONFIG 설정 확인');
        console.log(`   - ZOOM_DENSE_THRESHOLD: ${CONFIG.ZOOM_DENSE_THRESHOLD}%`);
        console.log(`   - NODE_WIDTH_DENSE: ${CONFIG.NODE_WIDTH_DENSE}px`);
        console.log(`   - BUCKET_THRESHOLD: ${CONFIG.BUCKET_THRESHOLD}`);
        
        if (typeof OrgChartState !== 'undefined') {
            const isDense = OrgChartState.zoomLevel < CONFIG.ZOOM_DENSE_THRESHOLD;
            console.log(`   - 현재 줌: ${OrgChartState.zoomLevel}%`);
            console.log(`   - Dense 모드: ${isDense ? '활성' : '비활성'}`);
        }
    } else {
        console.error('❌ TEST 4: CONFIG를 찾을 수 없음');
    }
};

// 테스트 5: CSS 스타일 확인
const test5 = () => {
    const styles = document.styleSheets;
    let found = false;
    
    for (let sheet of styles) {
        try {
            const rules = sheet.cssRules || sheet.rules;
            for (let rule of rules) {
                if (rule.selectorText && rule.selectorText.includes('vertical-cjk')) {
                    found = true;
                    console.log('✅ TEST 5: vertical-cjk CSS 규칙 확인');
                    console.log(`   - writing-mode: ${rule.style.writingMode}`);
                    console.log(`   - text-orientation: ${rule.style.textOrientation}`);
                    break;
                }
            }
        } catch (e) {
            // CORS 에러 무시
        }
    }
    
    if (!found) {
        // 인라인 스타일에서 확인
        const elem = document.querySelector('.vertical-cjk');
        if (elem) {
            console.log('✅ TEST 5: vertical-cjk 요소 발견 (인라인 스타일)');
        } else {
            console.warn('⚠️ TEST 5: vertical-cjk CSS 규칙을 찾을 수 없음');
        }
    }
};

// 테스트 실행
test1();
test2();
test3();
test4();
test5();

console.log('%c📊 테스트 완료!', 'color: #10b981; font-size: 14px; font-weight: bold');

// 줌 전환 테스트
console.log('\n%c🔍 줌 전환 테스트', 'color: #f59e0b; font-size: 14px; font-weight: bold');
console.log('다음 명령을 실행하여 Dense 모드를 테스트하세요:');
console.log('%cupdateZoom(90)  // Dense 모드 활성화', 'color: #00d4ff; font-family: monospace');
console.log('%cupdateZoom(100) // Normal 모드로 복귀', 'color: #00d4ff; font-family: monospace');

// 확장 테스트
console.log('\n%c📂 확장 테스트', 'color: #f59e0b; font-size: 14px; font-weight: bold');
console.log('다음 명령을 실행하여 노드 확장을 테스트하세요:');
console.log('%cexpandToDepth("OK금융그룹", 2) // 레벨 2까지', 'color: #00d4ff; font-family: monospace');
console.log('%cexpandToDepth("OK금융그룹", 3) // 레벨 3까지', 'color: #00d4ff; font-family: monospace');