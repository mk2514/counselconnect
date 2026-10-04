import { AlertCircle, FileSearch, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from './button';

export function EmptyState({
  title = 'No records found',
  description = 'There are currently no records available in this section.',
  actionLabel,
  onAction,
  icon: Icon = FileSearch,
  className,
}: {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ElementType;
  className?: string;
}) {
  return (
    <div className={cn("flex min-h-[300px] flex-col items-center justify-center rounded-lg border border-dashed border-border bg-white p-8 text-center", className)}>
      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-sidebar">
        <Icon className="h-6 w-6 text-secondary-text" aria-hidden="true" />
      </div>
      <h3 className="mb-1 text-[16px] font-medium text-primary-text">{title}</h3>
      <p className="mb-6 max-w-sm text-[14px] text-secondary-text">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button onClick={onAction} variant="outline">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

export function ErrorState({
  title = 'Something went wrong',
  description = 'An error occurred while loading this data. Please try again.',
  actionLabel = 'Try again',
  onAction,
  className,
}: {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}) {
  return (
    <div className={cn("flex min-h-[300px] flex-col items-center justify-center rounded-lg border border-dashed border-red-200 bg-red-50 p-8 text-center", className)}>
      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
        <AlertCircle className="h-6 w-6 text-red-600" aria-hidden="true" />
      </div>
      <h3 className="mb-1 text-[16px] font-medium text-red-900">{title}</h3>
      <p className="mb-6 max-w-sm text-[14px] text-red-700">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button onClick={onAction} variant="outline" className="border-red-200 text-red-700 hover:bg-red-100 hover:text-red-900">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

export function LoadingState({
  message = 'Loading data...',
  className,
}: {
  message?: string;
  className?: string;
}) {
  return (
    <div className={cn("flex min-h-[300px] flex-col items-center justify-center rounded-lg border border-dashed border-border bg-white p-8 text-center", className)}>
      <Loader2 className="mb-4 h-8 w-8 animate-spin text-terracotta" aria-hidden="true" />
      <p className="text-[14px] font-medium text-secondary-text">{message}</p>
    </div>
  );
}

export function PermissionDenied({
  title = 'Access Denied',
  description = 'You do not have the required permissions to view this content.',
  className,
}: {
  title?: string;
  description?: string;
  className?: string;
}) {
  return (
    <div className={cn("flex min-h-[300px] flex-col items-center justify-center rounded-lg border border-border bg-white p-8 text-center shadow-sm", className)}>
      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-terracotta-bg">
        <AlertCircle className="h-6 w-6 text-terracotta" aria-hidden="true" />
      </div>
      <h3 className="mb-1 text-[18px] font-semibold text-primary-text">{title}</h3>
      <p className="max-w-sm text-[14px] text-secondary-text">
        {description}
      </p>
    </div>
  );
}
