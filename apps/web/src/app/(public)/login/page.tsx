'use client';

import { useState, useEffect, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiClient, ApiError } from '@/lib/api-client';

type Role = 'POLICE' | 'LAWYER' | 'COURT_AUTHORITY';

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<Role>('POLICE');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('expired') === 'true') {
        setError('Your session has expired due to inactivity. Please log in again.');
      }
    }
  }, []);

  const getIdentifierLabel = () => {
    switch (role) {
      case 'POLICE': return 'Police Station Code';
      case 'LAWYER': return 'Bar Registration ID';
      case 'COURT_AUTHORITY': return 'JO Code';
    }
  };

  const getIdentifierPlaceholder = () => {
    switch (role) {
      case 'POLICE': return 'e.g., PS001';
      case 'LAWYER': return 'e.g., BAR/2024/001';
      case 'COURT_AUTHORITY': return 'e.g., JO-2024-001';
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!identifier.trim() || !password.trim()) {
      setError('Please fill in all fields.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await apiClient.post('/api/auth/login', { role, identifier: identifier.trim(), password });
      router.push('/dashboard');
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center',
      backgroundColor: '#F7F6F3', padding: '16px', fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      <div style={{ width: '100%', maxWidth: '420px' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div style={{
            width: '48px', height: '48px', borderRadius: '12px', 
            background: 'linear-gradient(135deg, #B85C3A 0%, #8E432B 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>
            </svg>
          </div>
          <h1 style={{ fontSize: '20px', fontWeight: 600, color: '#1F2428', margin: 0 }}>Counsel Connect</h1>
          <p style={{ fontSize: '14px', color: '#667085', marginTop: '4px' }}>
            Secure access for authorized Police, Lawyers and Court Authorities.
          </p>
        </div>

        {/* Form Card */}
        <div style={{
          backgroundColor: '#fff', borderRadius: '8px', padding: '24px',
          border: '1px solid #E4E1DC', boxShadow: '0 1px 3px rgba(0,0,0,0.06)'
        }}>
          {error && (
            <div style={{
              marginBottom: '16px', padding: '12px 16px', borderRadius: '8px',
              backgroundColor: '#fef2f2', border: '1px solid #fecaca', fontSize: '14px', color: '#b91c1c'
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Role */}
            <div>
              <label htmlFor="role" style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#1F2428', marginBottom: '4px' }}>
                Role
              </label>
              <select
                id="role"
                value={role}
                onChange={(e) => { setRole(e.target.value as Role); setIdentifier(''); setPassword(''); setError(''); }}
                style={{
                  width: '100%', padding: '8px 12px', borderRadius: '8px', fontSize: '14px',
                  border: '1px solid #E4E1DC', backgroundColor: '#fff', outline: 'none'
                }}
              >
                <option value="POLICE">Police</option>
                <option value="LAWYER">Lawyer</option>
                <option value="COURT_AUTHORITY">Court Authority</option>
              </select>
            </div>

            {/* Identifier */}
            <div>
              <label htmlFor="identifier" style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#1F2428', marginBottom: '4px' }}>
                {getIdentifierLabel()}
              </label>
              <input
                id="identifier"
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder={getIdentifierPlaceholder()}
                style={{
                  width: '100%', padding: '8px 12px', borderRadius: '8px', fontSize: '14px',
                  border: '1px solid #E4E1DC', backgroundColor: '#fff', outline: 'none', boxSizing: 'border-box'
                }}
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#1F2428', marginBottom: '4px' }}>
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  width: '100%', padding: '8px 12px', borderRadius: '8px', fontSize: '14px',
                  border: '1px solid #E4E1DC', backgroundColor: '#fff', outline: 'none', boxSizing: 'border-box'
                }}
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%', padding: '10px 16px', borderRadius: '8px', fontSize: '14px', fontWeight: 500,
                backgroundColor: loading ? '#d4956e' : '#B85C3A', color: '#fff', border: 'none', cursor: loading ? 'not-allowed' : 'pointer',
                marginTop: '8px', transition: 'background-color 0.2s'
              }}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>

        <p style={{ textAlign: 'center', fontSize: '14px', color: '#667085', marginTop: '16px' }}>
          Need an account?{' '}
          <Link href="/register" style={{ color: '#B85C3A', fontWeight: 500, textDecoration: 'none' }}>
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
