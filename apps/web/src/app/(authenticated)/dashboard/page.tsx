'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    async function redirectBasedOnRole() {
      try {
        const data = await apiClient.get<any>('/api/auth/me');
        if (data.role === 'POLICE') {
          router.replace('/police/firs');
        } else if (data.role === 'LAWYER') {
          router.replace('/lawyer/cases');
        } else if (data.role === 'COURT_AUTHORITY') {
          router.replace('/court/today');
        }
      } catch (err) {
        // Ignored
      }
    }
    redirectBasedOnRole();
  }, [router]);

  return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', backgroundColor: '#F7F6F3' }}>
      <p style={{ color: '#667085' }}>Loading dashboard...</p>
    </div>
  );
}
