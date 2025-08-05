import { useEffect, useCallback } from 'react';

interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  action: () => void;
  description: string;
}

export const useKeyboardNavigation = (shortcuts: KeyboardShortcut[]) => {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    for (const shortcut of shortcuts) {
      const matchesKey = event.key.toLowerCase() === shortcut.key.toLowerCase();
      const matchesCtrl = shortcut.ctrl ? event.ctrlKey || event.metaKey : true;
      const matchesAlt = shortcut.alt ? event.altKey : true;
      const matchesShift = shortcut.shift ? event.shiftKey : true;

      if (matchesKey && matchesCtrl && matchesAlt && matchesShift) {
        event.preventDefault();
        shortcut.action();
        break;
      }
    }
  }, [shortcuts]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return shortcuts;
};

// 기본 키보드 단축키
export const defaultShortcuts: KeyboardShortcut[] = [
  {
    key: '/',
    description: '검색 포커스',
    action: () => {
      const searchInput = document.querySelector('input[type="search"]') as HTMLInputElement;
      searchInput?.focus();
    },
  },
  {
    key: 'h',
    alt: true,
    description: '홈으로 이동',
    action: () => {
      window.location.href = '/dashboard';
    },
  },
  {
    key: 'n',
    alt: true,
    description: '새 직원 추가',
    action: () => {
      const addButton = document.querySelector('[data-action="add-employee"]') as HTMLElement;
      addButton?.click();
    },
  },
  {
    key: 'Escape',
    description: '대화상자 닫기',
    action: () => {
      const closeButton = document.querySelector('[data-action="close-dialog"]') as HTMLElement;
      closeButton?.click();
    },
  },
];