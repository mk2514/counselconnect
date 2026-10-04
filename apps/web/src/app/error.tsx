'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div style={{
      display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center',
      backgroundColor: '#F7F6F3', padding: '16px', fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      <div style={{
        width: '100%', maxWidth: '420px', borderRadius: '8px', border: '1px solid #E4E1DC',
        backgroundColor: '#fff', padding: '32px', textAlign: 'center',
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)'
      }}>
        <div style={{
          width: '48px', height: '48px', borderRadius: '50%', backgroundColor: '#fef2f2',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 16px', fontSize: '24px'
        }}>⚠️</div>
        <h1 style={{ fontSize: '18px', fontWeight: 600, color: '#1F2428', marginBottom: '8px' }}>
          Something went wrong
        </h1>
        <p style={{ fontSize: '14px', color: '#667085', marginBottom: '24px' }}>
          {error.message || 'An unexpected error occurred. Please try again.'}
        </p>
        <button onClick={reset} style={{
          padding: '10px 24px', borderRadius: '8px', fontSize: '14px', fontWeight: 500,
          backgroundColor: '#B85C3A', color: '#fff', border: 'none', cursor: 'pointer'
        }}>
          Try again
        </button>
      </div>
    </div>
  );
}
