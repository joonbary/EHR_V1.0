/**
 * EHR-AIRISS Integration Component
 * EHR 시스템에 AIRISS AI 분석 기능을 통합하는 React 컴포넌트
 */

import React, { useState, useEffect } from 'react';
import './EHR_AirissIntegration.css';

// AIRISS MSA Service URL
const AIRISS_SERVICE_URL = 'https://web-production-4066.up.railway.app';

const EHRAirissIntegration = ({ employees = [] }) => {
  const [loading, setLoading] = useState(false);
  const [analysisResults, setAnalysisResults] = useState({});
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [serviceHealth, setServiceHealth] = useState(null);
  const [error, setError] = useState(null);

  // 서비스 헬스 체크
  useEffect(() => {
    checkServiceHealth();
    const interval = setInterval(checkServiceHealth, 60000); // 1분마다 체크
    return () => clearInterval(interval);
  }, []);

  const checkServiceHealth = async () => {
    try {
      const response = await fetch(`${AIRISS_SERVICE_URL}/health`);
      const health = await response.json();
      setServiceHealth(health.status === 'healthy');
    } catch (err) {
      console.error('Health check failed:', err);
      setServiceHealth(false);
    }
  };

  // 단일 직원 분석
  const analyzeEmployee = async (employee) => {
    setLoading(true);
    setError(null);
    
    try {
      const requestBody = {
        employee_data: {
          employee_id: employee.id,
          name: employee.name,
          department: employee.department,
          position: employee.position,
          performance_data: {
            목표달성률: employee.goalAchievement || 85,
            프로젝트성공률: employee.projectSuccess || 90,
            고객만족도: employee.customerSatisfaction || 88,
            출근율: employee.attendance || 95
          },
          competencies: {
            리더십: employee.leadership || 80,
            기술력: employee.technical || 85,
            커뮤니케이션: employee.communication || 82,
            문제해결: employee.problemSolving || 88,
            팀워크: employee.teamwork || 90,
            창의성: employee.creativity || 75,
            적응력: employee.adaptability || 85,
            성실성: employee.reliability || 92
          }
        },
        analysis_type: 'comprehensive',
        include_recommendations: true
      };

      const response = await fetch(`${AIRISS_SERVICE_URL}/api/v1/llm/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.status}`);
      }

      const result = await response.json();
      
      setAnalysisResults(prev => ({
        ...prev,
        [employee.id]: result
      }));
      
      return result;
    } catch (err) {
      console.error('Analysis error:', err);
      setError(`분석 실패: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 선택된 직원들 배치 분석
  const batchAnalyze = async () => {
    if (selectedEmployees.length === 0) {
      alert('분석할 직원을 선택해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const employeesData = selectedEmployees.map(emp => ({
        employee_id: emp.id,
        name: emp.name,
        department: emp.department,
        position: emp.position,
        performance_data: {
          목표달성률: emp.goalAchievement || 85,
          프로젝트성공률: emp.projectSuccess || 90,
          고객만족도: emp.customerSatisfaction || 88,
          출근율: emp.attendance || 95
        },
        competencies: {
          리더십: emp.leadership || 80,
          기술력: emp.technical || 85,
          커뮤니케이션: emp.communication || 82,
          문제해결: emp.problemSolving || 88,
          팀워크: emp.teamwork || 90,
          창의성: emp.creativity || 75,
          적응력: emp.adaptability || 85,
          성실성: emp.reliability || 92
        }
      }));

      const response = await fetch(`${AIRISS_SERVICE_URL}/api/v1/llm/batch-analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          employees: employeesData,
          analysis_type: 'comprehensive',
          include_recommendations: false
        })
      });

      if (!response.ok) {
        throw new Error(`Batch analysis failed: ${response.status}`);
      }

      const result = await response.json();
      
      // 결과를 개별 직원별로 저장
      const newResults = {};
      result.results.forEach(r => {
        newResults[r.employee_id] = r;
      });
      
      setAnalysisResults(prev => ({
        ...prev,
        ...newResults
      }));
      
      alert(`${result.success_count}명 분석 완료!`);
    } catch (err) {
      console.error('Batch analysis error:', err);
      setError(`배치 분석 실패: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 직원 선택 토글
  const toggleEmployeeSelection = (employee) => {
    setSelectedEmployees(prev => {
      const exists = prev.find(emp => emp.id === employee.id);
      if (exists) {
        return prev.filter(emp => emp.id !== employee.id);
      } else {
        return [...prev, employee];
      }
    });
  };

  // 등급별 색상
  const getGradeColor = (grade) => {
    const colors = {
      'S': '#4CAF50',
      'A+': '#8BC34A',
      'A': '#CDDC39',
      'B': '#FFC107',
      'C': '#FF9800',
      'D': '#F44336'
    };
    return colors[grade] || '#999';
  };

  return (
    <div className="ehr-airiss-integration">
      <div className="integration-header">
        <h2>AIRISS AI 직원 분석 시스템</h2>
        <div className="service-status">
          {serviceHealth !== null && (
            <span className={`status-badge ${serviceHealth ? 'healthy' : 'unhealthy'}`}>
              {serviceHealth ? '● 서비스 정상' : '● 서비스 점검 중'}
            </span>
          )}
          <a 
            href={`${AIRISS_SERVICE_URL}/docs`} 
            target="_blank" 
            rel="noopener noreferrer"
            className="api-docs-link"
          >
            API 문서
          </a>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="actions-bar">
        <button 
          onClick={batchAnalyze}
          disabled={loading || selectedEmployees.length === 0}
          className="batch-analyze-btn"
        >
          선택된 {selectedEmployees.length}명 일괄 분석
        </button>
        <button 
          onClick={() => setSelectedEmployees([])}
          className="clear-selection-btn"
        >
          선택 초기화
        </button>
      </div>

      <div className="employees-grid">
        {employees.map(employee => {
          const analysis = analysisResults[employee.id];
          const isSelected = selectedEmployees.find(emp => emp.id === employee.id);
          
          return (
            <div key={employee.id} className={`employee-card ${isSelected ? 'selected' : ''}`}>
              <div className="employee-header">
                <input
                  type="checkbox"
                  checked={!!isSelected}
                  onChange={() => toggleEmployeeSelection(employee)}
                />
                <h3>{employee.name}</h3>
                <span className="employee-id">{employee.id}</span>
              </div>
              
              <div className="employee-info">
                <p><strong>부서:</strong> {employee.department}</p>
                <p><strong>직급:</strong> {employee.position}</p>
              </div>

              {analysis ? (
                <div className="analysis-result">
                  <div className="score-section">
                    <div className="ai-score">
                      <span className="score-label">AI 점수</span>
                      <span className="score-value">{analysis.ai_score}</span>
                    </div>
                    <div 
                      className="grade-badge"
                      style={{ backgroundColor: getGradeColor(analysis.grade) }}
                    >
                      {analysis.grade}
                    </div>
                  </div>
                  
                  {analysis.strengths && analysis.strengths.length > 0 && (
                    <div className="strengths">
                      <h4>강점</h4>
                      <ul>
                        {analysis.strengths.slice(0, 3).map((strength, idx) => (
                          <li key={idx}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysis.improvements && analysis.improvements.length > 0 && (
                    <div className="improvements">
                      <h4>개선점</h4>
                      <ul>
                        {analysis.improvements.slice(0, 3).map((improvement, idx) => (
                          <li key={idx}>{improvement}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysis.ai_feedback && (
                    <div className="feedback">
                      <h4>AI 피드백</h4>
                      <p>{analysis.ai_feedback.substring(0, 200)}...</p>
                    </div>
                  )}
                  
                  <button 
                    onClick={() => analyzeEmployee(employee)}
                    disabled={loading}
                    className="reanalyze-btn"
                  >
                    재분석
                  </button>
                </div>
              ) : (
                <div className="no-analysis">
                  <p>분석 데이터 없음</p>
                  <button 
                    onClick={() => analyzeEmployee(employee)}
                    disabled={loading}
                    className="analyze-btn"
                  >
                    {loading ? '분석 중...' : 'AI 분석 시작'}
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>AI 분석 중...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default EHRAirissIntegration;