'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import type { FileSystem, Template } from '@/lib/types';

interface SidebarProps {
  files: FileSystem;
  activeFileName: string | null;
  onSelectFile: (name: string) => void;
  onCreateFile: () => void;
  onDeleteFile: (name: string) => void;
  templates: Template[];
  onImportTemplate: (template: Template) => void;
}

interface ContextMenuState {
  show: boolean;
  x: number;
  y: number;
  fileName: string | null;
}

const FileIcon = ({ filename }: { filename: string }) => {
  if (filename.endsWith('.py')) {
    return <Image src="/assets/python.svg" alt="" width={16} height={16} />;
  }
  if (filename.endsWith('.c')) {
    return <Image src="/assets/c.svg" alt="" width={16} height={16} />;
  }
  if (filename.endsWith('.cpp') || filename.endsWith('.cc')) {
    return <Image src="/assets/cpp.svg" alt="" width={16} height={16} />;
  }
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="#505050">
      <path d="M4 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.5L9.5 0H4zm5.5 0v3a1.5 1.5 0 0 0 1.5 1.5h3"/>
    </svg>
  );
};

export function Sidebar({
  files,
  activeFileName,
  onSelectFile,
  onCreateFile,
  onDeleteFile,
  templates,
  onImportTemplate,
}: SidebarProps) {
  const [showExamples, setShowExamples] = useState(false);
  const [contextMenu, setContextMenu] = useState<ContextMenuState>({
    show: false,
    x: 0,
    y: 0,
    fileName: null,
  });
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = () => setContextMenu(prev => ({ ...prev, show: false }));
    if (contextMenu.show) {
      document.addEventListener('click', handleClick);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [contextMenu.show]);

  const handleContextMenu = (e: React.MouseEvent, fileName: string | null) => {
    e.preventDefault();
    setContextMenu({
      show: true,
      x: e.clientX,
      y: e.clientY,
      fileName,
    });
  };

  return (
    <aside 
      className="w-52 flex flex-col shrink-0"
      style={{
        backgroundColor: '#252526',
        borderRight: '1px solid #333',
      }}
    >
      {/* Files Header */}
      <div 
        className="h-10 px-4 flex items-center"
        onContextMenu={(e) => handleContextMenu(e, null)}
      >
        <span 
          style={{ 
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '11px',
            color: '#858585',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          {'// files'}
        </span>
      </div>

      {/* File List */}
      <div 
        className="flex-1 overflow-y-auto"
        onContextMenu={(e) => {
          if (e.target === e.currentTarget) handleContextMenu(e, null);
        }}
      >
        {Object.values(files).map((file) => (
          <div
            key={file.name}
            className="flex items-center gap-3 cursor-pointer transition-all"
            style={{
              height: '34px',
              paddingLeft: '16px',
              paddingRight: '16px',
              backgroundColor: activeFileName === file.name ? 'rgba(0, 255, 136, 0.1)' : 'transparent',
              borderLeft: activeFileName === file.name ? '2px solid #00ff88' : '2px solid transparent',
              color: activeFileName === file.name ? '#00ff88' : '#cccccc',
            }}
            onClick={() => onSelectFile(file.name)}
            onContextMenu={(e) => handleContextMenu(e, file.name)}
            onMouseEnter={(e) => {
              if (activeFileName !== file.name) {
                e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
              }
            }}
            onMouseLeave={(e) => {
              if (activeFileName !== file.name) {
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            <FileIcon filename={file.name} />
            <span 
              className="flex-1 truncate"
              style={{ 
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '13px',
              }}
            >
              {file.name}
            </span>
          </div>
        ))}
        
        {Object.keys(files).length === 0 && (
          <div 
            className="px-4 py-8 text-center"
            style={{ 
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '12px',
              color: '#666',
            }}
            onContextMenu={(e) => handleContextMenu(e, null)}
          >
            {'// right-click to create'}
          </div>
        )}
      </div>

      {/* Examples Section */}
      <div style={{ borderTop: '1px solid #333' }}>
        <button
          onClick={() => setShowExamples(!showExamples)}
          className="w-full px-4 flex justify-start h-9 flex items-center gap-2 transition-colors"
          style={{ 
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '11px',
            color: '#858585',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
        >
          <svg 
            width="10" 
            height="10" 
            viewBox="0 0 16 16" 
            fill="#858585"
            style={{ 
              transform: showExamples ? 'rotate(90deg)' : 'rotate(0deg)',
              transition: 'transform 0.15s ease',
            }}
          >
            <path d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>
          </svg>
          <span>examples</span>
        </button>

        {showExamples && (
          <div className="pb-2">
            {templates.map((template) => (
              <button
                key={template.path}
                onClick={() => onImportTemplate(template)}
                className="w-full flex items-center gap-3 px-4 transition-colors"
                style={{ 
                  height: '28px',
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '12px',
                  color: '#999',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                  e.currentTarget.style.color = '#ccc';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = '#999';
                }}
              >
                <FileIcon filename={template.name} />
                <span className="flex-1 truncate text-left">{template.name}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Context Menu */}
      {contextMenu.show && (
        <div
          ref={menuRef}
          className="fixed rounded-lg shadow-2xl py-1 z-50 min-w-[160px]"
          style={{ 
            left: contextMenu.x, 
            top: contextMenu.y,
            backgroundColor: '#2d2d2d',
            border: '1px solid #454545',
          }}
        >
          <button
            onClick={() => {
              onCreateFile();
              setContextMenu(prev => ({ ...prev, show: false }));
            }}
            className="w-full py-2 text-left flex items-center gap-3 transition-colors"
            style={{ 
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '12px',
              color: '#00ff88',
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(0, 255, 136, 0.1)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>
            new_file()
          </button>
          {contextMenu.fileName && (
            <>
              <div style={{ height: '1px', backgroundColor: '#2a2a2a', margin: '4px 0' }} />
              <button
                onClick={() => {
                  onDeleteFile(contextMenu.fileName!);
                  setContextMenu(prev => ({ ...prev, show: false }));
                }}
                className="w-full py-2 text-left flex items-center gap-3 transition-colors"
                style={{ 
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '12px',
                  color: '#ff4444',

                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 68, 68, 0.1)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                  <path fillRule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4L4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                </svg>
                delete()
              </button>
            </>
          )}
        </div>
      )}
    </aside>
  );
}
