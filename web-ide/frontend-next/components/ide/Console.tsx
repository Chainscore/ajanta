'use client';

import type { Status } from '@/lib/types';

interface ConsolePanelProps {
  logs: string;
  status: Status;
}

const Icons = {
  terminal: () => (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
      <path d="M6 9a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3A.5.5 0 0 1 6 9zM3.854 4.146a.5.5 0 1 0-.708.708L4.793 6.5 3.146 8.146a.5.5 0 1 0 .708.708l2-2a.5.5 0 0 0 0-.708l-2-2z"/>
      <path d="M2 1a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2H2zm12 1a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1h12z"/>
    </svg>
  ),
  loader: () => (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor" className="animate-spin">
      <path d="M8 0a8 8 0 1 0 8 8h-1.5A6.5 6.5 0 1 1 8 1.5V0z"/>
    </svg>
  ),
  check: () => (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
    </svg>
  ),
  error: () => (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/>
    </svg>
  ),
};

export function Console({ logs, status }: ConsolePanelProps) {
  const getStatusIcon = () => {
    switch (status) {
      case 'compiling':
      case 'running':
        return <span style={{ color: '#00c8ff' }}><Icons.loader /></span>;
      case 'success':
        return <span style={{ color: '#00ff88' }}><Icons.check /></span>;
      case 'error':
        return <span style={{ color: '#ff4444' }}><Icons.error /></span>;
      default:
        return <span style={{ color: '#858585' }}><Icons.terminal /></span>;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'compiling': return 'compiling...';
      case 'running': return 'running...';
      case 'deploying': return 'deploying...';
      case 'invoking': return 'invoking...';
      case 'success': return 'success';
      case 'error': return 'error';
      default: return 'ready';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'compiling':
      case 'running':
        return '#00c8ff';
      case 'deploying':
      case 'invoking':
        return '#ff8800';
      case 'success':
        return '#00ff88';
      case 'error':
        return '#ff4444';
      default:
        return '#858585';
    }
  };

  return (
    <div 
      className="h-32 flex flex-col shrink-0"
      style={{
        backgroundColor: '#1e1e1e',
        borderTop: '1px solid #333',
      }}
    >
      {/* Console Header */}
      <div 
        className="h-8 flex items-center px-4 justify-between shrink-0"
        style={{ backgroundColor: '#252526' }}
      >
        <div 
          className="flex items-center gap-2"
          style={{ 
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '11px',
            color: '#858585',
          }}
        >
          <Icons.terminal />
          <span>{'// console'}</span>
        </div>
        <div 
          className="flex items-center gap-2"
          style={{ 
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '11px',
            color: getStatusColor(),
          }}
        >
          {getStatusIcon()}
          <span>{getStatusText()}</span>
        </div>
      </div>

      {/* Console Output */}
      <div 
        className="flex-1 overflow-auto px-4 py-2"
        style={{ fontFamily: 'JetBrains Mono, monospace' }}
      >
        {logs ? (
          <pre 
            className="whitespace-pre-wrap"
            style={{ 
              fontSize: '12px',
              lineHeight: '1.5',
              color: status === 'error' ? '#ff4444' : '#ccc',
            }}
          >
            {logs}
          </pre>
        ) : (
          <span style={{ fontSize: '12px', color: '#666' }}>
            {'// ⌘B to build'}
          </span>
        )}
      </div>
    </div>
  );
}
