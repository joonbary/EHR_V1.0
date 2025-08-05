
// 스킬맵 대시보드 수정 검증 테스트

describe('Skillmap Dashboard Fixed Tests', () => {
    beforeEach(() => {
        cy.visit('/dashboards/skillmap/');
        cy.wait(1000);
    });
    
    it('should not have infinite loading on heatmap', () => {
        // 로딩 인디케이터 확인
        cy.get('.heatmap-container.loading').should('be.visible');
        
        // 5초 내에 로딩 완료 확인
        cy.get('.heatmap-container', { timeout: 5000 })
            .should('not.have.class', 'loading');
        
        // 차트 또는 빈 상태 메시지 확인
        cy.get('.heatmap-container').within(() => {
            cy.get('canvas').should('exist')
                .or(cy.get('.alert').should('exist'));
        });
    });
    
    it('should handle empty data gracefully', () => {
        // 빈 부서 선택
        cy.get('.department-selector select').select('HR');
        cy.wait(2000);
        
        // 빈 데이터 메시지 확인
        cy.get('.heatmap-container.empty .alert-info')
            .should('be.visible')
            .and('contain', 'No Data Available');
    });
    
    it('should not have infinite scroll on sidebar', () => {
        // 사이드바 스크롤 컨테이너 확인
        cy.get('.panel-body').should('have.css', 'max-height', '500px');
        cy.get('.panel-body').should('have.css', 'overflow-y', 'auto');
        
        // 직원 목록 확인
        cy.get('.employee-list .employee-item').should('have.length.at.least', 1);
        
        // 스크롤 테스트
        cy.get('.panel-body').scrollTo('bottom');
        cy.wait(500);
        
        // 추가 로드 확인 (있는 경우)
        cy.get('.employee-list .employee-item').then($items => {
            const initialCount = $items.length;
            cy.log(`Initial employee count: ${initialCount}`);
        });
    });
    
    it('should log all state changes', () => {
        // 콘솔 로그 캡처
        cy.window().then((win) => {
            cy.spy(win.console, 'log');
        });
        
        // 부서 변경
        cy.get('.department-selector select').select('Sales');
        cy.wait(2000);
        
        // 로그 확인
        cy.window().then((win) => {
            expect(win.console.log).to.be.calledWithMatch('[SkillmapDashboard');
            expect(win.console.log).to.be.calledWithMatch('DEPARTMENT_CHANGE');
            expect(win.console.log).to.be.calledWithMatch('FETCH_START');
            expect(win.console.log).to.be.calledWithMatch('FETCH_COMPLETE');
        });
    });
});
