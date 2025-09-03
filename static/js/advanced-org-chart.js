/**
 * Advanced Organization Chart JavaScript
 * 리팩토링: HTML에서 JavaScript 분리 (작업지시서 4.1절)
 * Version: 2.2
 * Date: 2025-01-21
 */

// ===========================
// 1. 설정 및 상수 (Configuration)
// ===========================
const CONFIG = {
    // 카드 너비 설정
    NODE_WIDTH: 180,           // Normal 모드
    NODE_WIDTH_DENSE: 92,       // Dense 모드
    NODE_WIDTH_ULTRA: 72,       // Ultra 모드
    
    // 줌 설정
    ZOOM_MIN: 30,
    ZOOM_MAX: 200,
    ZOOM_STEP: 10,
    ZOOM_ULTRA_THRESHOLD: 80,
    ZOOM_DENSE_THRESHOLD: 95,
    
    // 클러스터 간격
    GROUP_SPACING_MULTIPLIER: {
        SAME_PARENT: 1.0,
        SAME_GRANDPARENT: 2.5,
        DIFFERENT_ROOT: 4.0
    },
    
    // 기타 설정
    BUCKET_THRESHOLD: 12,
    ANIMATION_DURATION: 300,
    SEARCH_DELAY: 300
};

// ===========================
// 2. 상태 관리 (State Management)
// ===========================
class OrgChartState {
    constructor() {
        this.nodes = new Map();
        this.edges = [];
        this.expandedNodes = new Set();
        this.focusedNode = null;
        this.zoomLevel = 100;
        this.currentView = 'vertical';
        this.searchQuery = '';
    }
    
    reset() {
        this.nodes.clear();
        this.edges = [];
        this.expandedNodes.clear();
        this.focusedNode = null;
    }
}

// ===========================
// 3. 유틸리티 함수 (Utilities)
// ===========================
const OrgChartUtils = {
    /**
     * 현재 뷰 모드 판별
     */
    getCurrentViewMode() {
        const zoom = window.orgChartState?.zoomLevel || 100;
        if (zoom < CONFIG.ZOOM_ULTRA_THRESHOLD) return 'ultra';
        if (zoom < CONFIG.ZOOM_DENSE_THRESHOLD) return 'dense';
        return 'normal';
    },
    
    /**
     * 모드별 설정 가져오기
     */
    getModeConfig(mode) {
        switch(mode) {
            case 'ultra':
                return {
                    width: CONFIG.NODE_WIDTH_ULTRA,
                    spacing: 18,
                    isVertical: true
                };
            case 'dense':
                return {
                    width: CONFIG.NODE_WIDTH_DENSE,
                    spacing: 24,
                    isVertical: true
                };
            default:
                return {
                    width: CONFIG.NODE_WIDTH,
                    spacing: 48,
                    isVertical: false
                };
        }
    },
    
    /**
     * 디바운스 함수
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// ===========================
// 4. 노드 렌더링 (Node Rendering)
// ===========================
class NodeRenderer {
    /**
     * Ultra 모드 노드 생성 (72px)
     */
    static createUltraNode(node) {
        const div = document.createElement('div');
        div.className = 'ultra-node org-node';
        div.id = `node-${node.id}`;
        div.style.width = `${CONFIG.NODE_WIDTH_ULTRA}px`;
        
        // 템플릿 리터럴로 HTML 생성
        div.innerHTML = this.getUltraNodeTemplate(node);
        this.attachEventListeners(div, node);
        
        return div;
    }
    
    /**
     * Dense 모드 노드 생성 (92px)
     */
    static createDenseNode(node) {
        const div = document.createElement('div');
        div.className = 'dense-node org-node';
        div.id = `node-${node.id}`;
        div.style.width = `${CONFIG.NODE_WIDTH_DENSE}px`;
        
        div.innerHTML = this.getDenseNodeTemplate(node);
        this.attachEventListeners(div, node);
        
        return div;
    }
    
    /**
     * Normal 모드 노드 생성 (180px)
     */
    static createNormalNode(node) {
        const div = document.createElement('div');
        div.className = 'org-node';
        div.id = `node-${node.id}`;
        div.style.width = `${CONFIG.NODE_WIDTH}px`;
        
        div.innerHTML = this.getNormalNodeTemplate(node);
        this.attachEventListeners(div, node);
        
        return div;
    }
    
    /**
     * 노드 템플릿 생성 함수들
     */
    static getUltraNodeTemplate(node) {
        return `
            <div class="node-spine ${node.type}"></div>
            <div class="node-content">
                <div class="vertical-cjk">${node.name}</div>
                <div class="node-stats">
                    <div class="v-chip">인원 ${node.headcount || 0}</div>
                </div>
            </div>
        `;
    }
    
    static getDenseNodeTemplate(node) {
        return `
            <div class="node-spine ${node.type}"></div>
            <div class="node-content">
                <div class="vertical-cjk">${node.name}</div>
                <div class="node-stats">
                    <div class="v-chip">인원 ${node.headcount || 0}</div>
                    <div class="v-chip">하위 ${node.childrenCount || 0}</div>
                </div>
            </div>
        `;
    }
    
    static getNormalNodeTemplate(node) {
        return `
            <div class="node-spine ${node.type}"></div>
            <div class="node-content">
                <div class="node-header">
                    <span class="node-type-badge">${this.getNodeTypeLabel(node.type)}</span>
                </div>
                <div class="node-name">${node.name}</div>
                <div class="node-stats">
                    <span>인원: ${node.headcount || 0}</span>
                    <span>하위: ${node.childrenCount || 0}</span>
                </div>
            </div>
        `;
    }
    
    static getNodeTypeLabel(type) {
        const labels = {
            'company': '회사',
            'division': '본부',
            'department': '부서',
            'team': '팀',
            'person': '개인'
        };
        return labels[type] || type;
    }
    
    static attachEventListeners(element, node) {
        element.addEventListener('click', () => {
            window.orgChart?.focusNode(node.id);
        });
    }
}

// ===========================
// 5. 레이아웃 엔진 (Layout Engine)
// ===========================
class LayoutEngine {
    /**
     * 클러스터 기반 간격 계산
     */
    static getClusterSpacing(node1, node2, baseSpacing) {
        if (!node1 || !node2) return baseSpacing;
        
        if (node1.parentId === node2.parentId) {
            return baseSpacing * CONFIG.GROUP_SPACING_MULTIPLIER.SAME_PARENT;
        }
        
        // 조부모 확인 로직...
        return baseSpacing * CONFIG.GROUP_SPACING_MULTIPLIER.DIFFERENT_ROOT;
    }
    
    /**
     * 트리 레이아웃 계산
     */
    static calculateTreeLayout(nodes, mode) {
        const config = OrgChartUtils.getModeConfig(mode);
        // 레이아웃 계산 로직...
        return nodes;
    }
}

// ===========================
// 6. 메인 차트 클래스 (Main Chart Class)
// ===========================
class AdvancedOrgChart {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.state = new OrgChartState();
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadData();
    }
    
    setupEventListeners() {
        // 줌 버튼
        document.getElementById('zoomIn')?.addEventListener('click', () => {
            this.updateZoom(this.state.zoomLevel + CONFIG.ZOOM_STEP);
        });
        
        document.getElementById('zoomOut')?.addEventListener('click', () => {
            this.updateZoom(this.state.zoomLevel - CONFIG.ZOOM_STEP);
        });
        
        // 검색
        const searchInput = document.getElementById('orgSearch');
        if (searchInput) {
            searchInput.addEventListener('input', 
                OrgChartUtils.debounce((e) => this.search(e.target.value), CONFIG.SEARCH_DELAY)
            );
        }
    }
    
    updateZoom(level) {
        this.state.zoomLevel = Math.max(CONFIG.ZOOM_MIN, Math.min(CONFIG.ZOOM_MAX, level));
        document.getElementById('zoomLevel').textContent = `${this.state.zoomLevel}%`;
        this.render();
    }
    
    focusNode(nodeId) {
        this.state.focusedNode = nodeId;
        this.render();
    }
    
    search(query) {
        this.state.searchQuery = query;
        this.render();
    }
    
    async loadData() {
        try {
            const response = await fetch('/api/organization/tree/');
            const data = await response.json();
            this.processData(data);
            this.render();
        } catch (error) {
            console.error('Failed to load organization data:', error);
        }
    }
    
    processData(data) {
        // 데이터 처리 로직
        this.state.reset();
        // ... 노드 추가 로직
    }
    
    render() {
        const mode = OrgChartUtils.getCurrentViewMode();
        const nodes = LayoutEngine.calculateTreeLayout(
            Array.from(this.state.nodes.values()),
            mode
        );
        
        // 기존 내용 제거
        this.container.innerHTML = '';
        
        // 노드 렌더링
        nodes.forEach(node => {
            let element;
            switch(mode) {
                case 'ultra':
                    element = NodeRenderer.createUltraNode(node);
                    break;
                case 'dense':
                    element = NodeRenderer.createDenseNode(node);
                    break;
                default:
                    element = NodeRenderer.createNormalNode(node);
            }
            this.container.appendChild(element);
        });
    }
}

// ===========================
// 7. 초기화 (Initialization)
// ===========================
document.addEventListener('DOMContentLoaded', () => {
    window.orgChart = new AdvancedOrgChart('treeContainer');
    window.orgChartState = window.orgChart.state; // 하위 호환성
    
    console.log('🎯 Advanced Org Chart v2.2 - Refactored');
});

// ===========================
// 8. 전역 함수 (Global Functions) - 하위 호환성
// ===========================
window.updateZoom = (level) => window.orgChart?.updateZoom(level);
window.getCurrentViewMode = () => OrgChartUtils.getCurrentViewMode();
window.expandToDepth = async (rootId, depth) => {
    // 구현...
    console.log(`Expanding to depth ${depth} from ${rootId}`);
};