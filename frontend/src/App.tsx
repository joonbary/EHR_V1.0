import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { SnackbarProvider } from 'notistack';
import { QueryClient, QueryClientProvider } from 'react-query';

// Components
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import EvaluationList from './pages/EvaluationList';
import EvaluationDetail from './pages/EvaluationDetail';
import ContributionEvaluation from './pages/ContributionEvaluation';
import TaskManagement from './pages/TaskManagement';
import GoalSetting from './pages/GoalSetting';
import NotificationCenter from './pages/NotificationCenter';
import Profile from './pages/Profile';

// Services
import { AuthProvider } from './services/AuthContext';
import PrivateRoute from './components/PrivateRoute';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider maxSnack={3} autoHideDuration={3000}>
          <AuthProvider>
            <Router>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route
                  path="/"
                  element={
                    <PrivateRoute>
                      <Layout />
                    </PrivateRoute>
                  }
                >
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  <Route path="dashboard" element={<Dashboard />} />
                  <Route path="evaluations" element={<EvaluationList />} />
                  <Route path="evaluations/:id" element={<EvaluationDetail />} />
                  <Route path="evaluations/contribution" element={<ContributionEvaluation />} />
                  <Route path="tasks" element={<TaskManagement />} />
                  <Route path="goals" element={<GoalSetting />} />
                  <Route path="notifications" element={<NotificationCenter />} />
                  <Route path="profile" element={<Profile />} />
                </Route>
              </Routes>
            </Router>
          </AuthProvider>
        </SnackbarProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;