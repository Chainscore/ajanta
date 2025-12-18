'use client';

import { useState, useEffect, useRef } from 'react';

interface NewFileModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (filename: string) => void;
}

export function NewFileModal({ isOpen, onClose, onSubmit }: NewFileModalProps) {
  const [filename, setFilename] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setFilename('');
      // Focus input after modal opens
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, onClose]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (filename.trim()) {
      onSubmit(filename.trim());
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="rounded-xl p-6 w-96 shadow-2xl"
        style={{
          backgroundColor: '#1e1e1e',
          border: '1px solid #3c3c3c',
          animation: 'modalSlideIn 0.15s ease-out',
        }}
      >
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: 'rgba(0, 255, 136, 0.1)' }}
          >
            <svg width="20" height="20" viewBox="0 0 16 16" fill="#00ff88">
              <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>
          </div>
          <div>
            <h2
              style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '16px',
                color: '#ffffff',
                margin: 0,
              }}
            >
              new_file()
            </h2>
            <p
              style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '11px',
                color: '#858585',
                margin: 0,
              }}
            >
              create a new JAM service
            </p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '11px',
                color: '#858585',
                display: 'block',
                marginBottom: '8px',
              }}
            >
              {'// filename'}
            </label>
            <input
              ref={inputRef}
              type="text"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="service.py, main.c, app.cpp"
              className="w-full px-4 py-3 rounded-lg focus:outline-none transition-all"
              style={{
                backgroundColor: '#252526',
                border: '1px solid #3c3c3c',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '14px',
                color: '#ffffff',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = '#00ff88';
                e.currentTarget.style.boxShadow = '0 0 0 2px rgba(0, 255, 136, 0.1)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = '#3c3c3c';
                e.currentTarget.style.boxShadow = 'none';
              }}
            />
          </div>

          {/* File type hints */}
          <div className="flex gap-2 mb-6">
            {['.py', '.c', '.cpp'].map((ext) => (
              <button
                key={ext}
                type="button"
                onClick={() => setFilename((prev) => {
                  const base = prev.replace(/\.(py|c|cpp|cc)$/, '');
                  return (base || 'service') + ext;
                })}
                className="px-3 py-1.5 rounded-lg transition-all"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid #3c3c3c',
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '11px',
                  color: '#858585',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(0, 255, 136, 0.1)';
                  e.currentTarget.style.borderColor = 'rgba(0, 255, 136, 0.3)';
                  e.currentTarget.style.color = '#00ff88';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                  e.currentTarget.style.borderColor = '#3c3c3c';
                  e.currentTarget.style.color = '#858585';
                }}
              >
                {ext}
              </button>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-lg transition-all"
              style={{
                backgroundColor: 'transparent',
                border: '1px solid #3c3c3c',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '13px',
                color: '#858585',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                e.currentTarget.style.borderColor = '#555';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.borderColor = '#3c3c3c';
              }}
            >
              cancel
            </button>
            <button
              type="submit"
              disabled={!filename.trim()}
              className="flex-1 py-2.5 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                backgroundColor: 'rgba(0, 255, 136, 0.15)',
                border: '1px solid rgba(0, 255, 136, 0.3)',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '13px',
                color: '#00ff88',
              }}
              onMouseEnter={(e) => {
                if (!e.currentTarget.disabled) {
                  e.currentTarget.style.backgroundColor = 'rgba(0, 255, 136, 0.25)';
                  e.currentTarget.style.borderColor = 'rgba(0, 255, 136, 0.5)';
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(0, 255, 136, 0.15)';
                e.currentTarget.style.borderColor = 'rgba(0, 255, 136, 0.3)';
              }}
            >
              create
            </button>
          </div>
        </form>
      </div>

      <style jsx global>{`
        @keyframes modalSlideIn {
          from {
            opacity: 0;
            transform: scale(0.95) translateY(-10px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
