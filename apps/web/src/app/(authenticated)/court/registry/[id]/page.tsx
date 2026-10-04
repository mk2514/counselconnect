'use client';

import { useEffect, useState } from 'react';
import { PageHeader, SectionHeader } from '@/components/ui/typography';
import { ReviewPanel, ReviewField } from '@/components/ui/dialogs';
import { Button } from '@/components/ui/button';
import { FormField, Select } from '@/components/ui/forms';
import { LoadingState, ErrorState } from '@/components/ui/feedback';
import { apiClient } from '@/lib/api-client';
import { Loader2, Bot } from 'lucide-react';
import { useToast } from '@/components/providers/toast-provider';

interface Lawyer {
  id: string;
  full_name: string;
  bar_registration_id: string;
}

interface AIOutput {
  id: string;
  output_type: string;
  content: string;
  model_metadata?: { model?: string; provider?: string } | null;
}

interface AIJob {
  id: string;
  job_type: string;
  status: string;
  outputs: AIOutput[];
  error_message?: string;
  created_at?: string;
}

export default function CourtCaseDetailsPage({ params }: { params: { id: string } }) {
  const [caseRecord, setCaseRecord] = useState<any>(null);
  const [lawyers, setLawyers] = useState<Lawyer[]>([]);
  const [aiJobs, setAiJobs] = useState<AIJob[]>([]);
  const [aiError, setAiError] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { addToast } = useToast();
  
  // Assignment state
  const [isAssigning, setIsAssigning] = useState(false);
  const [selectedPartyId, setSelectedPartyId] = useState('');
  const [selectedLawyerId, setSelectedLawyerId] = useState('');
  const [assignmentError, setAssignmentError] = useState('');
  
  // AI state
  const [isGeneratingAi, setIsGeneratingAi] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [caseData, lawyersData] = await Promise.all([
          apiClient.get<any>(`/api/court/cases/${params.id}`),
          apiClient.get<Lawyer[]>('/api/court/lawyers'),
        ]);
        const aiData = await apiClient.get<AIJob[]>(`/api/ai/cases/${params.id}/jobs`).catch((err: unknown) => {
          setAiError(err instanceof Error ? err.message : 'AI job history is currently unavailable.');
          return [];
        });
        setCaseRecord(caseData);
        setLawyers(lawyersData);
        setAiJobs(aiData);
      } catch (err: any) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [params.id]);

  const handleAssignLawyer = async () => {
    if (!selectedPartyId || !selectedLawyerId) {
      setAssignmentError('Please select both a party and a lawyer.');
      return;
    }
    
    setAssignmentError('');
    setIsAssigning(true);
    
    try {
      await apiClient.post(`/api/court/cases/${params.id}/assignments`, {
        party_id: selectedPartyId,
        lawyer_id: selectedLawyerId,
      });
      addToast('Lawyer assigned successfully!', 'success');
      setSelectedPartyId('');
      setSelectedLawyerId('');
      window.location.reload();
    } catch (err: any) {
      setAssignmentError(err.message || 'Failed to assign lawyer.');
    } finally {
      setIsAssigning(false);
    }
  };

  const pollSummary = async (jobId: string): Promise<void> => {
    try {
      const updatedJob = await apiClient.get<AIJob>(`/api/ai/jobs/${jobId}`);
      setAiJobs((current) => current.map((job) => job.id === jobId ? updatedJob : job));
      if (updatedJob.status === 'PENDING' || updatedJob.status === 'PROCESSING') {
        window.setTimeout(() => void pollSummary(jobId), 2000);
      } else {
        setIsGeneratingAi(false);
      }
    } catch (err: unknown) {
      setAiError(err instanceof Error ? err.message : 'Could not retrieve the AI summary status.');
      setIsGeneratingAi(false);
    }
  };

  const handleGenerateSummary = async () => {
    setIsGeneratingAi(true);
    setAiError('');
    try {
      const job = await apiClient.post<AIJob>('/api/ai/jobs/summarize', { case_id: params.id });
      setAiJobs((current) => [job, ...current]);
      void pollSummary(job.id);
    } catch (err: unknown) {
      setAiError(err instanceof Error ? err.message : 'Failed to start AI summarization.');
      setIsGeneratingAi(false);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState description={error.message} />;
  if (!caseRecord) return <ErrorState description="Case not found" />;

  return (
    <div className="space-y-6">
      <PageHeader 
        title={`Manage Case: ${caseRecord.csr_number}`} 
        description="View case details and assign representation."
      />

      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-6">
          <SectionHeader title="Case Details" />
          <ReviewPanel title="Case Details">
            <ReviewField label="FIR Number" value={caseRecord.fir_number || 'N/A'} />
            <ReviewField label="Case Type" value={caseRecord.case_type} />
            <ReviewField label="Status" value={caseRecord.case_status} />
            <ReviewField label="Incident Location" value={caseRecord.incident_location || 'N/A'} />
          </ReviewPanel>
          
          <SectionHeader title="Parties" />
          <div className="space-y-3">
            {caseRecord.parties.map((party: any) => (
              <div key={party.id} className="rounded-md border border-[var(--color-border)] bg-white p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium text-[var(--color-primary-text)]">{party.full_name}</h4>
                    <p className="text-sm text-[var(--color-secondary-text)]">{party.party_type}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <SectionHeader title="Assign Representation" />
          <div className="rounded-md border border-[var(--color-border)] bg-white p-6 space-y-4">
            <p className="text-sm text-[var(--color-secondary-text)]">
              Select a party and assign a registered lawyer to represent them.
            </p>
            
            {assignmentError && (
              <div className="rounded-md bg-red-50 p-3 text-sm text-red-800 border border-red-200">
                {assignmentError}
              </div>
            )}
            
            <FormField id="party_select" label="Select Party" required>
              <Select id="party_select" value={selectedPartyId} onChange={(e) => setSelectedPartyId(e.target.value)}>
                <option value="">-- Select Party --</option>
                {caseRecord.parties.map((p: any) => (
                  <option key={p.id} value={p.id}>{p.full_name} ({p.party_type})</option>
                ))}
              </Select>
            </FormField>
            
            <FormField id="lawyer_select" label="Select Lawyer" required>
              <Select id="lawyer_select" value={selectedLawyerId} onChange={(e) => setSelectedLawyerId(e.target.value)}>
                <option value="">-- Select Lawyer --</option>
                {lawyers.map((l: any) => (
                  <option key={l.id} value={l.id}>{l.full_name} (Bar: {l.bar_registration_id})</option>
                ))}
              </Select>
            </FormField>

            <Button 
              className="w-full mt-4" 
              onClick={handleAssignLawyer} 
              disabled={isAssigning || !selectedPartyId || !selectedLawyerId}
            >
              {isAssigning && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Assign Lawyer
            </Button>
          </div>
          
          <SectionHeader title="AI Intelligence" />
          <div className="rounded-md border border-[var(--color-border)] bg-[#fafafa] p-6 space-y-4">
            <div className="flex items-center space-x-2 text-[var(--color-primary-text)] font-medium">
              <Bot className="h-5 w-5 text-[var(--color-terracotta)]" />
              <span>Case Summarization</span>
            </div>
            
            {aiJobs.length > 0 ? (
              <div className="space-y-4">
                {aiJobs.map(job => (
                  <div key={job.id} className="p-3 bg-white border border-gray-200 rounded-md shadow-sm">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-semibold uppercase text-gray-500">{job.job_type}</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${job.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : job.status === 'FAILED' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {job.status}
                      </span>
                    </div>
                    {job.outputs.map(out => (
                      <p key={out.id} className="text-sm text-gray-700 whitespace-pre-wrap">{out.content}</p>
                    ))}
                    {job.outputs.map((out) => out.model_metadata?.model && (
                      <p key={`${out.id}-source`} className="mt-2 text-xs text-gray-500">
                        Generated locally with {out.model_metadata.provider || 'local provider'} / {out.model_metadata.model}. Review before use.
                      </p>
                    ))}
                    {job.status === 'FAILED' && (
                      <p className="text-sm text-red-600">{job.error_message}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-[var(--color-secondary-text)]">
                No AI summary has been generated for this case yet. AI output is candidate information only and must be reviewed.
              </p>
            )}
            {aiError && (
              <p role="alert" className="text-sm text-amber-800">
                {aiError} Case management remains available; review the case manually.
              </p>
            )}
            
            <Button 
              variant="outline"
              className="w-full" 
              onClick={handleGenerateSummary} 
              disabled={isGeneratingAi || aiJobs.some(j => j.status === 'PENDING' || j.status === 'PROCESSING')}
            >
              {isGeneratingAi && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Generate AI Summary
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
