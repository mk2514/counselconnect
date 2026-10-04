'use client';

import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { Loader2 } from 'lucide-react';

/**
 * Button component with variants and states.
 *
 * Per project rules:
 * - Primary buttons are rectangular with modest rounding (8px)
 * - Every action needs loading, success, error, and disabled states
 * - No pill-shaped buttons
 */

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  loadingText?: string;
}

const variantClasses: Record<NonNullable<ButtonProps['variant']>, string> = {
  primary:
    'bg-terracotta text-white hover:bg-terracotta-dark focus-visible:ring-terracotta/40 disabled:bg-terracotta/50',
  secondary:
    'bg-terracotta-bg text-terracotta hover:bg-terracotta-soft/40 focus-visible:ring-terracotta/30',
  outline:
    'border border-border bg-surface text-primary-text hover:bg-background focus-visible:ring-terracotta/30',
  ghost:
    'text-secondary-text hover:bg-background hover:text-primary-text focus-visible:ring-terracotta/30',
  danger:
    'bg-status-error text-white hover:bg-red-700 focus-visible:ring-status-error/40 disabled:bg-status-error/50',
};

const sizeClasses: Record<NonNullable<ButtonProps['size']>, string> = {
  sm: 'h-8 px-3 text-sm gap-1.5',
  md: 'h-9 px-4 text-sm gap-2',
  lg: 'h-10 px-5 text-sm gap-2',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      loadingText,
      disabled,
      children,
      className = '',
      ...props
    },
    ref,
  ) => {
    const isDisabled = disabled || isLoading;

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={[
          'inline-flex items-center justify-center rounded-[8px] font-medium transition-colors',
          'outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-surface',
          'disabled:cursor-not-allowed disabled:opacity-60',
          variantClasses[variant],
          sizeClasses[size],
          className,
        ].join(' ')}
        {...props}
      >
        {isLoading && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
        {isLoading && loadingText ? loadingText : children}
      </button>
    );
  },
);

Button.displayName = 'Button';
