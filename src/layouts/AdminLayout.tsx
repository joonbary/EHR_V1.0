import React, { useState } from 'react';
import { Settings, Users, FileText, BarChart3, Shield, Database } from 'lucide-react';
import MainLayout from './MainLayout';

interface AdminLayoutProps {
  children: React.ReactNode;
}

interface StatCard {
  title: string;
  value: string | number;
  change: string;
  isPositive: boolean;
  icon: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const quickTabs = [
    { id: 'overview', label: '개요', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'users', label: '사용자 관리', icon: <Users className="w-4 h-4" /> },
    { id: 'permissions', label: '권한 설정', icon: <Shield className="w-4 h-4" /> },
    { id: 'reports', label: '리포트', icon: <FileText className="w-4 h-4" /> },
    { id: 'system', label: '시스템 설정', icon: <Settings className="w-4 h-4" /> },
    { id: 'database', label: '데이터베이스', icon: <Database className="w-4 h-4" /> },
  ];

  const stats: StatCard[] = [
    {
      title: '활성 사용자',
      value: '1,234',
      change: '+12.3%',
      isPositive: true,
      icon: <Users className="w-5 h-5 text-primary" />,
    },
    {
      title: '오늘 로그인',
      value: '892',
      change: '+5.2%',
      isPositive: true,
      icon: <Shield className="w-5 h-5 text-accent" />,
    },
    {
      title: '시스템 상태',
      value: '정상',
      change: '99.9%',
      isPositive: true,
      icon: <Settings className="w-5 h-5 text-success" />,
    },
    {
      title: '데이터 용량',
      value: '45.2GB',
      change: '+2.1GB',
      isPositive: false,
      icon: <Database className="w-5 h-5 text-warning" />,
    },
  ];

  const adminContent = (
    <div className="space-y-6">
      {/* Admin Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              관리자 대시보드
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              시스템 관리 및 모니터링
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">
              마지막 업데이트:
            </span>
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {new Date().toLocaleString('ko-KR')}
            </span>
          </div>
        </div>

        {/* Quick Tabs */}
        <div className="flex space-x-1 border-b border-gray-200 dark:border-gray-700">
          {quickTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-primary text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                {stat.icon}
              </div>
              <span
                className={`text-sm font-medium ${
                  stat.isPositive ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {stat.change}
              </span>
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                {stat.value}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {stat.title}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Admin Actions */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          빠른 작업
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
            <Users className="w-6 h-6 text-primary mb-2" />
            <h3 className="font-medium text-gray-900 dark:text-white">
              사용자 추가
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              새로운 직원 계정 생성
            </p>
          </button>
          
          <button className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
            <FileText className="w-6 h-6 text-accent mb-2" />
            <h3 className="font-medium text-gray-900 dark:text-white">
              리포트 생성
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              월간 통계 리포트 다운로드
            </p>
          </button>
          
          <button className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
            <Database className="w-6 h-6 text-success mb-2" />
            <h3 className="font-medium text-gray-900 dark:text-white">
              백업 실행
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              데이터베이스 백업 시작
            </p>
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        {children}
      </div>
    </div>
  );

  return <MainLayout>{adminContent}</MainLayout>;
};

export default AdminLayout;