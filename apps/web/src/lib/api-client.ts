/**
 * API client for communicating with the CounselConnect backend.
 *
 * All requests include credentials for session cookie handling.
 * Error responses are mapped to typed ApiError instances with
 * status, message, and detail information.
 */

const API_BASE_URL = '';

export class ApiError extends Error {
  public readonly status: number;
  public readonly detail: unknown;

  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
  /**
   * If true, do not parse the response as JSON.
   * Useful for endpoints that return no content (204).
   */
  rawResponse?: boolean;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { body, headers: customHeaders, rawResponse, ...rest } = options;

  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;

  const headers: HeadersInit = isFormData
    ? { Accept: 'application/json', ...customHeaders }
    : { 'Content-Type': 'application/json', Accept: 'application/json', ...customHeaders };

  // Remove Content-Type for FormData so the browser sets multipart/form-data with boundary
  if (isFormData && 'Content-Type' in headers) {
    delete (headers as Record<string, string>)['Content-Type'];
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...rest,
    headers,
    body: isFormData ? (body as FormData) : body ? JSON.stringify(body) : undefined,
    credentials: 'include',
  });

  if (!response.ok) {
    let detail: unknown = null;
    try {
      detail = await response.json();
    } catch {
      // Response body may not be JSON
    }

    let message = `Request failed: ${response.status} ${response.statusText}`;
    
    if (detail && typeof detail === 'object') {
      if ('detail' in detail && Array.isArray(detail.detail)) {
        // FastAPI validation error format
        message = detail.detail.map((err: any) => err.msg).join(', ');
      } else if ('detail' in detail && typeof detail.detail === 'string') {
        // FastAPI generic error format
        message = detail.detail;
      } else if ('message' in detail) {
        // Fallback
        message = String((detail as Record<string, unknown>).message);
      }
    }

    throw new ApiError(response.status, message, detail);
  }

  if (rawResponse || response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'POST', body }),

  put: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'PUT', body }),

  patch: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'PATCH', body }),

  delete: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'DELETE' }),
};
