'use client';

import { useRef, useEffect } from 'react';
import Image from 'next/image';
import Editor from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import type { File, Template } from '@/lib/types';
import { X } from 'lucide-react';

interface EditorAreaProps {
  activeFile: File | null;
  openTabs: string[];
  onEditorChange: (value: string) => void;
  onTabChange: (filename: string) => void;
  onTabClose: (filename: string) => void;
  onCreateFile: () => void;
  templates: Template[];
  onImportTemplate: (template: Template) => void;
}

const FileIcon = ({ filename }: { filename: string }) => {
  if (filename.endsWith('.py')) {
    return <Image src="/assets/python.svg" alt="" width={14} height={14} className="shrink-0" />;
  }
  if (filename.endsWith('.c')) {
    return <Image src="/assets/c.svg" alt="" width={14} height={14} className="shrink-0" />;
  }
  if (filename.endsWith('.cpp') || filename.endsWith('.cc')) {
    return <Image src="/assets/cpp.svg" alt="" width={14} height={14} className="shrink-0" />;
  }
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="#858585" className="shrink-0">
      <path d="M4 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.5L9.5 0H4zm5.5 0v3a1.5 1.5 0 0 0 1.5 1.5h3"/>
    </svg>
  );
};

const getLanguage = (filename: string) => {
  if (filename.endsWith('.py')) return 'python';
  if (filename.endsWith('.c')) return 'c';
  if (filename.endsWith('.cpp') || filename.endsWith('.cc')) return 'cpp';
  return 'plaintext';
}

export function EditorArea({
  activeFile,
  openTabs,
  onEditorChange,
  onTabChange,
  onTabClose,
  onCreateFile,
  templates,
  onImportTemplate,
}: EditorAreaProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  useEffect(() => {
    if (editorRef.current) {
      // Custom theme or settings could go here
    }
  }, []);

  return (
    <div className="flex-1 flex flex-col min-w-0" style={{ backgroundColor: '#1e1e1e' }}>
      {/* Tab Bar */}
      {openTabs.length > 0 && (
        <div 
          className="flex items-center shrink-0 overflow-x-auto"
          style={{ 
            height: '36px',
            backgroundColor: '#252526',
            borderBottom: '1px solid #333',
          }}
        >
          {openTabs.map((filename) => (
            <div
              key={filename}
              className="group flex items-center cursor-pointer"
              style={{
                height: '36px',
                paddingLeft: '14px',
                paddingRight: '14px',
                gap: '10px',
                borderLeft: activeFile?.name === filename ? '2px solid #00ff88' : '2px solid transparent',
                backgroundColor: activeFile?.name === filename ? 'rgba(0, 255, 136, 0.08)' : 'transparent',
                color: activeFile?.name === filename ? '#00ff88' : '#969696',
                fontFamily: 'JetBrains Mono, monospace',
                transition: 'all 0.15s ease',
              }}
              onClick={() => onTabChange(filename)}
              onMouseEnter={(e) => {
                if (activeFile?.name !== filename) {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                }
              }}
              onMouseLeave={(e) => {
                if (activeFile?.name !== filename) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <FileIcon filename={filename} />
              <span style={{ fontSize: '12px' }}>
                {filename}
              </span>
              <button
                type="button"
                aria-label={`Close ${filename}`}
                onClick={(e) => {
                  e.stopPropagation();
                  onTabClose(filename);
                }}
                className="opacity-0 group-hover:opacity-100"
                style={{
                  width: '20px',
                  height: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: '4px',
                  marginLeft: '4px',
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <X style={{ width: '12px', height: '12px', color: '#808080' }} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Editor */}
      <div className="flex-1 relative min-h-0">
        {activeFile ? (
          <Editor
            height="100%"
            language={getLanguage(activeFile.name)}
            theme="vs-dark"
            value={activeFile.content}
            onChange={(value) => onEditorChange(value || '')}
            onMount={(editor) => {
              editorRef.current = editor;
            }}
            options={{
              minimap: { enabled: false },
              fontSize: 13,
              fontFamily: 'JetBrains Mono, Fira Code, monospace',
              fontLigatures: true,
              scrollBeyondLastLine: false,
              padding: { top: 16, bottom: 16 },
              lineNumbers: 'on',
              glyphMargin: false,
              folding: true,
              lineDecorationsWidth: 8,
              lineNumbersMinChars: 4,
              renderLineHighlight: 'line',
              renderLineHighlightOnlyWhenFocus: true,
              cursorBlinking: 'smooth',
              cursorSmoothCaretAnimation: 'on',
              smoothScrolling: true,
              scrollbar: {
                vertical: 'auto',
                horizontal: 'auto',
                useShadows: false,
                verticalScrollbarSize: 8,
                horizontalScrollbarSize: 8,
              },
              overviewRulerLanes: 0,
              hideCursorInOverviewRuler: true,
              overviewRulerBorder: false,
            }}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center overflow-auto">
            <div className="text-center max-w-md px-8 py-12">
              {/* Logo / Branding - Coder/Gamer themed */}
              <div className="mb-10">
                {/* Terminal-style icon */}
                <div 
                  className="inline-flex items-center justify-center w-16 h-16 rounded-xl mb-6 relative"
                  style={{ 
                    // background: 'linear-gradient(135deg, #1e1e1e 0%, #2d2d3a 100%)',
                    // border: '1px solid #404040',
                    // boxShadow: '0 0 30px rgba(0, 255, 136, 0.1), inset 0 1px 0 rgba(255,255,255,0.05)'
                  }}
                >
                  <span style={{ 
                    fontFamily: 'JetBrains Mono, Fira Code, monospace',
                    fontSize: '24px',
                    fontWeight: 700,
                    color: '#00ff88',
                    textShadow: '0 0 10px rgba(0, 255, 136, 0.5)'
                  }}>&gt;_</span>
                </div>
                
                {/* Brand name - monospace coder style */}
                <h1 
                  className="mb-3"
                  style={{ 
                    fontFamily: 'JetBrains Mono, Fira Code, monospace',
                    fontSize: '28px',
                    fontWeight: 700,
                    letterSpacing: '-0.5px',
                  }}
                >
                  <span style={{ color: '#ffffff' }}>jam</span>
                  <span style={{ 
                    color: '#00ff88',
                    textShadow: '0 0 20px rgba(0, 255, 136, 0.4)'
                  }}>code</span>
                  <span style={{ color: '#666' }}>.fun</span>
                </h1>
                
                <p style={{ 
                  color: '#858585',
                  fontSize: '13px',
                  fontFamily: 'JetBrains Mono, monospace',
                }}>
                  {'// build JAM services in py, c, c++'}
                </p>
              </div>

              {/* Quick Actions */}
              <div className="space-y-2 mb-8">
                <button
                  onClick={onCreateFile}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all group"
                  style={{
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    border: '1px solid rgba(0, 255, 136, 0.2)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(0, 255, 136, 0.15)';
                    e.currentTarget.style.borderColor = 'rgba(0, 255, 136, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(0, 255, 136, 0.1)';
                    e.currentTarget.style.borderColor = 'rgba(0, 255, 136, 0.2)';
                  }}
                >
                  <div 
                    className="w-8 h-8 rounded flex items-center justify-center"
                    style={{ backgroundColor: 'rgba(0, 255, 136, 0.15)' }}
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="#00ff88">
                      <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
                    </svg>
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-sm" style={{ color: '#00ff88', fontFamily: 'JetBrains Mono, monospace' }}>new_file()</div>
                    <div className="text-xs" style={{ color: '#858585' }}>start from scratch</div>
                  </div>
                  <span className="text-xs px-2 py-1 rounded" style={{ backgroundColor: '#333', color: '#999', fontFamily: 'JetBrains Mono, monospace' }}>⌘N</span>
                </button>
              </div>

              {/* Examples */}
              {templates.length > 0 && (
                <div>
                  <div 
                    className="text-left mb-3"
                    style={{ 
                      fontSize: '11px',
                      color: '#858585',
                      fontFamily: 'JetBrains Mono, monospace',
                    }}
                  >
                    {'// examples'}
                  </div>
                  <div className="grid gap-2">
                    {templates.map((template) => (
                      <button
                        key={template.path}
                        onClick={() => onImportTemplate(template)}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all"
                        style={{ 
                          backgroundColor: '#252526',
                          border: '1px solid #333',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#2d2d2d';
                          e.currentTarget.style.borderColor = '#444';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = '#252526';
                          e.currentTarget.style.borderColor = '#333';
                        }}
                      >
                        <FileIcon filename={template.name} />
                        <div className="flex-1">
                          <div 
                            className="text-sm"
                            style={{ color: '#cccccc', fontFamily: 'JetBrains Mono, monospace' }}
                          >
                            {template.name}
                          </div>
                        </div>
                        <span 
                          className="text-xs px-2 py-0.5 rounded"
                          style={{ 
                            backgroundColor: template.language === 'python' ? 'rgba(255, 212, 59, 0.15)' : 
                                           template.language === 'c' ? 'rgba(85, 85, 255, 0.15)' : 
                                           'rgba(243, 75, 125, 0.15)',
                            color: template.language === 'python' ? '#ffd43b' : 
                                  template.language === 'c' ? '#5555ff' : '#f34b7d',
                            fontFamily: 'JetBrains Mono, monospace',
                          }}
                        >
                          {template.language}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Footer hint */}
              <div className="mt-10 pt-6 border-t" style={{ borderColor: '#333' }}>
                <div 
                  className="flex items-center justify-center gap-6 text-xs"
                  style={{ color: '#666', fontFamily: 'JetBrains Mono, monospace' }}
                >
                  <span>⌘B build</span>
                  <span>⌘R run</span>
                  <span>⌘S save</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Status Bar */}
      {activeFile && (
        <div 
          className="h-[24px] flex items-center justify-between px-4 shrink-0"
          style={{
            backgroundColor: '#252526',
            borderTop: '1px solid #333',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '11px',
          }}
        >
          <div className="flex items-center gap-4" style={{ color: '#858585' }}>
            <span 
              className="px-1.5 py-0.5 rounded"
              style={{ 
                backgroundColor: activeFile.language === 'python' ? 'rgba(255, 212, 59, 0.15)' : 
                               activeFile.language === 'c' ? 'rgba(85, 85, 255, 0.15)' : 
                               'rgba(243, 75, 125, 0.15)',
                color: activeFile.language === 'python' ? '#ffd43b' : 
                      activeFile.language === 'c' ? '#5555ff' : '#f34b7d',
              }}
            >
              {activeFile.language}
            </span>
            <span>utf-8</span>
          </div>
          <div className="flex items-center gap-4" style={{ color: '#666' }}>
            <span>{new Date(activeFile.lastModified).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        </div>
      )}
    </div>
  );
}
