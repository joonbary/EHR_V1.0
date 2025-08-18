import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/token/', credentials),
  logout: () => {
    localStorage.removeItem('token');
    return Promise.resolve();
  },
  getProfile: () => api.get('/users/me/'),
  changePassword: (data: { old_password: string; new_password: string }) =>
    api.post('/users/change_password/', data),
};

export const evaluationApi = {
  // Evaluation periods
  getPeriods: () => api.get('/evaluations/periods/'),
  getActivePeriod: () => api.get('/evaluations/periods/active/'),
  
  // Evaluations
  getEvaluations: (params?: any) => api.get('/evaluations/evaluations/', { params }),
  getEvaluation: (id: string) => api.get(`/evaluations/evaluations/${id}/`),
  createEvaluation: (data: any) => api.post('/evaluations/evaluations/', data),
  updateEvaluation: (id: string, data: any) => api.patch(`/evaluations/evaluations/${id}/`, data),
  submitEvaluation: (data: any) => api.post('/evaluations/evaluations/', data),
  approveEvaluation: (id: string) => api.post(`/evaluations/evaluations/${id}/approve/`),
  rejectEvaluation: (id: string) => api.post(`/evaluations/evaluations/${id}/reject/`),
  getEvaluationAnalytics: (id: string) => api.get(`/evaluations/evaluations/${id}/analytics/`),
  
  // Tasks
  getTasks: (params?: any) => api.get('/evaluations/tasks/', { params }),
  getTask: (id: string) => api.get(`/evaluations/tasks/${id}/`),
  createTask: (data: any) => api.post('/evaluations/tasks/', data),
  updateTask: (id: string, data: any) => api.patch(`/evaluations/tasks/${id}/`, data),
  completeTask: (id: string) => api.post(`/evaluations/tasks/${id}/complete/`),
  
  // Scores
  getScores: (evaluationId: string) => api.get('/evaluations/scores/', { params: { evaluation: evaluationId } }),
  updateScore: (id: string, data: any) => api.patch(`/evaluations/scores/${id}/`, data),
  
  // Criteria
  getCriteria: (category?: string) => api.get('/evaluations/criteria/', { params: { category } }),
  
  // Feedback
  getFeedback: (evaluationId: string) => api.get('/evaluations/feedbacks/', { params: { evaluation: evaluationId } }),
  createFeedback: (data: any) => api.post('/evaluations/feedbacks/', data),
  generateAIFeedback: (data: any) => api.post('/evaluations/feedbacks/generate_ai/', data),
  
  // Goals
  getGoals: (params?: any) => api.get('/evaluations/goals/', { params }),
  createGoal: (data: any) => api.post('/evaluations/goals/', data),
  updateGoal: (id: string, data: any) => api.patch(`/evaluations/goals/${id}/`, data),
  updateGoalProgress: (id: string, data: any) => api.post(`/evaluations/goals/${id}/update_progress/`, data),
  
  // Employees
  getEmployees: () => api.get('/users/employees/'),
  getEvaluators: () => api.get('/users/evaluators/'),
};

export const notificationApi = {
  getNotifications: (params?: any) => api.get('/notifications/', { params }),
  getUnreadCount: () => api.get('/notifications/unread_count/'),
  markAsRead: (id: string) => api.post(`/notifications/${id}/mark_as_read/`),
  markAllAsRead: () => api.post('/notifications/mark_all_as_read/'),
  deleteRead: () => api.delete('/notifications/delete_read/'),
};

export const dashboardApi = {
  getOverview: () => api.get('/dashboard/overview/'),
  getPerformanceChart: (period: string) => api.get(`/dashboard/performance/${period}/`),
  getTeamAnalytics: () => api.get('/dashboard/team-analytics/'),
  getRecentActivities: () => api.get('/dashboard/activities/'),
};

export default api;