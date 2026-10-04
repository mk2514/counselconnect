'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { PageHeader } from '@/components/ui/typography';
import { DataTable, Column } from '@/components/ui/data-table';
import { StatusBadge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';

export default function LawyerCasesPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadCases() {
      try {
        const data = await apiClient.get<any[]>('/api/lawyer/cases');
        setCases(data);
      } catch (err: any) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    loadCases();
  }, []);

  const columns: Column<any>[] = [
    {
      key: 'csr_number',
      header: 'CSR Number',
      render: (row) => <span className="font-mono text-sm font-semibold">{row.csr_number}</span>,
    },
    {
      key: 'case_type',
      header: 'Case Type',
      render: (row) => <span className="text-sm">{row.case_type}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => <StatusBadge variant="default">{row.case_status}</StatusBadge>,
    },
    {
      key: 'actions',
      header: 'Actions',
      className: 'text-right',
      render: (row) => (
        <Link 
          href={`/lawyer/cases/${row.id}`} 
          className="text-sm font-medium text-[var(--color-terracotta)] hover:underline"
        >
          Open Workspace
        </Link>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="My Cases" 
        description="View and manage cases where you hold an active representation assignment."
      />

      <DataTable
        columns={columns}
        data={cases}
        getRowKey={(row) => row.id}
        isLoading={loading}
        error={error}
        emptyMessage="No active case assignments found."
      />
    </div>
  );
}
