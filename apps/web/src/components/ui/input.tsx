'use client';

import { forwardRef, useId, type InputHTMLAttributes } from 'react';

/**
 * Input component with label and error display.
 *
 * Per project rules (accessibility + form validation):
 * - Every field must have a label
 * - Labels must be visible and persistent
 * - Error messages must be specific (e.g., "FIR number is required.")
 * - Focus state must be visible
 */

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, required, className = '', ...props }, ref) => {
    const generatedId = useId();
    const inputId = `input-${generatedId}`;
    const errorId = error ? `error-${generatedId}` : undefined;
    const hintId = hint ? `hint-${generatedId}` : undefined;

    const describedBy = [errorId, hintId].filter(Boolean).join(' ') || undefined;

    return (
      <div className="space-y-1.5">
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-primary-text"
        >
          {label}
          {required && (
            <span className="ml-0.5 text-status-error" aria-hidden="true">
              *
            </span>
          )}
        </label>

        <input
          ref={ref}
          id={inputId}
          required={required}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={describedBy}
          className={[
            'block w-full rounded-[8px] border bg-surface px-3 py-2 text-sm text-primary-text',
            'placeholder:text-secondary-text/60',
            'outline-none transition-colors',
            'focus:border-terracotta focus:ring-2 focus:ring-terracotta/20',
            error
              ? 'border-status-error focus:border-status-error focus:ring-status-error/20'
              : 'border-border',
            'disabled:cursor-not-allowed disabled:bg-background disabled:opacity-60',
            className,
          ].join(' ')}
          {...props}
        />

        {hint && !error && (
          <p id={hintId} className="text-xs text-secondary-text">
            {hint}
          </p>
        )}

        {error && (
          <p id={errorId} className="text-xs text-status-error" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  },
);

Input.displayName = 'Input';
