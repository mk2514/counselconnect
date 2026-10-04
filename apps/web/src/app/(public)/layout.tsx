/**
 * Public route group layout.
 * Pages within this group (login, register) render without
 * the authenticated shell (sidebar, header).
 * 
 * Each page handles its own centering/layout to avoid nesting conflicts.
 */
export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
