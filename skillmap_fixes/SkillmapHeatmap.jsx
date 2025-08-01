
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Chart as ChartJS, registerables } from 'chart.js';
import { HeatmapChart } from '@chartjs/chart-heatmap';

ChartJS.register(...registerables);

const SkillmapHeatmap = ({ departmentId }) => {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const chartRef = useRef(null);
    const chartInstance = useRef(null);
    
    // 디버그 로깅
    const log = useCallback((stage, details) => {
        console.log(`[SkillmapHeatmap] ${stage}:`, {
            timestamp: new Date().toISOString(),
            loading,
            hasData: !!data,
            dataLength: data?.length || 0,
            error: error?.message || null,
            ...details
        });
    }, [loading, data, error]);
    
    // 데이터 페칭
    const fetchData = useCallback(async () => {
        log('FETCH_START', { departmentId });
        
        // 이미 로딩 중이면 중복 호출 방지
        if (loading && data) {
            log('FETCH_SKIP', { reason: 'Already loading' });
            return;
        }
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`/api/skillmap/heatmap/${departmentId}/`);
            log('FETCH_RESPONSE', { status: response.status });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const responseData = await response.json();
            log('FETCH_DATA', { 
                dataKeys: Object.keys(responseData),
                hasResults: !!responseData.results 
            });
            
            // 데이터 검증
            if (!responseData.results || responseData.results.length === 0) {
                log('DATA_EMPTY', { responseData });
                setData([]);
                return;
            }
            
            // 데이터 정제
            const cleanedData = responseData.results.map(item => ({
                x: item.skill || 'Unknown',
                y: item.employee || 'Unknown',
                v: Number.isFinite(item.proficiency) ? item.proficiency : 0
            }));
            
            log('DATA_CLEANED', { 
                originalCount: responseData.results.length,
                cleanedCount: cleanedData.length 
            });
            
            setData(cleanedData);
            
        } catch (err) {
            log('FETCH_ERROR', { error: err.message });
            setError(err);
            setData([]);
        } finally {
            // 무조건 로딩 상태 해제
            log('FETCH_COMPLETE', { willSetLoading: false });
            setLoading(false);
        }
    }, [departmentId, loading, data, log]);
    
    // 차트 렌더링
    const renderChart = useCallback(() => {
        log('RENDER_START', { hasData: !!data, dataLength: data?.length });
        
        if (!chartRef.current || !data || data.length === 0) {
            log('RENDER_SKIP', { 
                hasRef: !!chartRef.current,
                hasData: !!data,
                dataLength: data?.length 
            });
            return;
        }
        
        // 기존 차트 정리
        if (chartInstance.current) {
            log('RENDER_CLEANUP', { hadPreviousChart: true });
            chartInstance.current.destroy();
            chartInstance.current = null;
        }
        
        try {
            const ctx = chartRef.current.getContext('2d');
            
            chartInstance.current = new ChartJS(ctx, {
                type: 'heatmap',
                data: {
                    datasets: [{
                        label: 'Skill Proficiency',
                        data: data,
                        backgroundColor(context) {
                            const value = context.dataset.data[context.dataIndex].v;
                            const alpha = value / 100;
                            return `rgba(75, 192, 192, ${alpha})`;
                        },
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
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
                                label: (context) => {
                                    const item = context.dataset.data[context.dataIndex];
                                    return `${item.y}: ${item.v}% proficiency in ${item.x}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            type: 'category',
                            labels: [...new Set(data.map(d => d.x))]
                        },
                        y: {
                            type: 'category',
                            labels: [...new Set(data.map(d => d.y))]
                        }
                    }
                }
            });
            
            log('RENDER_SUCCESS', { chartCreated: true });
            
        } catch (err) {
            log('RENDER_ERROR', { error: err.message });
            console.error('Chart render error:', err);
        }
    }, [data, log]);
    
    // 초기 데이터 로드
    useEffect(() => {
        log('EFFECT_MOUNT', { departmentId });
        fetchData();
        
        return () => {
            log('EFFECT_CLEANUP', {});
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [departmentId]); // fetchData 의존성 제거로 무한 루프 방지
    
    // 데이터 변경 시 차트 렌더링
    useEffect(() => {
        if (!loading && data) {
            log('EFFECT_RENDER', { dataLength: data.length });
            renderChart();
        }
    }, [loading, data, renderChart]);
    
    // 렌더링
    log('COMPONENT_RENDER', { loading, hasData: !!data, hasError: !!error });
    
    if (loading) {
        return (
            <div className="heatmap-container loading">
                <div className="spinner-border" role="status">
                    <span className="sr-only">Loading...</span>
                </div>
                <p>Loading heatmap data...</p>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="heatmap-container error">
                <div className="alert alert-danger" role="alert">
                    <h4 className="alert-heading">Error loading heatmap</h4>
                    <p>{error.message}</p>
                    <button 
                        className="btn btn-primary" 
                        onClick={() => {
                            log('RETRY_CLICK', {});
                            fetchData();
                        }}
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }
    
    if (!data || data.length === 0) {
        return (
            <div className="heatmap-container empty">
                <div className="alert alert-info" role="alert">
                    <h4 className="alert-heading">No Data Available</h4>
                    <p>There is no skill proficiency data available for this department.</p>
                    <p>This could be because:</p>
                    <ul>
                        <li>No employees are assigned to this department</li>
                        <li>Skill assessments have not been completed</li>
                        <li>Data is still being processed</li>
                    </ul>
                </div>
            </div>
        );
    }
    
    return (
        <div className="heatmap-container">
            <div className="chart-wrapper" style={{ position: 'relative', height: '400px' }}>
                <canvas ref={chartRef}></canvas>
            </div>
            <div className="chart-info">
                <small className="text-muted">
                    Showing {data.length} skill proficiency data points
                </small>
            </div>
        </div>
    );
};

export default SkillmapHeatmap;
