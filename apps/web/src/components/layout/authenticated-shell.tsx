'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { PageShell } from './page-shell';
import { Shield, Briefcase, Landmark, LayoutDashboard, FileText, Gavel, FileClock, FilePlus2, Search, FolderOpen, ShieldAlert, Users, Activity, QrCode, History } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { LoadingState } from '../ui/feedback';

type Role = 'POLICE' | 'LAWYER' | 'COURT_AUTHORITY';

interface UserProfile {
  id: string;
  role: Role;
  name: string;
}

export function AuthenticatedShell({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    async function loadUser() {
      try {
        const data = await apiClient.get<any>('/api/auth/me');
        setUser({
          id: data.id,
          role: data.role,
          name: data.display_name || 'User',
        });
      } catch (err) {
        // If 401, we MUST hit logout first to clear the HttpOnly cookie, 
        // otherwise middleware will bounce us right back to dashboard!
        try {
          await apiClient.post('/api/auth/logout', {});
        } catch (e) {
          // ignore
        }
        router.push('/login');
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, [router]);

  // Session timeout for inactivity (15 minutes)
  useEffect(() => {
    if (!user) return; // Only track if logged in

    let timeoutId: NodeJS.Timeout;
    
    const logoutDueToInactivity = async () => {
      try {
        await apiClient.post('/api/auth/logout', {});
      } catch (e) {}
      // Redirect to login with a query parameter so we can show 'Session Expired' message
      router.push('/login?expired=true');
    };

    const resetTimer = () => {
      clearTimeout(timeoutId);
      // 15 minutes = 15 * 60 * 1000 ms
      timeoutId = setTimeout(logoutDueToInactivity, 15 * 60 * 1000);
    };

    resetTimer();

    const events = ['mousemove', 'keydown', 'mousedown', 'touchstart', 'scroll'];
    events.forEach(event => window.addEventListener(event, resetTimer));

    return () => {
      clearTimeout(timeoutId);
      events.forEach(event => window.removeEventListener(event, resetTimer));
    };
  }, [user, router]);

  if (loading) {
    return (
      <div style={{ display: 'flex', height: '100vh', width: '100%', alignItems: 'center', justifyContent: 'center', backgroundColor: '#F7F6F3' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '32px', height: '32px', border: '3px solid #B85C3A', borderBottomColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
          <p style={{ fontSize: '14px', color: '#667085' }}>Loading your workspace...</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  // Build role-specific navigation
  const navItems = [
    { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  ];

  if (user.role === 'POLICE') {
    navItems.push(
      { label: 'Create Case', href: '/police/firs/new', icon: FilePlus2 },
      { label: 'My Cases', href: '/police/firs', icon: FileText },
      { label: 'Investigation', href: '/police/investigations', icon: Search },
      { label: 'Documents', href: '/police/documents', icon: FolderOpen },
      { label: 'Evidence', href: '/police/evidence', icon: ShieldAlert },
      { label: 'Assigned Lawyers', href: '/police/lawyers', icon: Users },
      { label: 'Case Status', href: '/police/status', icon: Activity },
      { label: 'QR Cases', href: '/police/qr', icon: QrCode },
      { label: 'Audit', href: '/police/audit', icon: History }
    );
  } else if (user.role === 'LAWYER') {
    navItems.push(
      { label: 'My Cases', href: '/lawyer/cases', icon: Briefcase },
      { label: 'Hearings', href: '/lawyer/hearings', icon: FileClock },
      { label: 'Court Agenda', href: '/lawyer/agenda', icon: Gavel },
      { label: 'Documents', href: '/lawyer/documents', icon: FolderOpen },
      { label: 'Submissions', href: '/lawyer/submissions', icon: FilePlus2 },
      { label: 'Attendance', href: '/lawyer/attendance', icon: Users },
      { label: 'Requests', href: '/lawyer/requests', icon: ShieldAlert },
      { label: 'NFC Access', href: '/lawyer/nfc', icon: QrCode },
      { label: 'Activity', href: '/lawyer/activity', icon: Activity }
    );
  } else if (user.role === 'COURT_AUTHORITY') {
    navItems.push(
      { label: "Today's Cases", href: '/court/today', icon: FileClock },
      { label: 'Categorization', href: '/court/categorization', icon: FileText },
      { label: 'Prioritization', href: '/court/prioritization', icon: Activity },
      { label: 'Court Agenda', href: '/court/agenda', icon: Gavel },
      { label: 'Lawyer Assignments', href: '/court/lawyers', icon: Users },
      { label: 'Absence Requests', href: '/court/absence-requests', icon: FileClock },
      { label: 'Rep Requests', href: '/court/rep-requests', icon: Users },
      { label: 'Withdrawal Requests', href: '/court/withdrawals', icon: ShieldAlert },
      { label: 'Compliance Alerts', href: '/court/compliance', icon: ShieldAlert },
      { label: 'Proceedings', href: '/court/proceedings', icon: FolderOpen },
      { label: 'Judgments', href: '/court/judgments', icon: Landmark },
      { label: 'Audit Logs', href: '/court/audit', icon: History }
    );
  }

  const pageTitle = pathname.split('/').pop()?.replace('-', ' ') || 'Dashboard';
  const capitalizedTitle = pageTitle.charAt(0).toUpperCase() + pageTitle.slice(1);

  return (
    <PageShell navItems={navItems} title={capitalizedTitle} userName={user.name}>
      {children}
    </PageShell>
  );
}
