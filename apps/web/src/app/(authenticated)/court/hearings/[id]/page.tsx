'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { PageHeader, SectionHeader } from '@/components/ui/typography';
import { Button } from '@/components/ui/button';
import { FormField, TextArea, TextInput } from '@/components/ui/forms';
import { LoadingState, ErrorState } from '@/components/ui/feedback';
import { apiClient } from '@/lib/api-client';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/components/providers/toast-provider';

export default function CourtHearingDetailsPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { addToast } = useToast();
  
  // Proceeding state
  const [transcript, setTranscript] = useState('');
  const [orderSummary, setOrderSummary] = useState('');
  const [nextDate, setNextDate] = useState('');

  const handleLogProceeding = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    try {
      await apiClient.post(`/api/court/hearings/${params.id}/proceedings`, {
        hearing_id: params.id,
        transcript: transcript,
        order_summary: orderSummary || undefined,
        next_hearing_date: nextDate || undefined,
      });
      addToast('Proceeding logged successfully!', 'success');
      router.push('/court/hearings');
    } catch (err: any) {
      setError(err.message || 'Failed to log proceeding.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Log Court Proceeding" 
        description="Enter the official transcript and court orders for this hearing."
      />

      <div className="rounded-md border border-[var(--color-border)] bg-white p-6 max-w-3xl">
        <SectionHeader title="Proceeding Details" />
        
        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-800 border border-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleLogProceeding} className="space-y-4">
          <FormField label="Official Transcript" required>
            <TextArea 
              id="transcript"
              rows={8}
              placeholder="Enter the full official transcript of the proceeding..."
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              required
            />
          </FormField>
          
          <FormField id="order_summary" label="Order Summary / Disposition">
            <TextArea 
              id="order_summary"
              rows={4}
              placeholder="Enter the judge's official order or disposition..."
              value={orderSummary}
              onChange={(e) => setOrderSummary(e.target.value)}
            />
          </FormField>
          
          <FormField id="next_date" label="Next Scheduled Hearing Date (Optional)">
            <TextInput 
              id="next_date"
              type="date"
              value={nextDate}
              onChange={(e) => setNextDate(e.target.value)}
            />
          </FormField>

          <div className="pt-4 flex justify-end space-x-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => router.push('/court/hearings')}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting || !transcript}>
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Submit Proceeding
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
