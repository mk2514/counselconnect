import { ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from './button';

export function ConfirmationDialog({
  isOpen,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isDestructive = false,
  onConfirm,
  onCancel,
}: {
  isOpen: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg shadow-black/10 mx-4">
        <div className="mb-4 flex items-start gap-4">
          <div className={cn(
            "flex h-10 w-10 shrink-0 items-center justify-center rounded-full",
            isDestructive ? "bg-red-100" : "bg-terracotta-bg"
          )}>
            <AlertTriangle className={cn(
              "h-5 w-5",
              isDestructive ? "text-red-600" : "text-terracotta"
            )} />
          </div>
          <div>
            <h2 className="text-[18px] font-semibold text-primary-text tracking-tight">
              {title}
            </h2>
            <p className="mt-1 text-[14px] text-secondary-text">
              {description}
            </p>
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="outline" onClick={onCancel}>
            {cancelLabel}
          </Button>
          <Button
            variant="primary"
            className={cn(isDestructive && "bg-red-600 hover:bg-red-700")}
            onClick={onConfirm}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}

export function ReviewPanel({
  title,
  children,
  className,
}: {
  title: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("rounded-lg border border-border bg-sidebar p-5", className)}>
      <h3 className="mb-4 text-[16px] font-semibold text-primary-text tracking-tight border-b border-border pb-2">
        {title}
      </h3>
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
}

export function ReviewField({
  label,
  value,
}: {
  label: string;
  value: ReactNode;
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-baseline gap-1 sm:gap-4">
      <span className="text-[13px] font-medium text-secondary-text sm:w-1/3">
        {label}
      </span>
      <span className="text-[14px] text-primary-text sm:w-2/3">
        {value || <span className="text-gray-400 italic">Not provided</span>}
      </span>
    </div>
  );
}
