'use client';

export function Header() {
  return (
    <header 
      className="h-10 flex items-center px-4 justify-between select-none shrink-0"
      style={{
        backgroundColor: '#1e1e1e',
        borderBottom: '1px solid #333',
      }}
    >
      {/* Logo & Title */}
      <div className="flex items-center gap-3">
        <span 
          style={{ 
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '14px',
            fontWeight: 600,
          }}
        >
          <span style={{ color: '#ffffff' }}>jam</span>
          <span style={{ color: '#00ff88' }}>code</span>
          <span style={{ color: '#404040' }}>.fun</span>
        </span>
      </div>
      
      {/* Version */}
      <span 
        style={{ 
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '11px',
          color: '#666',
        }}
      >
        v0.1.0
      </span>
    </header>
  );
}
