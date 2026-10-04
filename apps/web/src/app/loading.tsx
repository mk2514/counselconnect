import { Loader2 } from 'lucide-react';

export default function Loading() {
  return (
    <div
      className="flex min-h-screen items-center justify-center bg-background"
      role="status"
      aria-label="Loading"
    >
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="h-8 w-8 animate-spin text-terracotta" aria-hidden="true" />
        <p className="text-sm text-secondary-text">Loading...</p>
      </div>
    </div>
  );
}
