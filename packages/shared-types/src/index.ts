/**
 * Shared types for CounselConnect.
 *
 * Types in this package are shared across the frontend application
 * and any other TypeScript packages in the monorepo.
 */

/** Platform user roles */
export type UserRole = 'police' | 'lawyer' | 'court_authority';

/** Audit action types */
export type AuditAction =
  | 'created'
  | 'updated'
  | 'deleted'
  | 'approved'
  | 'rejected'
  | 'assigned'
  | 'reassigned'
  | 'submitted'
  | 'withdrawn'
  | 'scheduled'
  | 'rescheduled'
  | 'cancelled';

/** Base entity with common fields */
export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

/** Case Status Record - the central organizing entity */
export interface CSR extends BaseEntity {
  csrNumber: string;
  status: string;
}
