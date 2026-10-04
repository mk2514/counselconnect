import { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Counsel Connect - Judicial Case Management',
    short_name: 'CounselConnect',
    description: 'Judicial Case Management Platform connecting Police, Lawyers, and Court Authorities.',
    start_url: '/',
    display: 'standalone',
    background_color: '#FDFCFB',
    theme_color: '#B85C3A',
    icons: [
      {
        src: '/icon.svg',
        sizes: '192x192',
        type: 'image/svg+xml',
      },
      {
        src: '/icon.svg',
        sizes: '512x512',
        type: 'image/svg+xml',
      },
    ],
  };
}
