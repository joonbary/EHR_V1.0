/**
 * Organization Chart Minimap Module
 * 미니맵 기능 전용 모듈
 * Version: 1.0
 * Date: 2025-01-21
 */

class OrgChartMinimap {
    constructor(canvasId, viewportId) {
        this.canvas = document.getElementById(canvasId);
        this.viewport = document.getElementById(viewportId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.scale = 0.1;
        this.initialized = false;
    }

    /**
     * 미니맵 초기화
     */
    init() {
        if (!this.canvas || !this.ctx) {
            console.warn('Minimap canvas not found');
            return;
        }

        // Canvas 크기 설정
        this.canvas.width = 150;
        this.canvas.height = 120;

        // 클릭 이벤트 리스너
        this.canvas.addEventListener('click', (e) => this.handleClick(e));

        this.initialized = true;
        console.log('✅ Minimap initialized');
    }

    /**
     * 미니맵 업데이트
     */
    update(nodes, viewport) {
        if (!this.initialized) return;

        // Canvas 클리어
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // 배경
        this.ctx.fillStyle = '#0a0f1e';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // 노드들의 경계 계산
        const bounds = this.calculateBounds(nodes);
        if (!bounds) return;

        // 스케일 계산
        const scaleX = this.canvas.width / bounds.width;
        const scaleY = this.canvas.height / bounds.height;
        this.scale = Math.min(scaleX, scaleY) * 0.9;

        // 오프셋 계산 (중앙 정렬)
        const offsetX = (this.canvas.width - bounds.width * this.scale) / 2;
        const offsetY = (this.canvas.height - bounds.height * this.scale) / 2;

        // 노드 그리기
        this.drawNodes(nodes, bounds, offsetX, offsetY);

        // 뷰포트 영역 그리기
        if (viewport) {
            this.drawViewport(viewport, bounds, offsetX, offsetY);
        }
    }

    /**
     * 노드들의 경계 계산
     */
    calculateBounds(nodes) {
        if (nodes.length === 0) return null;

        let minX = Infinity, minY = Infinity;
        let maxX = -Infinity, maxY = -Infinity;

        nodes.forEach(node => {
            if (node.x !== undefined && node.y !== undefined) {
                minX = Math.min(minX, node.x);
                minY = Math.min(minY, node.y);
                maxX = Math.max(maxX, node.x + (node.width || 180));
                maxY = Math.max(maxY, node.y + (node.height || 120));
            }
        });

        return {
            x: minX,
            y: minY,
            width: maxX - minX,
            height: maxY - minY
        };
    }

    /**
     * 노드 그리기
     */
    drawNodes(nodes, bounds, offsetX, offsetY) {
        nodes.forEach(node => {
            if (node.x === undefined || node.y === undefined) return;

            const x = (node.x - bounds.x) * this.scale + offsetX;
            const y = (node.y - bounds.y) * this.scale + offsetY;
            const width = (node.width || 180) * this.scale;
            const height = (node.height || 120) * this.scale;

            // 노드 타입별 색상
            const colors = {
                'company': '#22d3ee',
                'division': '#d946ef',
                'department': '#14b8a6',
                'team': '#64748b',
                'person': '#fbbf24'
            };

            this.ctx.fillStyle = colors[node.type] || '#38bdf8';
            this.ctx.globalAlpha = 0.6;
            this.ctx.fillRect(x, y, width, height);

            // 포커스된 노드 강조
            if (node.focused) {
                this.ctx.strokeStyle = '#00d4ff';
                this.ctx.lineWidth = 2;
                this.ctx.strokeRect(x - 1, y - 1, width + 2, height + 2);
            }
        });

        this.ctx.globalAlpha = 1;
    }

    /**
     * 뷰포트 영역 그리기
     */
    drawViewport(viewport, bounds, offsetX, offsetY) {
        const x = (viewport.x - bounds.x) * this.scale + offsetX;
        const y = (viewport.y - bounds.y) * this.scale + offsetY;
        const width = viewport.width * this.scale;
        const height = viewport.height * this.scale;

        // 뷰포트 영역
        this.ctx.strokeStyle = '#00d4ff';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(x, y, width, height);

        // 반투명 배경
        this.ctx.fillStyle = 'rgba(0, 212, 255, 0.1)';
        this.ctx.fillRect(x, y, width, height);

        // DOM 뷰포트 업데이트
        if (this.viewport) {
            this.viewport.style.left = `${x + 8}px`; // 8px padding
            this.viewport.style.top = `${y + 8}px`;
            this.viewport.style.width = `${width}px`;
            this.viewport.style.height = `${height}px`;
        }
    }

    /**
     * 클릭 핸들러
     */
    handleClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        // 클릭 위치를 실제 좌표로 변환
        const realX = x / this.scale;
        const realY = y / this.scale;

        // 이벤트 발생
        const customEvent = new CustomEvent('minimapClick', {
            detail: { x: realX, y: realY }
        });
        document.dispatchEvent(customEvent);
    }

    /**
     * 미니맵 표시/숨기기
     */
    toggle() {
        const container = this.canvas?.parentElement;
        if (container) {
            container.style.display = container.style.display === 'none' ? 'block' : 'none';
        }
    }

    /**
     * 미니맵 파괴
     */
    destroy() {
        if (this.canvas) {
            this.canvas.removeEventListener('click', this.handleClick);
        }
        this.initialized = false;
    }
}