
import React, { useState, useEffect, useCallback } from 'react';
import SkillmapHeatmap from './SkillmapHeatmap';
import SkillmapSidebar from './SkillmapSidebar';

const SkillmapDashboard = () => {
    const [selectedDepartment, setSelectedDepartment] = useState('IT');
    const [selectedEmployee, setSelectedEmployee] = useState(null);
    const [dashboardLoading, setDashboardLoading] = useState(false);
    
    // 마스터 로깅
    const log = useCallback((component, stage, details) => {
        console.log(`[SkillmapDashboard-${component}] ${stage}:`, {
            timestamp: new Date().toISOString(),
            selectedDepartment,
            selectedEmployee: selectedEmployee?.id || null,
            dashboardLoading,
            ...details
        });
    }, [selectedDepartment, selectedEmployee, dashboardLoading]);
    
    // 부서 변경 핸들러
    const handleDepartmentChange = useCallback((dept) => {
        log('MAIN', 'DEPARTMENT_CHANGE', { 
            from: selectedDepartment, 
            to: dept 
        });
        setSelectedDepartment(dept);
        setSelectedEmployee(null);
    }, [selectedDepartment, log]);
    
    // 직원 선택 핸들러
    const handleEmployeeSelect = useCallback((employee) => {
        log('MAIN', 'EMPLOYEE_SELECT', { 
            employee: employee.name,
            employeeId: employee.id 
        });
        setSelectedEmployee(employee);
    }, [log]);
    
    // 전체 로딩 상태 모니터링
    useEffect(() => {
        log('MAIN', 'RENDER_STATE', {
            hasSelectedDepartment: !!selectedDepartment,
            hasSelectedEmployee: !!selectedEmployee
        });
    }, [selectedDepartment, selectedEmployee, log]);
    
    return (
        <div className="skillmap-dashboard">
            <div className="dashboard-header">
                <h1>Skillmap Dashboard</h1>
                <div className="department-selector">
                    <select 
                        className="form-control"
                        value={selectedDepartment}
                        onChange={(e) => handleDepartmentChange(e.target.value)}
                    >
                        <option value="IT">IT Department</option>
                        <option value="Sales">Sales Department</option>
                        <option value="Marketing">Marketing Department</option>
                        <option value="HR">HR Department</option>
                    </select>
                </div>
            </div>
            
            <div className="dashboard-body">
                <div className="row">
                    <div className="col-md-3">
                        <SkillmapSidebar 
                            departmentId={selectedDepartment}
                            onEmployeeSelect={handleEmployeeSelect}
                        />
                    </div>
                    
                    <div className="col-md-9">
                        <div className="main-content">
                            <SkillmapHeatmap 
                                departmentId={selectedDepartment}
                                selectedEmployee={selectedEmployee}
                            />
                            
                            {selectedEmployee && (
                                <div className="employee-details mt-4">
                                    <h3>Selected Employee: {selectedEmployee.name}</h3>
                                    <p>Title: {selectedEmployee.job_title}</p>
                                    <p>Department: {selectedDepartment}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SkillmapDashboard;
