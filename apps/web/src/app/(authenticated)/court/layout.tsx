/**
 * Court Authority role route layout.
 *
 * When role authorization is implemented, this layout will verify
 * that the authenticated user has the Court Authority role before
 * rendering child pages. Unauthorized users will receive a 403 response.
 *
 * Per project rules: Court Authority does not automatically receive
 * unrestricted system-administrator powers beyond the defined
 * judicial workflow.
 */
export default function CourtLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
