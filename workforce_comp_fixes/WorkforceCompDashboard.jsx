
import React, { useState, useEffect, useCallback } from 'react';
import { APIResponseTransformer } from './api_transformer';
import { SafeDataAccessor } from './safe_data_accessor';

const WorkforceCompDashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // 디버그 로깅
    const log = useCallback((action, details) => {
        console.log(`[WorkforceCompDashboard] ${action}:`, {
            timestamp: new Date().toISOString(),
            ...details
        });
    }, []);
    
    // 데이터 페칭
    const fetchDashboardData = useCallback(async () => {
        log('FETCH_START', { endpoint: '/api/workforce-comp/summary/' });
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch('/api/workforce-comp/summary/');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const rawData = await response.json();
            log('FETCH_SUCCESS', { rawData });
            
            // 데이터 변환
            const transformedData = APIResponseTransformer.transform(rawData);
            log('DATA_TRANSFORMED', { transformedData });
            
            setData(transformedData);
            
        } catch (err) {
            log('FETCH_ERROR', { error: err.message });
            setError(err);
            setData(APIResponseTransformer.getDefaultResponse());
        } finally {
            setLoading(false);
        }
    }, [log]);
    
    // 초기 데이터 로드
    useEffect(() => {
        fetchDashboardData();
    }, [fetchDashboardData]);
    
    // Summary Cards 렌더링
    const renderSummaryCards = () => {
        const workforce = SafeDataAccessor.get(data, 'workforce', {});
        const compensation = SafeDataAccessor.get(data, 'compensation', {});
        
        const cards = [
            {
                title: '전체 직원수',
                value: SafeDataAccessor.get(workforce, 'totalEmployees', 0),
                change: SafeDataAccessor.get(workforce, 'changePercent', 0),
                icon: '👥'
            },
            {
                title: '평균 급여',
                value: SafeDataAccessor.formatCurrency(
                    SafeDataAccessor.get(compensation, 'avgSalary', 0)
                ),
                change: SafeDataAccessor.get(compensation, 'salaryGrowth', 0),
                icon: '💰'
            },
            {
                title: '신규 채용',
                value: SafeDataAccessor.get(workforce, 'newHiresMonth', 0),
                change: SafeDataAccessor.get(workforce, 'hiringTrend', 0),
                icon: '📈'
            },
            {
                title: '총 인건비',
                value: SafeDataAccessor.formatCurrency(
                    SafeDataAccessor.get(compensation, 'totalPayroll', 0)
                ),
                change: SafeDataAccessor.get(compensation, 'payrollGrowth', 0),
                icon: '💵'
            }
        ];
        
        return (
            <div className="summary-cards">
                {cards.map((card, index) => (
                    <div key={index} className="summary-card">
                        <div className="card-icon">{card.icon}</div>
                        <div className="card-content">
                            <h3>{card.title}</h3>
                            <p className="card-value">{card.value}</p>
                            <p className={`card-change ${card.change >= 0 ? 'positive' : 'negative'}`}>
                                {card.change >= 0 ? '▲' : '▼'} {Math.abs(card.change)}%
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        );
    };
    
    // Department Table 렌더링
    const renderDepartmentTable = () => {
        const departments = SafeDataAccessor.getArray(
            SafeDataAccessor.get(data, 'departments', [])
        );
        
        if (departments.length === 0) {
            return <div className="no-data">부서 데이터가 없습니다.</div>;
        }
        
        return (
            <table className="department-table">
                <thead>
                    <tr>
                        <th>부서명</th>
                        <th>직원수</th>
                        <th>평균 급여</th>
                        <th>총 인건비</th>
                        <th>변동률</th>
                    </tr>
                </thead>
                <tbody>
                    {departments.map((dept, index) => (
                        <tr key={index}>
                            <td>{SafeDataAccessor.getString(dept.name, 'Unknown')}</td>
                            <td>{SafeDataAccessor.get(dept, 'employeeCount', 0)}</td>
                            <td>{SafeDataAccessor.formatCurrency(dept.avgSalary)}</td>
                            <td>{SafeDataAccessor.formatCurrency(dept.totalSalary)}</td>
                            <td className={dept.change >= 0 ? 'positive' : 'negative'}>
                                {SafeDataAccessor.formatPercent(dept.change)}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        );
    };
    
    // 로딩 상태
    if (loading) {
        return (
            <div className="dashboard-loading">
                <div className="spinner"></div>
                <p>대시보드 데이터를 불러오는 중...</p>
            </div>
        );
    }
    
    // 에러 상태
    if (error && !data) {
        return (
            <div className="dashboard-error">
                <h2>데이터 로드 실패</h2>
                <p>{error.message}</p>
                <button onClick={fetchDashboardData}>다시 시도</button>
            </div>
        );
    }
    
    // 메인 렌더링
    return (
        <div className="workforce-comp-dashboard">
            <div className="dashboard-header">
                <h1>인력/보상 현황 대시보드</h1>
                <button className="refresh-btn" onClick={fetchDashboardData}>
                    새로고침
                </button>
            </div>
            
            {error && (
                <div className="warning-banner">
                    일부 데이터를 불러오는데 문제가 있습니다. 
                    표시된 데이터는 캐시된 정보일 수 있습니다.
                </div>
            )}
            
            <section className="dashboard-section">
                <h2>핵심 지표</h2>
                {renderSummaryCards()}
            </section>
            
            <section className="dashboard-section">
                <h2>부서별 현황</h2>
                {renderDepartmentTable()}
            </section>
            
            <section className="dashboard-section">
                <h2>급여 분포</h2>
                <SalaryDistributionChart 
                    data={SafeDataAccessor.get(data, 'salaryDistribution', [])} 
                />
            </section>
        </div>
    );
};

// 급여 분포 차트 컴포넌트
const SalaryDistributionChart = ({ data }) => {
    const chartData = SafeDataAccessor.getArray(data);
    
    if (chartData.length === 0) {
        return <div className="no-data">차트 데이터가 없습니다.</div>;
    }
    
    // Chart.js 또는 다른 차트 라이브러리 사용
    return (
        <div className="salary-chart">
            {/* 차트 구현 */}
            <canvas id="salaryChart"></canvas>
        </div>
    );
};

export default WorkforceCompDashboard;
