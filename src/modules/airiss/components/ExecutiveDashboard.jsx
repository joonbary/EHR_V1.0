/**
 * AIRISS Executive Dashboard Component
 * EHR 시스템 내 경영진 대시보드
 */

import React, { useEffect, useState } from 'react';
import { useAiriss } from '../context/AirissContext';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  CircularProgress,
  Alert,
  Button,
  Chip,
  LinearProgress,
  Paper,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  People,
  Assessment,
  Warning,
  CheckCircle,
  Refresh,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ExecutiveDashboard = () => {
  const {
    isLoading,
    error,
    serviceHealth,
    getDashboardSummary,
    checkServiceHealth,
    statistics,
  } = useAiriss();

  const [dashboardData, setDashboardData] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 300000); // 5분마다 갱신
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = () => {
    const summary = getDashboardSummary();
    setDashboardData(summary);
    setLastUpdated(new Date());
  };

  const handleRefresh = async () => {
    await checkServiceHealth();
    loadDashboardData();
  };

  // 등급별 색상
  const gradeColors = {
    'S': '#4CAF50',
    'A+': '#8BC34A',
    'A': '#CDDC39',
    'B': '#FFC107',
    'C': '#FF9800',
    'D': '#F44336',
  };

  // 차트 데이터 준비
  const prepareGradeChartData = () => {
    if (!dashboardData) return [];
    
    return Object.entries(dashboardData.gradeDistribution).map(([grade, count]) => ({
      name: grade,
      value: count,
      fill: gradeColors[grade] || '#999',
    }));
  };

  if (!serviceHealth.status) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        <Typography variant="h6">AIRISS 서비스 연결 실패</Typography>
        <Typography variant="body2">{serviceHealth.error}</Typography>
        <Button onClick={checkServiceHealth} startIcon={<Refresh />} sx={{ mt: 1 }}>
          재연결 시도
        </Button>
      </Alert>
    );
  }

  if (isLoading && !dashboardData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* 헤더 */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          AIRISS 경영진 대시보드
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <Chip
            label={serviceHealth.status ? '서비스 정상' : '서비스 점검 중'}
            color={serviceHealth.status ? 'success' : 'warning'}
            icon={serviceHealth.status ? <CheckCircle /> : <Warning />}
          />
          <Typography variant="caption" color="textSecondary">
            마지막 업데이트: {lastUpdated.toLocaleTimeString()}
          </Typography>
          <Button
            variant="outlined"
            size="small"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={isLoading}
          >
            새로고침
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* 주요 지표 카드 */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    총 분석 인원
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData?.totalEmployees || 0}
                  </Typography>
                </Box>
                <People fontSize="large" color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    평균 AI 점수
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData?.averageScore?.toFixed(1) || 0}
                  </Typography>
                </Box>
                <Assessment fontSize="large" color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    우수 인재
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData?.topPerformers?.length || 0}
                  </Typography>
                </Box>
                <TrendingUp fontSize="large" color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    개선 필요
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData?.needsImprovement?.length || 0}
                  </Typography>
                </Box>
                <TrendingDown fontSize="large" color="error" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 차트 섹션 */}
      <Grid container spacing={3}>
        {/* 등급 분포 차트 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              등급 분포
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={prepareGradeChartData()}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}명`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {prepareGradeChartData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Top Performers 리스트 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Top Performers
            </Typography>
            <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
              {dashboardData?.topPerformers?.map((employee, index) => (
                <Box key={employee.employeeId} sx={{ mb: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">
                      {index + 1}. {employee.employeeId}
                    </Typography>
                    <Box display="flex" gap={1} alignItems="center">
                      <Chip
                        label={employee.grade}
                        size="small"
                        style={{
                          backgroundColor: gradeColors[employee.grade],
                          color: 'white',
                        }}
                      />
                      <Typography variant="body2" fontWeight="bold">
                        {employee.aiScore}점
                      </Typography>
                    </Box>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={employee.aiScore}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* 개선 필요 인원 리스트 */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              개선 필요 인원
            </Typography>
            <Grid container spacing={2}>
              {dashboardData?.needsImprovement?.map((employee) => (
                <Grid item xs={12} sm={6} md={4} key={employee.employeeId}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="textSecondary">
                        {employee.employeeId}
                      </Typography>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}>
                        <Typography variant="h6">
                          {employee.aiScore}점
                        </Typography>
                        <Chip
                          label={employee.grade}
                          size="small"
                          color="error"
                        />
                      </Box>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="caption" color="textSecondary">
                        주요 개선점:
                      </Typography>
                      <Box sx={{ mt: 0.5 }}>
                        {employee.improvements?.slice(0, 2).map((item, idx) => (
                          <Chip
                            key={idx}
                            label={item}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      {/* 통계 요약 */}
      <Box mt={3}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            분석 통계
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="textSecondary">
                총 분석 횟수
              </Typography>
              <Typography variant="h6">{statistics.totalAnalyses}</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="textSecondary">
                평균 처리 시간
              </Typography>
              <Typography variant="h6">2.5초</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="textSecondary">
                성공률
              </Typography>
              <Typography variant="h6">98.5%</Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" color="textSecondary">
                서비스 가동률
              </Typography>
              <Typography variant="h6">99.9%</Typography>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    </Box>
  );
};

export default ExecutiveDashboard;