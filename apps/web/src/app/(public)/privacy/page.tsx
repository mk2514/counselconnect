import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans">
      <header className="border-b sticky top-0 bg-white/80 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-6 h-16 flex items-center">
          <Link href="/" className="inline-flex items-center justify-center -ml-2 px-3 py-1.5 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
          </Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-12 pb-24">
        <h1 className="text-3xl font-semibold mb-8">Privacy Policy</h1>
        
        <div className="space-y-8 text-slate-700 leading-relaxed">
          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">1. Account Data</h2>
            <p>We collect essential account data required for system access, including passwords (stored as bcrypt hashes) and primary contact details provided during registration.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">2. Role Identity Information</h2>
            <p>We process verifiable identifiers relevant to your official role, such as Bar Registration IDs for Lawyers, Station Codes for Police Officers, and JO Codes for Court Authorities. This data is used exclusively to verify authorization and enforce role-based access controls.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">3. Case Data</h2>
            <p>The system stores official judicial case data including FIRs, party details, investigation notes, evidence records, proceedings, and judgments. Case data is strictly compartmentalized; users may only access cases for which they hold an active, authorized assignment or official jurisdiction.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">4. Documents</h2>
            <p>Uploaded documents (PDFs, images) are securely stored. File hashes (SHA256) are computed upon upload to maintain document integrity and prevent duplicate submissions.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">5. Audit History</h2>
            <p>To ensure non-repudiation and system integrity, we maintain immutable audit logs of all substantive actions. This includes timestamps, user IDs, roles, and the specific state changes associated with viewing or modifying case data.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">6. Device and Passkey Metadata</h2>
            <p>For users utilizing WebAuthn or NFC, we store cryptographic public keys and registered device identifiers. We do not process or store your biometric data; all biometric verification occurs locally on your personal device.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">7. NFC Identifiers</h2>
            <p>NFC cards are issued with mathematically opaque tokens. No personal identifiable information (PII) is stored physically on the NFC card itself.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">8. Purpose of Processing</h2>
            <p>All data is processed strictly for the administration of justice, facilitation of court proceedings, and the secure management of legal representation.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">9. AI Processing</h2>
            <p>Documents and audio recordings may be processed by localized AI models for OCR and speech-to-text transcription. This processing is performed within our controlled infrastructure. We do not use case data to train public generative AI models.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">10. Retention Principles</h2>
            <p>Data is retained in accordance with statutory judicial archiving requirements. Audit logs are retained indefinitely to ensure historical integrity.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">11. Security Controls</h2>
            <p>We implement role-based access control, cryptographic hashing, and secure session management. We regularly audit the system to protect against unauthorized access or disclosure.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">12. User Access Restrictions</h2>
            <p>Your access is strictly limited to the scope of your legal authority. Lawyers can only view cases they are assigned to. System administrators cannot access the substantive content of sealed cases without judicial authorization.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">13. Contact</h2>
            <p>For privacy inquiries or to report unauthorized access, please contact the IT Administration desk or the designated Data Protection Officer for your jurisdiction.</p>
          </section>
        </div>
      </main>
    </div>
  );
}
