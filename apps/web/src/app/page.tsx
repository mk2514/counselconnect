'use client';

import Link from 'next/link';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Shield, FileText, Gavel, CheckCircle2, Bot, Fingerprint, Lock, ShieldCheck, Network, AlertCircle, ArrowRight, XCircle, Briefcase, Scale, LayoutDashboard } from 'lucide-react';
import { useRef } from 'react';

// Fade in up animation variant
const fadeInUp: any = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } }
};

const staggerContainer: any = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15 }
  }
};

export default function RootPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: containerRef, offset: ["start start", "end start"] });
  const yBg = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const rotateSculpture = useTransform(scrollYProgress, [0, 1], [-25, 25]);
  
  // Dramatic Scroll Transitions (Smartphone Landing Page Style)
  const heroOpacity = useTransform(scrollYProgress, [0, 0.1], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.1], [1, 0.95]);
  const dashboardScale = useTransform(scrollYProgress, [0.05, 0.25], [0.95, 1.05]);
  const dashboardY = useTransform(scrollYProgress, [0.05, 0.25], [60, -60]);

  // Floating Files Parallax (pops out after workflow section ~0.5)
  const file1Y = useTransform(scrollYProgress, [0.5, 0.8], [300, -200]);
  const file1X = useTransform(scrollYProgress, [0.5, 0.8], [-200, 100]);
  const file1Rotate = useTransform(scrollYProgress, [0.5, 0.8], [-45, 15]);
  const file1Opacity = useTransform(scrollYProgress, [0.5, 0.55, 0.75, 0.8], [0, 1, 1, 0]);

  const file2Y = useTransform(scrollYProgress, [0.55, 0.85], [400, -100]);
  const file2X = useTransform(scrollYProgress, [0.55, 0.85], [200, -50]);
  const file2Rotate = useTransform(scrollYProgress, [0.55, 0.85], [60, -25]);
  const file2Opacity = useTransform(scrollYProgress, [0.55, 0.6, 0.8, 0.85], [0, 1, 1, 0]);

  const file3Y = useTransform(scrollYProgress, [0.52, 0.82], [350, -150]);
  const file3X = useTransform(scrollYProgress, [0.52, 0.82], [-100, -150]);
  const file3Rotate = useTransform(scrollYProgress, [0.52, 0.82], [30, -35]);
  const file3Opacity = useTransform(scrollYProgress, [0.52, 0.57, 0.77, 0.82], [0, 1, 1, 0]);

  return (
    <div ref={containerRef} className="min-h-screen bg-transparent flex flex-col font-sans overflow-hidden relative">
      
      {/* Background Soft Abstract Glass/Gradient */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden" style={{ perspective: 1200 }}>
        <motion.div 
          style={{ y: yBg }}
          className="absolute -top-[20%] -left-[10%] w-[70%] h-[70%] rounded-full bg-gradient-to-br from-[#F6E7E0]/40 to-transparent blur-3xl opacity-80"
        />
        <motion.div 
          style={{ y: useTransform(scrollYProgress, [0, 1], ["0%", "-30%"]) }}
          className="absolute top-[40%] -right-[20%] w-[60%] h-[60%] rounded-full bg-gradient-to-bl from-[#E8B49F]/20 to-transparent blur-3xl opacity-70"
        />
        
        {/* 3D Sculpture Background */}
        <motion.div
          initial={{ opacity: 0, filter: "blur(10px)" }}
          animate={{ opacity: 0.4, filter: "blur(0px)" }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          className="fixed inset-0 w-full h-[100vh] z-[-1] pointer-events-none mix-blend-multiply flex items-center justify-center"
        >
          <img src="/justice-realistic.jpg" alt="Justice Sculpture" className="w-full h-full object-cover md:object-contain opacity-60 filter blur-[1px] saturate-0" />
        </motion.div>
        {/* Floating Parallax Files (Stacks) */}
        {/* Left Stack */}
        <motion.div 
          style={{ y: file1Y, x: file1X, rotate: file1Rotate, opacity: file1Opacity }} 
          className="fixed left-[5%] top-[50%] w-48 h-64 z-[5] pointer-events-none"
        >
          <div className="absolute inset-0 bg-white rounded-xl shadow-[0_10px_20px_-5px_rgba(0,0,0,0.1)] border border-[#E4E1DC] rotate-[-10deg] origin-bottom-left" />
          <div className="absolute inset-0 bg-[#FCFBF8] rounded-xl shadow-[0_10px_20px_-5px_rgba(0,0,0,0.1)] border border-[#E4E1DC] rotate-[-5deg] origin-bottom-left" />
          <div className="absolute inset-0 bg-white rounded-xl shadow-[0_20px_40px_-10px_rgba(0,0,0,0.15)] border border-[#E4E1DC] p-5 flex flex-col gap-4">
            <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center mb-2"><FileText className="text-blue-600 w-6 h-6"/></div>
            <div className="w-full h-3 bg-gray-100 rounded" />
            <div className="w-3/4 h-3 bg-gray-100 rounded" />
            <div className="w-1/2 h-3 bg-gray-100 rounded" />
            <div className="w-full h-3 bg-gray-50 rounded mt-auto" />
            <div className="w-full h-3 bg-gray-50 rounded" />
          </div>
        </motion.div>

        {/* Right Stack */}
        <motion.div 
          style={{ y: file2Y, x: file2X, rotate: file2Rotate, opacity: file2Opacity }} 
          className="fixed right-[5%] top-[35%] w-56 h-72 z-[5] pointer-events-none"
        >
          <div className="absolute inset-0 bg-white rounded-xl shadow-[0_10px_20px_-5px_rgba(0,0,0,0.1)] border border-[#E4E1DC] rotate-[12deg] origin-bottom-right" />
          <div className="absolute inset-0 bg-[#FCFBF8] rounded-xl shadow-[0_10px_20px_-5px_rgba(0,0,0,0.1)] border border-[#E4E1DC] rotate-[6deg] origin-bottom-right" />
          <div className="absolute inset-0 bg-white rounded-xl shadow-[0_20px_40px_-10px_rgba(0,0,0,0.15)] border border-[#E4E1DC] p-5 flex flex-col gap-4">
            <div className="w-12 h-12 bg-emerald-50 rounded-xl flex items-center justify-center mb-2"><ShieldCheck className="text-emerald-600 w-6 h-6"/></div>
            <div className="w-full h-3 bg-gray-100 rounded" />
            <div className="w-5/6 h-3 bg-gray-100 rounded" />
            <div className="w-4/5 h-3 bg-gray-100 rounded" />
            <div className="w-full h-3 bg-gray-50 rounded mt-auto" />
            <div className="w-4/5 h-3 bg-gray-50 rounded" />
          </div>
        </motion.div>

        {/* Center-Left Stack */}
        <motion.div 
          style={{ y: file3Y, x: file3X, rotate: file3Rotate, opacity: file3Opacity }} 
          className="fixed left-[30%] top-[40%] w-52 h-64 z-[5] pointer-events-none"
        >
          <div className="absolute inset-0 bg-white rounded-xl shadow-[0_10px_20px_-5px_rgba(0,0,0,0.1)] border border-[#E4E1DC] rotate-[-12deg] origin-top-right" />
          <div className="absolute inset-0 bg-white rounded-xl shadow-[0_20px_40px_-10px_rgba(0,0,0,0.15)] border border-[#E4E1DC] p-5 flex flex-col gap-4">
            <div className="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center mb-2"><Briefcase className="text-purple-600 w-6 h-6"/></div>
            <div className="w-full h-3 bg-gray-100 rounded" />
            <div className="w-2/3 h-3 bg-gray-100 rounded" />
            <div className="w-full h-3 bg-gray-100 rounded" />
          </div>
        </motion.div>
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-[#E4E1DC]/50 bg-white/70 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#B85C3A] to-[#8E432B] flex items-center justify-center shadow-md">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-xl tracking-tight text-[#1F2428]">CounselConnect</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/login" className="text-sm font-medium text-[#667085] hover:text-[#1F2428] transition-colors">
              Sign In
            </Link>
            <Link href="/register" className="inline-flex items-center justify-center px-6 py-2.5 bg-[#B85C3A] hover:bg-[#8E432B] text-white rounded-md text-sm font-medium transition-colors shadow-sm">
              Register
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1 relative z-10">
        
        {/* Section 1: Hero */}
        <section className="pt-32 pb-48 px-6 relative">
          <div className="max-w-7xl mx-auto text-center">
            <motion.div style={{ opacity: heroOpacity, scale: heroScale }} initial="hidden" animate="visible" variants={staggerContainer} className="max-w-3xl mx-auto origin-top">
              <motion.div variants={fadeInUp} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#F6E7E0] text-[#8E432B] text-xs font-semibold uppercase tracking-wider mb-8">
                <Shield className="w-3.5 h-3.5" />
                <span>Authorized Judicial Platform</span>
              </motion.div>
              <motion.h1 variants={fadeInUp} className="text-5xl md:text-6xl font-semibold text-[#1F2428] leading-[1.1] mb-8 tracking-tight">
                The Operating System for <br/><span className="text-[#B85C3A]">Legal Case Management</span>
              </motion.h1>
              <motion.p variants={fadeInUp} className="text-lg text-[#667085] leading-relaxed mb-10 max-w-2xl mx-auto">
                A highly secure, AI-assisted platform establishing a continuous digital lifecycle for cases. Connecting Police, Lawyers, and Court Authorities through one unified workflow.
              </motion.p>
              <motion.div variants={fadeInUp} className="flex flex-wrap items-center justify-center gap-4">
                <Link href="/login" className="inline-flex items-center justify-center px-8 py-4 bg-[#1F2428] hover:bg-black text-white rounded-md text-base font-medium transition-colors shadow-lg hover:shadow-xl">
                  Sign In to Workspace
                </Link>
                <Link href="/register" className="inline-flex items-center justify-center px-8 py-4 bg-[#B85C3A] hover:bg-[#8E432B] text-white rounded-md text-base font-medium transition-colors shadow-lg hover:shadow-xl">
                  Register Role
                </Link>
                <Link href="#workflow" className="inline-flex items-center justify-center px-8 py-4 bg-white border border-[#E4E1DC] text-[#1F2428] hover:bg-gray-50 rounded-md text-base font-medium transition-colors shadow-sm">
                  Explore Workflow
                </Link>
              </motion.div>
            </motion.div>

            {/* Hero Dashboard Preview (Glassmorphism) */}
            <motion.div 
              style={{ scale: dashboardScale, y: dashboardY }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.4, ease: 'easeOut' }}
              className="mt-10 max-w-5xl mx-auto origin-top"
            >
              <div className="relative rounded-2xl border border-white/40 bg-white/40 backdrop-blur-xl p-4 shadow-2xl ring-1 ring-black/5">
                <div className="rounded-xl border border-[#E4E1DC] bg-[#FCFBF8] overflow-hidden flex">
                  {/* Fake Sidebar */}
                  <div className="w-64 border-r border-[#E4E1DC] bg-white p-6 hidden md:block text-left">
                    <div className="flex items-center gap-2 mb-10">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#B85C3A] to-[#8E432B] flex items-center justify-center shadow-sm">
                        <Scale className="w-4 h-4 text-white" />
                      </div>
                      <span className="font-semibold text-sm text-[#1F2428]">CounselConnect</span>
                    </div>
                    <div className="space-y-2">
                      <div className="w-full h-9 bg-[#F6E7E0] rounded flex items-center px-3 gap-3">
                        <LayoutDashboard className="w-4 h-4 text-[#8E432B]" />
                        <span className="text-sm font-medium text-[#8E432B]">Dashboard</span>
                      </div>
                      <div className="w-full h-9 hover:bg-gray-50 rounded flex items-center px-3 gap-3">
                        <Briefcase className="w-4 h-4 text-[#667085]" />
                        <span className="text-sm font-medium text-[#667085]">My Cases</span>
                      </div>
                      <div className="w-full h-9 hover:bg-gray-50 rounded flex items-center px-3 gap-3">
                        <FileText className="w-4 h-4 text-[#667085]" />
                        <span className="text-sm font-medium text-[#667085]">Documents</span>
                      </div>
                    </div>
                  </div>
                  {/* Fake Content */}
                  <div className="flex-1 p-8 text-left bg-[#FCFBF8]">
                    <div className="flex justify-between items-center mb-8">
                      <div>
                        <h2 className="text-xl font-semibold text-[#1F2428]">Overview</h2>
                        <p className="text-sm text-[#667085]">Welcome back, Counsel.</p>
                      </div>
                      <div className="flex gap-2">
                        <div className="h-9 w-64 bg-white border border-[#E4E1DC] rounded-md flex items-center px-3 shadow-sm">
                          <span className="text-xs text-gray-400">Search active cases...</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-6 mb-8">
                      <div className="bg-white border border-[#E4E1DC] rounded-xl p-5 shadow-sm">
                        <div className="flex justify-between items-start mb-4">
                          <div className="w-10 h-10 bg-[#F6E7E0] rounded-lg flex items-center justify-center">
                            <Briefcase className="w-5 h-5 text-[#8E432B]" />
                          </div>
                          <span className="text-[10px] font-semibold text-green-700 bg-green-50 px-2 py-1 rounded border border-green-100">+2 Active</span>
                        </div>
                        <div className="text-sm text-[#667085] mb-1">Total Cases</div>
                        <div className="text-2xl font-semibold text-[#1F2428]">124</div>
                      </div>
                      <div className="bg-white border border-[#E4E1DC] rounded-xl p-5 shadow-sm">
                        <div className="flex justify-between items-start mb-4">
                          <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                            <Gavel className="w-5 h-5 text-blue-600" />
                          </div>
                          <span className="text-[10px] font-semibold text-orange-700 bg-orange-50 px-2 py-1 rounded border border-orange-100">This Week</span>
                        </div>
                        <div className="text-sm text-[#667085] mb-1">Upcoming Hearings</div>
                        <div className="text-2xl font-semibold text-[#1F2428]">8</div>
                      </div>
                      <div className="bg-white border border-[#E4E1DC] rounded-xl p-5 shadow-sm">
                        <div className="flex justify-between items-start mb-4">
                          <div className="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center">
                            <CheckCircle2 className="w-5 h-5 text-purple-600" />
                          </div>
                        </div>
                        <div className="text-sm text-[#667085] mb-1">Resolved (YTD)</div>
                        <div className="text-2xl font-semibold text-[#1F2428]">47</div>
                      </div>
                    </div>

                    <div className="bg-white border border-[#E4E1DC] rounded-xl overflow-hidden shadow-sm">
                      <div className="border-b border-[#E4E1DC] p-4 bg-gray-50/50">
                        <h3 className="text-sm font-semibold text-[#1F2428]">Recent Activity</h3>
                      </div>
                      <div className="p-4 space-y-4">
                        {[1, 2, 3].map(i => (
                          <div key={i} className="flex items-center gap-4 p-2">
                            <div className="w-2 h-2 rounded-full bg-[#B85C3A]" />
                            <div className="flex-1">
                              <div className="text-sm font-medium text-[#1F2428]">Motion filed in State v. Johnson</div>
                              <div className="text-xs text-[#667085]">2 hours ago</div>
                            </div>
                            <div className="text-[10px] font-medium px-2 py-1 bg-gray-100 rounded text-gray-600 border border-gray-200">Document</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Section 2: Why This Platform */}
        <section className="pt-48 pb-24 px-6 bg-white/60 backdrop-blur-md border-y border-[#E4E1DC]/50">
          <div className="max-w-7xl mx-auto">
            <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }} variants={fadeInUp} className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl font-semibold text-[#1F2428] mb-6">The End of Fragmented Workflows</h2>
              <p className="text-[#667085] text-lg leading-relaxed mb-6">
                Historically, legal workflows have suffered from manual document handling, lack of continuous case visibility, and poor coordination between actors.
              </p>
              <p className="text-[#1F2428] text-lg font-medium leading-relaxed">
                CounselConnect unifies this. One continuous CSR lifecycle. A deeply connected workflow between Police, Lawyers, and Court Authorities. AI-assisted, but strictly human-controlled.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Section 3: Platform Modules */}
        <section className="py-24 px-6 relative">
          <div className="max-w-7xl mx-auto">
            <div className="mb-16 text-center">
              <h2 className="text-3xl font-semibold text-[#1F2428] mb-4">Core Platform Modules</h2>
              <p className="text-[#667085] text-lg">Specialized toolsets designed for precise judicial needs.</p>
            </div>
            
            <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={staggerContainer} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                { icon: Shield, color: 'text-blue-600', bg: 'bg-blue-50', title: 'Case Creation & FIR Intake', desc: 'Securely register new cases, upload FIR documents, manage party details, and generate foundational CSR tracking.' },
                { icon: FileText, color: 'text-blue-600', bg: 'bg-blue-50', title: 'Investigation & Evidence', desc: 'Chronological investigation diaries, categorized evidence management, and document cataloging for active case building.' },
                { icon: Briefcase, color: 'text-[#B85C3A]', bg: 'bg-[#F6E7E0]', title: 'Lawyer Workspace', desc: 'Assigned case dashboards, hearing schedules, NFC access, attendance reporting, and absence submission.' },
                { icon: Gavel, color: 'text-emerald-600', bg: 'bg-emerald-50', title: 'Court Authority Workspace', desc: 'Agenda management, absence review, AI schedule recommendations, proceedings logging, and judgment finalization.' },
                { icon: Bot, color: 'text-purple-600', bg: 'bg-purple-50', title: 'Document Intelligence', desc: 'Automated OCR, structured data extraction from unstructured FIRs, and semantic searching.' },
                { icon: ShieldCheck, color: 'text-slate-600', bg: 'bg-slate-100', title: 'Secure Access & Audit', desc: 'Role-based access, cryptographic SHA-256 document hashing, and immutable action histories.' }
              ].map((item, i) => (
                <motion.div key={i} variants={fadeInUp} className="p-8 rounded-2xl bg-white/60 backdrop-blur-md border border-[#E4E1DC]/50 hover:shadow-md transition-shadow relative overflow-hidden group">
                  <div className={`w-12 h-12 rounded-xl ${item.bg} ${item.color} flex items-center justify-center mb-6`}>
                    <item.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-semibold text-[#1F2428] mb-4">{item.title}</h3>
                  <p className="text-[#667085] leading-relaxed relative z-10">{item.desc}</p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Section 4: Workflow Visualization */}
        <section id="workflow" className="py-24 px-6 bg-[#FCFBF8]/60 backdrop-blur-md border-y border-[#E4E1DC]/50">
          <div className="max-w-7xl mx-auto">
            <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="text-center mb-16">
              <h2 className="text-3xl font-semibold text-[#1F2428] mb-4">The Continuous Digital Journey</h2>
              <p className="text-[#667085] text-lg">A single, immutable line of truth from incident to judgment.</p>
            </motion.div>
            
            <div className="relative max-w-4xl mx-auto">
              <div className="absolute left-[27px] md:left-1/2 top-4 bottom-4 w-1 bg-[#E4E1DC] md:-translate-x-1/2" />
              
              {[
                { title: 'Case Creation', role: 'Police' },
                { title: 'FIR Upload', role: 'Police' },
                { title: 'OCR / AI Extraction', role: 'System' },
                { title: 'Human Verification', role: 'Police' },
                { title: 'Evidence & Documents', role: 'Police' },
                { title: 'Lawyer Assignment', role: 'Court' },
                { title: 'Hearing Management', role: 'System' },
                { title: 'Attendance / Absence', role: 'Lawyer' },
                { title: 'Court Review', role: 'Court' },
                { title: 'Scheduling Recommendation', role: 'System' },
                { title: 'Judgment', role: 'Court' },
                { title: 'Audit Trail Finalized', role: 'System' },
              ].map((step, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ delay: i * 0.1 }}
                  className={`relative flex items-center gap-8 mb-8 ${i % 2 === 0 ? 'md:flex-row-reverse' : ''}`}
                >
                  <div className={`hidden md:block w-1/2 ${i % 2 === 0 ? 'text-left' : 'text-right'}`}>
                    <span className="text-sm font-bold text-[#B85C3A] uppercase tracking-wider">{step.role}</span>
                  </div>
                  <div className="w-14 h-14 rounded-full bg-white/80 backdrop-blur-md border-4 border-[#B85C3A] flex items-center justify-center font-bold text-[#B85C3A] shadow-md relative z-10 shrink-0">
                    {i + 1}
                  </div>
                  <div className="w-full md:w-1/2">
                    <div className="bg-white/60 backdrop-blur-md p-6 rounded-xl border border-[#E4E1DC]/50 shadow-sm">
                      <span className="md:hidden text-xs font-bold text-[#B85C3A] uppercase tracking-wider mb-2 block">{step.role}</span>
                      <h4 className="text-lg font-semibold text-[#1F2428]">{step.title}</h4>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Section 5: AI Capabilities */}
        <section className="py-24 px-6 bg-white/60 backdrop-blur-md text-[#1F2428]">
          <div className="max-w-7xl mx-auto">
            <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeInUp} className="text-center max-w-3xl mx-auto mb-16">
              <Bot className="w-12 h-12 text-[#B85C3A] mx-auto mb-6" />
              <h2 className="text-3xl font-semibold mb-6">Intelligence that Assists. Humans that Decide.</h2>
              <p className="text-[#667085] text-lg leading-relaxed mb-8">
                CounselConnect uses local, privacy-preserving AI to accelerate bureaucratic tasks.
              </p>
            </motion.div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
              <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="space-y-6">
                <div className="flex items-center gap-3 border-b border-[#E4E1DC]/50 pb-4 mb-6">
                  <CheckCircle2 className="w-6 h-6 text-emerald-600" />
                  <h3 className="text-2xl font-semibold">What AI Does</h3>
                </div>
                {[
                  'OCR & Document Parsing',
                  'Data Extraction',
                  'Case Summaries',
                  'Categorization & Semantic Similarity',
                  'Explainable Prioritization',
                  'Speech-to-Text Transcription',
                  'Schedule Recommendations (OR-Tools)'
                ].map((item, i) => (
                  <motion.div key={i} variants={fadeInUp} className="flex items-center gap-3 text-[#667085]">
                    <div className="w-2 h-2 rounded-full bg-emerald-500" /> {item}
                  </motion.div>
                ))}
              </motion.div>

              <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="space-y-6">
                <div className="flex items-center gap-3 border-b border-[#E4E1DC]/50 pb-4 mb-6">
                  <XCircle className="w-6 h-6 text-red-600" />
                  <h3 className="text-2xl font-semibold">What AI Does NOT Do</h3>
                </div>
                {[
                  'No independent approvals',
                  'No judicial judgments',
                  'No final legal decisions',
                  'No unverified database modifications'
                ].map((item, i) => (
                  <motion.div key={i} variants={fadeInUp} className="flex items-center gap-3 text-[#667085]">
                    <div className="w-2 h-2 rounded-full bg-red-500" /> {item}
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </div>
        </section>

        {/* Section 6: Secure Access */}
        <section className="py-24 px-6 bg-white/60 backdrop-blur-md border-b border-[#E4E1DC]/50">
          <div className="max-w-7xl mx-auto text-center">
            <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeInUp} className="mb-16">
              <h2 className="text-3xl font-semibold text-[#1F2428] mb-6">Ironclad Access & Integrity</h2>
              <p className="text-[#667085] text-lg max-w-2xl mx-auto">
                Built to handle highly sensitive legal documentation with zero-trust principles.
              </p>
            </motion.div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 text-left">
              {[
                { icon: Fingerprint, title: 'Role-Based Logins', desc: 'Distinct flows for Police, Lawyers, and Court Authorities.' },
                { icon: Lock, title: 'Hardware Security', desc: 'NFC and Passkey (WebAuthn) support for rapid, secure lawyer access.' },
                { icon: ShieldCheck, title: 'Document Integrity', desc: 'Mandatory SHA-256 cryptographic hashing for every uploaded file.' },
                { icon: Network, title: 'Append-Only Audit', desc: 'Every action is logged immutably, ensuring full systemic accountability.' }
              ].map((item, i) => (
                <motion.div key={i} initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeInUp} transition={{ delay: i * 0.1 }} className="p-6 rounded-xl bg-[#FCFBF8]/60 backdrop-blur-md border border-[#E4E1DC]/50">
                  <item.icon className="w-8 h-8 text-[#B85C3A] mb-4" />
                  <h4 className="font-semibold text-[#1F2428] mb-2">{item.title}</h4>
                  <p className="text-[#667085] text-sm">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Section 7: Final CTA */}
        <section className="py-32 px-6 bg-[#FCFBF8]/60 backdrop-blur-md relative overflow-hidden">
          <div className="absolute inset-0 opacity-20 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at center, #B85C3A 1px, transparent 1px)', backgroundSize: '24px 24px' }} />
          <div className="max-w-3xl mx-auto text-center relative z-10">
            <h2 className="text-4xl font-semibold text-[#1F2428] mb-6">Access Your Secure Workspace</h2>
            <p className="text-[#667085] text-lg mb-10">
              Log in with your authorized credentials to access your designated dashboard.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link href="/login" className="inline-flex items-center justify-center px-8 py-4 bg-[#B85C3A] hover:bg-[#8E432B] text-white rounded-md text-base font-medium transition-colors shadow-lg hover:shadow-xl">
                Sign In Now <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link href="/register" className="inline-flex items-center justify-center px-8 py-4 bg-white border border-[#E4E1DC] text-[#1F2428] hover:bg-gray-50 rounded-md text-base font-medium transition-colors shadow-sm">
                Register New Role
              </Link>
            </div>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="py-8 text-center text-sm text-[#667085] bg-white/60 backdrop-blur-md border-t border-[#E4E1DC]/50 relative z-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} CounselConnect Judicial System. Authorized Personnel Only.</p>
          <div className="flex gap-6">
            <Link href="/terms" className="hover:text-[#1F2428]">Terms</Link>
            <Link href="/privacy" className="hover:text-[#1F2428]">Privacy</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
