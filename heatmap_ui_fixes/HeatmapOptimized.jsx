
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
