'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Scale,
  LayoutDashboard,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

/**
 * Reusable sidebar component.
 *
 * Per project rules:
 * - Light or white sidebar (bg: #FCFBF8)
 * - Professional iconography from one consistent library (Lucide)
 * - Keyboard navigation must function
 * - Strong information hierarchy
 */

export interface NavItem {
  label: string;
  href: string;
  icon: any;
}

interface SidebarProps {
  navItems?: NavItem[];
}

const defaultNavItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: null },
];

export function Sidebar({ navItems = defaultNavItems }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <aside style={{
      display: 'flex', flexDirection: 'column', height: '100%',
      width: collapsed ? '64px' : '240px', transition: 'width 0.2s',
      borderRight: '1px solid rgba(228, 225, 220, 0.5)', backgroundColor: 'transparent',
      flexShrink: 0
    }}>
      <div style={{ display: 'flex', height: '56px', alignItems: 'center', borderBottom: '1px solid rgba(228, 225, 220, 0.5)', padding: '0 16px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
          <div style={{ 
            display: 'flex', height: '32px', width: '32px', alignItems: 'center', justifyContent: 'center', 
            borderRadius: '8px', background: 'linear-gradient(135deg, #B85C3A 0%, #8E432B 100%)', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)', flexShrink: 0 
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>
            </svg>
          </div>
          {!collapsed && <span style={{ fontSize: '14px', fontWeight: 600, color: '#1F2428', whiteSpace: 'nowrap' }}>Counsel Connect</span>}
        </Link>
      </div>

      <nav style={{ flex: 1, overflowY: 'auto', padding: '12px 8px' }}>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <li key={item.href}>
                <Link href={item.href} style={{
                  display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 12px',
                  textDecoration: 'none', fontSize: '14px', fontWeight: 500,
                  borderLeft: `4px solid ${isActive ? '#B85C3A' : 'transparent'}`,
                  backgroundColor: isActive ? 'rgba(246, 231, 224, 0.6)' : 'transparent',
                  color: isActive ? '#8E432B' : '#667085',
                  transition: 'all 0.15s'
                }}>
                  <div style={{ fontSize: '14px', flexShrink: 0, display: 'flex', justifyContent: 'center', width: '16px' }}>
                    {isActive ? '▸' : '▹'}
                  </div>
                  {!collapsed && <span style={{ whiteSpace: 'nowrap' }}>{item.label}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div style={{ borderTop: '1px solid rgba(228, 225, 220, 0.5)', padding: '8px' }}>
        <button onClick={() => setCollapsed(!collapsed)} style={{
          display: 'flex', width: '100%', alignItems: 'center', justifyContent: 'center',
          padding: '8px 12px', borderRadius: '8px', color: '#667085', backgroundColor: 'transparent',
          border: 'none', cursor: 'pointer', transition: 'background-color 0.2s', fontSize: '12px'
        }}>
          {collapsed ? '»' : '« Collapse'}
        </button>
      </div>
    </aside>
  );
}
