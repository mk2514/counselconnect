import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function TermsPage() {
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
        <h1 className="text-3xl font-semibold mb-8">Terms of Service</h1>
        
        <div className="space-y-8 text-slate-700 leading-relaxed">
          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">1. Eligibility</h2>
            <p>Access to this system is restricted to authorized Police officers, registered Lawyers, and Court Authorities. Users must provide valid identification and credentials (e.g., Bar Registration ID, Police Station Code, JO Code) which are subject to verification.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">2. Authorized Use</h2>
            <p>The system is provided solely for the administration of judicial cases, filing of First Information Reports (FIRs), management of legal representation, and court scheduling. Users must not use the system for personal, commercial, or unauthorized administrative purposes.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">3. Account Responsibility</h2>
            <p>Users are strictly responsible for maintaining the confidentiality of their credentials and passkeys. Sharing accounts is explicitly prohibited. All actions performed under an account are legally attributed to the registered individual.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">4. Role Responsibilities</h2>
            <ul className="list-disc pl-5 space-y-2">
              <li><strong>Police:</strong> Responsible for accurate entry of CSRs, FIRs, investigation notes, and evidence logs.</li>
              <li><strong>Lawyers:</strong> Responsible for accurate representation requests, attendance logging, and absence requests.</li>
              <li><strong>Court Authorities:</strong> Responsible for official scheduling decisions, final agenda generation, and oversight of case progression.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">5. NFC Access Responsibility</h2>
            <p>Lawyers utilizing NFC cards for quick access must ensure the physical security of their issued card. The NFC card must be paired with the user&apos;s primary authorized mobile device. In the event of a lost card, the user must immediately revoke it via their dashboard.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">6. Prohibited Access</h2>
            <p>Attempting to bypass role-based access controls, accessing cases without active representation assignments, or utilizing automated scraping tools against the platform is strictly prohibited and subject to legal penalty.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">7. Document Responsibility</h2>
            <p>Users uploading documents are responsible for the accuracy and authenticity of the files. The system implements hashing to verify document integrity. Uploading malicious files or forged documents is a criminal offense.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">8. AI Assistance Limitations</h2>
            <p>The system provides AI-assisted document extraction (OCR) and speech-to-text transcriptions. These are draft outputs and do not constitute official records until explicitly reviewed, verified, and confirmed by an authorized human user.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">9. Official Decision Authority</h2>
            <p>AI scheduling recommendations are advisory. All final judicial scheduling, agenda ordering, and case judgments remain the exclusive authority and responsibility of the Court Authority.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">10. Security</h2>
            <p>The system monitors and creates immutable audit logs of all critical actions (including viewing, updating, and withdrawing from cases). Users consent to this monitoring as a condition of access.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">11. Availability</h2>
            <p>The system strives for high availability but does not guarantee uninterrupted access. System maintenance may occur outside of standard court operating hours.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">12. Termination and Suspension</h2>
            <p>Access may be suspended immediately without notice in the event of suspected credential compromise, unauthorized access attempts, or revocation of the user&apos;s official legal standing (e.g., disbarment).</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">13. Intellectual Property</h2>
            <p>The underlying software, workflows, and platform design are proprietary to the governing judicial body. Case data remains the property of the state.</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">14. Prototype Limitations</h2>
            <p>This system is currently operating in a prototype phase. While functional, certain integrations with external state legacy databases may be simulated.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mb-3">15. Contact</h2>
            <p>For support, credential revocation, or to report security incidents, please contact the IT Administration desk of your respective jurisdiction.</p>
          </section>
        </div>
      </main>
    </div>
  );
}
