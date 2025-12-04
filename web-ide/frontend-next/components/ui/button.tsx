import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'primary' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'md', ...props }, ref) => {
    return (
      <button
        className={cn(
          'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200',
          'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--accent-blue)]',
          'disabled:opacity-40 disabled:cursor-not-allowed',
          {
            'bg-[var(--surface-2)] text-[var(--text-secondary)] border border-[var(--border-default)] hover:bg-[var(--bg-hover)] hover:border-[var(--border-strong)]': variant === 'default',
            'bg-[var(--accent-blue)] text-white hover:bg-blue-500 shadow-sm': variant === 'primary',
            'bg-transparent hover:bg-[var(--bg-hover)] text-[var(--text-tertiary)] hover:text-[var(--text-primary)]': variant === 'ghost',
            'bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20': variant === 'destructive',
          },
          {
            'px-2 py-1 text-[11px]': size === 'sm',
            'px-3 py-1.5 text-[13px]': size === 'md',
            'px-4 py-2 text-sm': size === 'lg',
          },
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);

Button.displayName = 'Button';

export { Button };
