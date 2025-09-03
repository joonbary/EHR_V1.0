/**
 * Organization Chart API Module
 * API 통신 전용 모듈
 * Version: 1.0
 * Date: 2025-01-21
 */

class OrgChartAPI {
    constructor(endpoint, csrfToken) {
        this.endpoint = endpoint;
        this.csrfToken = csrfToken;
    }

    /**
     * 조직도 트리 데이터 로드
     */
    async loadTreeData() {
        try {
            const data = await ApiUtils.get(this.endpoint);
            console.log('✅ Organization tree data loaded');
            return data;
        } catch (error) {
            console.error('❌ Failed to load organization tree:', error);
            
            if (error instanceof ApiError) {
                Toast.error(error.getUserMessage());
            } else {
                Toast.error('조직도 데이터를 불러올 수 없습니다.');
            }
            
            throw error;
        }
    }

    /**
     * 노드 자식 로드 (Lazy Loading)
     */
    async loadNodeChildren(nodeId, depth = 1) {
        try {
            const data = await ApiUtils.get(`${this.endpoint}/${nodeId}/children`, {
                depth: depth
            });
            
            console.log(`✅ Loaded children for node ${nodeId}`);
            return data;
        } catch (error) {
            console.error(`❌ Failed to load children for node ${nodeId}:`, error);
            Toast.error('하위 조직 정보를 불러올 수 없습니다.');
            throw error;
        }
    }

    /**
     * 노드 검색
     */
    async searchNodes(query) {
        try {
            const data = await ApiUtils.get(`${this.endpoint}/search`, {
                q: query
            });
            
            return data;
        } catch (error) {
            console.error('❌ Search failed:', error);
            return [];
        }
    }

    /**
     * 노드 업데이트
     */
    async updateNode(nodeId, updates) {
        try {
            const data = await ApiUtils.put(`${this.endpoint}/${nodeId}`, updates);
            Toast.success('조직 정보가 업데이트되었습니다.');
            return data;
        } catch (error) {
            console.error(`❌ Failed to update node ${nodeId}:`, error);
            Toast.error('조직 정보 업데이트에 실패했습니다.');
            throw error;
        }
    }

    /**
     * 노드 이동 (재배치)
     */
    async moveNode(nodeId, newParentId) {
        try {
            const data = await ApiUtils.post(`${this.endpoint}/${nodeId}/move`, {
                parent_id: newParentId
            });
            
            Toast.success('조직이 성공적으로 이동되었습니다.');
            return data;
        } catch (error) {
            console.error(`❌ Failed to move node ${nodeId}:`, error);
            Toast.error('조직 이동에 실패했습니다.');
            throw error;
        }
    }

    /**
     * Excel 내보내기
     */
    async exportToExcel() {
        try {
            const response = await fetch(`${this.endpoint}/export`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });
            
            if (!response.ok) {
                throw new Error('Export failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `organization_chart_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            Toast.success('Excel 파일이 다운로드되었습니다.');
        } catch (error) {
            console.error('❌ Export failed:', error);
            Toast.error('Excel 내보내기에 실패했습니다.');
            throw error;
        }
    }

    /**
     * Excel 가져오기
     */
    async importFromExcel(file) {
        try {
            const data = await ApiUtils.upload(`${this.endpoint}/import`, file);
            Toast.success('Excel 파일이 성공적으로 가져와졌습니다.');
            return data;
        } catch (error) {
            console.error('❌ Import failed:', error);
            Toast.error('Excel 가져오기에 실패했습니다.');
            throw error;
        }
    }
}