import { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export function PageHeader({
  title,
  description,
  children,
  className,
}: {
  title: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col gap-1 pb-6 sm:flex-row sm:items-center sm:justify-between", className)}>
      <div>
        <h1 className="text-[28px] font-semibold text-primary-text tracking-tight">
          {title}
        </h1>
        {description && (
          <p className="mt-1 text-sm text-secondary-text">
            {description}
          </p>
        )}
      </div>
      {children && <div className="mt-4 flex items-center gap-3 sm:mt-0">{children}</div>}
    </div>
  );
}

export function SectionHeader({
  title,
  description,
  children,
  className,
}: {
  title: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col gap-1 pb-4 sm:flex-row sm:items-center sm:justify-between", className)}>
      <div>
        <h2 className="text-[18px] font-semibold text-primary-text tracking-tight">
          {title}
        </h2>
        {description && (
          <p className="text-[14px] text-secondary-text mt-1">
            {description}
          </p>
        )}
      </div>
      {children && <div className="mt-3 flex items-center gap-2 sm:mt-0">{children}</div>}
    </div>
  );
}

export function TextBody({ children, className, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("text-[14px] leading-relaxed text-primary-text", className)} {...props}>
      {children}
    </p>
  );
}

export function TextMeta({ children, className, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("text-[12px] text-secondary-text", className)} {...props}>
      {children}
    </p>
  );
}
