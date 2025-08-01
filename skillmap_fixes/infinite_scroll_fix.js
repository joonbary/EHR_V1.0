
// 스킬맵 대시보드 무한 스크롤 수정
(function() {
    'use strict';
    
    // 1. 스크롤 이벤트 디바운싱
    let scrollTimeout;
    const handleScroll = (e) => {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        
        scrollTimeout = setTimeout(() => {
            // 실제 스크롤 처리 로직
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight;
            const clientHeight = window.innerHeight;
            
            // 바닥 도달 체크 (100px 여유)
            if (scrollTop + clientHeight >= scrollHeight - 100) {
                loadMoreData();
            }
        }, 150); // 150ms 디바운스
    };
    
    // 2. 데이터 로딩 상태 관리
    let isLoading = false;
    let hasMoreData = true;
    let currentPage = 1;
    
    const loadMoreData = async () => {
        if (isLoading || !hasMoreData) return;
        
        isLoading = true;
        showLoadingIndicator();
        
        try {
            const response = await fetch(`/api/skillmap/data?page=${currentPage}`);
            if (!response.ok) throw new Error('Failed to load data');
            
            const data = await response.json();
            
            if (data.results.length === 0) {
                hasMoreData = false;
            } else {
                renderData(data.results);
                currentPage++;
            }
        } catch (error) {
            console.error('Error loading data:', error);
            showErrorMessage();
        } finally {
            isLoading = false;
            hideLoadingIndicator();
        }
    };
    
    // 3. 클린업 함수
    const cleanup = () => {
        window.removeEventListener('scroll', handleScroll);
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
    };
    
    // 4. 초기화
    const init = () => {
        // 기존 리스너 제거
        cleanup();
        
        // 새 리스너 추가
        window.addEventListener('scroll', handleScroll, { passive: true });
        
        // 페이지 언로드 시 클린업
        window.addEventListener('beforeunload', cleanup);
    };
    
    // DOM 준비 시 초기화
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
