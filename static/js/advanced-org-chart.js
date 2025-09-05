/**
 * Advanced Organization Chart JavaScript
 * 리팩토링: HTML에서 JavaScript 분리 (작업지시서 4.1절)
 * Version: 2.2
 * Date: 2025-01-21
 */

// 전역 스코프 관리를 위한 네임스페이스
// ===========================
// 1. 설정 및 상수 (Configuration)
// ===========================
// 전역 충돌 방지를 위해 조건부로 할당 (const 사용하지 않음)
if (!window.CONFIG) {
    window.CONFIG = {
        // 카드 너비 설정
        NODE_WIDTH: 180,           // Normal 모드
        NODE_WIDTH_DENSE: 35,       // Dense 모드 (PDF 스타일)
        NODE_WIDTH_ULTRA: 25,       // Ultra 모드 (PDF 스타일)
        
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
}

// CONFIG를 로컬 변수로 참조 (성능 향상)
const CONFIG = window.CONFIG;

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
     * 현재 뷰 모드 판별 - 항상 dense 모드 (PDF 스타일)
     */
    getCurrentViewMode() {
        // 줌 레벨과 상관없이 항상 PDF 스타일의 좁은 노드 사용
        // 줌은 CSS transform: scale로 처리하여 노드 크기는 일정하게 유지
        // 이렇게 하면 줌인/아웃 시에도 노드의 실제 크기는 35px로 유지됨
        return 'dense';
    },
    
    /**
     * 모드별 설정 가져오기
     */
    getModeConfig(mode) {
        switch(mode) {
            case 'ultra':
                return {
                    width: 25,  // PDF 스타일 좁은 노드
                    spacing: 35,
                    isVertical: true
                };
            case 'dense':
                return {
                    width: 35,  // PDF 스타일 좁은 노드 (약간 넓게)
                    spacing: 50,  // 노드 간 간격 (겹침 방지)
                    levelSpacing: 100, // 레벨 간 간격 (충분한 여유)
                    isVertical: true
                };
            default:
                return {
                    width: 30,  // 항상 좁은 노드
                    spacing: 40,
                    isVertical: true
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
        
        // 기본 스타일 추가 (CSS가 로드되지 않은 경우를 위한 fallback)
        div.style.cssText = `
            width: 25px;
            height: 40px;
            background: white;
            border: 1px solid #000;
            border-radius: 0;
            padding: 1px;
            cursor: pointer;
            color: black;
        `;
        
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
        
        // 글자 수에 따른 높이 동적 조정
        const nameLength = node.name.length;
        const minHeight = 45;  // 최소 높이를 약간 늘림
        const charHeight = 12; // 글자당 높이 (세로 모드)
        const padding = 20;    // 상하 패딩
        const nodeHeight = Math.max(minHeight, nameLength * charHeight + padding);
        
        // 기본 스타일 추가 (CSS가 로드되지 않은 경우를 위한 fallback)
        div.style.cssText = `
            width: 35px;
            height: ${nodeHeight}px;
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
        
        // 기본 스타일 추가 (CSS가 로드되지 않은 경우를 위한 fallback)
        div.style.cssText = `
            width: 30px;
            height: 40px;
            background: white;
            border: 1px solid #000;
            border-radius: 0;
            padding: 1px;
            cursor: pointer;
            color: black;
        `;
        
        div.innerHTML = this.getNormalNodeTemplate(node);
        this.attachEventListeners(div, node);
        
        return div;
    }
    
    /**
     * 노드 템플릿 생성 함수들
     */
    static getUltraNodeTemplate(node) {
        return `
            <div class="vertical-cjk" style="font-size: 10px; text-align: center; height: 100%;">${node.name}</div>
        `;
    }
    
    static getDenseNodeTemplate(node) {
        // 글자 수에 따른 폰트 크기 동적 조정
        const nameLength = node.name.length;
        let fontSize = 10;
        if (nameLength <= 4) {
            fontSize = 11;
        } else if (nameLength >= 8) {
            fontSize = 8;
        }
        
        return `
            <div class="vertical-cjk" style="font-size: ${fontSize}px; text-align: center; height: 100%; padding: 2px; line-height: 1.1;">${node.name}</div>
        `;
    }
    
    static getNormalNodeTemplate(node) {
        // Normal 모드도 PDF 스타일로 통일
        return `
            <div class="vertical-cjk" style="font-size: 10px; text-align: center; height: 100%;">${node.name}</div>
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
        
        // 루트 노드부터 시작
        const rootNodes = nodes.filter(n => !n.parent_id);
        if (rootNodes.length === 0) {
            console.warn('No root nodes found');
            return nodes;
        }
        
        // 노드를 레벨별로 그룹화
        const nodesByLevel = {};
        nodes.forEach(node => {
            const level = node.level || 1;
            if (!nodesByLevel[level]) {
                nodesByLevel[level] = [];
            }
            nodesByLevel[level].push(node);
        });
        
        // 각 레벨별로 위치 계산
        let currentY = 50; // 시작 Y 위치
        const levelKeys = Object.keys(nodesByLevel).sort((a, b) => a - b);
        
        levelKeys.forEach(level => {
            const levelNodes = nodesByLevel[level];
            let currentX = 50; // 각 레벨의 시작 X 위치
            
            // 부모별로 그룹화
            const nodesByParent = {};
            levelNodes.forEach(node => {
                const parentId = node.parent_id || 'root';
                if (!nodesByParent[parentId]) {
                    nodesByParent[parentId] = [];
                }
                nodesByParent[parentId].push(node);
            });
            
            // 각 그룹별로 위치 계산
            Object.keys(nodesByParent).forEach((parentId, groupIndex) => {
                const groupNodes = nodesByParent[parentId];
                
                // 그룹 간 추가 간격 (부서/팀 구분)
                if (groupIndex > 0) {
                    currentX += 30; // 그룹 간 추가 간격
                }
                
                groupNodes.forEach((node, index) => {
                    // 노드 위치 설정
                    node.x = currentX;
                    node.y = currentY;
                    node.width = config.width;
                    node.height = 40;  // 기본 높이 (createDenseNode에서 동적 조정됨)
                    
                    // 다음 노드를 위한 X 위치 업데이트
                    currentX += config.width + config.spacing;
                });
            });
            
            // 다음 레벨을 위한 Y 위치 업데이트
            currentY += config.levelSpacing || 100; // 레벨 간 충분한 간격
        });
        
        console.log('✅ Layout calculated for', nodes.length, 'nodes');
        return nodes;
    }
}

// ===========================
// 6. 메인 차트 클래스 (Main Chart Class)
// ===========================
class AdvancedOrgChart {
    constructor(config) {
        console.log('🎯 AdvancedOrgChart Constructor called with:', config);
        
        // Support both string and object parameters for backward compatibility
        if (typeof config === 'string') {
            this.containerId = config;
            this.container = document.getElementById(config);
            this.config = {
                apiEndpoint: '/employees/api/org/root',
                csrfToken: '',
                initialZoom: 100,
                enableMinimap: true,
                enableSearch: true
            };
        } else {
            this.containerId = config.container;
            this.container = document.getElementById(config.container);
            this.config = config;
        }
        
        // 컨테이너 존재 확인
        if (!this.container) {
            console.error('❌ Container element not found:', this.containerId);
            return;
        }
        
        console.log('✅ Container found:', this.container);
        console.log('📊 Config:', this.config);
        
        this.state = new OrgChartState();
        
        // API와 Minimap 초기화 전 null 체크
        if (typeof OrgChartAPI !== 'undefined') {
            this.api = new OrgChartAPI(this.config.apiEndpoint, this.config.csrfToken);
            console.log('✅ API initialized');
        } else {
            console.error('❌ OrgChartAPI class not found');
        }
        
        if (typeof OrgChartMinimap !== 'undefined') {
            this.minimap = new OrgChartMinimap('minimapCanvas', 'minimapViewport');
            console.log('✅ Minimap initialized');
        } else {
            console.warn('⚠️ OrgChartMinimap class not found');
        }
        
        this.init();
    }
    
    init() {
        console.log('🔄 Initializing AdvancedOrgChart...');
        this.setupEventListeners();
        this.loadData();
    }
    
    setupEventListeners() {
        // 이벤트 중복 등록 방지
        if (this.eventListenersSetup) {
            console.log('⚠️ Event listeners already set up, skipping...');
            return;
        }
        
        // 줌 버튼
        document.getElementById('zoomIn')?.addEventListener('click', () => {
            this.updateZoom(this.state.zoomLevel + CONFIG.ZOOM_STEP);
        });
        
        document.getElementById('zoomOut')?.addEventListener('click', () => {
            this.updateZoom(this.state.zoomLevel - CONFIG.ZOOM_STEP);
        });
        
        document.getElementById('zoomReset')?.addEventListener('click', () => {
            this.updateZoom(100);
        });
        
        // 검색
        const searchInput = document.getElementById('orgSearch');
        if (searchInput) {
            searchInput.addEventListener('input', 
                OrgChartUtils.debounce((e) => this.search(e.target.value), CONFIG.SEARCH_DELAY)
            );
        }
        
        this.eventListenersSetup = true;
    }
    
    updateZoom(level) {
        this.state.zoomLevel = Math.max(CONFIG.ZOOM_MIN, Math.min(CONFIG.ZOOM_MAX, level));
        document.getElementById('zoomLevel').textContent = `${this.state.zoomLevel}%`;
        
        // CSS transform을 사용하여 줌 적용 (노드 크기는 변하지 않음)
        const scale = this.state.zoomLevel / 100;
        if (this.container) {
            // transform-origin을 왼쪽 상단으로 설정하여 확대/축소 기준점 고정
            this.container.style.transform = `scale(${scale})`;
            this.container.style.transformOrigin = '0 0';
            
            // 스크롤 가능 영역 조정
            const viewport = document.getElementById('chartViewport');
            if (viewport) {
                // scale에 따른 실제 컨테이너 크기 조정
                const originalWidth = parseInt(this.container.style.width) || this.container.offsetWidth;
                const originalHeight = parseInt(this.container.style.height) || this.container.offsetHeight;
                viewport.style.width = `${originalWidth * scale}px`;
                viewport.style.height = `${originalHeight * scale}px`;
            }
        }
        
        // 미니맵 업데이트
        if (this.minimap) {
            this.minimap.update();
        }
    }
    
    focusNode(nodeId) {
        this.state.focusedNode = nodeId;
        this.render();
    }
    
    search(query) {
        this.state.searchQuery = query;
        this.render();
    }
    
    showErrorMessage(message) {
        if (this.container) {
            this.container.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 300px; color: #94a3b8;">
                    <div style="text-align: center;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                        <p style="font-size: 1.1rem;">${message}</p>
                    </div>
                </div>
            `;
        }
    }
    
    async loadData() {
        try {
            console.log('🔄 Loading organization data from:', this.config.apiEndpoint);
            
            // API가 없는 경우 직접 fetch
            if (!this.api) {
                console.log('⚠️ Using direct fetch as API is not initialized');
                const response = await fetch(this.config.apiEndpoint);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                console.log('📊 Fetched data:', data);
                this.processData(data);
                this.render();
                console.log('✅ Organization data loaded and rendered via direct fetch');
            } else {
                const data = await this.api.loadTreeData();
                console.log('📊 API returned data:', data);
                this.processData(data);
                this.render();
                console.log('✅ Organization data loaded and rendered via API');
            }
        } catch (error) {
            console.error('❌ Failed to load organization data:', error);
            console.error('Error stack:', error.stack);
            this.showErrorMessage('조직도 데이터를 불러올 수 없습니다. 서버 연결을 확인해주세요.');
        }
    }
    
    processData(data) {
        console.log('🔄 Processing organization data:', data);
        console.log('📊 Data type:', typeof data);
        console.log('📊 Is Array:', Array.isArray(data));
        console.log('📊 Has children:', data && data.children ? 'Yes' : 'No');
        
        if (data && data.children) {
            console.log('📊 Number of children:', data.children.length);
            console.log('📊 Children:', data.children);
        }
        
        // 데이터 처리 로직
        this.state.reset();
        
        // 단일 객체인 경우 배열로 래핑
        let nodeArray = data;
        if (!Array.isArray(data)) {
            if (data && typeof data === 'object') {
                // children이 있으면 평면화
                if (data.children && Array.isArray(data.children)) {
                    console.log('📊 Flattening tree structure...');
                    nodeArray = this.flattenTree(data);
                    console.log('📊 Flattened nodes count:', nodeArray.length);
                } else {
                    // 단일 노드만 있는 경우
                    nodeArray = [data];
                }
            } else {
                console.error('❌ Invalid data format:', data);
                return;
            }
        }
        
        // 노드 데이터를 Map에 저장
        nodeArray.forEach(node => {
            // 자식 노드 수 계산
            const childrenCount = nodeArray.filter(n => n.parent_id === node.id).length;
            
            // 멤버 수 계산 (members 배열이 있으면 사용, 없으면 기본값)
            const headcount = node.members ? node.members.length : (node.headcount || 0);
            
            this.state.nodes.set(node.id, {
                id: node.id,
                name: node.name,
                type: node.type || 'department',
                parent_id: node.parent_id,
                level: node.level || 1,
                description: node.description || '',
                members: node.members || [],
                headcount: headcount,
                childrenCount: childrenCount,
                x: 0,
                y: 0,
                width: CONFIG.NODE_WIDTH,
                height: 120,
                expanded: true
            });
        });
        
        console.log('✅ Processed', this.state.nodes.size, 'organization nodes');
        console.log('📊 Nodes in state:', Array.from(this.state.nodes.values()));
    }
    
    /**
     * 트리 구조를 평면 배열로 변환
     */
    flattenTree(node, result = [], parentId = null, level = 1) {
        // 현재 노드 추가
        const nodeData = {
            id: node.id || String(Date.now() + Math.random()),
            name: node.name,
            type: node.type || 'department',
            parent_id: parentId || node.parentId || node.parent_id || null,
            level: level,
            description: node.description || '',
            members: node.members || [],
            headcount: node.headcount || 0,
            childrenCount: node.childrenCount || (node.children ? node.children.length : 0)
        };
        
        result.push(nodeData);
        console.log(`  ➕ Added node: ${nodeData.name} (ID: ${nodeData.id}, Level: ${nodeData.level})`);
        
        // 자식 노드들 재귀적으로 처리
        if (node.children && Array.isArray(node.children)) {
            console.log(`  📂 Processing ${node.children.length} children of ${node.name}...`);
            node.children.forEach(child => {
                this.flattenTree(child, result, nodeData.id, level + 1);
            });
        }
        
        return result;
    }
    
    render() {
        console.log('🎨 Starting render process...');
        
        if (!this.container) {
            console.error('❌ Container not found');
            return;
        }
        
        console.log('📊 Container dimensions:', {
            width: this.container.offsetWidth,
            height: this.container.offsetHeight
        });
        
        const mode = OrgChartUtils.getCurrentViewMode();
        console.log('📊 Current view mode:', mode);
        
        const nodes = LayoutEngine.calculateTreeLayout(
            Array.from(this.state.nodes.values()),
            mode
        );
        
        console.log('📊 Nodes after layout calculation:', nodes.length);
        
        // 기존 내용 제거
        this.container.innerHTML = '';
        
        // 컨테이너 스타일 설정
        this.container.style.position = 'relative';
        this.container.style.width = '100%';
        this.container.style.height = '100%';
        
        // 노드가 없는 경우
        if (nodes.length === 0) {
            this.showErrorMessage('표시할 조직도 데이터가 없습니다.');
            return;
        }
        
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
            
            // 위치 스타일 적용
            element.style.position = 'absolute';
            element.style.left = `${node.x}px`;
            element.style.top = `${node.y}px`;
            
            // Dense 모드에서는 동적 높이 사용
            if (mode === 'dense') {
                // height는 createDenseNode에서 이미 설정됨
                element.style.width = '35px';
            } else {
                element.style.width = `${node.width}px`;
                element.style.height = `${node.height}px`;
            }
            
            this.container.appendChild(element);
            
            // DOM에 실제로 추가되었는지 확인
            const addedElement = document.getElementById(`node-${node.id}`);
            if (addedElement) {
                console.log(`✅ Node ${node.id} added to DOM at (${node.x}, ${node.y})`);
                console.log(`   Dimensions: ${node.width}x${node.height}`);
                console.log(`   Computed styles:`, {
                    display: window.getComputedStyle(addedElement).display,
                    visibility: window.getComputedStyle(addedElement).visibility,
                    position: window.getComputedStyle(addedElement).position
                });
            } else {
                console.error(`❌ Failed to add node ${node.id} to DOM`);
            }
        });
        
        // 컨테이너 크기 조정 (스크롤 가능하도록)
        const maxX = Math.max(...nodes.map(n => n.x + n.width)) + 100;
        const maxY = Math.max(...nodes.map(n => n.y + n.height)) + 100;
        this.container.style.minWidth = `${maxX}px`;
        this.container.style.minHeight = `${maxY}px`;
        
        console.log(`✅ Rendered ${nodes.length} nodes in ${mode} mode`);
    }
}

// ===========================
// 7. 전역 노출 (Global Export)
// ===========================
// 클래스들을 전역으로 노출
window.AdvancedOrgChart = AdvancedOrgChart;
window.OrgChartState = OrgChartState;
window.NodeRenderer = NodeRenderer;
window.LayoutEngine = LayoutEngine;
window.OrgChartUtils = OrgChartUtils;
window.CONFIG = CONFIG; // CONFIG도 전역으로 노출

console.log('🎯 Advanced Org Chart v2.2 - Classes Exported');

// ===========================
// 8. 전역 함수 (Global Functions) - 하위 호환성
// ===========================
window.updateZoom = (level) => window.orgChart?.updateZoom(level);
window.getCurrentViewMode = () => OrgChartUtils.getCurrentViewMode();
window.expandToDepth = async (rootId, depth) => {
    console.log(`Expanding to depth ${depth} from ${rootId}`);
    // TODO: 실제 depth 확장 구현 필요
    // 현재는 로그만 출력
};