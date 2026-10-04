'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { PageHeader } from '@/components/ui/typography';
import { Button } from '@/components/ui/button';
import { DataTable, Column } from '@/components/ui/data-table';
import { StatusBadge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';

interface HearingRecord {
  id: string;
  case_id: string;
  court_id: string;
  judge_name: string;
  hearing_date: string;
  hearing_time: string | null;
  status: string;
}

export default function CourtHearingsPage() {
  const [hearings, setHearings] = useState<HearingRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadHearings() {
      try {
        const data = await apiClient.get<HearingRecord[]>('/api/court/hearings');
        setHearings(data);
      } catch (err: any) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    loadHearings();
  }, []);

  const columns: Column<HearingRecord>[] = [
    {
      key: 'date',
      header: 'Date & Time',
      render: (row) => (
        <div className="flex flex-col">
          <span className="font-medium text-[var(--color-primary-text)]">{row.hearing_date}</span>
          <span className="text-xs text-[var(--color-secondary-text)]">{row.hearing_time || 'TBD'}</span>
        </div>
      ),
    },
    {
      key: 'judge',
      header: 'Presiding Officer',
      render: (row) => <span className="text-sm font-medium">{row.judge_name}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <StatusBadge variant={row.status === 'SCHEDULED' ? 'default' : row.status === 'CONCLUDED' ? 'outline' : 'destructive'}>
          {row.status}
        </StatusBadge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      className: 'text-right',
      render: (row) => (
        <Link 
          href={`/court/hearings/${row.id}`} 
          className="text-sm font-medium text-[var(--color-terracotta)] hover:underline"
        >
          {row.status === 'SCHEDULED' ? 'Log Proceedings' : 'View Details'}
        </Link>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Court Agenda & Hearings" 
        description="Manage the court's schedule, hearings, and official proceedings."
      >
        <Link href="/court/registry">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Schedule Hearing (via Registry)
          </Button>
        </Link>
      </PageHeader>

      <DataTable
        columns={columns}
        data={hearings}
        getRowKey={(row) => row.id}
        isLoading={loading}
        error={error}
        emptyMessage="No hearings are currently scheduled."
      />
    </div>
  );
}
