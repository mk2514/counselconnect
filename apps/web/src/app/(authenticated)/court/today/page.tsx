'use client';

import { useEffect, useState } from 'react';
import { PageHeader, SectionHeader } from '@/components/ui/typography';
import { DataTable, Column } from '@/components/ui/data-table';
import { StatusBadge } from '@/components/ui/badge';
import { LoadingState, ErrorState } from '@/components/ui/feedback';
import { apiClient } from '@/lib/api-client';

export default function CourtTodayCasesPage() {
  const [hearings, setHearings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadHearings() {
      try {
        const data = await apiClient.get<any[]>('/api/court/hearings/today');
        setHearings(data);
      } catch (err: any) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    loadHearings();
  }, []);

  const columns: Column<any>[] = [
    {
      key: 'case_id',
      header: 'Case ID',
      render: (row) => <span className="font-mono text-sm font-semibold">{row.case_id.substring(0, 8)}...</span>,
    },
    {
      key: 'judge_name',
      header: 'Judge',
      render: (row) => <span className="text-sm">{row.judge_name}</span>,
    },
    {
      key: 'hearing_time',
      header: 'Time',
      render: (row) => <span className="text-sm font-medium">{row.hearing_time || 'TBD'}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => <StatusBadge variant={row.status === 'SCHEDULED' ? 'default' : 'outline'}>{row.status}</StatusBadge>,
    }
  ];

  if (error) return <ErrorState description={error.message} />;

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Today's Cases" 
        description="Real-time view of all scheduled hearings for the current date."
      />

      <div className="bg-white p-6 rounded-md border border-[var(--color-border)]">
        <SectionHeader title="Scheduled Hearings" />
        <DataTable
          columns={columns}
          data={hearings}
          getRowKey={(row) => row.id}
          isLoading={loading}
          emptyMessage="No hearings scheduled for today."
        />
      </div>
    </div>
  );
}
