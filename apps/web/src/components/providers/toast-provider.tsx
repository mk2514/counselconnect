'use client';

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { X, CheckCircle2, AlertTriangle, AlertCircle, Info } from 'lucide-react';

/**
 * Toast notification system.
 *
 * Per project rules:
 * - Status colors: green (success), amber (pending/warning), red (error), blue (info)
 * - Status indicators require text labels (not just color)
 */

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  variant: ToastVariant;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return ctx;
}

const variantConfig: Record<
  ToastVariant,
  { icon: typeof CheckCircle2; bg: string; border: string; text: string; label: string }
> = {
  success: {
    icon: CheckCircle2,
    bg: 'bg-status-success-bg',
    border: 'border-status-success/20',
    text: 'text-status-success',
    label: 'Success',
  },
  error: {
    icon: AlertCircle,
    bg: 'bg-status-error-bg',
    border: 'border-status-error/20',
    text: 'text-status-error',
    label: 'Error',
  },
  warning: {
    icon: AlertTriangle,
    bg: 'bg-status-pending-bg',
    border: 'border-status-pending/20',
    text: 'text-status-pending',
    label: 'Warning',
  },
  info: {
    icon: Info,
    bg: 'bg-status-info-bg',
    border: 'border-status-info/20',
    text: 'text-status-info',
    label: 'Information',
  },
};

let toastCounter = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(
    (toast: Omit<Toast, 'id'>) => {
      const id = `toast-${++toastCounter}`;
      const duration = toast.duration ?? 5000;

      setToasts((prev) => [...prev, { ...toast, id }]);

      if (duration > 0) {
        setTimeout(() => removeToast(id), duration);
      }
    },
    [removeToast],
  );

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}

      {/* Toast container */}
      <div
        className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2"
        aria-live="polite"
        aria-label="Notifications"
      >
        {toasts.map((toast) => {
          const config = variantConfig[toast.variant];
          const Icon = config.icon;

          return (
            <div
              key={toast.id}
              role="status"
              className={[
                'flex w-80 items-start gap-3 rounded-lg border p-4 shadow-dropdown',
                'animate-in slide-in-from-right',
                config.bg,
                config.border,
              ].join(' ')}
            >
              <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${config.text}`} aria-hidden="true" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-primary-text">
                  <span className="sr-only">{config.label}: </span>
                  {toast.title}
                </p>
                {toast.message && (
                  <p className="mt-1 text-xs text-secondary-text">{toast.message}</p>
                )}
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="shrink-0 rounded-[6px] p-0.5 text-secondary-text hover:text-primary-text outline-none focus-visible:ring-2 focus-visible:ring-terracotta/40"
                aria-label={`Dismiss ${config.label.toLowerCase()} notification`}
              >
                <X className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}
