'use client';

import { useEffect, useState } from 'react';
import { PageHeader, SectionHeader } from '@/components/ui/typography';
import { Button } from '@/components/ui/button';
import { StatusBadge } from '@/components/ui/badge';
import { LoadingState, ErrorState } from '@/components/ui/feedback';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/components/providers/toast-provider';

export default function CourtRepRequestsPage() {
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const { addToast } = useToast();

  useEffect(() => {
    loadRequests();
  }, []);

  async function loadRequests() {
    try {
      const data = await apiClient.get<any[]>('/api/court/representation-requests');
      setRequests(data);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  const handleAction = async (id: string, action: 'APPROVE' | 'REJECT') => {
    setProcessingId(id);
    try {
      await apiClient.put(`/api/court/representation-requests/${id}`, { action });
      addToast(`Request ${action === 'APPROVE' ? 'approved' : 'rejected'} successfully`, 'success');
      await loadRequests();
    } catch (err: any) {
      addToast(err.message || 'Failed to process request', 'error');
    } finally {
      setProcessingId(null);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState description={error.message} />;

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Representation Changes" 
        description="Review requests from lawyers stepping down. Approval retires the current assignment."
      />
      {requests.length === 0 ? (
        <div className="bg-white p-8 rounded-md border border-dashed border-gray-300 text-center text-gray-500">
          No pending representation change requests.
        </div>
      ) : (
        <div className="space-y-4">
          {requests.map(req => (
            <div key={req.id} className="bg-white p-6 rounded-md border border-gray-200 shadow-sm flex items-start justify-between">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <span className="font-semibold text-lg text-gray-900">{req.request_type}</span>
                  <StatusBadge variant="warning">{req.status}</StatusBadge>
                </div>
                <p className="text-sm text-gray-600 mb-4">Reason: {req.reason}</p>
                <div className="text-xs text-gray-500">
                  <p>Case ID: {req.case_id}</p>
                  <p>Requested By: {req.requested_by}</p>
                  <p>Date: {new Date(req.created_at).toLocaleString()}</p>
                </div>
              </div>
              <div className="flex space-x-3">
                <Button 
                  variant="outline" 
                  className="text-red-600 border-red-200 hover:bg-red-50"
                  disabled={processingId === req.id}
                  onClick={() => handleAction(req.id, 'REJECT')}
                >
                  Reject
                </Button>
                <Button 
                  variant="primary"
                  disabled={processingId === req.id}
                  onClick={() => handleAction(req.id, 'APPROVE')}
                >
                  Approve
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
