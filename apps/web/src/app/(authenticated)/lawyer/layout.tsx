/**
 * Lawyer role route layout.
 *
 * When role authorization is implemented, this layout will verify
 * that the authenticated user has the Lawyer role before rendering
 * child pages. Unauthorized users will receive a 403 response.
 */
export default function LawyerLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
