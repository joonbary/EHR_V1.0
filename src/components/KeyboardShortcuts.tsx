import React from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Card } from './ui/card';
import { Keyboard } from 'lucide-react';

interface KeyboardShortcutsProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const shortcuts = [
  { category: '일반', items: [
    { keys: ['Alt', 'H'], description: '홈으로 이동' },
    { keys: ['/'], description: '검색창 포커스' },
    { keys: ['Esc'], description: '대화상자 닫기' },
    { keys: ['Alt', 'D'], description: '다크모드 전환' },
  ]},
  { category: '네비게이션', items: [
    { keys: ['Alt', '1'], description: '대시보드' },
    { keys: ['Alt', '2'], description: '직원 관리' },
    { keys: ['Alt', '3'], description: '평가 관리' },
    { keys: ['Alt', '4'], description: '조직도' },
  ]},
  { category: '작업', items: [
    { keys: ['Alt', 'N'], description: '새 직원 추가' },
    { keys: ['Ctrl', 'S'], description: '저장' },
    { keys: ['Ctrl', 'Enter'], description: '폼 제출' },
    { keys: ['Alt', 'E'], description: '편집 모드' },
  ]},
  { category: '접근성', items: [
    { keys: ['Alt', 'A'], description: '접근성 설정' },
    { keys: ['Alt', '+'], description: '글꼴 크기 증가' },
    { keys: ['Alt', '-'], description: '글꼴 크기 감소' },
    { keys: ['Alt', 'C'], description: '고대비 모드' },
  ]},
];

const KeyboardShortcuts: React.FC<KeyboardShortcutsProps> = ({ open, onOpenChange }) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Keyboard className="w-5 h-5" />
            키보드 단축키
          </DialogTitle>
          <DialogDescription>
            작업을 빠르게 수행하기 위한 키보드 단축키 목록입니다.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          {shortcuts.map((section) => (
            <Card key={section.category} className="p-4">
              <h3 className="font-semibold mb-3 text-primary">{section.category}</h3>
              <div className="space-y-2">
                {section.items.map((shortcut, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {shortcut.description}
                    </span>
                    <div className="flex items-center gap-1">
                      {shortcut.keys.map((key, keyIndex) => (
                        <React.Fragment key={keyIndex}>
                          <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">
                            {key}
                          </kbd>
                          {keyIndex < shortcut.keys.length - 1 && (
                            <span className="text-gray-400">+</span>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
        
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            <strong>팁:</strong> 키보드 단축키 도움말을 언제든지 보려면 <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">?</kbd> 키를 누르세요.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default KeyboardShortcuts;