/**
 * Session handling structure.
 *
 * Provides types and utilities for managing user sessions.
 * Actual session validation will be implemented when the
 * authentication system is built.
 *
 * Per project rules:
 * - Registration before first login
 * - Identity types: Police (Police Station Code), Lawyer (Bar Registration ID), Court Authority (JO Code)
 * - No auto-login for unverified accounts
 */

/** Platform user roles */
export type UserRole = 'police' | 'lawyer' | 'court_authority';

/** Session user data loaded after authentication */
export interface SessionUser {
  id: string;
  role: UserRole;
  displayName: string;
  identifier: string; // Police Station Code, Bar Registration ID, or JO Code
}

/** Session state for the application */
export interface Session {
  user: SessionUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

/** Initial session state before authentication check */
export const INITIAL_SESSION: Session = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
};

/**
 * Get the user-facing label for a role.
 */
export function getRoleLabel(role: UserRole): string {
  const labels: Record<UserRole, string> = {
    police: 'Police',
    lawyer: 'Lawyer',
    court_authority: 'Court Authority',
  };
  return labels[role];
}

/**
 * Get the identifier field label for a role.
 */
export function getIdentifierLabel(role: UserRole): string {
  const labels: Record<UserRole, string> = {
    police: 'Police Station Code',
    lawyer: 'Bar Registration ID',
    court_authority: 'JO Code',
  };
  return labels[role];
}
