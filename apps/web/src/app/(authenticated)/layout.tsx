import { AuthenticatedShell } from '@/components/layout/authenticated-shell';

/**
 * Authenticated route group layout.
 *
 * All pages within this group render inside the AuthenticatedShell
 * which fetches the user profile securely, constructs role-based nav,
 * and renders the sidebar, top header, and main content area.
 */
export default function AuthenticatedLayout({ children }: { children: React.ReactNode }) {
  return <AuthenticatedShell>{children}</AuthenticatedShell>;
}
