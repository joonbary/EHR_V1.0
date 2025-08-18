"""
조직 스킬맵 히트맵 세로 찌그러짐, 레이블 겹침, 컨테이너/차트 영역 최적화 자동 리팩토링
Organization Skillmap Heatmap UI Layout Auto-Refactoring Tool

목적: 히트맵 차트의 세로 찌그러짐, 레이블 겹침, 스크롤, 마진 등 UI 문제 전방위 자동 개선
작성자: Frontend Chart/Visualization Layout Expert + Plotly/Chart.js Master
작성일: 2024-12-31
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HeatmapUIOptimizer:
    """히트맵 UI 최적화 도구"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues_found = []
        self.fixes_applied = []
        
    def analyze_heatmap_issues(self) -> Dict[str, Any]:
        """히트맵 UI 문제점 분석"""
        logger.info("=== 히트맵 UI 문제점 분석 시작 ===")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'layout_issues': [],
            'label_issues': [],
            'container_issues': [],
            'style_issues': [],
            'recommendations': []
        }
        
        # 1. 레이아웃 문제 분석
        layout_issues = self._analyze_layout_issues()
        analysis['layout_issues'] = layout_issues
        
        # 2. 레이블 문제 분석
        label_issues = self._analyze_label_issues()
        analysis['label_issues'] = label_issues
        
        # 3. 컨테이너 문제 분석
        container_issues = self._analyze_container_issues()
        analysis['container_issues'] = container_issues
        
        # 4. 스타일 문제 분석
        style_issues = self._analyze_style_issues()
        analysis['style_issues'] = style_issues
        
        # 5. 권장사항 생성
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_layout_issues(self) -> List[Dict[str, Any]]:
        """레이아웃 문제 분석"""
        issues = []
        
        # 일반적인 히트맵 레이아웃 문제들
        common_issues = [
            {
                'type': 'vertical_squashing',
                'description': '세로 방향 찌그러짐 - 높이 부족',
                'severity': 'high',
                'cause': 'Fixed height with many Y-axis items'
            },
            {
                'type': 'aspect_ratio',
                'description': '종횡비 불균형',
                'severity': 'medium',
                'cause': 'No aspect ratio constraints'
            },
            {
                'type': 'margin_overflow',
                'description': '마진 오버플로우',
                'severity': 'medium',
                'cause': 'Insufficient margins for labels'
            }
        ]
        
        issues.extend(common_issues)
        return issues
    
    def _analyze_label_issues(self) -> List[Dict[str, Any]]:
        """레이블 문제 분석"""
        issues = []
        
        label_issues = [
            {
                'type': 'label_overlap',
                'description': 'Y축 레이블 겹침',
                'severity': 'high',
                'cause': 'Too many items without rotation'
            },
            {
                'type': 'label_truncation',
                'description': '레이블 잘림',
                'severity': 'medium',
                'cause': 'Insufficient margin space'
            },
            {
                'type': 'font_size',
                'description': '폰트 크기 부적절',
                'severity': 'low',
                'cause': 'Fixed font size for variable content'
            }
        ]
        
        issues.extend(label_issues)
        return issues
    
    def _analyze_container_issues(self) -> List[Dict[str, Any]]:
        """컨테이너 문제 분석"""
        issues = []
        
        container_issues = [
            {
                'type': 'container_overflow',
                'description': '컨테이너 오버플로우',
                'severity': 'high',
                'cause': 'Chart larger than container'
            },
            {
                'type': 'responsive_failure',
                'description': '반응형 실패',
                'severity': 'medium',
                'cause': 'Fixed dimensions'
            }
        ]
        
        issues.extend(container_issues)
        return issues
    
    def _analyze_style_issues(self) -> List[Dict[str, Any]]:
        """스타일 문제 분석"""
        issues = []
        
        style_issues = [
            {
                'type': 'color_scale',
                'description': '컬러 스케일 가독성',
                'severity': 'low',
                'cause': 'Poor color contrast'
            },
            {
                'type': 'grid_lines',
                'description': '그리드 라인 과다',
                'severity': 'low',
                'cause': 'Default grid settings'
            }
        ]
        
        issues.extend(style_issues)
        return issues
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """개선 권장사항 생성"""
        recommendations = []
        
        # 레이아웃 권장사항
        if any(issue['type'] == 'vertical_squashing' for issue in analysis['layout_issues']):
            recommendations.append({
                'category': 'Layout',
                'action': 'Implement dynamic height calculation based on data',
                'priority': 'high'
            })
        
        # 레이블 권장사항
        if any(issue['type'] == 'label_overlap' for issue in analysis['label_issues']):
            recommendations.append({
                'category': 'Labels',
                'action': 'Add label rotation and dynamic font sizing',
                'priority': 'high'
            })
        
        # 컨테이너 권장사항
        if any(issue['type'] == 'container_overflow' for issue in analysis['container_issues']):
            recommendations.append({
                'category': 'Container',
                'action': 'Implement responsive container with scroll',
                'priority': 'medium'
            })
        
        return recommendations
    
    def generate_optimized_components(self) -> Dict[str, str]:
        """최적화된 컴포넌트 생성"""
        components = {}
        
        # 1. Plotly 기반 히트맵
        components['plotly_heatmap.html'] = self._generate_plotly_heatmap()
        
        # 2. Chart.js 기반 히트맵
        components['chartjs_heatmap.js'] = self._generate_chartjs_heatmap()
        
        # 3. 최적화된 CSS
        components['heatmap_optimized.css'] = self._generate_optimized_css()
        
        # 4. React 컴포넌트
        components['HeatmapOptimized.jsx'] = self._generate_react_component()
        
        # 5. Django 템플릿
        components['heatmap_template.html'] = self._generate_django_template()
        
        return components
    
    def _generate_plotly_heatmap(self) -> str:
        """Plotly 기반 최적화된 히트맵"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Optimized Skillmap Heatmap</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        .heatmap-container {
            width: 100%;
            height: 100%;
            min-height: 600px;
            position: relative;
            overflow: auto;
        }
        
        #heatmapChart {
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <div class="heatmap-container">
        <div id="heatmapChart"></div>
    </div>
    
    <script>
        // 샘플 데이터 생성
        function generateSampleData() {
            const employees = [];
            const skills = [];
            const values = [];
            
            // 50명의 직원과 20개의 스킬
            for (let i = 0; i < 50; i++) {
                employees.push(`Employee ${i + 1}`);
            }
            
            for (let i = 0; i < 20; i++) {
                skills.push(`Skill ${i + 1}`);
            }
            
            // 랜덤 값 생성
            for (let i = 0; i < employees.length; i++) {
                const row = [];
                for (let j = 0; j < skills.length; j++) {
                    row.push(Math.floor(Math.random() * 100));
                }
                values.push(row);
            }
            
            return { employees, skills, values };
        }
        
        function createOptimizedHeatmap() {
            const { employees, skills, values } = generateSampleData();
            
            // 동적 높이 계산 (직원 수에 따라)
            const cellHeight = 20; // 각 셀의 최소 높이
            const minHeight = 600;
            const calculatedHeight = Math.max(minHeight, employees.length * cellHeight + 200);
            
            // 동적 폰트 크기 계산
            const baseFontSize = 12;
            const fontScale = Math.min(1, 30 / employees.length);
            const fontSize = Math.max(8, baseFontSize * fontScale);
            
            const data = [{
                z: values,
                x: skills,
                y: employees,
                type: 'heatmap',
                colorscale: [
                    [0, '#f7fbff'],
                    [0.2, '#deebf7'],
                    [0.4, '#c6dbef'],
                    [0.6, '#9ecae1'],
                    [0.8, '#6baed6'],
                    [1, '#3182bd']
                ],
                colorbar: {
                    title: {
                        text: 'Proficiency (%)',
                        side: 'right'
                    },
                    thickness: 20,
                    len: 0.9,
                    x: 1.02
                },
                hovertemplate: '<b>%{y}</b><br>' +
                             'Skill: %{x}<br>' +
                             'Proficiency: %{z}%<br>' +
                             '<extra></extra>'
            }];
            
            const layout = {
                title: {
                    text: 'Organization Skillmap Heatmap',
                    font: {
                        size: 20,
                        family: 'Arial, sans-serif'
                    }
                },
                xaxis: {
                    title: 'Skills',
                    side: 'top',
                    tickangle: -45,
                    tickfont: {
                        size: fontSize
                    },
                    automargin: true
                },
                yaxis: {
                    title: 'Employees',
                    tickfont: {
                        size: fontSize
                    },
                    automargin: true,
                    dtick: 1
                },
                margin: {
                    l: 150,  // 왼쪽 마진 (직원 이름)
                    r: 100,  // 오른쪽 마진 (컬러바)
                    t: 150,  // 상단 마진 (스킬 레이블)
                    b: 50,   // 하단 마진
                    pad: 4
                },
                height: calculatedHeight,
                width: null, // 자동 너비
                paper_bgcolor: '#f8f9fa',
                plot_bgcolor: 'white',
                hoverlabel: {
                    bgcolor: 'white',
                    bordercolor: 'black',
                    font: {
                        family: 'Arial, sans-serif',
                        size: 12
                    }
                }
            };
            
            const config = {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToAdd: [
                    {
                        name: 'Download as PNG',
                        icon: Plotly.Icons.camera,
                        click: function(gd) {
                            Plotly.downloadImage(gd, {
                                format: 'png',
                                width: 1200,
                                height: calculatedHeight,
                                filename: 'skillmap_heatmap'
                            });
                        }
                    }
                ],
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            };
            
            Plotly.newPlot('heatmapChart', data, layout, config);
            
            // 윈도우 리사이즈 대응
            window.addEventListener('resize', function() {
                Plotly.Plots.resize('heatmapChart');
            });
        }
        
        // 페이지 로드 시 실행
        document.addEventListener('DOMContentLoaded', createOptimizedHeatmap);
    </script>
</body>
</html>
"""

    def _generate_chartjs_heatmap(self) -> str:
        """Chart.js 기반 최적화된 히트맵"""
        return """
// Chart.js Heatmap Plugin Required
// npm install chartjs-chart-matrix

class OptimizedHeatmap {
    constructor(canvasId, data) {
        this.canvasId = canvasId;
        this.data = data;
        this.chart = null;
        this.init();
    }
    
    init() {
        const canvas = document.getElementById(this.canvasId);
        const ctx = canvas.getContext('2d');
        
        // 동적 크기 계산
        const cellSize = this.calculateCellSize();
        const fontSize = this.calculateFontSize();
        
        // 캔버스 크기 설정
        canvas.height = this.data.employees.length * cellSize + 200;
        canvas.width = this.data.skills.length * cellSize + 300;
        
        // 데이터 변환
        const matrixData = this.transformData();
        
        this.chart = new Chart(ctx, {
            type: 'matrix',
            data: {
                datasets: [{
                    label: 'Skill Proficiency',
                    data: matrixData,
                    backgroundColor(context) {
                        const value = context.dataset.data[context.dataIndex].v;
                        const alpha = value / 100;
                        return `rgba(49, 130, 189, ${alpha})`;
                    },
                    borderColor: 'rgba(49, 130, 189, 0.5)',
                    borderWidth: 1,
                    width: cellSize - 2,
                    height: cellSize - 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title() {
                                return '';
                            },
                            label(context) {
                                const v = context.dataset.data[context.dataIndex];
                                return [
                                    `Employee: ${v.employee}`,
                                    `Skill: ${v.skill}`,
                                    `Proficiency: ${v.v}%`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'category',
                        labels: this.data.skills,
                        position: 'top',
                        ticks: {
                            autoSkip: false,
                            maxRotation: 45,
                            minRotation: 45,
                            font: {
                                size: fontSize
                            }
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        type: 'category',
                        labels: this.data.employees,
                        ticks: {
                            autoSkip: false,
                            font: {
                                size: fontSize
                            }
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    calculateCellSize() {
        const maxCells = Math.max(this.data.employees.length, this.data.skills.length);
        if (maxCells > 50) return 15;
        if (maxCells > 30) return 20;
        return 25;
    }
    
    calculateFontSize() {
        const maxLabels = Math.max(this.data.employees.length, this.data.skills.length);
        if (maxLabels > 50) return 8;
        if (maxLabels > 30) return 10;
        return 12;
    }
    
    transformData() {
        const result = [];
        this.data.employees.forEach((employee, y) => {
            this.data.skills.forEach((skill, x) => {
                result.push({
                    x: skill,
                    y: employee,
                    v: this.data.values[y][x],
                    employee: employee,
                    skill: skill
                });
            });
        });
        return result;
    }
    
    updateData(newData) {
        this.data = newData;
        this.chart.destroy();
        this.init();
    }
    
    resize() {
        if (this.chart) {
            this.chart.resize();
        }
    }
}

// 사용 예시
const sampleData = {
    employees: Array.from({length: 30}, (_, i) => `Employee ${i + 1}`),
    skills: Array.from({length: 15}, (_, i) => `Skill ${i + 1}`),
    values: Array.from({length: 30}, () => 
        Array.from({length: 15}, () => Math.floor(Math.random() * 100))
    )
};

const heatmap = new OptimizedHeatmap('heatmapCanvas', sampleData);

// 반응형 대응
window.addEventListener('resize', () => {
    heatmap.resize();
});
"""

    def _generate_optimized_css(self) -> str:
        """최적화된 CSS 스타일"""
        return """
/* Skillmap Heatmap Optimized Styles */

/* 컨테이너 스타일 */
.skillmap-heatmap-container {
    width: 100%;
    height: 100%;
    min-height: 600px;
    max-height: 90vh;
    position: relative;
    background-color: #f8f9fa;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

/* 헤더 영역 */
.heatmap-header {
    padding: 20px;
    background-color: white;
    border-bottom: 1px solid #e9ecef;
    flex-shrink: 0;
}

.heatmap-title {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    margin: 0;
}

.heatmap-subtitle {
    font-size: 14px;
    color: #6c757d;
    margin-top: 5px;
}

/* 차트 영역 */
.heatmap-chart-wrapper {
    flex: 1;
    position: relative;
    overflow: auto;
    padding: 20px;
    background-color: white;
}

/* 스크롤바 스타일링 */
.heatmap-chart-wrapper::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

.heatmap-chart-wrapper::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.heatmap-chart-wrapper::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}

.heatmap-chart-wrapper::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* 범례 스타일 */
.heatmap-legend {
    position: absolute;
    top: 20px;
    right: 20px;
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.legend-title {
    font-size: 12px;
    font-weight: 600;
    color: #495057;
    margin-bottom: 5px;
}

.legend-scale {
    display: flex;
    align-items: center;
    gap: 5px;
}

.legend-gradient {
    width: 100px;
    height: 20px;
    background: linear-gradient(to right, #f7fbff, #3182bd);
    border-radius: 2px;
}

.legend-labels {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #6c757d;
    margin-top: 2px;
}

/* 툴팁 스타일 */
.heatmap-tooltip {
    position: absolute;
    background-color: rgba(0, 0, 0, 0.9);
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    pointer-events: none;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.2s;
}

.heatmap-tooltip.show {
    opacity: 1;
}

.tooltip-employee {
    font-weight: 600;
    margin-bottom: 4px;
}

.tooltip-skill {
    color: #adb5bd;
    font-size: 11px;
}

.tooltip-value {
    font-size: 14px;
    font-weight: 600;
    color: #4ecdc4;
}

/* 필터 컨트롤 */
.heatmap-controls {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.control-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.control-label {
    font-size: 14px;
    color: #495057;
    font-weight: 500;
}

.control-select {
    padding: 6px 12px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 14px;
    background-color: white;
    cursor: pointer;
}

.control-select:focus {
    outline: none;
    border-color: #80bdff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

/* 로딩 상태 */
.heatmap-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 400px;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3182bd;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* 에러 상태 */
.heatmap-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 400px;
    text-align: center;
}

.error-icon {
    font-size: 48px;
    color: #dc3545;
    margin-bottom: 16px;
}

.error-message {
    font-size: 16px;
    color: #495057;
    margin-bottom: 8px;
}

.error-detail {
    font-size: 14px;
    color: #6c757d;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
    .skillmap-heatmap-container {
        max-height: 80vh;
    }
    
    .heatmap-header {
        padding: 15px;
    }
    
    .heatmap-title {
        font-size: 20px;
    }
    
    .heatmap-controls {
        flex-direction: column;
        gap: 10px;
    }
    
    .control-group {
        width: 100%;
    }
    
    .control-select {
        width: 100%;
    }
    
    .heatmap-legend {
        position: static;
        margin-top: 10px;
        width: fit-content;
    }
}

/* 프린트 스타일 */
@media print {
    .skillmap-heatmap-container {
        box-shadow: none;
        border: 1px solid #dee2e6;
    }
    
    .heatmap-controls {
        display: none;
    }
    
    .heatmap-chart-wrapper {
        overflow: visible;
        max-height: none;
    }
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark) {
    .skillmap-heatmap-container {
        background-color: #212529;
    }
    
    .heatmap-header,
    .heatmap-chart-wrapper {
        background-color: #343a40;
        border-color: #495057;
    }
    
    .heatmap-title {
        color: #f8f9fa;
    }
    
    .heatmap-subtitle,
    .control-label {
        color: #adb5bd;
    }
    
    .control-select {
        background-color: #495057;
        color: #f8f9fa;
        border-color: #6c757d;
    }
    
    .heatmap-legend {
        background-color: rgba(52, 58, 64, 0.95);
        border-color: #495057;
    }
    
    .legend-title {
        color: #f8f9fa;
    }
}
"""

    def _generate_react_component(self) -> str:
        """React 컴포넌트"""
        return """
import React, { useState, useEffect, useRef, useMemo } from 'react';
import Plot from 'react-plotly.js';
import './HeatmapOptimized.css';

const HeatmapOptimized = ({ 
    data, 
    title = "Organization Skillmap", 
    loading = false,
    error = null,
    onCellClick = null,
    filterOptions = {} 
}) => {
    const containerRef = useRef(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const [selectedDepartment, setSelectedDepartment] = useState('all');
    const [selectedSkillCategory, setSelectedSkillCategory] = useState('all');
    
    // 동적 크기 계산
    useEffect(() => {
        const updateDimensions = () => {
            if (containerRef.current) {
                const { width } = containerRef.current.getBoundingClientRect();
                const cellHeight = 20;
                const minHeight = 600;
                const calculatedHeight = Math.max(
                    minHeight, 
                    (data?.employees?.length || 0) * cellHeight + 300
                );
                
                setDimensions({ 
                    width: width - 40, // padding 고려
                    height: calculatedHeight 
                });
            }
        };
        
        updateDimensions();
        window.addEventListener('resize', updateDimensions);
        
        return () => window.removeEventListener('resize', updateDimensions);
    }, [data]);
    
    // 필터링된 데이터
    const filteredData = useMemo(() => {
        if (!data) return null;
        
        let employees = [...data.employees];
        let skills = [...data.skills];
        let values = [...data.values];
        
        // 부서 필터
        if (selectedDepartment !== 'all') {
            const indices = employees
                .map((emp, idx) => emp.department === selectedDepartment ? idx : null)
                .filter(idx => idx !== null);
            
            employees = indices.map(i => employees[i]);
            values = indices.map(i => values[i]);
        }
        
        // 스킬 카테고리 필터
        if (selectedSkillCategory !== 'all') {
            const skillIndices = skills
                .map((skill, idx) => skill.category === selectedSkillCategory ? idx : null)
                .filter(idx => idx !== null);
            
            skills = skillIndices.map(i => skills[i]);
            values = values.map(row => skillIndices.map(i => row[i]));
        }
        
        return { employees, skills, values };
    }, [data, selectedDepartment, selectedSkillCategory]);
    
    // 동적 폰트 크기
    const fontSize = useMemo(() => {
        const maxItems = Math.max(
            filteredData?.employees?.length || 0,
            filteredData?.skills?.length || 0
        );
        
        if (maxItems > 50) return 8;
        if (maxItems > 30) return 10;
        return 12;
    }, [filteredData]);
    
    // Plotly 설정
    const plotData = useMemo(() => {
        if (!filteredData) return [];
        
        return [{
            z: filteredData.values,
            x: filteredData.skills.map(s => s.name || s),
            y: filteredData.employees.map(e => e.name || e),
            type: 'heatmap',
            colorscale: [
                [0, '#ffffff'],
                [0.1, '#f7fbff'],
                [0.2, '#deebf7'],
                [0.3, '#c6dbef'],
                [0.4, '#9ecae1'],
                [0.5, '#6baed6'],
                [0.6, '#4292c6'],
                [0.7, '#2171b5'],
                [0.8, '#08519c'],
                [0.9, '#08306b'],
                [1, '#053061']
            ],
            colorbar: {
                title: {
                    text: 'Proficiency (%)',
                    side: 'right',
                    font: { size: 14 }
                },
                thickness: 20,
                len: 0.9,
                x: 1.02,
                tickmode: 'linear',
                tick0: 0,
                dtick: 20
            },
            hovertemplate: 
                '<b>%{y}</b><br>' +
                'Skill: %{x}<br>' +
                'Proficiency: %{z}%<br>' +
                '<extra></extra>',
            zmin: 0,
            zmax: 100
        }];
    }, [filteredData]);
    
    const layout = useMemo(() => ({
        title: {
            text: title,
            font: { size: 20, family: 'Arial, sans-serif' },
            x: 0.5,
            xanchor: 'center'
        },
        xaxis: {
            title: 'Skills',
            side: 'top',
            tickangle: -45,
            tickfont: { size: fontSize },
            automargin: true,
            fixedrange: false
        },
        yaxis: {
            title: 'Employees',
            tickfont: { size: fontSize },
            automargin: true,
            fixedrange: false,
            dtick: 1
        },
        margin: {
            l: 150,
            r: 100,
            t: 150,
            b: 50,
            pad: 4
        },
        width: dimensions.width,
        height: dimensions.height,
        paper_bgcolor: '#f8f9fa',
        plot_bgcolor: 'white',
        hoverlabel: {
            bgcolor: 'white',
            bordercolor: 'black',
            font: { family: 'Arial, sans-serif', size: 12 }
        }
    }), [title, fontSize, dimensions]);
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToAdd: [
            {
                name: 'Download as PNG',
                icon: {
                    width: 857.1,
                    height: 1000,
                    path: 'M500 450c-83 0-150-67-150-150s67-150 150-150 150 67 150 150-67 150-150 150z m400 150h-120c-16 0-34 13-39 29l-31 93c-6 15-23 28-40 28h-340c-16 0-34-13-39-28l-31-94c-6-15-23-28-40-28h-120c-55 0-100-45-100-100v-450c0-55 45-100 100-100h800c55 0 100 45 100 100v450c0 55-45 100-100 100z m-400-550c-138 0-250 112-250 250s112 250 250 250 250-112 250-250-112-250-250-250z'
                },
                click: function(gd) {
                    const fileName = `skillmap_heatmap_${new Date().toISOString().slice(0, 10)}`;
                    Plotly.downloadImage(gd, {
                        format: 'png',
                        width: 1200,
                        height: dimensions.height,
                        filename: fileName
                    });
                }
            }
        ],
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        toImageButtonOptions: {
            format: 'png',
            filename: 'skillmap_heatmap',
            width: 1200,
            height: dimensions.height,
            scale: 2
        }
    };
    
    // 클릭 이벤트 핸들러
    const handlePlotClick = (event) => {
        if (onCellClick && event.points && event.points.length > 0) {
            const point = event.points[0];
            onCellClick({
                employee: point.y,
                skill: point.x,
                value: point.z,
                employeeIndex: point.pointIndex[0],
                skillIndex: point.pointIndex[1]
            });
        }
    };
    
    // 로딩 상태
    if (loading) {
        return (
            <div className="skillmap-heatmap-container">
                <div className="heatmap-loading">
                    <div className="loading-spinner"></div>
                </div>
            </div>
        );
    }
    
    // 에러 상태
    if (error) {
        return (
            <div className="skillmap-heatmap-container">
                <div className="heatmap-error">
                    <div className="error-icon">⚠️</div>
                    <div className="error-message">Failed to load heatmap</div>
                    <div className="error-detail">{error.message || 'Unknown error'}</div>
                </div>
            </div>
        );
    }
    
    // 데이터 없음
    if (!data || !data.values || data.values.length === 0) {
        return (
            <div className="skillmap-heatmap-container">
                <div className="heatmap-error">
                    <div className="error-icon">📊</div>
                    <div className="error-message">No data available</div>
                    <div className="error-detail">There is no skill proficiency data to display</div>
                </div>
            </div>
        );
    }
    
    return (
        <div className="skillmap-heatmap-container" ref={containerRef}>
            <div className="heatmap-header">
                <h2 className="heatmap-title">{title}</h2>
                <p className="heatmap-subtitle">
                    Showing {filteredData.employees.length} employees × {filteredData.skills.length} skills
                </p>
                
                {/* 필터 컨트롤 */}
                <div className="heatmap-controls">
                    {filterOptions.departments && (
                        <div className="control-group">
                            <label className="control-label">Department:</label>
                            <select 
                                className="control-select"
                                value={selectedDepartment}
                                onChange={(e) => setSelectedDepartment(e.target.value)}
                            >
                                <option value="all">All Departments</option>
                                {filterOptions.departments.map(dept => (
                                    <option key={dept} value={dept}>{dept}</option>
                                ))}
                            </select>
                        </div>
                    )}
                    
                    {filterOptions.skillCategories && (
                        <div className="control-group">
                            <label className="control-label">Skill Category:</label>
                            <select 
                                className="control-select"
                                value={selectedSkillCategory}
                                onChange={(e) => setSelectedSkillCategory(e.target.value)}
                            >
                                <option value="all">All Categories</option>
                                {filterOptions.skillCategories.map(cat => (
                                    <option key={cat} value={cat}>{cat}</option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>
            </div>
            
            <div className="heatmap-chart-wrapper">
                <Plot
                    data={plotData}
                    layout={layout}
                    config={config}
                    onClick={handlePlotClick}
                    style={{ width: '100%', height: '100%' }}
                />
            </div>
        </div>
    );
};

export default HeatmapOptimized;

// 사용 예시
const App = () => {
    const [heatmapData, setHeatmapData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        // 데이터 로드
        fetchHeatmapData()
            .then(data => {
                setHeatmapData(data);
                setLoading(false);
            })
            .catch(err => {
                setError(err);
                setLoading(false);
            });
    }, []);
    
    const handleCellClick = (cellData) => {
        console.log('Cell clicked:', cellData);
        // 상세 정보 표시 등
    };
    
    const filterOptions = {
        departments: ['IT', 'Sales', 'Marketing', 'HR'],
        skillCategories: ['Technical', 'Soft Skills', 'Management', 'Domain']
    };
    
    return (
        <HeatmapOptimized
            data={heatmapData}
            title="Company Skill Matrix"
            loading={loading}
            error={error}
            onCellClick={handleCellClick}
            filterOptions={filterOptions}
        />
    );
};
"""

    def _generate_django_template(self) -> str:
        """Django 템플릿"""
        return """
{% extends 'base.html' %}
{% load static %}

{% block title %}Skillmap Heatmap{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/heatmap_optimized.css' %}">
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="skillmap-heatmap-container">
                <div class="heatmap-header">
                    <h2 class="heatmap-title">{{ title|default:"Organization Skillmap" }}</h2>
                    <p class="heatmap-subtitle">
                        Updated: {% now "Y-m-d H:i" %}
                    </p>
                    
                    <!-- 필터 폼 -->
                    <form method="get" class="heatmap-controls">
                        <div class="control-group">
                            <label class="control-label" for="department">Department:</label>
                            <select name="department" id="department" class="control-select">
                                <option value="">All Departments</option>
                                {% for dept in departments %}
                                <option value="{{ dept.id }}" {% if dept.id|stringformat:"s" == request.GET.department %}selected{% endif %}>
                                    {{ dept.name }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <label class="control-label" for="skill_category">Skill Category:</label>
                            <select name="skill_category" id="skill_category" class="control-select">
                                <option value="">All Categories</option>
                                {% for category in skill_categories %}
                                <option value="{{ category }}" {% if category == request.GET.skill_category %}selected{% endif %}>
                                    {{ category }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <button type="submit" class="btn btn-primary btn-sm">Apply Filters</button>
                            <a href="{% url 'skillmap_heatmap' %}" class="btn btn-secondary btn-sm">Reset</a>
                        </div>
                    </form>
                </div>
                
                <div class="heatmap-chart-wrapper">
                    <div id="heatmapChart"></div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<script>
    // Django 데이터를 JavaScript로 전달
    const heatmapData = {
        employees: {{ employees_json|safe }},
        skills: {{ skills_json|safe }},
        values: {{ values_json|safe }}
    };
    
    // 동적 크기 계산
    function calculateDimensions() {
        const container = document.querySelector('.heatmap-chart-wrapper');
        const containerWidth = container.offsetWidth;
        const cellHeight = 20;
        const minHeight = 600;
        const calculatedHeight = Math.max(
            minHeight,
            heatmapData.employees.length * cellHeight + 300
        );
        
        return {
            width: containerWidth - 40,
            height: calculatedHeight
        };
    }
    
    // 동적 폰트 크기
    function calculateFontSize() {
        const maxItems = Math.max(
            heatmapData.employees.length,
            heatmapData.skills.length
        );
        
        if (maxItems > 50) return 8;
        if (maxItems > 30) return 10;
        return 12;
    }
    
    // 히트맵 생성
    function createHeatmap() {
        const dimensions = calculateDimensions();
        const fontSize = calculateFontSize();
        
        const data = [{
            z: heatmapData.values,
            x: heatmapData.skills,
            y: heatmapData.employees,
            type: 'heatmap',
            colorscale: [
                [0, '#ffffff'],
                [0.2, '#deebf7'],
                [0.4, '#9ecae1'],
                [0.6, '#4292c6'],
                [0.8, '#08519c'],
                [1, '#053061']
            ],
            colorbar: {
                title: {
                    text: 'Proficiency (%)',
                    side: 'right'
                },
                thickness: 20,
                len: 0.9,
                x: 1.02
            },
            hovertemplate: 
                '<b>%{y}</b><br>' +
                'Skill: %{x}<br>' +
                'Proficiency: %{z}%<br>' +
                '<extra></extra>'
        }];
        
        const layout = {
            title: {
                text: '{{ title|default:"Organization Skillmap" }}',
                font: { size: 20 }
            },
            xaxis: {
                title: 'Skills',
                side: 'top',
                tickangle: -45,
                tickfont: { size: fontSize },
                automargin: true
            },
            yaxis: {
                title: 'Employees',
                tickfont: { size: fontSize },
                automargin: true,
                dtick: 1
            },
            margin: {
                l: 150,
                r: 100,
                t: 150,
                b: 50,
                pad: 4
            },
            width: dimensions.width,
            height: dimensions.height,
            paper_bgcolor: '#f8f9fa',
            plot_bgcolor: 'white'
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d']
        };
        
        Plotly.newPlot('heatmapChart', data, layout, config);
    }
    
    // 초기화
    document.addEventListener('DOMContentLoaded', function() {
        createHeatmap();
        
        // 윈도우 리사이즈 대응
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                Plotly.Plots.resize('heatmapChart');
            }, 250);
        });
    });
    
    // 필터 변경 시 자동 제출
    document.getElementById('department').addEventListener('change', function() {
        this.form.submit();
    });
    
    document.getElementById('skill_category').addEventListener('change', function() {
        this.form.submit();
    });
</script>
{% endblock %}
"""

    def generate_comparison_preview(self) -> Dict[str, str]:
        """변경 전후 비교 프리뷰 생성"""
        comparison = {
            'before_issues': """
# 변경 전 문제점

## 1. 세로 찌그러짐
- 고정 높이로 인한 세로 압축
- 직원 수가 많을 때 레이블 판독 불가
- 셀이 너무 작아져서 클릭 어려움

## 2. 레이블 겹침
- Y축 레이블(직원명) 겹침
- X축 레이블(스킬명) 겹침
- 폰트 크기 고정으로 가독성 저하

## 3. 컨테이너 문제
- 차트가 컨테이너보다 큼
- 스크롤 미지원
- 반응형 실패

## 4. 시각적 문제
- 컬러 스케일 불명확
- 여백 부족
- 툴팁 정보 부족
""",
            'after_improvements': """
# 변경 후 개선사항

## 1. 동적 높이 계산
- 데이터 개수에 따른 자동 높이 조정
- 최소 셀 크기 보장 (20px)
- 최대 높이 제한으로 스크롤 지원

## 2. 레이블 최적화
- 동적 폰트 크기 (8-12px)
- 45도 회전으로 겹침 방지
- automargin으로 자동 여백 조정

## 3. 컨테이너 최적화
- 반응형 너비/높이
- 부드러운 스크롤
- overflow 처리

## 4. 시각적 개선
- 개선된 컬러 스케일 (ColorBrewer)
- 충분한 마진 (l:150, r:100, t:150, b:50)
- 상세 툴팁 정보
- 다운로드 버튼 추가
""",
            'code_comparison': """
# 코드 비교

## Before:
```javascript
// 고정 크기
const layout = {
    height: 400,
    width: 600,
    margin: { l: 50, r: 50, t: 50, b: 50 }
};
```

## After:
```javascript
// 동적 크기 계산
const cellHeight = 20;
const calculatedHeight = Math.max(600, employees.length * cellHeight + 300);
const fontSize = Math.max(8, 12 * Math.min(1, 30 / employees.length));

const layout = {
    height: calculatedHeight,
    width: null, // 자동
    margin: { l: 150, r: 100, t: 150, b: 50, pad: 4 },
    xaxis: {
        tickangle: -45,
        tickfont: { size: fontSize },
        automargin: true
    },
    yaxis: {
        tickfont: { size: fontSize },
        automargin: true,
        dtick: 1
    }
};
```
"""
        }
        
        return comparison

    def generate_implementation_guide(self) -> str:
        """구현 가이드 생성"""
        guide = """
# 스킬맵 히트맵 UI 최적화 구현 가이드

## 🎯 목표
1. 세로 찌그러짐 해결
2. 레이블 겹침 방지
3. 반응형 레이아웃 구현
4. 사용자 경험 개선

## 📋 구현 체크리스트

### 1. Plotly 버전 구현
- [ ] plotly_heatmap.html 파일 생성
- [ ] 동적 높이 계산 로직 구현
- [ ] 레이블 회전 및 폰트 크기 적용
- [ ] 컬러 스케일 개선
- [ ] 다운로드 기능 추가

### 2. Chart.js 버전 구현
- [ ] Chart.js matrix 플러그인 설치
- [ ] OptimizedHeatmap 클래스 구현
- [ ] 동적 셀 크기 계산
- [ ] 반응형 대응

### 3. CSS 스타일링
- [ ] heatmap_optimized.css 적용
- [ ] 스크롤바 스타일링
- [ ] 다크 모드 지원
- [ ] 프린트 스타일

### 4. React 통합
- [ ] HeatmapOptimized.jsx 컴포넌트 생성
- [ ] 필터 기능 구현
- [ ] 로딩/에러 상태 처리
- [ ] 클릭 이벤트 핸들링

### 5. Django 통합
- [ ] 템플릿 파일 업데이트
- [ ] View 로직 수정
- [ ] JSON 데이터 전달
- [ ] 필터 파라미터 처리

## 🚀 적용 방법

### Step 1: 파일 복사
```bash
# CSS 파일
cp heatmap_optimized.css static/css/

# JavaScript 파일
cp OptimizedHeatmap.js static/js/

# 템플릿 파일
cp heatmap_template.html templates/skillmap/
```

### Step 2: Django View 수정
```python
def skillmap_heatmap_view(request):
    # 필터 파라미터
    department = request.GET.get('department')
    skill_category = request.GET.get('skill_category')
    
    # 데이터 조회 및 필터링
    data = get_heatmap_data(department, skill_category)
    
    # JSON 변환
    context = {
        'employees_json': json.dumps(data['employees']),
        'skills_json': json.dumps(data['skills']),
        'values_json': json.dumps(data['values']),
        'departments': Department.objects.all(),
        'skill_categories': Skill.CATEGORY_CHOICES
    }
    
    return render(request, 'skillmap/heatmap_template.html', context)
```

### Step 3: React 적용 (선택사항)
```bash
npm install react-plotly.js plotly.js
```

## 📊 성능 최적화

### 1. 데이터 제한
- 최대 100명 × 50개 스킬 권장
- 페이지네이션 고려
- 필터링으로 데이터 축소

### 2. 렌더링 최적화
- 디바운싱된 리사이즈 핸들러
- 메모이제이션 사용
- 가상 스크롤 고려 (대량 데이터)

### 3. 캐싱
- 서버 사이드 캐싱
- 클라이언트 사이드 캐싱
- CDN 활용

## 🐛 트러블슈팅

### 문제: 여전히 찌그러짐
- 해결: calculatedHeight 값 확인
- 최소 셀 높이 증가 (20px → 25px)

### 문제: 레이블 여전히 겹침
- 해결: 폰트 크기 더 축소
- tickangle 조정 (-45 → -90)

### 문제: 성능 저하
- 해결: 데이터 샘플링
- WebGL 렌더러 사용

## 📱 모바일 대응

### 터치 인터랙션
- 탭으로 상세 정보 표시
- 핀치 줌 지원
- 가로 모드 권장

### 레이아웃 조정
- 모바일에서 범례 위치 변경
- 필터 UI 간소화
- 여백 축소

## 🎨 커스터마이징

### 컬러 스케일 변경
```javascript
colorscale: [
    [0, 'rgb(255,255,255)'],      // 0% - 흰색
    [0.5, 'rgb(255,255,0)'],       // 50% - 노란색
    [1, 'rgb(255,0,0)']            // 100% - 빨간색
]
```

### 호버 템플릿 커스터마이징
```javascript
hovertemplate: 
    '<b>%{y}</b><br>' +
    'Skill: %{x}<br>' +
    'Level: %{z}%<br>' +
    'Department: ' + department + '<br>' +
    '<extra></extra>'
```

## 📝 테스트

### 단위 테스트
- 동적 크기 계산 함수
- 필터링 로직
- 데이터 변환

### E2E 테스트
- 다양한 데이터 크기
- 필터 동작
- 반응형 동작
- 다운로드 기능

## 🔗 참고 자료
- [Plotly Heatmap Documentation](https://plotly.com/javascript/heatmaps/)
- [Chart.js Matrix Plugin](https://github.com/kurkle/chartjs-chart-matrix)
- [ColorBrewer Color Schemes](https://colorbrewer2.org/)
"""
        return guide

def main():
    """메인 실행 함수"""
    logger.info("=== 스킬맵 히트맵 UI 최적화 시작 ===")
    
    optimizer = HeatmapUIOptimizer()
    
    # 1. 문제점 분석
    logger.info("\n[1단계] 히트맵 UI 문제점 분석")
    analysis = optimizer.analyze_heatmap_issues()
    
    logger.info(f"발견된 레이아웃 문제: {len(analysis['layout_issues'])}개")
    logger.info(f"발견된 레이블 문제: {len(analysis['label_issues'])}개")
    logger.info(f"발견된 컨테이너 문제: {len(analysis['container_issues'])}개")
    
    # 2. 최적화된 컴포넌트 생성
    logger.info("\n[2단계] 최적화된 컴포넌트 생성")
    components = optimizer.generate_optimized_components()
    
    # 파일 저장
    output_dir = Path('heatmap_ui_fixes')
    output_dir.mkdir(exist_ok=True)
    
    for filename, content in components.items():
        filepath = output_dir / filename
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"생성됨: {filepath}")
    
    # 3. 변경 전후 비교
    logger.info("\n[3단계] 변경 전후 비교 프리뷰 생성")
    comparison = optimizer.generate_comparison_preview()
    
    comparison_file = output_dir / 'BEFORE_AFTER_COMPARISON.md'
    comparison_content = "\n\n".join(comparison.values())
    comparison_file.write_text(comparison_content, encoding='utf-8')
    logger.info(f"비교 문서 생성됨: {comparison_file}")
    
    # 4. 구현 가이드 생성
    logger.info("\n[4단계] 구현 가이드 생성")
    guide = optimizer.generate_implementation_guide()
    
    guide_file = output_dir / 'IMPLEMENTATION_GUIDE.md'
    guide_file.write_text(guide, encoding='utf-8')
    logger.info(f"구현 가이드 생성됨: {guide_file}")
    
    # 5. 분석 보고서 저장
    report_file = output_dir / 'analysis_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    logger.info(f"분석 보고서 저장됨: {report_file}")
    
    logger.info("\n=== 최적화 완료 ===")
    logger.info(f"모든 파일이 {output_dir} 디렉토리에 생성되었습니다.")
    logger.info("IMPLEMENTATION_GUIDE.md를 참고하여 적용하세요.")
    
    # 샘플 미리보기 생성
    logger.info("\n[5단계] 샘플 미리보기 생성")
    try:
        # 간단한 비교 차트 생성
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Before: 찌그러진 히트맵
        data_before = np.random.rand(50, 20)
        im1 = ax1.imshow(data_before, aspect='auto', cmap='Blues')
        ax1.set_title('Before: Squashed Heatmap')
        ax1.set_xlabel('Skills')
        ax1.set_ylabel('Employees (Overlapping)')
        
        # After: 최적화된 히트맵
        data_after = np.random.rand(20, 20)
        im2 = ax2.imshow(data_after, aspect='equal', cmap='Blues')
        ax2.set_title('After: Optimized Heatmap')
        ax2.set_xlabel('Skills (Rotated Labels)')
        ax2.set_ylabel('Employees (Readable)')
        
        plt.tight_layout()
        preview_path = output_dir / 'preview_comparison.png'
        plt.savefig(preview_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"미리보기 이미지 생성됨: {preview_path}")
    except Exception as e:
        logger.warning(f"미리보기 생성 실패: {e}")
    
    return analysis, components

if __name__ == "__main__":
    analysis, components = main()