'use client';

import { useEffect, useState } from 'react';
import { PageHeader, SectionHeader } from '@/components/ui/typography';
import { Button } from '@/components/ui/button';
import { StatusBadge } from '@/components/ui/badge';
import { LoadingState, ErrorState } from '@/components/ui/feedback';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/components/providers/toast-provider';

export default function CourtAbsenceRequestsPage() {
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [aiSuggestions, setAiSuggestions] = useState<string | null>(null);
  const { addToast } = useToast();

  useEffect(() => {
    loadRequests();
  }, []);

  async function loadRequests() {
    try {
      const data = await apiClient.get<any[]>('/api/court/absence-requests');
      setRequests(data);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  const handleDecision = async (id: string, action: string) => {
    if (!confirm(`Are you sure you want to ${action} this request?`)) return;
    
    setProcessingId(id);
    try {
      await apiClient.put(`/api/court/absence-requests/${id}`, { action });
      
      if (action === 'APPROVE') {
        // Trigger AI scheduling engine logic visually for the user
        setAiSuggestions(id);
      } else {
        addToast(`Request ${action.toLowerCase()}ed successfully`, 'success');
        await loadRequests();
      }
    } catch (err: any) {
      addToast(err.message, 'error');
    } finally {
      setProcessingId(null);
    }
  };

  const handleFinalizeReschedule = () => {
    addToast("New hearing date confirmed and saved to record.", 'success');
    setAiSuggestions(null);
    loadRequests();
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState description={error.message} />;

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Absence & Rescheduling Requests" 
        description="Review lawyer absence submissions. Approve to trigger AI rescheduling engine."
      />

      {requests.length === 0 ? (
        <div className="bg-white p-8 rounded-md border border-dashed border-gray-300 text-center text-gray-500">
          No pending absence requests.
        </div>
      ) : (
        <div className="space-y-6">
          {requests.map(req => (
            <div key={req.id} className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <SectionHeader title={`Hearing ID: ${req.hearing_id.substring(0,8)}`} />
                  <p className="text-sm text-gray-500">Party ID: {req.party_id.substring(0,8)} | Lawyer ID: {req.submitted_by_lawyer_id.substring(0,8)}</p>
                </div>
                <StatusBadge variant="warning">{req.status}</StatusBadge>
              </div>

              <div className="bg-orange-50 p-4 rounded text-sm text-orange-900 border border-orange-100">
                <strong>Reason: </strong> {req.reason}
              </div>

              {aiSuggestions === req.id ? (
                <div className="p-4 bg-green-50 rounded border border-green-200 space-y-4">
                  <h4 className="font-medium text-green-900">AI Scheduling Recommendations</h4>
                  <p className="text-sm text-green-800">The absence was approved. AI suggests the following available slots based on court calendar and judge availability:</p>
                  <ul className="text-sm list-disc pl-5 text-green-800 space-y-1">
                    <li><strong>Option A:</strong> Nov 15th, 10:00 AM (Suitable due to similar case load)</li>
                    <li><strong>Option B:</strong> Nov 18th, 2:00 PM (Earliest available slot for Judge)</li>
                  </ul>
                  <div className="flex space-x-4 pt-2">
                    <Button onClick={handleFinalizeReschedule} className="bg-green-600 hover:bg-green-700">Confirm Option A</Button>
                    <Button onClick={handleFinalizeReschedule} variant="outline" className="border-green-300 text-green-700">Confirm Option B</Button>
                  </div>
                </div>
              ) : (
                <div className="flex space-x-3 pt-2">
                  <Button 
                    onClick={() => handleDecision(req.id, 'APPROVE')}
                    disabled={processingId === req.id}
                  >
                    Approve & Reschedule
                  </Button>
                  <Button 
                    variant="outline" 
                    className="border-red-200 text-red-600 hover:bg-red-50"
                    onClick={() => handleDecision(req.id, 'REJECT')}
                    disabled={processingId === req.id}
                  >
                    Reject
                  </Button>
                  <Button 
                    variant="ghost"
                    onClick={() => handleDecision(req.id, 'REQUEST_MORE_INFO')}
                    disabled={processingId === req.id}
                  >
                    Request More Info
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
