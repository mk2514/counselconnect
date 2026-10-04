'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { PageHeader } from '@/components/ui/typography';
import { Button } from '@/components/ui/button';
import { DataTable, Column } from '@/components/ui/data-table';
import { StatusBadge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';

export default function PoliceCasesPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadCases() {
      try {
        const data = await apiClient.get<any[]>('/api/police/cases');
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
      render: (row) => <StatusBadge variant={row.case_status === 'REGISTERED' ? 'default' : 'outline'}>{row.case_status}</StatusBadge>,
    },
    {
      key: 'actions',
      header: 'Actions',
      className: 'text-right',
      render: (row) => (
        <Link 
          href={`/police/firs/${row.id}`} 
          className="text-sm font-medium text-[var(--color-terracotta)] hover:underline"
        >
          View Dashboard
        </Link>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="My Cases" 
        description="View and manage cases registered at your jurisdiction."
      >
        <Link href="/police/firs/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Register New Case
          </Button>
        </Link>
      </PageHeader>

      <DataTable
        columns={columns}
        data={cases}
        getRowKey={(row) => row.id}
        isLoading={loading}
        error={error}
        emptyMessage="No cases found in your jurisdiction."
      />
    </div>
  );
}
