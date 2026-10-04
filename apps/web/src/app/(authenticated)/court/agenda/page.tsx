'use client';

import { useEffect, useState } from 'react';
import { PageHeader, SectionHeader } from '@/components/ui/typography';
import { Button } from '@/components/ui/button';
import { LoadingState, ErrorState } from '@/components/ui/feedback';
import { apiClient } from '@/lib/api-client';

export default function CourtAgendaPage() {
  const [agenda, setAgenda] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadAgenda() {
      try {
        const data = await apiClient.get<any>('/api/court/agenda/today');
        setAgenda(data);
      } catch (err: any) {
        if (err.status === 404) {
          setAgenda(null);
        } else {
          setError(err);
        }
      } finally {
        setLoading(false);
      }
    }
    loadAgenda();
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState description={error.message} />;

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Court Agenda" 
        description="Review AI proposed agenda. Reorder or alter slots. Confirm final schedule."
      />

      {!agenda ? (
        <div className="bg-white p-8 rounded-md border border-dashed border-gray-300 text-center text-gray-500">
          No agenda has been drafted for today. Wait for the scheduling AI to run its batch process.
        </div>
      ) : (
        <div className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-6">
          <SectionHeader title={`Agenda for ${agenda.agenda_date}`} />
          <p className="text-sm text-gray-500 mb-4">
            Drag items to change the <strong>Final Order</strong>. Original AI proposals remain preserved.
          </p>

          <div className="space-y-3">
            {agenda.items.map((item: any, idx: number) => (
              <div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-md">
                <div>
                  <span className="font-bold text-[var(--color-terracotta)] mr-4">Slot {item.final_order || idx + 1}</span>
                  <span className="text-sm font-mono text-gray-600 mr-4">Case: {item.hearing_id.substring(0, 8)}</span>
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">AI Proposed Slot: {item.ai_proposed_order}</span>
                </div>
                <div className="text-sm text-gray-500">
                  Drag Handle
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end space-x-4 pt-4">
            <Button variant="outline">Reset to AI Proposal</Button>
            <Button>Confirm Final Agenda</Button>
          </div>
        </div>
      )}
    </div>
  );
}
