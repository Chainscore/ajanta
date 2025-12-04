'use client';

import type { Status } from '@/lib/types';

interface ControlPanelProps {
  onCompile: () => void;
  onRun: () => void;
  status: Status;
  pvmHex: string | null;
  payload: string;
  onPayloadChange: (value: string) => void;
}

const Icons = {
  build: () => (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="M9.972 2.508a.5.5 0 0 0-.16-.556l-.178-.129a5.009 5.009 0 0 0-2.076-.783C6.215.862 4.504 1.229 2.84 3.133H1.786a.5.5 0 0 0-.354.147L.146 4.567a.5.5 0 0 0 0 .706l2.571 2.579a.5.5 0 0 0 .708 0l1.286-1.29a.5.5 0 0 0 .146-.353V5.57l8.387 8.873A.5.5 0 0 0 14 14.5l1.5-1.5a.5.5 0 0 0 .017-.689l-9.129-8.63c.747-.456 1.772-.839 3.112-.839a.5.5 0 0 0 .472-.334z"/>
    </svg>
  ),
  play: () => (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>
    </svg>
  ),
  download: () => (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
      <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
    </svg>
  ),
};

export function ControlPanel({
  onCompile,
  onRun,
  status,
  pvmHex,
  payload,
  onPayloadChange,
}: ControlPanelProps) {
  return (
    <aside 
      className="w-56 flex flex-col shrink-0"
      style={{
        backgroundColor: '#252526',
        borderLeft: '1px solid #333',
      }}
    >
      {/* Actions Header */}
      <div className="h-10 px-4 flex items-center">
        <span 
          style={{ 
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '11px',
            color: '#858585',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          {'// actions'}
        </span>
      </div>
      
      {/* Buttons */}
      <div className="px-3 space-y-2">
        {/* Compile Button - Cyan themed */}
        <button
          onClick={onCompile}
          disabled={status === 'compiling' || status === 'running'}
          className="w-[88%] px-3 flex items-center gap-3 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            height: '40px',
            backgroundColor: 'rgba(0, 200, 255, 0.1)',
            border: '1px solid rgba(0, 200, 255, 0.2)',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '13px',
            color: '#00c8ff',
            
          }}
          onMouseEnter={(e) => {
            if (!e.currentTarget.disabled) {
              e.currentTarget.style.backgroundColor = 'rgba(0, 200, 255, 0.15)';
              e.currentTarget.style.borderColor = 'rgba(0, 200, 255, 0.4)';
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(0, 200, 255, 0.1)';
            e.currentTarget.style.borderColor = 'rgba(0, 200, 255, 0.2)';
          }}
        >
          <Icons.build />
          <span>build()</span>
          <span 
            className="ml-auto px-1.5 py-0.5 rounded"
            style={{ 
              fontSize: '10px',
              backgroundColor: '#333',
              color: '#888',
            }}
          >
            ⌘B
          </span>
        </button>

        {/* Run Button - Green themed */}
        <button
          onClick={onRun}
          disabled={!pvmHex || status === 'running' || status === 'compiling'}
          className="w-[88%] px-3 flex items-center gap-3 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            height: '40px',
            backgroundColor: pvmHex ? 'rgba(0, 255, 136, 0.1)' : 'rgba(255, 255, 255, 0.02)',
            border: `1px solid ${pvmHex ? 'rgba(0, 255, 136, 0.2)' : 'rgba(255, 255, 255, 0.05)'}`,
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '13px',
            color: pvmHex ? '#00ff88' : '#404040',
          }}
          onMouseEnter={(e) => {
            if (!e.currentTarget.disabled && pvmHex) {
              e.currentTarget.style.backgroundColor = 'rgba(0, 255, 136, 0.15)';
              e.currentTarget.style.borderColor = 'rgba(0, 255, 136, 0.4)';
            }
          }}
          onMouseLeave={(e) => {
            if (pvmHex) {
              e.currentTarget.style.backgroundColor = 'rgba(0, 255, 136, 0.1)';
              e.currentTarget.style.borderColor = 'rgba(0, 255, 136, 0.2)';
            }
          }}
        >
          <Icons.play />
          <span>run()</span>
          <span 
            className="ml-auto px-1.5 py-0.5 rounded"
            style={{ 
              fontSize: '10px',
              backgroundColor: '#333',
              color: '#888',
            }}
          >
            ⌘R
          </span>
        </button>
      </div>

      {/* Payload Input */}
      <div className="px-3 pt-4">
        <div 
          className="mb-2"
          style={{ 
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '11px',
            color: '#858585',
          }}
        >
          {'// payload'}
        </div>
        <textarea
          value={payload}
          onChange={(e) => onPayloadChange(e.target.value)}
          className="w-full h-20 px-3 py-2 rounded-lg resize-none focus:outline-none"
          style={{
            backgroundColor: '#1e1e1e',
            border: '1px solid #3c3c3c',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '12px',
            color: '#ccc',
          }}
          placeholder="input data..."
          onFocus={(e) => {
            e.currentTarget.style.borderColor = '#00ff88';
            e.currentTarget.style.boxShadow = '0 0 0 1px rgba(0, 255, 136, 0.1)';
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = '#1a1a1a';
            e.currentTarget.style.boxShadow = 'none';
          }}
        />
      </div>

      {/* Bytecode Status */}
      {pvmHex && (
        <div 
          className="mx-3 mt-3 p-3 rounded-lg flex items-center justify-between"
          style={{
            backgroundColor: '#1e1e1e',
            border: '1px solid #3c3c3c',
          }}
        >
          <div>
            <div 
              style={{ 
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '11px',
                color: '#858585',
              }}
            >
              bytecode
            </div>
            <div 
              style={{ 
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '12px',
                color: '#00ff88',
              }}
            >
              {(pvmHex.length / 2).toLocaleString()} bytes
            </div>
          </div>
          <button
            onClick={() => {
              const bytes = new Uint8Array(pvmHex.length / 2);
              for (let i = 0; i < pvmHex.length; i += 2) {
                bytes[i / 2] = parseInt(pvmHex.substr(i, 2), 16);
              }
              const blob = new Blob([bytes], { type: 'application/octet-stream' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = 'service.jam';
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              URL.revokeObjectURL(url);
            }}
            className="flex items-center justify-center w-8 h-8 rounded-lg transition-colors"
            style={{ backgroundColor: '#333' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#444';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#333';
            }}
          >
            <Icons.download />
          </button>
        </div>
      )}

      {/* Shortcuts */}
      <div 
        className="mt-auto px-3 py-3"
        style={{ borderTop: '1px solid #333' }}
      >
        <div 
          className="space-y-1"
          style={{ 
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '10px',
            color: '#666',
          }}
        >
          <div className="flex items-center justify-between">
            <span>⌘N</span><span>new</span>
          </div>
          <div className="flex items-center justify-between">
            <span>⌘B</span><span>build</span>
          </div>
          <div className="flex items-center justify-between">
            <span>⌘R</span><span>run</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
