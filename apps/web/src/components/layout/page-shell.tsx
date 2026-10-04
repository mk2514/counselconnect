'use client';

import { Sidebar, type NavItem } from './sidebar';
import { TopHeader } from './top-header';
import type { ReactNode } from 'react';

/**
 * Reusable page shell.
 *
 * Combines the sidebar, top header, and main content area
 * into the standard authenticated page layout.
 *
 * Per project rules:
 * - Desktop/laptop primary target
 * - Compact but readable layout
 * - Light theme with warm white backgrounds
 */

interface PageShellProps {
  children: ReactNode;
  /** Override the default navigation items (role-specific) */
  navItems?: NavItem[];
  /** Page title for the header */
  title?: string;
  /** User name for display */
  userName?: string;
}

export function PageShell({ children, navItems, title, userName }: PageShellProps) {
  return (
    <div style={{ 
      display: 'flex', height: '100vh', overflow: 'hidden', 
      backgroundColor: '#C88360',
      backgroundImage: 'radial-gradient(circle at top right, #E4A685, #A86749)',
      fontFamily: 'Inter, system-ui, sans-serif',
      padding: '20px'
    }}>
      <div style={{
        display: 'flex', 
        flex: 1, 
        backgroundColor: 'rgba(253, 252, 251, 0.90)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderRadius: '20px',
        border: '1px solid rgba(255, 255, 255, 0.5)',
        boxShadow: '0 30px 60px -15px rgba(0, 0, 0, 0.3)',
        overflow: 'hidden'
      }}>
        <Sidebar navItems={navItems} />

        <div style={{ display: 'flex', flex: 1, flexDirection: 'column', overflow: 'hidden' }}>
          <TopHeader title={title} userName={userName} />

          <main style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
