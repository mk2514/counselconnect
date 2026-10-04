/**
 * Shared TypeScript types for CounselConnect.
 *
 * These types are co-located in the web app for now.
 * When the packages/shared-types package is populated,
 * shared types should migrate there.
 */

/** Platform user roles */
export type UserRole = 'police' | 'lawyer' | 'court_authority';

/** API error response shape from the backend */
export interface ApiErrorResponse {
  message: string;
  detail?: string;
  errors?: Record<string, string[]>;
}

/** Standard paginated response */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/** Health check response */
export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version?: string;
}

/** Readiness check response */
export interface ReadyResponse {
  status: 'ready' | 'not_ready';
  checks: {
    database: 'connected' | 'disconnected';
    redis: 'connected' | 'disconnected';
  };
}
