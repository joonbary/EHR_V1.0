/**
 * AIRISS Employee Analysis Table Component
 * EHR 시스템 내 직원 분석 테이블
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useAiriss } from '../context/AirissContext';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  TextField,
  Button,
  Box,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Search,
  Refresh,
  Download,
  Visibility,
  Psychology,
  FilterList,
  Clear,
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

const EmployeeAnalysisTable = ({ employees = [] }) => {
  const {
    isLoading,
    error,
    analysisResults,
    analyzeEmployee,
    batchAnalyzeEmployees,
    getEmployeeAnalysis,
    invalidateEmployee,
  } = useAiriss();

  // 상태 관리
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('');
  const [filterGrade, setFilterGrade] = useState('');
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [analyzing, setAnalyzing] = useState({});
  const [localEmployees, setLocalEmployees] = useState(employees);

  // 부서 목록 추출
  const departments = [...new Set(employees.map(emp => emp.department))].filter(Boolean);

  // 등급별 색상
  const gradeColors = {
    'S': '#4CAF50',
    'A+': '#8BC34A',
    'A': '#CDDC39',
    'B': '#FFC107',
    'C': '#FF9800',
    'D': '#F44336',
  };

  useEffect(() => {
    // employees prop 변경 시 로컬 상태 업데이트
    setLocalEmployees(employees.map(emp => ({
      ...emp,
      analysis: getEmployeeAnalysis(emp.id),
    })));
  }, [employees, analysisResults]);

  /**
   * 필터링된 직원 목록
   */
  const filteredEmployees = localEmployees.filter(employee => {
    const matchesSearch = !searchTerm || 
      employee.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.id?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDepartment = !filterDepartment || employee.department === filterDepartment;
    
    const matchesGrade = !filterGrade || employee.analysis?.grade === filterGrade;

    return matchesSearch && matchesDepartment && matchesGrade;
  });

  /**
   * 개별 직원 분석
   */
  const handleAnalyzeEmployee = async (employee) => {
    setAnalyzing(prev => ({ ...prev, [employee.id]: true }));
    
    try {
      await analyzeEmployee(employee);
    } catch (error) {
      console.error('분석 실패:', error);
    } finally {
      setAnalyzing(prev => ({ ...prev, [employee.id]: false }));
    }
  };

  /**
   * 선택된 직원들 배치 분석
   */
  const handleBatchAnalysis = async () => {
    const unanalyzedEmployees = filteredEmployees.filter(
      emp => !emp.analysis && !analyzing[emp.id]
    );

    if (unanalyzedEmployees.length === 0) {
      alert('분석할 직원이 없습니다.');
      return;
    }

    try {
      await batchAnalyzeEmployees(unanalyzedEmployees);
    } catch (error) {
      console.error('배치 분석 실패:', error);
    }
  };

  /**
   * 직원 상세 정보 보기
   */
  const handleViewDetails = (employee) => {
    setSelectedEmployee(employee);
    setDetailDialogOpen(true);
  };

  /**
   * 분석 결과 재분석
   */
  const handleReanalyze = async (employee) => {
    invalidateEmployee(employee.id);
    await handleAnalyzeEmployee(employee);
  };

  /**
   * CSV 내보내기
   */
  const handleExportCSV = () => {
    const csvData = filteredEmployees.map(emp => ({
      ID: emp.id,
      이름: emp.name,
      부서: emp.department,
      직급: emp.position,
      AI점수: emp.analysis?.aiScore || '',
      등급: emp.analysis?.grade || '',
      강점: emp.analysis?.strengths?.join(', ') || '',
      개선점: emp.analysis?.improvements?.join(', ') || '',
    }));

    const headers = Object.keys(csvData[0]).join(',');
    const rows = csvData.map(row => Object.values(row).join(','));
    const csv = [headers, ...rows].join('\n');

    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `직원분석_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  /**
   * 역량 레이더 차트 데이터 준비
   */
  const prepareRadarData = (employee) => {
    if (!employee || !employee.competencies) return [];

    return Object.entries(employee.competencies).map(([key, value]) => ({
      subject: key,
      value: value || 0,
      fullMark: 100,
    }));
  };

  return (
    <Box>
      {/* 툴바 */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="이름 또는 ID 검색"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                endAdornment: searchTerm && (
                  <IconButton size="small" onClick={() => setSearchTerm('')}>
                    <Clear />
                  </IconButton>
                ),
              }}
            />
          </Grid>

          <Grid item xs={12} sm={2}>
            <FormControl fullWidth>
              <InputLabel>부서</InputLabel>
              <Select
                value={filterDepartment}
                onChange={(e) => setFilterDepartment(e.target.value)}
                label="부서"
              >
                <MenuItem value="">전체</MenuItem>
                {departments.map(dept => (
                  <MenuItem key={dept} value={dept}>{dept}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={2}>
            <FormControl fullWidth>
              <InputLabel>등급</InputLabel>
              <Select
                value={filterGrade}
                onChange={(e) => setFilterGrade(e.target.value)}
                label="등급"
              >
                <MenuItem value="">전체</MenuItem>
                {['S', 'A+', 'A', 'B', 'C', 'D'].map(grade => (
                  <MenuItem key={grade} value={grade}>{grade}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={5}>
            <Box display="flex" gap={1} justifyContent="flex-end">
              <Button
                variant="contained"
                startIcon={<Psychology />}
                onClick={handleBatchAnalysis}
                disabled={isLoading}
              >
                전체 분석
              </Button>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleExportCSV}
              >
                CSV 내보내기
              </Button>
              <IconButton onClick={() => window.location.reload()}>
                <Refresh />
              </IconButton>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* 테이블 */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>이름</TableCell>
              <TableCell>부서</TableCell>
              <TableCell>직급</TableCell>
              <TableCell align="center">AI 점수</TableCell>
              <TableCell align="center">등급</TableCell>
              <TableCell align="center">상태</TableCell>
              <TableCell align="center">작업</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredEmployees
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((employee) => (
                <TableRow key={employee.id}>
                  <TableCell>{employee.id}</TableCell>
                  <TableCell>{employee.name}</TableCell>
                  <TableCell>{employee.department}</TableCell>
                  <TableCell>{employee.position}</TableCell>
                  <TableCell align="center">
                    {employee.analysis ? (
                      <Typography variant="body2" fontWeight="bold">
                        {employee.analysis.aiScore}
                      </Typography>
                    ) : '-'}
                  </TableCell>
                  <TableCell align="center">
                    {employee.analysis ? (
                      <Chip
                        label={employee.analysis.grade}
                        size="small"
                        style={{
                          backgroundColor: gradeColors[employee.analysis.grade],
                          color: 'white',
                        }}
                      />
                    ) : '-'}
                  </TableCell>
                  <TableCell align="center">
                    {analyzing[employee.id] ? (
                      <CircularProgress size={20} />
                    ) : employee.analysis ? (
                      <Chip label="분석완료" color="success" size="small" />
                    ) : (
                      <Chip label="미분석" color="default" size="small" />
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <Box display="flex" gap={0.5} justifyContent="center">
                      {employee.analysis ? (
                        <>
                          <Tooltip title="상세보기">
                            <IconButton
                              size="small"
                              onClick={() => handleViewDetails(employee)}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="재분석">
                            <IconButton
                              size="small"
                              onClick={() => handleReanalyze(employee)}
                              disabled={analyzing[employee.id]}
                            >
                              <Refresh />
                            </IconButton>
                          </Tooltip>
                        </>
                      ) : (
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<Psychology />}
                          onClick={() => handleAnalyzeEmployee(employee)}
                          disabled={analyzing[employee.id]}
                        >
                          분석
                        </Button>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredEmployees.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>

      {/* 상세 정보 다이얼로그 */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedEmployee && (
          <>
            <DialogTitle>
              직원 상세 분석 - {selectedEmployee.name}
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={3}>
                {/* 기본 정보 */}
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        기본 정보
                      </Typography>
                      <List dense>
                        <ListItem>
                          <ListItemText
                            primary="직원 ID"
                            secondary={selectedEmployee.id}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="부서"
                            secondary={selectedEmployee.department}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="직급"
                            secondary={selectedEmployee.position}
                          />
                        </ListItem>
                      </List>
                    </CardContent>
                  </Card>
                </Grid>

                {/* AI 분석 결과 */}
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        AI 분석 결과
                      </Typography>
                      {selectedEmployee.analysis ? (
                        <List dense>
                          <ListItem>
                            <ListItemText
                              primary="AI 점수"
                              secondary={
                                <Box display="flex" alignItems="center" gap={1}>
                                  <Typography variant="h6">
                                    {selectedEmployee.analysis.aiScore}
                                  </Typography>
                                  <Chip
                                    label={selectedEmployee.analysis.grade}
                                    size="small"
                                    style={{
                                      backgroundColor: gradeColors[selectedEmployee.analysis.grade],
                                      color: 'white',
                                    }}
                                  />
                                </Box>
                              }
                            />
                          </ListItem>
                          <ListItem>
                            <ListItemText
                              primary="위험 수준"
                              secondary={
                                <Chip
                                  label={selectedEmployee.analysis.riskLevel}
                                  size="small"
                                  color={
                                    selectedEmployee.analysis.riskLevel === 'high' ? 'error' :
                                    selectedEmployee.analysis.riskLevel === 'medium' ? 'warning' :
                                    'success'
                                  }
                                />
                              }
                            />
                          </ListItem>
                        </List>
                      ) : (
                        <Typography color="textSecondary">
                          분석 데이터 없음
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                {/* 역량 레이더 차트 */}
                {selectedEmployee.competencies && (
                  <Grid item xs={12}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          역량 분석
                        </Typography>
                        <ResponsiveContainer width="100%" height={300}>
                          <RadarChart data={prepareRadarData(selectedEmployee)}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="subject" />
                            <PolarRadiusAxis angle={90} domain={[0, 100]} />
                            <Radar
                              name="역량"
                              dataKey="value"
                              stroke="#8884d8"
                              fill="#8884d8"
                              fillOpacity={0.6}
                            />
                          </RadarChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {/* 강점 및 개선점 */}
                {selectedEmployee.analysis && (
                  <>
                    <Grid item xs={12} md={6}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            <TrendingUp sx={{ verticalAlign: 'middle', mr: 1 }} />
                            강점
                          </Typography>
                          <Box>
                            {selectedEmployee.analysis.strengths?.map((strength, idx) => (
                              <Chip
                                key={idx}
                                label={strength}
                                color="success"
                                variant="outlined"
                                sx={{ m: 0.5 }}
                              />
                            ))}
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            <TrendingDown sx={{ verticalAlign: 'middle', mr: 1 }} />
                            개선점
                          </Typography>
                          <Box>
                            {selectedEmployee.analysis.improvements?.map((improvement, idx) => (
                              <Chip
                                key={idx}
                                label={improvement}
                                color="warning"
                                variant="outlined"
                                sx={{ m: 0.5 }}
                              />
                            ))}
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  </>
                )}

                {/* AI 피드백 */}
                {selectedEmployee.analysis?.feedback && (
                  <Grid item xs={12}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          AI 피드백
                        </Typography>
                        <Typography variant="body2" paragraph>
                          {selectedEmployee.analysis.feedback}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailDialogOpen(false)}>
                닫기
              </Button>
              <Button
                variant="contained"
                onClick={() => handleReanalyze(selectedEmployee)}
                startIcon={<Refresh />}
              >
                재분석
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default EmployeeAnalysisTable;