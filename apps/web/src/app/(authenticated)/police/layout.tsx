/**
 * Police role route layout.
 *
 * When role authorization is implemented, this layout will verify
 * that the authenticated user has the Police role before rendering
 * child pages. Unauthorized users will receive a 403 response.
 */
export default function PoliceLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
