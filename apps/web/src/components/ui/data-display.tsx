import { ChevronRight, FileText, CheckCircle2, Circle } from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import { StatusBadge } from './badge';

export function CaseIdentifier({
  csrNumber,
  title,
  status,
  className,
}: {
  csrNumber: string;
  title?: string;
  status?: string;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col gap-1", className)}>
      <div className="flex items-center gap-2">
        <span className="text-[16px] font-bold text-primary-text font-mono tracking-tight">
          {csrNumber}
        </span>
        {status && <StatusBadge variant={status === 'ACTIVE' ? 'success' : 'default'}>{status}</StatusBadge>}
      </div>
      {title && (
        <span className="text-[14px] text-secondary-text">{title}</span>
      )}
    </div>
  );
}

export function Breadcrumb({
  items,
  className,
}: {
  items: { label: string; href?: string }[];
  className?: string;
}) {
  return (
    <nav className={cn("flex items-center space-x-1 text-[13px] text-secondary-text", className)}>
      {items.map((item, index) => (
        <div key={index} className="flex items-center">
          {index > 0 && <ChevronRight className="mx-1 h-3.5 w-3.5" />}
          {item.href ? (
            <Link href={item.href} className="hover:text-primary-text hover:underline">
              {item.label}
            </Link>
          ) : (
            <span className="font-medium text-primary-text">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
}

export function DocumentRow({
  title,
  type,
  date,
  size,
  onView,
  onDownload,
  className,
}: {
  title: string;
  type: string;
  date: string;
  size?: string;
  onView?: () => void;
  onDownload?: () => void;
  className?: string;
}) {
  return (
    <div className={cn("flex items-center justify-between rounded-md border border-border bg-white p-3 transition-colors hover:bg-sidebar", className)}>
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded bg-terracotta-bg/50">
          <FileText className="h-5 w-5 text-terracotta-dark" />
        </div>
        <div>
          <p className="text-[14px] font-medium text-primary-text">{title}</p>
          <div className="flex items-center gap-2 text-[12px] text-secondary-text">
            <span>{type}</span>
            <span>•</span>
            <span>{date}</span>
            {size && (
              <>
                <span>•</span>
                <span>{size}</span>
              </>
            )}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {onView && (
          <button onClick={onView} className="text-[13px] font-medium text-terracotta hover:underline focus-ring rounded">
            View
          </button>
        )}
        {onDownload && (
          <button onClick={onDownload} className="text-[13px] font-medium text-secondary-text hover:text-primary-text hover:underline focus-ring rounded">
            Download
          </button>
        )}
      </div>
    </div>
  );
}

export function CaseStageProgress({
  stages,
  currentStageIdx,
  className,
}: {
  stages: string[];
  currentStageIdx: number;
  className?: string;
}) {
  return (
    <div className={cn("flex w-full items-center justify-between", className)}>
      {stages.map((stage, idx) => {
        const isCompleted = idx < currentStageIdx;
        const isCurrent = idx === currentStageIdx;
        
        return (
          <div key={stage} className="flex flex-1 flex-col items-center relative">
            {/* Connecting line */}
            {idx < stages.length - 1 && (
              <div 
                className={cn(
                  "absolute left-[50%] top-[10px] h-[2px] w-full",
                  isCompleted ? "bg-terracotta" : "bg-border"
                )}
              />
            )}
            
            <div className="relative z-10 flex flex-col items-center gap-2 bg-background px-2">
              {isCompleted ? (
                <CheckCircle2 className="h-5 w-5 text-terracotta" />
              ) : isCurrent ? (
                <div className="flex h-5 w-5 items-center justify-center rounded-full border-2 border-terracotta bg-white">
                  <div className="h-2 w-2 rounded-full bg-terracotta" />
                </div>
              ) : (
                <Circle className="h-5 w-5 text-border" />
              )}
              <span className={cn(
                "text-[12px] font-medium",
                isCurrent || isCompleted ? "text-primary-text" : "text-secondary-text"
              )}>
                {stage}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function AuditTimeline({
  events,
  className,
}: {
  events: { id: string; action: string; actor: string; timestamp: string; details?: string }[];
  className?: string;
}) {
  return (
    <div className={cn("relative pl-4 border-l-2 border-border space-y-6", className)}>
      {events.map((event) => (
        <div key={event.id} className="relative">
          <div className="absolute -left-[21px] top-1 h-3 w-3 rounded-full border-2 border-white bg-secondary-text" />
          <div className="flex flex-col gap-0.5">
            <span className="text-[14px] font-medium text-primary-text">{event.action}</span>
            <div className="text-[12px] text-secondary-text">
              <span>By {event.actor}</span>
              <span className="mx-1">•</span>
              <span>{event.timestamp}</span>
            </div>
            {event.details && (
              <p className="mt-1 text-[13px] text-secondary-text bg-sidebar p-2 rounded border border-border">
                {event.details}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
