'use client';

import { useEffect } from 'react';

export function useKeyboardShortcuts(handlers: {
  onCompile?: () => void;
  onRun?: () => void;
  onNewFile?: () => void;
  onSave?: () => void;
}) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const cmdOrCtrl = isMac ? e.metaKey : e.ctrlKey;

      if (cmdOrCtrl && e.key === 'b') {
        e.preventDefault();
        handlers.onCompile?.();
      } else if (cmdOrCtrl && e.key === 'r') {
        e.preventDefault();
        handlers.onRun?.();
      } else if (cmdOrCtrl && e.key === 'n') {
        e.preventDefault();
        handlers.onNewFile?.();
      } else if (cmdOrCtrl && e.key === 's') {
        e.preventDefault();
        handlers.onSave?.();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handlers]);
}
