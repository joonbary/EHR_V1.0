import React, { useState } from 'react';
import MainLayout from '../layouts/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { 
  User, 
  Mail, 
  Phone, 
  Building2, 
  Briefcase, 
  Calendar,
  Edit,
  Save,
  X
} from 'lucide-react';

interface EmployeeProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  department: string;
  position: string;
  joinDate: string;
  employeeId: string;
  manager: string;
  location: string;
  skills: string[];
}

const ProfilePage: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState<EmployeeProfile>({
    id: '1',
    name: '홍길동',
    email: 'hong.gildong@okfn.co.kr',
    phone: '010-1234-5678',
    department: 'IT개발팀',
    position: '선임 개발자',
    joinDate: '2020-03-15',
    employeeId: 'EMP-2020-0315',
    manager: '김부장',
    location: '서울 본사',
    skills: ['React', 'TypeScript', 'Node.js', 'AWS'],
  });

  const [editedProfile, setEditedProfile] = useState(profile);

  const handleEdit = () => {
    setIsEditing(true);
    setEditedProfile(profile);
  };

  const handleSave = () => {
    setProfile(editedProfile);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedProfile(profile);
    setIsEditing(false);
  };

  const handleInputChange = (field: keyof EmployeeProfile, value: string) => {
    setEditedProfile({ ...editedProfile, [field]: value });
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            직원 프로필
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            개인 정보 및 업무 정보를 확인하고 관리합니다
          </p>
        </div>

        {/* 프로필 카드 */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-20 h-20 bg-gradient-to-br from-primary to-primary-hover rounded-full flex items-center justify-center">
                  <User className="w-10 h-10 text-white" />
                </div>
                <div>
                  <CardTitle className="text-2xl">{profile.name}</CardTitle>
                  <CardDescription>{profile.position} · {profile.department}</CardDescription>
                </div>
              </div>
              <div>
                {!isEditing ? (
                  <Button onClick={handleEdit} variant="outline">
                    <Edit className="w-4 h-4 mr-2" />
                    편집
                  </Button>
                ) : (
                  <div className="space-x-2">
                    <Button onClick={handleSave} variant="default">
                      <Save className="w-4 h-4 mr-2" />
                      저장
                    </Button>
                    <Button onClick={handleCancel} variant="outline">
                      <X className="w-4 h-4 mr-2" />
                      취소
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 기본 정보 */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  기본 정보
                </h3>
                
                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-gray-500 dark:text-gray-400">이메일</label>
                    {isEditing ? (
                      <Input
                        type="email"
                        value={editedProfile.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        className="mt-1"
                      />
                    ) : (
                      <div className="flex items-center mt-1">
                        <Mail className="w-4 h-4 mr-2 text-gray-400" />
                        <span>{profile.email}</span>
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-500 dark:text-gray-400">전화번호</label>
                    {isEditing ? (
                      <Input
                        type="tel"
                        value={editedProfile.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        className="mt-1"
                      />
                    ) : (
                      <div className="flex items-center mt-1">
                        <Phone className="w-4 h-4 mr-2 text-gray-400" />
                        <span>{profile.phone}</span>
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-500 dark:text-gray-400">사원번호</label>
                    <div className="flex items-center mt-1">
                      <span className="font-mono">{profile.employeeId}</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-500 dark:text-gray-400">입사일</label>
                    <div className="flex items-center mt-1">
                      <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                      <span>{new Date(profile.joinDate).toLocaleDateString('ko-KR')}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* 업무 정보 */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  업무 정보
                </h3>
                
                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-gray-500 dark:text-gray-400">부서</label>
                    {isEditing ? (
                      <Select
                        value={editedProfile.department}
                        onValueChange={(value) => handleInputChange('department', value)}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="IT개발팀">IT개발팀</SelectItem>
                          <SelectItem value="인사팀">인사팀</SelectItem>
                          <SelectItem value="재무팀">재무팀</SelectItem>
                          <SelectItem value="마케팅팀">마케팅팀</SelectItem>
                        </SelectContent>
                      </Select>
                    ) : (
                      <div className="flex items-center mt-1">
                        <Building2 className="w-4 h-4 mr-2 text-gray-400" />
                        <span>{profile.department}</span>
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-500 dark:text-gray-400">직급</label>
                    {isEditing ? (
                      <Select
                        value={editedProfile.position}
                        onValueChange={(value) => handleInputChange('position', value)}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="사원">사원</SelectItem>
                          <SelectItem value="주임">주임</SelectItem>
                          <SelectItem value="대리">대리</SelectItem>
                          <SelectItem value="과장">과장</SelectItem>
                          <SelectItem value="차장">차장</SelectItem>
                          <SelectItem value="부장">부장</SelectItem>
                          <SelectItem value="선임 개발자">선임 개발자</SelectItem>
                        </SelectContent>
                      </Select>
                    ) : (
                      <div className="flex items-center mt-1">
                        <Briefcase className="w-4 h-4 mr-2 text-gray-400" />
                        <span>{profile.position}</span>
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-500 dark:text-gray-400">상급자</label>
                    <div className="flex items-center mt-1">
                      <User className="w-4 h-4 mr-2 text-gray-400" />
                      <span>{profile.manager}</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-500 dark:text-gray-400">근무지</label>
                    <div className="flex items-center mt-1">
                      <Building2 className="w-4 h-4 mr-2 text-gray-400" />
                      <span>{profile.location}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 스킬 */}
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                보유 스킬
              </h3>
              <div className="flex flex-wrap gap-2">
                {profile.skills.map((skill, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 추가 정보 카드들 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 평가 이력 */}
          <Card>
            <CardHeader>
              <CardTitle>최근 평가 이력</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">2023년 하반기</span>
                  <span className="text-sm font-semibold text-green-600">우수</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">2023년 상반기</span>
                  <span className="text-sm font-semibold text-blue-600">양호</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">2022년 하반기</span>
                  <span className="text-sm font-semibold text-green-600">우수</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 교육 이수 */}
          <Card>
            <CardHeader>
              <CardTitle>최근 교육 이수</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <div className="font-medium">React 고급 과정</div>
                  <div className="text-sm text-gray-500">2024.01.15 수료</div>
                </div>
                <div>
                  <div className="font-medium">AWS 클라우드 기초</div>
                  <div className="text-sm text-gray-500">2023.11.20 수료</div>
                </div>
                <div>
                  <div className="font-medium">리더십 향상 과정</div>
                  <div className="text-sm text-gray-500">2023.09.05 수료</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default ProfilePage;