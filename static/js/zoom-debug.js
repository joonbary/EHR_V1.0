// 줌 디버깅 스크립트
console.log('🔍 줌 디버깅 시작...');

// 현재 DOM 상태 확인
function checkDOMStatus() {
    const results = {
        zoomWrapper: document.getElementById('zoomWrapper'),
        treeContainer: document.getElementById('treeContainer'),
        zoomLevel: document.getElementById('zoomLevel'),
        zoomIn: document.getElementById('zoomIn'),
        zoomOut: document.getElementById('zoomOut')
    };
    
    console.log('DOM 요소 상태:', results);
    
    // 각 요소 존재 여부 확인
    for (const [key, elem] of Object.entries(results)) {
        if (elem) {
            console.log(`✅ ${key} 존재함`);
            if (key === 'zoomWrapper') {
                const style = window.getComputedStyle(elem);
                console.log(`  - transform: ${style.transform}`);
                console.log(`  - transform-origin: ${style.transformOrigin}`);
            }
        } else {
            console.error(`❌ ${key} 없음!`);
        }
    }
    
    return results;
}

// 직접 줌 적용 테스트
function forceZoom(level) {
    console.log(`\n🎯 강제 줌 적용: ${level}%`);
    
    const wrapper = document.getElementById('zoomWrapper');
    const container = document.getElementById('treeContainer');
    const display = document.getElementById('zoomLevel');
    
    if (wrapper) {
        const scale = level / 100;
        
        // 방법 1: 직접 스타일 적용
        wrapper.style.transform = `scale(${scale})`;
        console.log(`✅ wrapper.style.transform = scale(${scale})`);
        
        // 방법 2: setAttribute 사용
        wrapper.setAttribute('style', 
            wrapper.getAttribute('style').replace(/transform:[^;]+;?/g, '') + 
            `transform: scale(${scale}) !important;`
        );
        console.log(`✅ setAttribute로 transform 적용`);
        
        // 방법 3: CSS 텍스트 직접 설정
        const currentStyle = wrapper.style.cssText;
        wrapper.style.cssText = currentStyle.replace(/transform:[^;]+;?/g, '') + 
            ` transform: scale(${scale}) !important;`;
        console.log(`✅ cssText로 transform 적용`);
        
        // 결과 확인
        setTimeout(() => {
            const computed = window.getComputedStyle(wrapper);
            console.log(`📊 적용 결과:`);
            console.log(`  - computed transform: ${computed.transform}`);
            console.log(`  - style.transform: ${wrapper.style.transform}`);
            
            const rect = wrapper.getBoundingClientRect();
            console.log(`  - 실제 크기: ${rect.width}x${rect.height}`);
        }, 100);
    } else if (container) {
        console.log('⚠️ zoomWrapper가 없어서 treeContainer에 적용 시도');
        const scale = level / 100;
        container.style.transform = `scale(${scale})`;
        container.style.transformOrigin = '0 0';
    } else {
        console.error('❌ 줌을 적용할 요소를 찾을 수 없습니다!');
    }
    
    // 디스플레이 업데이트
    if (display) {
        display.textContent = `${level}%`;
    }
    
    // 전역 상태 업데이트
    if (window.OrgChartState) {
        window.OrgChartState.zoomLevel = level;
    }
}

// 이벤트 리스너 확인
function checkEventListeners() {
    console.log('\n🔍 이벤트 리스너 확인...');
    
    const buttons = {
        zoomIn: document.getElementById('zoomIn'),
        zoomOut: document.getElementById('zoomOut'),
        zoomReset: document.getElementById('zoomReset')
    };
    
    for (const [name, btn] of Object.entries(buttons)) {
        if (btn) {
            // onclick 속성 확인
            console.log(`${name} onclick: ${btn.onclick || btn.getAttribute('onclick')}`);
            
            // 새 리스너 추가 (테스트용)
            const oldOnclick = btn.onclick;
            btn.onclick = function(e) {
                console.log(`🔘 ${name} 클릭됨!`);
                if (oldOnclick) oldOnclick.call(this, e);
            };
        }
    }
}

// 함수 존재 여부 확인
function checkFunctions() {
    console.log('\n🔍 함수 확인...');
    
    const functions = [
        'handleZoomIn',
        'handleZoomOut', 
        'handleZoomReset',
        'applyZoom',
        'updateZoom'
    ];
    
    functions.forEach(fname => {
        if (window[fname]) {
            console.log(`✅ window.${fname} 존재`);
            console.log(`  타입: ${typeof window[fname]}`);
        } else {
            console.error(`❌ window.${fname} 없음`);
        }
    });
}

// 전체 디버깅 실행
function runFullDebug() {
    console.log('====== 줌 기능 전체 디버깅 ======');
    
    checkDOMStatus();
    checkFunctions();
    checkEventListeners();
    
    console.log('\n📝 테스트 방법:');
    console.log('1. forceZoom(150) - 150%로 줌');
    console.log('2. forceZoom(50) - 50%로 줌');
    console.log('3. testZoomAnimation() - 애니메이션 테스트');
    
    // 전역 함수로 등록
    window.forceZoom = forceZoom;
    window.checkDOMStatus = checkDOMStatus;
    window.runZoomDebug = runFullDebug;
}

// 애니메이션 테스트
function testZoomAnimation() {
    console.log('🎬 줌 애니메이션 테스트 시작...');
    let level = 100;
    const interval = setInterval(() => {
        level += 10;
        if (level > 150) {
            level = 50;
        }
        forceZoom(level);
        
        if (level === 100) {
            clearInterval(interval);
            console.log('✅ 애니메이션 테스트 완료');
        }
    }, 500);
}

window.testZoomAnimation = testZoomAnimation;

// 페이지 로드 후 자동 실행
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runFullDebug);
} else {
    runFullDebug();
}

console.log('💡 콘솔에서 forceZoom(150) 또는 testZoomAnimation()을 실행해보세요.');