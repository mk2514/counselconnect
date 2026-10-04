'use client';

import { Bell, User, LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';

/**
 * Reusable top header component.
 *
 * Per project rules:
 * - Professional typography
 * - Strong information hierarchy
 * - Compact but readable layout
 * - Every control must have a label (accessibility)
 */

interface TopHeaderProps {
  /** Page title displayed in the header */
  title?: string;
  /** Current user's name */
  userName?: string;
}

export function TopHeader({ title, userName }: TopHeaderProps) {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await apiClient.post('/api/auth/logout', {});
    } catch (e) {
      // ignore
    } finally {
      router.push('/login');
    }
  };

  return (
    <header style={{ 
      display: 'flex', height: '56px', alignItems: 'center', justifyContent: 'space-between',
      borderBottom: '1px solid rgba(228, 225, 220, 0.5)', backgroundColor: 'transparent', padding: '0 24px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <a href="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
          <div style={{ 
            display: 'flex', height: '28px', width: '28px', alignItems: 'center', justifyContent: 'center', 
            borderRadius: '6px', background: 'linear-gradient(135deg, #B85C3A 0%, #8E432B 100%)', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)', flexShrink: 0 
          }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>
            </svg>
          </div>
          <span style={{ fontSize: '15px', fontWeight: 600, color: '#1F2428', whiteSpace: 'nowrap' }}>CounselConnect</span>
        </a>
        
        {title && (
          <>
            <div style={{ height: '20px', width: '1px', backgroundColor: '#E4E1DC' }} />
            <h1 style={{ fontSize: '14px', fontWeight: 600, color: '#667085', margin: 0 }}>{title}</h1>
          </>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ display: 'flex', height: '28px', width: '28px', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', backgroundColor: '#F6E7E0', fontSize: '14px' }}>
            👤
          </div>
          {userName && <span style={{ fontSize: '13px', fontWeight: 500, color: '#1F2428' }}>{userName}</span>}
        </div>

        <div style={{ height: '24px', width: '1px', backgroundColor: '#E4E1DC' }} />

        <button
          onClick={handleLogout}
          style={{
            display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', borderRadius: '6px',
            color: '#dc2626', backgroundColor: 'transparent', border: 'none', cursor: 'pointer',
            fontSize: '13px', fontWeight: 500
          }}
        >
          Logout
        </button>
      </div>
    </header>
  );
}
