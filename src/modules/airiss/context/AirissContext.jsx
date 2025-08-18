/**
 * AIRISS Context Provider
 * EHR 시스템 내에서 AIRISS 상태 관리
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import airissService from '../services/airissService';

const AirissContext = createContext(null);

export const useAiriss = () => {
  const context = useContext(AirissContext);
  if (!context) {
    throw new Error('useAiriss must be used within AirissProvider');
  }
  return context;
};

export const AirissProvider = ({ children }) => {
  // 상태 관리
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResults, setAnalysisResults] = useState({});
  const [batchResults, setBatchResults] = useState(null);
  const [serviceHealth, setServiceHealth] = useState({ status: true });
  const [statistics, setStatistics] = useState({
    totalAnalyses: 0,
    averageScore: 0,
    gradeDistribution: {},
    departmentStats: {},
  });

  // 서비스 상태 확인 (마운트 시)
  useEffect(() => {
    checkServiceHealth();
    const interval = setInterval(checkServiceHealth, 60000); // 1분마다 체크
    return () => clearInterval(interval);
  }, []);

  /**
   * 서비스 상태 확인
   */
  const checkServiceHealth = async () => {
    try {
      const health = await airissService.checkHealth();
      setServiceHealth(health);
      if (!health.status) {
        console.warn('AIRISS 서비스 상태 불량:', health.error);
      }
    } catch (error) {
      console.error('서비스 상태 확인 실패:', error);
      setServiceHealth({ status: false, error: error.message });
    }
  };

  /**
   * 단일 직원 분석
   */
  const analyzeEmployee = useCallback(async (employeeData) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await airissService.analyzeEmployee(employeeData);
      
      // 결과 저장
      setAnalysisResults(prev => ({
        ...prev,
        [employeeData.id]: result,
      }));

      // 통계 업데이트
      updateStatistics([result]);

      return result;
    } catch (error) {
      console.error('직원 분석 오류:', error);
      setError(error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * 배치 직원 분석
   */
  const batchAnalyzeEmployees = useCallback(async (employeeList) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await airissService.batchAnalyzeEmployees(employeeList);
      
      // 배치 결과 저장
      setBatchResults(result);

      // 개별 결과도 저장
      result.results.forEach(r => {
        setAnalysisResults(prev => ({
          ...prev,
          [r.employeeId]: r,
        }));
      });

      // 통계 업데이트
      updateStatistics(result.results);

      return result;
    } catch (error) {
      console.error('배치 분석 오류:', error);
      setError(error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * 통계 업데이트
   */
  const updateStatistics = (results) => {
    setStatistics(prev => {
      const newStats = { ...prev };
      
      // 총 분석 수 증가
      newStats.totalAnalyses += results.length;

      // 평균 점수 재계산
      const allScores = Object.values(analysisResults)
        .concat(results)
        .map(r => r.aiScore)
        .filter(score => score > 0);
      
      newStats.averageScore = allScores.length > 0
        ? allScores.reduce((sum, score) => sum + score, 0) / allScores.length
        : 0;

      // 등급 분포 업데이트
      results.forEach(result => {
        const grade = result.grade;
        newStats.gradeDistribution[grade] = (newStats.gradeDistribution[grade] || 0) + 1;
      });

      return newStats;
    });
  };

  /**
   * 특정 직원의 분석 결과 가져오기
   */
  const getEmployeeAnalysis = useCallback((employeeId) => {
    return analysisResults[employeeId] || null;
  }, [analysisResults]);

  /**
   * 캐시 초기화
   */
  const clearCache = useCallback(() => {
    airissService.clearCache();
    setAnalysisResults({});
    setBatchResults(null);
    console.log('AIRISS 캐시 초기화됨');
  }, []);

  /**
   * 특정 직원 캐시 무효화
   */
  const invalidateEmployee = useCallback((employeeId) => {
    airissService.invalidateEmployeeCache(employeeId);
    setAnalysisResults(prev => {
      const updated = { ...prev };
      delete updated[employeeId];
      return updated;
    });
  }, []);

  /**
   * 대시보드용 요약 데이터 생성
   */
  const getDashboardSummary = useCallback(() => {
    const allResults = Object.values(analysisResults);
    
    if (allResults.length === 0) {
      return {
        totalEmployees: 0,
        averageScore: 0,
        topPerformers: [],
        needsImprovement: [],
        gradeDistribution: {},
        departmentStats: {},
      };
    }

    // Top Performers (점수 85 이상)
    const topPerformers = allResults
      .filter(r => r.aiScore >= 85)
      .sort((a, b) => b.aiScore - a.aiScore)
      .slice(0, 10);

    // Needs Improvement (점수 60 미만)
    const needsImprovement = allResults
      .filter(r => r.aiScore < 60)
      .sort((a, b) => a.aiScore - b.aiScore)
      .slice(0, 10);

    return {
      totalEmployees: allResults.length,
      averageScore: statistics.averageScore,
      topPerformers,
      needsImprovement,
      gradeDistribution: statistics.gradeDistribution,
      departmentStats: statistics.departmentStats,
    };
  }, [analysisResults, statistics]);

  const value = {
    // 상태
    isLoading,
    error,
    analysisResults,
    batchResults,
    serviceHealth,
    statistics,

    // 액션
    analyzeEmployee,
    batchAnalyzeEmployees,
    getEmployeeAnalysis,
    clearCache,
    invalidateEmployee,
    checkServiceHealth,
    getDashboardSummary,
  };

  return (
    <AirissContext.Provider value={value}>
      {children}
    </AirissContext.Provider>
  );
};