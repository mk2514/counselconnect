'use client';

import { type ReactNode } from 'react';

/**
 * Data table foundation.
 *
 * Per project rules (accessibility):
 * - Tables require usable headings (th with scope)
 * - Data tables must not be used for layout
 */

import { EmptyState, LoadingState, ErrorState } from './feedback';

export interface Column<T> {
  /** Unique key for the column */
  key: string;
  /** Column header text */
  header: string;
  /** Render function for the cell content */
  render: (row: T, index: number) => ReactNode;
  /** Optional CSS class for the column */
  className?: string;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  /** Unique key extractor for each row */
  getRowKey: (row: T, index: number) => string;
  /** Optional caption for accessibility */
  caption?: string;
  /** Whether data is loading */
  isLoading?: boolean;
  /** Message when data is empty */
  emptyMessage?: string;
  /** Error state */
  error?: Error | string | null;
  /** Optional retry action for errors */
  onRetry?: () => void;
}

export function DataTable<T>({
  columns,
  data,
  getRowKey,
  caption,
  isLoading = false,
  emptyMessage = 'No records found.',
  error = null,
  onRetry,
}: DataTableProps<T>) {
  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-white shadow-sm">
      <table className="w-full border-collapse text-[14px]">
        {caption && <caption className="sr-only">{caption}</caption>}

        <thead>
          <tr className="border-b border-border bg-background">
            {columns.map((col) => (
              <th
                key={col.key}
                scope="col"
                className={[
                  'px-4 py-3 text-left text-[12px] font-semibold uppercase tracking-wider text-secondary-text',
                  col.className ?? '',
                ].join(' ')}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>

        <tbody className="divide-y divide-[var(--color-border)]">
          {isLoading ? (
            <tr>
              <td colSpan={columns.length} className="p-0">
                <LoadingState className="border-0 rounded-none shadow-none" />
              </td>
            </tr>
          ) : error ? (
            <tr>
              <td colSpan={columns.length} className="p-0">
                <ErrorState 
                  description={typeof error === 'string' ? error : error.message}
                  onAction={onRetry} 
                  className="border-0 rounded-none shadow-none" 
                />
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="p-0">
                <EmptyState title={emptyMessage} className="border-0 rounded-none shadow-none" />
              </td>
            </tr>
          ) : (
            data.map((row, index) => (
              <tr
                key={getRowKey(row, index)}
                className="transition-colors hover:bg-sidebar group"
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={[
                      'px-4 py-3 text-[13px] text-primary-text',
                      col.className ?? '',
                    ].join(' ')}
                  >
                    {col.render(row, index)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
