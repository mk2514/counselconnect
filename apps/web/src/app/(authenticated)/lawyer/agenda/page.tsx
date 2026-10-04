'use client';

import { PageHeader } from '@/components/ui/typography';
import { Gavel } from 'lucide-react';

export default function LawyerAgendaPage() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader 
        title="Court Agenda (Read-Only)" 
        description="View the final authorized court agenda for the day."
      />

      <div className="bg-white rounded-md border border-[var(--color-border)] p-8 text-center space-y-4">
        <Gavel className="h-12 w-12 mx-auto text-gray-400" />
        <h3 className="text-lg font-medium">No Court Agendas Published Today</h3>
        <p className="text-gray-500 text-sm max-w-md mx-auto">
          The court authority has not yet published the final agenda. Please check back later. 
          Note: This view is read-only. Only Court Authorities may modify the final agenda order.
        </p>
      </div>
    </div>
  );
}
