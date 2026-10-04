'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiClient, ApiError } from '@/lib/api-client';

type Role = 'police' | 'lawyer' | 'court_authority';
type Step = 'select_role' | 'register_form';

interface Court { id: string; name: string; type: string; }

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '8px 12px', borderRadius: '8px', fontSize: '14px',
  border: '1px solid #E4E1DC', backgroundColor: '#fff', outline: 'none', boxSizing: 'border-box'
};
const inputErrorStyle: React.CSSProperties = { ...inputStyle, border: '1px solid #f87171', backgroundColor: '#fef2f2' };
const labelStyle: React.CSSProperties = { display: 'block', fontSize: '14px', fontWeight: 500, color: '#1F2428', marginBottom: '4px' };
const cardStyle: React.CSSProperties = {
  backgroundColor: '#fff', borderRadius: '8px', padding: '24px',
  border: '1px solid #E4E1DC', boxShadow: '0 1px 3px rgba(0,0,0,0.06)'
};
const btnStyle: React.CSSProperties = {
  width: '100%', padding: '10px 16px', borderRadius: '8px', fontSize: '14px', fontWeight: 500,
  backgroundColor: '#B85C3A', color: '#fff', border: 'none', cursor: 'pointer', marginTop: '8px'
};

function Field({ id, label, type = 'text', value, onChange, error, placeholder, required }: {
  id: string; label: string; type?: string; value: string; onChange: (v: string) => void;
  error?: string; placeholder?: string; required?: boolean;
}) {
  return (
    <div style={{ marginBottom: '12px' }}>
      <label htmlFor={id} style={labelStyle}>
        {label} {required && <span style={{ color: '#ef4444' }}>*</span>}
      </label>
      <input id={id} type={type} value={value} onChange={e => onChange(e.target.value)}
        placeholder={placeholder} style={error ? inputErrorStyle : inputStyle} />
      {error && <p style={{ fontSize: '12px', color: '#dc2626', marginTop: '4px' }}>{error}</p>}
    </div>
  );
}

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('select_role');
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [serverError, setServerError] = useState('');
  const [courts, setCourts] = useState<Court[]>([]);
  const [loading, setLoading] = useState(false);

  // Form fields
  const [fields, setFields] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const setField = (k: string, v: string) => { setFields(p => ({ ...p, [k]: v })); setErrors(p => ({ ...p, [k]: '' })); };

  const handleRoleSelect = async (role: Role) => {
    setSelectedRole(role);
    setServerError('');
    setFields({});
    setErrors({});
    if (role === 'court_authority') {
      try {
        const data = await apiClient.get<Court[]>('/api/auth/courts');
        setCourts(data);
      } catch { setCourts([]); }
    }
    setStep('register_form');
  };

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) return 'Must be at least 8 characters.';
    if (!/[A-Z]/.test(pwd)) return 'Must contain an uppercase letter.';
    if (!/[a-z]/.test(pwd)) return 'Must contain a lowercase letter.';
    if (!/\d/.test(pwd)) return 'Must contain a digit.';
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd)) return 'Must contain a special character.';
    return null;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};

    // Validate based on role
    if (selectedRole === 'police') {
      if (!fields.station_code?.trim()) errs.station_code = 'Required';
      if (!fields.officer_name?.trim()) errs.officer_name = 'Required';
      if (!fields.station_name?.trim()) errs.station_name = 'Required';
    } else if (selectedRole === 'lawyer') {
      if (!fields.full_name?.trim()) errs.full_name = 'Required';
      if (!fields.bar_registration_id?.trim()) errs.bar_registration_id = 'Required';
      if (!fields.phone?.trim()) errs.phone = 'Required';
    } else if (selectedRole === 'court_authority') {
      if (!fields.full_name?.trim()) errs.full_name = 'Required';
      if (!fields.jo_code?.trim()) errs.jo_code = 'Required';
      if (!fields.court_id?.trim()) errs.court_id = 'Required';
    }

    if (!fields.password?.trim()) errs.password = 'Required';
    else {
      const pwdErr = validatePassword(fields.password);
      if (pwdErr) errs.password = pwdErr;
    }
    if (!fields.confirm_password?.trim()) errs.confirm_password = 'Required';
    else if (fields.password !== fields.confirm_password) errs.confirm_password = 'Passwords do not match.';

    if (Object.keys(errs).length > 0) { setErrors(errs); return; }

    setLoading(true);
    setServerError('');
    try {
      const endpoint = selectedRole === 'police' ? '/api/auth/register/police'
        : selectedRole === 'lawyer' ? '/api/auth/register/lawyer'
        : '/api/auth/register/court-authority';
      await apiClient.post(endpoint, fields);
      router.push('/dashboard');
    } catch (err) {
      if (err instanceof ApiError) setServerError(err.message);
      else setServerError('An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const roleCards = [
    { key: 'police' as Role, label: 'Police', desc: 'Law enforcement officers', icon: '🛡️' },
    { key: 'lawyer' as Role, label: 'Lawyer', desc: 'Legal practitioners', icon: '⚖️' },
    { key: 'court_authority' as Role, label: 'Court Authority', desc: 'Judicial officers', icon: '🏛️' },
  ];

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
          <p style={{ fontSize: '14px', color: '#667085', marginTop: '4px' }}>Judicial Case Management System</p>
        </div>

        <div style={cardStyle}>
          {step === 'select_role' && (
            <>
              <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#1F2428', marginBottom: '4px' }}>Create Account</h2>
              <p style={{ fontSize: '14px', color: '#667085', marginBottom: '20px' }}>Select your role to begin registration.</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {roleCards.map(r => (
                  <button key={r.key} onClick={() => handleRoleSelect(r.key)} style={{
                    display: 'flex', alignItems: 'center', gap: '12px', padding: '16px', borderRadius: '8px',
                    border: '1px solid #E4E1DC', backgroundColor: '#fff', cursor: 'pointer', textAlign: 'left', width: '100%',
                    transition: 'all 0.15s'
                  }}
                  onMouseOver={e => { (e.currentTarget as HTMLElement).style.borderColor = '#B85C3A'; (e.currentTarget as HTMLElement).style.backgroundColor = '#F6E7E0'; }}
                  onMouseOut={e => { (e.currentTarget as HTMLElement).style.borderColor = '#E4E1DC'; (e.currentTarget as HTMLElement).style.backgroundColor = '#fff'; }}
                  >
                    <div style={{
                      width: '40px', height: '40px', borderRadius: '8px', backgroundColor: '#F6E7E0',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px', flexShrink: 0
                    }}>{r.icon}</div>
                    <div>
                      <div style={{ fontSize: '14px', fontWeight: 500, color: '#1F2428' }}>{r.label}</div>
                      <div style={{ fontSize: '12px', color: '#667085' }}>{r.desc}</div>
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}

          {step === 'register_form' && (
            <>
              <button type="button" onClick={() => { setStep('select_role'); setSelectedRole(null); setServerError(''); }}
                style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '14px', color: '#667085', background: 'none', border: 'none', cursor: 'pointer', marginBottom: '16px', padding: 0 }}>
                ← Back to role selection
              </button>

              <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#1F2428', marginBottom: '4px' }}>
                {selectedRole === 'police' ? 'Police' : selectedRole === 'lawyer' ? 'Lawyer' : 'Court Authority'} Registration
              </h2>
              <p style={{ fontSize: '14px', color: '#667085', marginBottom: '20px' }}>
                Register as {selectedRole === 'police' ? 'a law enforcement officer' : selectedRole === 'lawyer' ? 'a legal practitioner' : 'a judicial officer'}.
              </p>

              {serverError && (
                <div style={{ marginBottom: '16px', padding: '12px 16px', borderRadius: '8px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', fontSize: '14px', color: '#b91c1c' }}>
                  {serverError}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                {selectedRole === 'police' && (
                  <>
                    <Field id="station_code" label="Police Station Code" value={fields.station_code || ''} onChange={v => setField('station_code', v)} error={errors.station_code} placeholder="e.g., PS001" required />
                    <Field id="officer_name" label="Officer Name" value={fields.officer_name || ''} onChange={v => setField('officer_name', v)} error={errors.officer_name} placeholder="Full name" required />
                    <Field id="station_name" label="Station Name" value={fields.station_name || ''} onChange={v => setField('station_name', v)} error={errors.station_name} placeholder="Police station name" required />
                    <Field id="jurisdiction" label="Jurisdiction" value={fields.jurisdiction || ''} onChange={v => setField('jurisdiction', v)} error={errors.jurisdiction} placeholder="District or area" />
                  </>
                )}
                {selectedRole === 'lawyer' && (
                  <>
                    <Field id="full_name" label="Full Name" value={fields.full_name || ''} onChange={v => setField('full_name', v)} error={errors.full_name} placeholder="As per bar registration" required />
                    <Field id="bar_registration_id" label="Bar Registration ID" value={fields.bar_registration_id || ''} onChange={v => setField('bar_registration_id', v)} error={errors.bar_registration_id} placeholder="e.g., BAR/2024/001" required />
                    <Field id="phone" label="Phone Number" value={fields.phone || ''} onChange={v => setField('phone', v)} error={errors.phone} placeholder="+91-XXXXXXXXXX" required />
                    <Field id="address" label="Address" value={fields.address || ''} onChange={v => setField('address', v)} error={errors.address} placeholder="Office address" />
                  </>
                )}
                {selectedRole === 'court_authority' && (
                  <>
                    <Field id="full_name" label="Full Name" value={fields.full_name || ''} onChange={v => setField('full_name', v)} error={errors.full_name} placeholder="Full name" required />
                    <Field id="jo_code" label="JO Code" value={fields.jo_code || ''} onChange={v => setField('jo_code', v)} error={errors.jo_code} placeholder="e.g., JO-2024-001" required />
                    <div style={{ marginBottom: '12px' }}>
                      <label htmlFor="court_id" style={labelStyle}>Court <span style={{ color: '#ef4444' }}>*</span></label>
                      <select id="court_id" value={fields.court_id || ''} onChange={e => setField('court_id', e.target.value)}
                        style={errors.court_id ? inputErrorStyle : inputStyle}>
                        <option value="">Select a court</option>
                        {courts.map(c => <option key={c.id} value={c.id}>{c.name} ({c.type})</option>)}
                      </select>
                      {errors.court_id && <p style={{ fontSize: '12px', color: '#dc2626', marginTop: '4px' }}>{errors.court_id}</p>}
                    </div>
                  </>
                )}
                <Field id="password" label="Password" type="password" value={fields.password || ''} onChange={v => setField('password', v)} error={errors.password} required />
                <Field id="confirm_password" label="Confirm Password" type="password" value={fields.confirm_password || ''} onChange={v => setField('confirm_password', v)} error={errors.confirm_password} required />
                <button type="submit" disabled={loading} style={{ ...btnStyle, opacity: loading ? 0.6 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}>
                  {loading ? 'Registering...' : 'Register'}
                </button>
              </form>
            </>
          )}
        </div>

        <p style={{ textAlign: 'center', fontSize: '14px', color: '#667085', marginTop: '16px' }}>
          Already have an account?{' '}
          <Link href="/login" style={{ color: '#B85C3A', fontWeight: 500, textDecoration: 'none' }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
