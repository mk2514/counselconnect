'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { PageHeader } from '@/components/ui/typography';
import { DataTable, Column } from '@/components/ui/data-table';
import { CaseIdentifier } from '@/components/ui/data-display';
import { StatusBadge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';

interface CaseRecord {
  id: string;
  csr_number: string;
  fir_number: string | null;
  case_type: string;
  case_status: string;
  incident_date: string | null;
}

export default function CourtRegistryPage() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadCases() {
      try {
        const data = await apiClient.get<CaseRecord[]>('/api/court/cases');
        setCases(data);
      } catch (err: any) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    loadCases();
  }, []);

  const columns: Column<CaseRecord>[] = [
    {
      key: 'csr',
      header: 'CSR Number',
      render: (row) => (
        <CaseIdentifier 
          csrNumber={row.csr_number} 
          title={row.fir_number ? `FIR: ${row.fir_number}` : 'No FIR Number'} 
        />
      ),
    },
    {
      key: 'type',
      header: 'Case Type',
      render: (row) => <span className="text-sm font-medium">{row.case_type}</span>,
    },
    {
      key: 'date',
      header: 'Incident Date',
      render: (row) => <span className="text-sm">{row.incident_date || 'Unknown'}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <StatusBadge variant={row.case_status === 'REGISTERED' ? 'default' : 'outline'}>
          {row.case_status}
        </StatusBadge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      className: 'text-right',
      render: (row) => (
        <Link 
          href={`/court/registry/${row.id}`} 
          className="text-sm font-medium text-[var(--color-terracotta)] hover:underline"
        >
          Manage Case
        </Link>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Court Registry" 
        description="View registered cases, manage parties, and assign legal representation."
      />

      <DataTable
        columns={columns}
        data={cases}
        getRowKey={(row) => row.id}
        isLoading={loading}
        error={error}
        emptyMessage="No cases are currently registered in the system."
      />
    </div>
  );
}
