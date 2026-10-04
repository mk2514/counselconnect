import type { Metadata, Viewport } from 'next';
import { ToastProvider } from '@/components/providers/toast-provider';
import './globals.css';

export const viewport: Viewport = {
  themeColor: '#B85C3A',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

export const metadata: Metadata = {
  title: 'Counsel Connect - Judicial Case Management',
  description:
    'Judicial Case Management Platform connecting Police, Lawyers, and Court Authorities.',
  manifest: '/manifest.json',
  icons: {
    icon: '/icon.svg',
    apple: '/icon.svg',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ToastProvider>{children}</ToastProvider>
      </body>
    </html>
  );
}
