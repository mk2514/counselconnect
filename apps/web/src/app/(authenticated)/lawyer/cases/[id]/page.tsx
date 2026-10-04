'use client';

import { useEffect, useState } from 'react';
import { PageHeader, SectionHeader } from '@/components/ui/typography';
import { Button } from '@/components/ui/button';
import { FormField, TextInput, TextArea, Select } from '@/components/ui/forms';
import { LoadingState, ErrorState } from '@/components/ui/feedback';
import { apiClient } from '@/lib/api-client';
import { StatusBadge } from '@/components/ui/badge';
import { FileText, Gavel, FileClock, Scale, LogOut, CheckCircle, XCircle } from 'lucide-react';
import { useToast } from '@/components/providers/toast-provider';

export default function LawyerCaseWorkspacePage({ params }: { params: { id: string } }) {
  const [caseRecord, setCaseRecord] = useState<any>(null);
  const [hearings, setHearings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { addToast } = useToast();
  
  const [activeTab, setActiveTab] = useState('Overview');

  const [retireReason, setRetireReason] = useState('');
  const [absenceReason, setAbsenceReason] = useState('');
  const [selectedPartyId, setSelectedPartyId] = useState('');
  const [selectedHearingId, setSelectedHearingId] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const c = await apiClient.get<any>(`/api/lawyer/cases/${params.id}`);
        setCaseRecord(c);
        const h = await apiClient.get<any[]>(`/api/lawyer/cases/${params.id}/hearings`);
        setHearings(h);
      } catch (err: any) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [params.id]);

  const handleRetire = async () => {
    if (!retireReason) return;
    setIsSubmitting(true);
    try {
      await apiClient.post(`/api/lawyer/cases/${params.id}/retire`, {
        request_type: 'RETIRE_REPRESENTATION',
        reason: retireReason,
      });
      addToast('Representation change request submitted to Court Authority.', 'success');
      setRetireReason('');
    } catch (err: any) {
      addToast(err.message || 'Failed to submit request', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleWithdraw = async () => {
    if (!retireReason) return;
    setIsSubmitting(true);
    try {
      await apiClient.post(`/api/lawyer/cases/${params.id}/withdraw`, {
        reason: retireReason,
      });
      addToast('Withdrawal/Disposal request submitted to Court Authority.', 'success');
      setRetireReason('');
    } catch (err: any) {
      addToast(err.message || 'Failed to submit request', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAbsence = async () => {
    if (!selectedHearingId || !selectedPartyId || !absenceReason) return;
    setIsSubmitting(true);
    try {
      await apiClient.post(`/api/lawyer/hearings/${selectedHearingId}/absence-requests`, {
        party_id: selectedPartyId,
        reason: absenceReason
      });
      addToast('Absence request submitted successfully.', 'success');
      setAbsenceReason('');
    } catch (err: any) {
      addToast(err.message || 'Failed to submit request', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState description={error.message} />;
  if (!caseRecord) return <ErrorState description="Case not found" />;

  const tabs = ['Overview', 'Documents', 'Hearings', 'Proceedings', 'Attendance', 'Requests', 'Judgment', 'Timeline'];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <PageHeader 
          title={`Case Workspace: ${caseRecord.csr_number}`} 
          description="Manage representation, submit documents, and track court proceedings."
        />
        <StatusBadge variant="default" className="text-sm">Assignment: ACTIVE</StatusBadge>
      </div>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-6 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab 
                  ? 'border-[var(--color-terracotta)] text-[var(--color-terracotta)]' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      <div className="pt-4">
        {activeTab === 'Overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-4">
              <SectionHeader title="Case Overview" />
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500 block">CSR Number</span>
                  <span className="font-mono font-medium">{caseRecord.csr_number}</span>
                </div>
                <div>
                  <span className="text-gray-500 block">FIR Number</span>
                  <span className="font-medium">{caseRecord.fir_number || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-gray-500 block">Case Type</span>
                  <span className="font-medium">{caseRecord.case_type}</span>
                </div>
                <div>
                  <span className="text-gray-500 block">Status</span>
                  <span className="font-medium">{caseRecord.case_status}</span>
                </div>
                <div>
                  <span className="text-gray-500 block">Court</span>
                  <span className="font-medium">Not Assigned</span>
                </div>
                <div>
                  <span className="text-gray-500 block">Judge</span>
                  <span className="font-medium">Not Assigned</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-4">
              <SectionHeader title="Represented Parties" />
              <div className="space-y-3">
                {caseRecord.parties.map((p: any) => (
                  <div key={p.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded border border-gray-100">
                    <div className="h-8 w-8 rounded-full bg-[var(--color-terracotta)] text-white flex items-center justify-center font-bold text-xs">
                      {p.full_name.charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{p.full_name}</p>
                      <p className="text-xs text-gray-500">{p.party_type}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'Requests' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-4 border-l-4 border-l-orange-500">
              <SectionHeader title="Retire Representation" />
              <p className="text-sm text-gray-500">
                Submit a request to step down from this case. Does not remove assignment immediately; pending Court Authority review.
              </p>
              <FormField id="retire_reason" label="Reason for Retirement" required>
                <TextArea id="retire_reason" rows={3} value={retireReason} onChange={(e) => setRetireReason(e.target.value)} />
              </FormField>
              <Button variant="outline" className="w-full text-orange-600 border-orange-200 hover:bg-orange-50" onClick={handleRetire} disabled={isSubmitting || !retireReason}>
                Submit Retirement Request
              </Button>
            </div>

            <div className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-4 border-l-4 border-l-red-500">
              <SectionHeader title="Withdrawal / Disposal Request" />
              <p className="text-sm text-gray-500">
                Request the court to withdraw or dispose of this case entirely. Subject to judicial approval.
              </p>
              <FormField id="withdraw_reason" label="Reason for Disposal" required>
                <TextArea id="withdraw_reason" rows={3} value={retireReason} onChange={(e) => setRetireReason(e.target.value)} />
              </FormField>
              <Button variant="outline" className="w-full text-red-600 border-red-200 hover:bg-red-50" onClick={handleWithdraw} disabled={isSubmitting || !retireReason}>
                Request Case Disposal
              </Button>
            </div>
          </div>
        )}

        {activeTab === 'Judgment' && (
          <div className="bg-white p-8 rounded-md border border-[var(--color-border)] text-center space-y-4">
            <Scale className="h-12 w-12 mx-auto text-gray-400" />
            <h3 className="text-lg font-medium">No Judgment Available</h3>
            <p className="text-gray-500 text-sm">
              The case has not yet reached a final disposition. Once the court issues a judgment, the official document and AI metadata summary will appear here.
            </p>
          </div>
        )}

        {activeTab === 'Attendance' && (
          <div className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-6">
            <SectionHeader title="Record Attendance or Absence" />
            <p className="text-sm text-gray-500 mb-4">
              Select a scheduled hearing to submit a formal absence request with proof.
            </p>
            {hearings.length === 0 ? (
              <div className="p-8 bg-gray-50 border border-dashed border-gray-200 rounded-md text-center text-sm text-gray-500">
                No active hearings found for this case.
              </div>
            ) : (
              <div className="space-y-4">
                <FormField id="hearing_select" label="Select Hearing" required>
                  <Select id="hearing_select" value={selectedHearingId} onChange={(e) => setSelectedHearingId(e.target.value)}>
                    <option value="">-- Choose a hearing --</option>
                    {hearings.map(h => (
                      <option key={h.id} value={h.id}>
                        {h.hearing_date} at {h.hearing_time} - {h.status}
                      </option>
                    ))}
                  </Select>
                </FormField>
                <FormField id="party_select" label="Select Party You Represent" required>
                  <Select id="party_select" value={selectedPartyId} onChange={(e) => setSelectedPartyId(e.target.value)}>
                    <option value="">-- Choose a party --</option>
                    {caseRecord.parties.map((p: any) => (
                      <option key={p.id} value={p.id}>
                        {p.full_name} ({p.party_type})
                      </option>
                    ))}
                  </Select>
                </FormField>
                <FormField id="absence_reason" label="Reason for Absence" required>
                  <TextArea id="absence_reason" rows={3} value={absenceReason} onChange={(e) => setAbsenceReason(e.target.value)} placeholder="e.g. Medical emergency (attach proof later)" />
                </FormField>
                <Button 
                  variant="outline" 
                  className="w-full text-blue-600 border-blue-200 hover:bg-blue-50" 
                  onClick={handleAbsence} 
                  disabled={isSubmitting || !selectedHearingId || !selectedPartyId || !absenceReason}
                >
                  Submit Absence Request
                </Button>
              </div>
            )}
          </div>
        )}

        {['Documents', 'Hearings', 'Proceedings', 'Timeline'].includes(activeTab) && (
          <div className="bg-white p-8 rounded-md border border-[var(--color-border)] text-center space-y-4">
            <FileText className="h-12 w-12 mx-auto text-gray-400" />
            <h3 className="text-lg font-medium">{activeTab}</h3>
            <p className="text-gray-500 text-sm">This section is currently empty or pending court action.</p>
          </div>
        )}
      </div>
    </div>
  );
}
