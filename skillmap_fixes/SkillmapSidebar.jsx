
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { throttle } from 'lodash';

const SkillmapSidebar = ({ departmentId, onEmployeeSelect }) => {
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [displayCount, setDisplayCount] = useState(20);
    const scrollContainerRef = useRef(null);
    
    // 디버그 로깅
    const log = useCallback((stage, details) => {
        console.log(`[SkillmapSidebar] ${stage}:`, {
            timestamp: new Date().toISOString(),
            loading,
            employeeCount: employees.length,
            displayCount,
            ...details
        });
    }, [loading, employees.length, displayCount]);
    
    // 직원 데이터 페칭
    const fetchEmployees = useCallback(async () => {
        log('FETCH_START', { departmentId });
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`/api/employees/department/${departmentId}/`);
            log('FETCH_RESPONSE', { status: response.status });
            
            if (!response.ok) {
                throw new Error(`Failed to fetch employees: ${response.status}`);
            }
            
            const data = await response.json();
            log('FETCH_DATA', { 
                employeeCount: data.results?.length || 0 
            });
            
            setEmployees(data.results || []);
            
        } catch (err) {
            log('FETCH_ERROR', { error: err.message });
            setError(err);
            setEmployees([]);
        } finally {
            log('FETCH_COMPLETE', { willSetLoading: false });
            setLoading(false);
        }
    }, [departmentId, log]);
    
    // 스크롤 핸들러 (throttled)
    const handleScroll = useRef(
        throttle(() => {
            if (!scrollContainerRef.current) return;
            
            const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
            const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
            
            log('SCROLL', { 
                scrollPercentage: scrollPercentage.toFixed(2),
                currentDisplay: displayCount 
            });
            
            // 80% 이상 스크롤 시 더 보기
            if (scrollPercentage > 80 && displayCount < employees.length) {
                const newCount = Math.min(displayCount + 20, employees.length);
                log('LOAD_MORE', { 
                    oldCount: displayCount, 
                    newCount 
                });
                setDisplayCount(newCount);
            }
        }, 300)
    ).current;
    
    // 초기 로드
    useEffect(() => {
        log('EFFECT_MOUNT', {});
        fetchEmployees();
    }, [departmentId]); // fetchEmployees 의존성 제거
    
    // 스크롤 이벤트 등록
    useEffect(() => {
        const container = scrollContainerRef.current;
        if (!container) return;
        
        log('SCROLL_ATTACH', {});
        container.addEventListener('scroll', handleScroll);
        
        return () => {
            log('SCROLL_DETACH', {});
            container.removeEventListener('scroll', handleScroll);
            handleScroll.cancel(); // throttle 취소
        };
    }, [handleScroll]);
    
    // 직원 클릭 핸들러
    const handleEmployeeClick = useCallback((employee) => {
        log('EMPLOYEE_CLICK', { employeeId: employee.id });
        onEmployeeSelect?.(employee);
    }, [onEmployeeSelect, log]);
    
    // 렌더링
    log('COMPONENT_RENDER', { 
        loading, 
        hasError: !!error,
        visibleEmployees: Math.min(displayCount, employees.length)
    });
    
    if (loading) {
        return (
            <div className="sidebar-panel loading">
                <div className="text-center p-4">
                    <div className="spinner-border" role="status">
                        <span className="sr-only">Loading...</span>
                    </div>
                    <p className="mt-2">Loading employees...</p>
                </div>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="sidebar-panel error">
                <div className="alert alert-danger m-3" role="alert">
                    <h5 className="alert-heading">Error</h5>
                    <p>{error.message}</p>
                    <button 
                        className="btn btn-sm btn-primary"
                        onClick={() => {
                            log('RETRY_CLICK', {});
                            fetchEmployees();
                        }}
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }
    
    if (employees.length === 0) {
        return (
            <div className="sidebar-panel empty">
                <div className="alert alert-info m-3" role="alert">
                    <h5 className="alert-heading">No Employees</h5>
                    <p>No employees found in this department.</p>
                </div>
            </div>
        );
    }
    
    // 표시할 직원 목록 (slice 적용)
    const visibleEmployees = employees.slice(0, displayCount);
    
    return (
        <div className="sidebar-panel">
            <div className="panel-header p-3 border-bottom">
                <h5 className="mb-0">Employees ({employees.length})</h5>
                <small className="text-muted">
                    Showing {visibleEmployees.length} of {employees.length}
                </small>
            </div>
            
            <div 
                ref={scrollContainerRef}
                className="panel-body"
                style={{
                    maxHeight: '500px',
                    overflowY: 'auto',
                    overflowX: 'hidden'
                }}
            >
                <div className="employee-list">
                    {visibleEmployees.map((employee) => (
                        <div
                            key={employee.id}
                            className="employee-item p-3 border-bottom"
                            onClick={() => handleEmployeeClick(employee)}
                            style={{ cursor: 'pointer' }}
                        >
                            <div className="employee-name font-weight-bold">
                                {employee.name}
                            </div>
                            <div className="employee-info text-muted small">
                                {employee.job_title || 'No Title'}
                            </div>
                            <div className="employee-skills">
                                <span className="badge badge-secondary">
                                    {employee.skill_count || 0} skills
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
                
                {displayCount < employees.length && (
                    <div className="text-center p-3">
                        <small className="text-muted">
                            Scroll down to load more...
                        </small>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SkillmapSidebar;
