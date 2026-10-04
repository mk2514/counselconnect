import { HTMLAttributes, InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';
import { UploadCloud } from 'lucide-react';

export function FormField({
  id,
  label,
  error,
  required,
  children,
  className,
}: {
  id?: string;
  label: string;
  error?: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("space-y-1.5", className)}>
      <label className="text-[14px] font-medium text-primary-text">
        {label}
        {required && <span className="ml-1 text-red-500" aria-label="required">*</span>}
      </label>
      {children}
      {error && <p className="text-[12px] text-red-600">{error}</p>}
    </div>
  );
}

const inputStyles = "w-full rounded-md border border-border bg-white px-3 py-2 text-[14px] text-primary-text transition-colors placeholder:text-secondary-text focus:border-terracotta focus:outline-none focus:ring-1 focus:ring-terracotta disabled:cursor-not-allowed disabled:opacity-50";
const errorStyles = "border-red-400 focus:border-red-500 focus:ring-red-500";

export const TextInput = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement> & { error?: boolean }>(
  ({ className, error, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(inputStyles, error && errorStyles, className)}
        {...props}
      />
    );
  }
);
TextInput.displayName = "TextInput";

export const TextArea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement> & { error?: boolean }>(
  ({ className, error, ...props }, ref) => {
    return (
      <textarea
        ref={ref}
        className={cn(inputStyles, "min-h-[80px]", error && errorStyles, className)}
        {...props}
      />
    );
  }
);
TextArea.displayName = "TextArea";

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement> & { error?: boolean }>(
  ({ className, error, children, ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={cn(inputStyles, error && errorStyles, className)}
        {...props}
      >
        {children}
      </select>
    );
  }
);
Select.displayName = "Select";

export const DateInput = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement> & { error?: boolean }>(
  ({ className, error, ...props }, ref) => {
    return (
      <input
        type="date"
        ref={ref}
        className={cn(inputStyles, error && errorStyles, className)}
        {...props}
      />
    );
  }
);
DateInput.displayName = "DateInput";

export const TimeInput = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement> & { error?: boolean }>(
  ({ className, error, ...props }, ref) => {
    return (
      <input
        type="time"
        ref={ref}
        className={cn(inputStyles, error && errorStyles, className)}
        {...props}
      />
    );
  }
);
TimeInput.displayName = "TimeInput";

export function FileUpload({
  onFileSelect,
  accept,
  error,
  className,
}: {
  onFileSelect: (file: File) => void;
  accept?: string;
  error?: boolean;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed border-border bg-sidebar px-6 py-8 transition-colors hover:border-terracotta hover:bg-terracotta-bg/20",
        error && "border-red-400 bg-red-50",
        className
      )}
      onClick={() => {
        const input = document.createElement('input');
        input.type = 'file';
        if (accept) input.accept = accept;
        input.onchange = (e) => {
          const file = (e.target as HTMLInputElement).files?.[0];
          if (file) onFileSelect(file);
        };
        input.click();
      }}
    >
      <UploadCloud className="mb-2 h-8 w-8 text-secondary-text" />
      <p className="text-[14px] font-medium text-primary-text">
        Click to upload a file
      </p>
      <p className="mt-1 text-[12px] text-secondary-text">
        {accept ? `Supported formats: ${accept}` : 'All files supported'}
      </p>
    </div>
  );
}
