import { cn } from '@/lib/utils';

interface TabsProps {
  tabs: Array<{ id: string; label: string; icon?: React.ReactNode }>;
  activeTab: string;
  onTabChange: (id: string) => void;
  onTabClose?: (id: string) => void;
}

export function Tabs({ tabs, activeTab, onTabChange, onTabClose }: TabsProps) {
  return (
    <div className="flex items-center bg-[var(--surface-1)] border-b border-[var(--border-subtle)] overflow-x-auto">
      {tabs.map((tab) => (
        <div
          key={tab.id}
          className={cn(
            'group flex items-center gap-2 px-3 py-2 text-[12px] font-medium cursor-pointer transition-all',
            'border-r border-[var(--border-subtle)]',
            activeTab === tab.id
              ? 'bg-[var(--bg-primary)] text-[var(--text-primary)]'
              : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'
          )}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.icon}
          <span className="whitespace-nowrap">{tab.label}</span>
          {onTabClose && tabs.length > 1 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onTabClose(tab.id);
              }}
              className="ml-1 p-0.5 rounded opacity-0 group-hover:opacity-100 hover:bg-[var(--bg-tertiary)] hover:text-[var(--accent-red)] transition-all"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
