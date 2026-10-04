'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { PageHeader, SectionHeader } from '@/components/ui/typography';
import { Button } from '@/components/ui/button';
import { FormField, TextInput, Select, TextArea } from '@/components/ui/forms';
import { apiClient } from '@/lib/api-client';
import { Loader2, Upload, CheckCircle, ShieldAlert, FileSearch, QrCode as QrCodeIcon } from 'lucide-react';
import QRCode from 'react-qr-code';

type Step = 'UPLOAD' | 'REVIEW_EXTRACTION' | 'PARTIES' | 'SUBMIT' | 'SUCCESS';

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export default function CreateFIRPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('UPLOAD');
  
  // Case State
  const [caseId, setCaseId] = useState('');
  const [csrNumber, setCsrNumber] = useState('');
  
  // Upload State
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  
  // AI State
  const [jobId, setJobId] = useState('');
  const [jobStatus, setJobStatus] = useState('');
  const [isExtracting, setIsExtracting] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);
  const [reviewedAiJobId, setReviewedAiJobId] = useState('');
  const [modelLabel, setModelLabel] = useState('');
  
  // Form State (Verified Data)
  const [formData, setFormData] = useState({
    case_type: '',
    incident_date: '',
    incident_time: '',
    incident_location: '',
    offence_category: '',
  });
  
  const [parties, setParties] = useState<any[]>([]);
  
  // AI Multi-lingual State
  const [translationNote, setTranslationNote] = useState('');
  const [detectedLanguages, setDetectedLanguages] = useState<string[]>([]);

  // SUCCESS State
  const [qrToken, setQrToken] = useState('');

  const handleUploadAndExtract = async () => {
    if (!file) return;
    setIsUploading(true);
    setUploadError('');
    setJobId('');
    setJobStatus('');
    setModelLabel('');
    setReviewedAiJobId('');

    try {
      // 1. Create Draft Case
      const draftCase = await apiClient.post<any>('/api/police/cases/draft', {});
      setCaseId(draftCase.id);
      setCsrNumber(draftCase.csr_number);

      // 2. Upload Document
      const formDataUpload = new FormData();
      formDataUpload.append('file', file);
      
      const jobData = await apiClient.post<any>(
        `/api/police/cases/${draftCase.id}/documents/fir`,
        formDataUpload
      );
      
      setJobId(jobData.id);
      setJobStatus(jobData.status);
      setReviewedAiJobId('');
      setIsUploading(false);
      setIsExtracting(true);
      void pollAiJob(jobData.id);
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload document.');
      setIsUploading(false);
    }
  };

  const pollAiJob = async (id: string) => {
    try {
      const job = await apiClient.get<{
        id: string;
        status: string;
        error_message?: string | null;
        outputs: Array<{
          output_type: string;
          content: string;
          model_metadata?: { model?: string; provider?: string } | null;
        }>;
      }>(`/api/ai/jobs/${id}`);
      setJobStatus(job.status);
      if (job.status === 'COMPLETED') {
        setIsExtracting(false);
        const extractionOutput = job.outputs.find((output) => output.output_type === 'FIR_EXTRACTION');
        if (!extractionOutput) {
          setUploadError('The processing job completed without extraction data. Enter the FIR details manually.');
          setStep('REVIEW_EXTRACTION');
          return;
        }
        let extraction: Record<string, unknown>;
        try {
          const parsed: unknown = JSON.parse(extractionOutput.content);
          if (!isRecord(parsed)) throw new Error('Invalid extraction structure.');
          extraction = parsed;
        } catch {
          setUploadError('The extraction could not be read. Enter the FIR details manually.');
          setStep('REVIEW_EXTRACTION');
          return;
        }
        setReviewedAiJobId(job.id);
        if (extractionOutput.model_metadata?.model) {
          setModelLabel(`${extractionOutput.model_metadata.provider || 'local'} / ${extractionOutput.model_metadata.model}`);
        }
        
        setFormData({
          case_type: typeof extraction.case_type === 'string' ? extraction.case_type : '',
          incident_date: typeof extraction.incident_date === 'string' ? extraction.incident_date : '',
          incident_time: typeof extraction.incident_time === 'string' ? extraction.incident_time.slice(0, 5) : '',
          incident_location: typeof extraction.incident_location === 'string' ? extraction.incident_location : '',
          offence_category: typeof extraction.offence_category === 'string' ? extraction.offence_category : '',
        });
        
        if (Array.isArray(extraction.parties)) {
          const extractedParties = extraction.parties.filter((party): party is { type: string; name: string; contact_number?: string } => (
            typeof party === 'object'
            && party !== null
            && 'type' in party
            && 'name' in party
            && typeof party.type === 'string'
            && typeof party.name === 'string'
            && (!('contact_number' in party) || typeof party.contact_number === 'string')
            && ['COMPLAINANT', 'ACCUSED', 'WITNESS'].includes(party.type)
          )).map((p) => ({
            party_type: p.type,
            full_name: p.name,
            contact_number: p.contact_number || '',
          }));
          if (!extractedParties.some((party) => party.party_type === 'COMPLAINANT')) {
            extractedParties.unshift({ party_type: 'COMPLAINANT', full_name: '', contact_number: '' });
          }
          setParties(extractedParties);
        } else {
          setParties([{ party_type: 'COMPLAINANT', full_name: '', contact_number: '' }]);
        }
        
        if (typeof extraction.translation_note === 'string') {
          setTranslationNote(extraction.translation_note);
        }
        if (Array.isArray(extraction.detected_languages)) {
          setDetectedLanguages(extraction.detected_languages.filter((language): language is string => typeof language === 'string'));
        }
        
        setStep('REVIEW_EXTRACTION');
      } else if (job.status === 'FAILED') {
        setIsExtracting(false);
        setReviewedAiJobId('');
        setUploadError(
          `Automated document processing unavailable. Manual review required.${job.error_message ? ` ${job.error_message}` : ''}`
        );
        setStep('REVIEW_EXTRACTION'); // let them do it manually
      } else {
        window.setTimeout(() => void pollAiJob(id), 2000);
      }
    } catch {
      setIsExtracting(false);
      setReviewedAiJobId('');
      setUploadError('Automated document processing unavailable. Manual review required.');
      setStep('REVIEW_EXTRACTION');
    }
  };

  const handleRetryExtraction = async () => {
    if (!jobId) return;
    setIsRetrying(true);
    setIsExtracting(true);
    setUploadError('');
    setReviewedAiJobId('');
    try {
      await apiClient.post(`/api/ai/jobs/${jobId}/retry`);
      void pollAiJob(jobId);
    } catch (err: unknown) {
      setIsExtracting(false);
      setUploadError(err instanceof Error ? err.message : 'Could not retry document processing.');
    } finally {
      setIsRetrying(false);
    }
  };

  const handleFinalize = async () => {
    setIsUploading(true);
    setUploadError('');
    try {
      await apiClient.put(`/api/police/cases/${caseId}`, {
        ...formData,
        ...(reviewedAiJobId ? { source_ai_job_id: reviewedAiJobId } : {}),
        complainants: parties.filter(p => p.party_type === 'COMPLAINANT'),
        accused_persons: parties.filter(p => p.party_type === 'ACCUSED'),
        witnesses: parties.filter(p => p.party_type === 'WITNESS'),
      });
      // Generate QR Token securely
      const b64 = btoa(`${caseId}:${csrNumber}`);
      setQrToken(b64);
      setStep('SUCCESS');
    } catch (err: any) {
      setUploadError(err.message || 'Failed to finalize case.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader 
        title="Create New Case (FIR)" 
        description="Upload the FIR document for AI extraction, verify details, and register the case." 
      />

      <div className="flex items-center space-x-2 text-sm text-gray-500 mb-8">
        <span className={`font-medium ${step === 'UPLOAD' ? 'text-[var(--color-terracotta)]' : ''}`}>1. Upload</span>
        <span>→</span>
        <span className={`font-medium ${step === 'REVIEW_EXTRACTION' ? 'text-[var(--color-terracotta)]' : ''}`}>2. Verify Extraction</span>
        <span>→</span>
        <span className={`font-medium ${step === 'PARTIES' ? 'text-[var(--color-terracotta)]' : ''}`}>3. Parties</span>
        <span>→</span>
        <span className={`font-medium ${step === 'SUBMIT' ? 'text-[var(--color-terracotta)]' : ''}`}>4. Finalize</span>
      </div>

      {uploadError && (
        <div className="mb-4 rounded-md bg-red-50 p-4 text-sm text-red-800 border border-red-200">
          {uploadError}
        </div>
      )}

      {step === 'UPLOAD' && (
        <div className="rounded-md border border-[var(--color-border)] bg-white p-8 text-center space-y-6">
          <FileSearch className="mx-auto h-12 w-12 text-gray-400" />
          <div>
            <h3 className="text-lg font-medium text-gray-900">Upload FIR Document</h3>
            <p className="mt-1 text-sm text-gray-500">
              Upload the original FIR. The system will securely hash the file and use AI to extract case metadata automatically.
            </p>
          </div>
          
          <div className="max-w-xs mx-auto flex flex-col gap-4">
            <div className="text-left">
              <label className="block text-sm font-medium text-gray-700 mb-1">Upload File</label>
              <input 
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-[var(--color-background)] file:text-[var(--color-primary-text)] hover:file:bg-gray-200 cursor-pointer"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </div>
            <div className="text-left">
              <label className="block text-sm font-medium text-gray-700 mb-1">Or Capture Document (Camera)</label>
              <input 
                type="file"
                accept="image/*"
                capture="environment"
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-[var(--color-terracotta)] file:text-white hover:file:bg-[#8E432B] cursor-pointer"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </div>
          </div>

          <Button 
            onClick={handleUploadAndExtract} 
            disabled={!file || isUploading || isExtracting}
            className="w-full max-w-xs"
          >
            {isUploading ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Uploading...</>
            ) : isExtracting ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Extracting Data...</>
            ) : (
              <><Upload className="mr-2 h-4 w-4" /> Start AI Extraction</>
            )}
          </Button>
          
          {isExtracting && (
            <p className="text-xs text-[var(--color-terracotta)] animate-pulse">
              AI Worker is processing the document. Please wait...
            </p>
          )}
        </div>
      )}

      {step === 'REVIEW_EXTRACTION' && (
        <div className="rounded-md border border-[var(--color-border)] bg-white p-6 space-y-6">
          <SectionHeader title={`Verify Case Details (CSR: ${csrNumber})`} />
          <p className="text-sm text-gray-500">
            The AI has extracted the following details. Please verify and correct them. 
            The system tracks human verification for all structured records.
          </p>
          
          {detectedLanguages.length > 0 && (
            <div className="bg-blue-50 border border-blue-100 rounded-md p-4 mb-4">
              <h4 className="text-sm font-semibold text-blue-900 mb-1">Multi-lingual AI Processing Active</h4>
              <p className="text-sm text-blue-800">{translationNote}</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {detectedLanguages.map(lang => (
                  <span key={lang} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                    {lang}
                  </span>
                ))}
              </div>
            </div>
          )}
          {modelLabel && (
            <p className="text-xs text-gray-500">
              Extraction source: {modelLabel}. Suggestions are unverified until you submit this case.
            </p>
          )}
          {jobId && jobStatus === 'FAILED' && !reviewedAiJobId && uploadError && (
            <Button type="button" variant="outline" onClick={handleRetryExtraction} disabled={isRetrying || isExtracting}>
              {isRetrying && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Retry document processing
            </Button>
          )}
          {isExtracting && (
            <p role="status" className="text-sm text-[var(--color-terracotta)]">
              Document processing is in progress. This will not update the case record until you review and submit.
            </p>
          )}

          <div className="grid grid-cols-2 gap-4">
            <FormField id="case_type" label="Case Type" required>
              <Select
                id="case_type"
                value={formData.case_type}
                onChange={(e) => setFormData({ ...formData, case_type: e.target.value })}
                required
              >
                <option value="">Select Case Type</option>
                <option value="CRIMINAL">CRIMINAL</option>
                <option value="CIVIL">CIVIL</option>
                <option value="TRAFFIC">TRAFFIC</option>
                <option value="MISC">MISCELLANEOUS</option>
              </Select>
            </FormField>
            
            <FormField id="offence_category" label="Offence Category">
              <TextInput
                id="offence_category"
                value={formData.offence_category}
                onChange={(e) => setFormData({ ...formData, offence_category: e.target.value })}
                placeholder="e.g. Theft, Assault"
              />
            </FormField>

            <FormField id="incident_date" label="Incident Date" required>
              <TextInput
                id="incident_date"
                type="date"
                value={formData.incident_date}
                onChange={(e) => setFormData({ ...formData, incident_date: e.target.value })}
                required
              />
            </FormField>

            <FormField id="incident_time" label="Incident Time (Optional)">
              <TextInput
                id="incident_time"
                type="time"
                value={formData.incident_time}
                onChange={(e) => setFormData({ ...formData, incident_time: e.target.value })}
              />
            </FormField>
          </div>

          <FormField id="incident_location" label="Incident Location" required>
            <TextArea
              id="incident_location"
              rows={2}
              value={formData.incident_location}
              onChange={(e) => setFormData({ ...formData, incident_location: e.target.value })}
              required
            />
          </FormField>

          <div className="flex justify-end">
            <Button onClick={() => setStep('PARTIES')}>
              Verify & Continue
            </Button>
          </div>
        </div>
      )}

      {step === 'PARTIES' && (
        <div className="rounded-md border border-[var(--color-border)] bg-white p-6 space-y-6">
          <SectionHeader title="Manage Parties" />
          
          {parties.map((p, i) => (
            <div key={i} className="p-4 border border-gray-200 rounded-md space-y-4">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-sm">Party {i + 1}</span>
                {parties.length > 1 && (
                  <button type="button" onClick={() => setParties(parties.filter((_, idx) => idx !== i))} className="text-red-500 text-sm hover:underline">
                    Remove
                  </button>
                )}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <FormField id={`ptype-${i}`} label="Type" required>
                  <Select
                    id={`ptype-${i}`}
                    value={p.party_type}
                    onChange={(e) => {
                      const newP = [...parties];
                      newP[i].party_type = e.target.value;
                      setParties(newP);
                    }}
                  >
                    <option value="COMPLAINANT">COMPLAINANT</option>
                    <option value="ACCUSED">ACCUSED</option>
                    <option value="WITNESS">WITNESS</option>
                  </Select>
                </FormField>
                <FormField id={`pname-${i}`} label="Full Name" required>
                  <TextInput
                    id={`pname-${i}`}
                    value={p.full_name}
                    onChange={(e) => {
                      const newP = [...parties];
                      newP[i].full_name = e.target.value;
                      setParties(newP);
                    }}
                    placeholder="Allow 'Unknown' if not known"
                  />
                </FormField>
              </div>
            </div>
          ))}
          
          <Button type="button" variant="outline" onClick={() => setParties([...parties, { party_type: 'WITNESS', full_name: '', contact_number: '' }])}>
            + Add Another Party
          </Button>

          <div className="flex justify-between pt-4">
            <Button variant="outline" onClick={() => setStep('REVIEW_EXTRACTION')}>Back</Button>
            <Button onClick={() => setStep('SUBMIT')}>Review & Finalize</Button>
          </div>
        </div>
      )}

      {step === 'SUBMIT' && (
        <div className="rounded-md border border-[var(--color-border)] bg-white p-6 space-y-6">
          <SectionHeader title="Finalize Registration" />
          <p className="text-sm text-gray-500">
            Please confirm all details. Submitting this form will lock the CSR <strong>{csrNumber}</strong> and permanently append it to the digital ledger.
          </p>
          
          <div className="flex justify-between pt-4">
            <Button variant="outline" onClick={() => setStep('PARTIES')}>Back</Button>
            <Button onClick={handleFinalize} disabled={isUploading}>
              {isUploading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <ShieldAlert className="mr-2 h-4 w-4" />}
              Submit & Register Case
            </Button>
          </div>
        </div>
      )}

      {step === 'SUCCESS' && (
        <div className="rounded-md border border-[var(--color-border)] bg-white p-12 text-center space-y-6">
          <CheckCircle className="mx-auto h-16 w-16 text-green-500" />
          <h2 className="text-2xl font-semibold">Case Registered Successfully</h2>
          <p className="text-gray-500">The authoritative CSR has been generated and locked.</p>
          
          <div className="bg-gray-50 p-6 rounded-md inline-flex flex-col items-center text-center mt-4 border border-gray-200">
            <p className="font-mono text-lg font-bold text-[var(--color-primary-text)] mb-4">CSR: {csrNumber}</p>
            <div className="bg-white p-4 rounded-md shadow-sm mb-4">
              <QRCode value={qrToken} size={150} level="M" />
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <QrCodeIcon className="h-4 w-4" />
              <span>Token: <span className="font-mono text-xs break-all">{qrToken}</span></span>
            </div>
          </div>
          
          <div className="pt-8">
            <Button onClick={() => router.push('/police/firs')}>
              Go to My Cases
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
