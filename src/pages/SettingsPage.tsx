import React, { useState } from 'react';
import MainLayout from '../layouts/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useTheme } from '../hooks/useTheme';
import AccessibilitySettings from '../components/AccessibilitySettings';
import KeyboardShortcuts from '../components/KeyboardShortcuts';
import { 
  Settings,
  Moon,
  Sun,
  Monitor,
  Bell,
  Lock,
  User,
  Keyboard,
  Eye,
  ChevronRight
} from 'lucide-react';

const SettingsPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false);
  const [activeTab, setActiveTab] = useState('general');

  const tabs = [
    { id: 'general', label: '일반', icon: Settings },
    { id: 'accessibility', label: '접근성', icon: Eye },
    { id: 'notifications', label: '알림', icon: Bell },
    { id: 'security', label: '보안', icon: Lock },
    { id: 'account', label: '계정', icon: User },
  ];

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            설정
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            시스템 설정 및 개인 환경을 관리합니다
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 사이드바 네비게이션 */}
          <div className="lg:col-span-1">
            <Card>
              <CardContent className="p-2">
                <nav className="space-y-1">
                  {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          activeTab === tab.id
                            ? 'bg-primary text-primary-foreground'
                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        <span>{tab.label}</span>
                        <ChevronRight className="w-4 h-4 ml-auto" />
                      </button>
                    );
                  })}
                </nav>
              </CardContent>
            </Card>

            {/* 키보드 단축키 버튼 */}
            <Button
              variant="outline"
              className="w-full mt-4"
              onClick={() => setShowKeyboardShortcuts(true)}
            >
              <Keyboard className="w-4 h-4 mr-2" />
              키보드 단축키
            </Button>
          </div>

          {/* 메인 콘텐츠 */}
          <div className="lg:col-span-3">
            {/* 일반 설정 */}
            {activeTab === 'general' && (
              <div className="space-y-6">
                {/* 테마 설정 */}
                <Card>
                  <CardHeader>
                    <CardTitle>테마 설정</CardTitle>
                    <CardDescription>
                      시스템 전체의 색상 테마를 변경합니다
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <p className="text-sm font-medium">다크 모드</p>
                        <p className="text-sm text-gray-500">
                          어두운 환경에서 눈의 피로를 줄여줍니다
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant={theme === 'light' ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => theme === 'dark' && toggleTheme()}
                        >
                          <Sun className="w-4 h-4" />
                        </Button>
                        <Button
                          variant={theme === 'dark' ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => theme === 'light' && toggleTheme()}
                        >
                          <Moon className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* 언어 설정 */}
                <Card>
                  <CardHeader>
                    <CardTitle>언어 설정</CardTitle>
                    <CardDescription>
                      시스템 언어를 변경합니다
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700">
                      <option value="ko">한국어</option>
                      <option value="en">English</option>
                      <option value="ja">日本語</option>
                      <option value="zh">中文</option>
                    </select>
                  </CardContent>
                </Card>

                {/* 날짜 및 시간 */}
                <Card>
                  <CardHeader>
                    <CardTitle>날짜 및 시간</CardTitle>
                    <CardDescription>
                      날짜 및 시간 표시 형식을 설정합니다
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">시간대</label>
                      <select className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700">
                        <option value="Asia/Seoul">서울 (GMT+9)</option>
                        <option value="Asia/Tokyo">도쿄 (GMT+9)</option>
                        <option value="America/New_York">뉴욕 (GMT-5)</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-sm font-medium">날짜 형식</label>
                      <select className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700">
                        <option value="yyyy-mm-dd">2024-01-15</option>
                        <option value="dd/mm/yyyy">15/01/2024</option>
                        <option value="mm/dd/yyyy">01/15/2024</option>
                      </select>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* 접근성 설정 */}
            {activeTab === 'accessibility' && <AccessibilitySettings />}

            {/* 알림 설정 */}
            {activeTab === 'notifications' && (
              <Card>
                <CardHeader>
                  <CardTitle>알림 설정</CardTitle>
                  <CardDescription>
                    시스템 알림을 관리합니다
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">이메일 알림</p>
                      <p className="text-sm text-gray-500">중요한 업데이트를 이메일로 받습니다</p>
                    </div>
                    <Button variant="outline" size="sm">활성화</Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">브라우저 알림</p>
                      <p className="text-sm text-gray-500">실시간 알림을 받습니다</p>
                    </div>
                    <Button variant="outline" size="sm">활성화</Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">평가 마감 알림</p>
                      <p className="text-sm text-gray-500">평가 마감일 3일 전 알림</p>
                    </div>
                    <Button variant="default" size="sm">활성화됨</Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 보안 설정 */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>비밀번호 변경</CardTitle>
                    <CardDescription>
                      계정 보안을 위해 정기적으로 비밀번호를 변경하세요
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">현재 비밀번호</label>
                      <input type="password" className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700" />
                    </div>
                    <div>
                      <label className="text-sm font-medium">새 비밀번호</label>
                      <input type="password" className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700" />
                    </div>
                    <div>
                      <label className="text-sm font-medium">새 비밀번호 확인</label>
                      <input type="password" className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700" />
                    </div>
                    <Button className="w-full">비밀번호 변경</Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>2단계 인증</CardTitle>
                    <CardDescription>
                      계정 보안을 강화합니다
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">2단계 인증 사용</p>
                        <p className="text-sm text-gray-500">로그인 시 추가 인증이 필요합니다</p>
                      </div>
                      <Button variant="outline">설정하기</Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* 계정 설정 */}
            {activeTab === 'account' && (
              <Card>
                <CardHeader>
                  <CardTitle>계정 정보</CardTitle>
                  <CardDescription>
                    기본 계정 정보를 관리합니다
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">이름</label>
                    <input type="text" value="홍길동" className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700" readOnly />
                  </div>
                  <div>
                    <label className="text-sm font-medium">이메일</label>
                    <input type="email" value="hong.gildong@okfn.co.kr" className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700" readOnly />
                  </div>
                  <div>
                    <label className="text-sm font-medium">부서</label>
                    <input type="text" value="IT개발팀" className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700" readOnly />
                  </div>
                  <div>
                    <label className="text-sm font-medium">직급</label>
                    <input type="text" value="선임 개발자" className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700" readOnly />
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* 키보드 단축키 모달 */}
        <KeyboardShortcuts 
          open={showKeyboardShortcuts} 
          onOpenChange={setShowKeyboardShortcuts} 
        />
      </div>
    </MainLayout>
  );
};

export default SettingsPage;