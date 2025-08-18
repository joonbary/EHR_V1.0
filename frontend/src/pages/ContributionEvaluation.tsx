import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Stepper,
  Step,
  StepLabel,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Chip,
  CircularProgress,
  Alert,
  Tab,
  Tabs,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Rating,
} from '@mui/material';
import {
  Assessment,
  CheckCircle,
  Assignment,
  Person,
  TrendingUp,
  Star,
  AutoAwesome,
  Send,
  Save,
  Edit,
  Visibility,
  ArrowForward,
  ArrowBack,
  Dashboard as DashboardIcon,
  Group,
  EmojiEvents,
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import { evaluationApi } from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ContributionEvaluation: React.FC = () => {
  const { enqueueSnackbar } = useSnackbar();
  const [activeStep, setActiveStep] = useState(0);
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [employees, setEmployees] = useState<any[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<any>(null);
  const [evaluationData, setEvaluationData] = useState<any>({
    tasks: [],
    scores: {},
    feedback: '',
    goals: [],
  });
  const [aiFeedback, setAiFeedback] = useState<string>('');
  const [openAIDialog, setOpenAIDialog] = useState(false);

  const steps = ['직원 선택', '업무 평가', '성과 점수', 'AI 피드백', '최종 검토'];

  const criteriaCategories = [
    {
      category: 'technical',
      label: '기술 역량',
      criteria: [
        { id: 1, name: '코드 품질', description: '깔끔하고 효율적인 코드 작성 능력' },
        { id: 2, name: '문제 해결', description: '복잡한 기술적 문제 해결 능력' },
        { id: 3, name: '기술 습득', description: '새로운 기술 학습 및 적용 능력' },
      ],
    },
    {
      category: 'contribution',
      label: '기여도',
      criteria: [
        { id: 4, name: '프로젝트 기여', description: '프로젝트 성공에 대한 기여도' },
        { id: 5, name: '팀 협업', description: '팀원들과의 협업 및 소통' },
        { id: 6, name: '업무 완성도', description: '할당된 업무의 완성도' },
      ],
    },
    {
      category: 'growth',
      label: '성장 및 발전',
      criteria: [
        { id: 7, name: '자기 개발', description: '지속적인 학습과 개선' },
        { id: 8, name: '목표 달성', description: '설정된 목표 달성률' },
        { id: 9, name: '혁신성', description: '새로운 아이디어와 접근 방식' },
      ],
    },
  ];

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const response = await evaluationApi.getEmployees();
      setEmployees(response.data);
    } catch (error) {
      enqueueSnackbar('직원 목록을 불러오는데 실패했습니다', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (activeStep === 0 && !selectedEmployee) {
      enqueueSnackbar('직원을 선택해주세요', { variant: 'warning' });
      return;
    }
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleGenerateAIFeedback = async () => {
    try {
      setLoading(true);
      setOpenAIDialog(true);
      const response = await evaluationApi.generateAIFeedback({
        employee: selectedEmployee,
        scores: evaluationData.scores,
        tasks: evaluationData.tasks,
      });
      setAiFeedback(response.data.feedback);
      enqueueSnackbar('AI 피드백이 생성되었습니다', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('AI 피드백 생성에 실패했습니다', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitEvaluation = async () => {
    try {
      setLoading(true);
      const response = await evaluationApi.submitEvaluation({
        ...evaluationData,
        employee: selectedEmployee.id,
        aiFeedback,
      });
      enqueueSnackbar('평가가 성공적으로 제출되었습니다', { variant: 'success' });
      // Reset form
      setActiveStep(0);
      setSelectedEmployee(null);
      setEvaluationData({ tasks: [], scores: {}, feedback: '', goals: [] });
      setAiFeedback('');
    } catch (error) {
      enqueueSnackbar('평가 제출에 실패했습니다', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const calculateOverallScore = () => {
    const scores = Object.values(evaluationData.scores) as number[];
    if (scores.length === 0) return 0;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          기여도 평가 시스템
        </Typography>
        <Typography variant="body1" color="text.secondary">
          직원의 성과와 기여도를 체계적으로 평가하고 AI 기반 피드백을 제공합니다
        </Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Step 1: Employee Selection */}
      {activeStep === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                평가할 직원 선택
              </Typography>
              <Grid container spacing={2} sx={{ mt: 2 }}>
                {employees.map((employee) => (
                  <Grid item xs={12} md={6} lg={4} key={employee.id}>
                    <Card
                      sx={{
                        cursor: 'pointer',
                        border: selectedEmployee?.id === employee.id ? 2 : 0,
                        borderColor: 'primary.main',
                      }}
                      onClick={() => setSelectedEmployee(employee)}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Avatar sx={{ mr: 2 }}>{employee.name[0]}</Avatar>
                          <Box>
                            <Typography variant="h6">{employee.name}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {employee.position}
                            </Typography>
                          </Box>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip label={employee.department} size="small" />
                          <Chip label={`${employee.experience}년차`} size="small" />
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Step 2: Task Evaluation */}
      {activeStep === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                업무 수행 평가
              </Typography>
              <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
                <Tab label="완료된 업무" />
                <Tab label="진행중인 업무" />
                <Tab label="목표 설정" />
              </Tabs>
              <TabPanel value={tabValue} index={0}>
                <List>
                  {[1, 2, 3].map((task) => (
                    <ListItem key={task}>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`프로젝트 ${task} 완료`}
                        secondary="2024년 1월 완료 - 우수한 성과"
                      />
                      <Rating value={4} readOnly />
                    </ListItem>
                  ))}
                </List>
              </TabPanel>
              <TabPanel value={tabValue} index={1}>
                <List>
                  {[1, 2].map((task) => (
                    <ListItem key={task}>
                      <ListItemIcon>
                        <Assignment color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`진행 중인 프로젝트 ${task}`}
                        secondary="진행률 70%"
                      />
                      <LinearProgress variant="determinate" value={70} sx={{ width: 100 }} />
                    </ListItem>
                  ))}
                </List>
              </TabPanel>
              <TabPanel value={tabValue} index={2}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="다음 분기 목표"
                  placeholder="다음 분기에 달성할 목표를 입력하세요"
                  sx={{ mb: 2 }}
                />
                <Button variant="contained" startIcon={<Save />}>
                  목표 저장
                </Button>
              </TabPanel>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Step 3: Performance Scoring */}
      {activeStep === 2 && (
        <Grid container spacing={3}>
          {criteriaCategories.map((category) => (
            <Grid item xs={12} key={category.category}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  {category.label}
                </Typography>
                <Grid container spacing={3}>
                  {category.criteria.map((criterion) => (
                    <Grid item xs={12} md={4} key={criterion.id}>
                      <Box>
                        <Typography variant="subtitle1">{criterion.name}</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {criterion.description}
                        </Typography>
                        <Box sx={{ px: 2 }}>
                          <Slider
                            value={evaluationData.scores[criterion.id] || 50}
                            onChange={(e, value) =>
                              setEvaluationData({
                                ...evaluationData,
                                scores: { ...evaluationData.scores, [criterion.id]: value },
                              })
                            }
                            valueLabelDisplay="on"
                            step={5}
                            marks
                            min={0}
                            max={100}
                          />
                        </Box>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Step 4: AI Feedback */}
      {activeStep === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h6">AI 기반 피드백</Typography>
                <Button
                  variant="contained"
                  startIcon={<AutoAwesome />}
                  onClick={handleGenerateAIFeedback}
                  disabled={loading}
                >
                  AI 피드백 생성
                </Button>
              </Box>
              {aiFeedback && (
                <Alert severity="info" sx={{ mb: 3 }}>
                  {aiFeedback}
                </Alert>
              )}
              <TextField
                fullWidth
                multiline
                rows={6}
                label="추가 피드백"
                placeholder="AI 피드백 외에 추가할 내용을 입력하세요"
                value={evaluationData.feedback}
                onChange={(e) =>
                  setEvaluationData({ ...evaluationData, feedback: e.target.value })
                }
              />
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Step 5: Final Review */}
      {activeStep === 4 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                최종 검토
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  평가 대상: {selectedEmployee?.name}
                </Typography>
                <Typography variant="h4" color="primary" sx={{ my: 2 }}>
                  종합 점수: {calculateOverallScore()}점
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={calculateOverallScore()}
                  sx={{ height: 10, borderRadius: 5 }}
                />
              </Box>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 4 }}>
                <Button
                  variant="outlined"
                  startIcon={<Save />}
                  onClick={() => enqueueSnackbar('임시 저장되었습니다', { variant: 'info' })}
                >
                  임시 저장
                </Button>
                <Button
                  variant="contained"
                  startIcon={<Send />}
                  onClick={handleSubmitEvaluation}
                  disabled={loading}
                >
                  평가 제출
                </Button>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button disabled={activeStep === 0} onClick={handleBack} startIcon={<ArrowBack />}>
          이전
        </Button>
        {activeStep < steps.length - 1 ? (
          <Button variant="contained" onClick={handleNext} endIcon={<ArrowForward />}>
            다음
          </Button>
        ) : (
          <Button
            variant="contained"
            color="success"
            onClick={handleSubmitEvaluation}
            disabled={loading}
          >
            평가 완료
          </Button>
        )}
      </Box>

      {/* AI Feedback Dialog */}
      <Dialog open={openAIDialog} onClose={() => setOpenAIDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>AI 피드백 생성 중...</DialogTitle>
        <DialogContent>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Typography>{aiFeedback}</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAIDialog(false)}>닫기</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ContributionEvaluation;