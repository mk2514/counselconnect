'use client';

import { useEffect, useState } from 'react';
import { PageHeader, SectionHeader } from '@/components/ui/typography';
import { Button } from '@/components/ui/button';
import { FormField, TextInput, TextArea, Select } from '@/components/ui/forms';
import { LoadingState, ErrorState } from '@/components/ui/feedback';
import { apiClient } from '@/lib/api-client';
import { Shield, FileText, Upload, Plus, QrCode as QrCodeIcon } from 'lucide-react';
import { StatusBadge } from '@/components/ui/badge';
import { useToast } from '@/components/providers/toast-provider';
import QRCode from 'react-qr-code';

export default function PoliceCaseDashboardPage({ params }: { params: { id: string } }) {
  const [caseRecord, setCaseRecord] = useState<any>(null);
  const [investigations, setInvestigations] = useState<any[]>([]);
  const [evidence, setEvidence] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { addToast } = useToast();

  // Forms
  const [note, setNote] = useState('');
  const [evidenceNumber, setEvidenceNumber] = useState('');
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');
  
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [c, i, e] = await Promise.all([
          apiClient.get<any>(`/api/police/cases/${params.id}`),
          apiClient.get<any[]>(`/api/police/cases/${params.id}/investigations`),
          apiClient.get<any[]>(`/api/police/cases/${params.id}/evidence`),
        ]);
        setCaseRecord(c);
        setInvestigations(i);
        setEvidence(e);
      } catch (err: any) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [params.id]);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const newNote = await apiClient.post(`/api/police/cases/${params.id}/investigations`, { note });
      setInvestigations([newNote, ...investigations]);
      setNote('');
      addToast({ title: 'Investigation note added successfully', type: 'success' });
    } catch (err: any) {
      addToast({ title: err.message || 'Failed to add note', type: 'error' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const newEv = await apiClient.post(`/api/police/cases/${params.id}/evidence`, {
        evidence_number: evidenceNumber,
        category,
        description,
      });
      setEvidence([newEv, ...evidence]);
      setEvidenceNumber('');
      setCategory('');
      setDescription('');
      addToast({ title: 'Evidence logged successfully', type: 'success' });
    } catch (err: any) {
      addToast({ title: err.message || 'Failed to add evidence', type: 'error' });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState description={error.message} />;
  if (!caseRecord) return <ErrorState description="Case not found" />;

  const qrToken = btoa(`${caseRecord.id}:${caseRecord.csr_number}`);

  return (
    <div className="space-y-8">
      <PageHeader 
        title={`Case Dashboard: ${caseRecord.csr_number}`} 
        description="Comprehensive view of case lifecycle, investigations, and evidence."
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <SectionHeader title="Case Status Lifecycle" />
          <div className="bg-white p-6 rounded-md border border-[var(--color-border)] flex space-x-4 items-center overflow-x-auto">
            <StatusBadge variant={caseRecord.case_status === 'DRAFT' ? 'outline' : 'default'}>CSR Draft</StatusBadge>
            <span>→</span>
            <StatusBadge variant={caseRecord.case_status === 'REGISTERED' ? 'default' : 'outline'}>FIR Registered</StatusBadge>
            <span>→</span>
            <StatusBadge variant="outline">Investigation</StatusBadge>
            <span>→</span>
            <StatusBadge variant="outline">Court Proceedings</StatusBadge>
          </div>

          <SectionHeader title="Investigation Diary" />
          <div className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-6">
            <form onSubmit={handleAddNote} className="space-y-4">
              <FormField id="note" label="Add Investigation Note" required>
                <TextArea 
                  id="note" 
                  value={note} 
                  onChange={e => setNote(e.target.value)} 
                  placeholder="Record investigation events..."
                  required 
                />
              </FormField>
              <Button type="submit" disabled={isSubmitting || !note}>
                <Plus className="mr-2 h-4 w-4" /> Add Note
              </Button>
            </form>
            
            <div className="space-y-4 pt-4 border-t border-gray-100">
              {investigations.map(inv => (
                <div key={inv.id} className="p-4 bg-gray-50 rounded-md border border-gray-100">
                  <p className="text-sm text-gray-800 whitespace-pre-wrap">{inv.note}</p>
                </div>
              ))}
            </div>
          </div>

          <SectionHeader title="Evidence Records" />
          <div className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-6">
            <form onSubmit={handleAddEvidence} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <FormField id="ev_no" label="Evidence Number" required>
                  <TextInput id="ev_no" value={evidenceNumber} onChange={e => setEvidenceNumber(e.target.value)} required />
                </FormField>
                <FormField id="cat" label="Category" required>
                  <Select id="cat" value={category} onChange={e => setCategory(e.target.value)} required>
                    <option value="">Select Category</option>
                    <option value="DOCUMENT">Document</option>
                    <option value="PHYSICAL">Physical Evidence</option>
                    <option value="DIGITAL">Digital / Media</option>
                  </Select>
                </FormField>
              </div>
              <FormField id="desc" label="Description">
                <TextArea id="desc" value={description} onChange={e => setDescription(e.target.value)} />
              </FormField>
              <Button type="submit" disabled={isSubmitting || !evidenceNumber || !category}>
                <Shield className="mr-2 h-4 w-4" /> Record Evidence
              </Button>
            </form>

            <div className="space-y-4 pt-4 border-t border-gray-100">
              {evidence.map(ev => (
                <div key={ev.id} className="p-4 bg-gray-50 rounded-md border border-gray-100 grid grid-cols-2">
                  <div>
                    <span className="font-medium block">{ev.evidence_number}</span>
                    <span className="text-xs text-gray-500 uppercase">{ev.category}</span>
                  </div>
                  <div className="text-sm text-gray-700">{ev.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <SectionHeader title="Case Details" />
          <div className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-4 text-sm">
            <div><span className="text-gray-500 block">Type</span> <span className="font-medium">{caseRecord.case_type}</span></div>
            <div><span className="text-gray-500 block">Category</span> <span className="font-medium">{caseRecord.offence_category}</span></div>
            <div><span className="text-gray-500 block">Incident Date</span> <span className="font-medium">{caseRecord.incident_date}</span></div>
            <div><span className="text-gray-500 block">Location</span> <span className="font-medium">{caseRecord.incident_location}</span></div>
            
            <div className="pt-4 border-t border-gray-100">
              <span className="text-gray-500 block mb-2">Secure QR Token</span>
              <div className="bg-gray-50 p-4 rounded-md flex flex-col items-center space-y-3 border border-gray-200 text-center">
                <div className="bg-white p-3 rounded-md shadow-sm">
                  <QRCode value={qrToken} size={150} level="M" />
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-500 justify-center">
                  <QrCodeIcon className="h-4 w-4" />
                  <span className="font-mono text-xs break-all">{qrToken}</span>
                </div>
              </div>
            </div>
          </div>

          <SectionHeader title="Parties" />
          <div className="bg-white p-6 rounded-md border border-[var(--color-border)] space-y-4 text-sm">
            {caseRecord.parties.map((p: any) => (
              <div key={p.id} className="border-b border-gray-100 pb-2 last:border-0">
                <span className="text-xs font-semibold text-gray-500 uppercase block">{p.party_type}</span>
                <span className="font-medium text-[var(--color-primary-text)]">{p.full_name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
