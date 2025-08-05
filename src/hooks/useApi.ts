import { useState, useEffect, useCallback } from 'react';
import { mockApi } from '../services/mockApi';

// API 호출 상태를 관리하는 커스텀 훅
export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<{ success: boolean; data?: T; error?: string }>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (...args: any[]) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiFunction(...args);
      
      if (response.success && response.data) {
        setData(response.data);
      } else {
        setError(response.error || '알 수 없는 오류가 발생했습니다');
      }
    } catch (err) {
      setError('네트워크 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

// 직원 목록을 가져오는 훅
export function useEmployees(page = 1, pageSize = 10, search?: string) {
  return useApi(
    () => mockApi.getEmployees(page, pageSize, search),
    [page, pageSize, search]
  );
}

// 특정 직원 정보를 가져오는 훅
export function useEmployee(id: string) {
  return useApi(
    () => mockApi.getEmployeeById(id),
    [id]
  );
}

// 부서 목록을 가져오는 훅
export function useDepartments() {
  return useApi(
    () => mockApi.getDepartments(),
    []
  );
}

// 평가 목록을 가져오는 훅
export function useEvaluations(employeeId?: string) {
  return useApi(
    () => mockApi.getEvaluations(employeeId),
    [employeeId]
  );
}

// 보상 정보를 가져오는 훅
export function useCompensations(employeeId?: string) {
  return useApi(
    () => mockApi.getCompensations(employeeId),
    [employeeId]
  );
}

// 승진 정보를 가져오는 훅
export function usePromotions(status?: string) {
  return useApi(
    () => mockApi.getPromotions(status),
    [status]
  );
}

// 통계 정보를 가져오는 훅
export function useStatistics() {
  return useApi(
    () => mockApi.getStatistics(),
    []
  );
}

// 최근 활동을 가져오는 훅
export function useRecentActivities() {
  return useApi(
    () => mockApi.getRecentActivities(),
    []
  );
}