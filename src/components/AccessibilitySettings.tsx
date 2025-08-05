import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useAccessibility } from '../hooks/useAccessibility';
import { 
  Type, 
  Contrast, 
  Zap, 
  Eye,
  RotateCcw
} from 'lucide-react';

const AccessibilitySettings: React.FC = () => {
  const { settings, updateSetting, resetSettings } = useAccessibility();

  return (
    <Card>
      <CardHeader>
        <CardTitle>접근성 설정</CardTitle>
        <CardDescription>
          사용자 경험을 개선하기 위한 접근성 옵션을 설정합니다.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 글꼴 크기 */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium">
            <Type className="w-4 h-4" />
            글꼴 크기
          </label>
          <Select 
            value={settings.fontSize} 
            onValueChange={(value) => updateSetting('fontSize', value as any)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="normal">보통 (100%)</SelectItem>
              <SelectItem value="large">크게 (112.5%)</SelectItem>
              <SelectItem value="extra-large">매우 크게 (125%)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* 고대비 모드 */}
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm font-medium">
            <Contrast className="w-4 h-4" />
            고대비 모드
          </label>
          <Button
            variant={settings.highContrast ? "default" : "outline"}
            size="sm"
            onClick={() => updateSetting('highContrast', !settings.highContrast)}
          >
            {settings.highContrast ? '켜짐' : '꺼짐'}
          </Button>
        </div>

        {/* 모션 감소 */}
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm font-medium">
            <Zap className="w-4 h-4" />
            애니메이션 감소
          </label>
          <Button
            variant={settings.reduceMotion ? "default" : "outline"}
            size="sm"
            onClick={() => updateSetting('reduceMotion', !settings.reduceMotion)}
          >
            {settings.reduceMotion ? '켜짐' : '꺼짐'}
          </Button>
        </div>

        {/* 스크린 리더 모드 */}
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm font-medium">
            <Eye className="w-4 h-4" />
            스크린 리더 최적화
          </label>
          <Button
            variant={settings.screenReaderMode ? "default" : "outline"}
            size="sm"
            onClick={() => updateSetting('screenReaderMode', !settings.screenReaderMode)}
          >
            {settings.screenReaderMode ? '켜짐' : '꺼짐'}
          </Button>
        </div>

        {/* 초기화 버튼 */}
        <div className="pt-4 border-t">
          <Button
            variant="outline"
            onClick={resetSettings}
            className="w-full"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            기본 설정으로 되돌리기
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default AccessibilitySettings;