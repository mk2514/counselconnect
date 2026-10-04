/**
 * Shared validation utilities for CounselConnect.
 *
 * Per project rules (docs/rules/04-form-validation.md):
 * - Required fields: not undefined, not null, not whitespace-only, not empty
 * - Trim before validate
 * - Specific error messages
 */

/**
 * Check if a value is empty per project rules.
 */
export function isEmpty(value: unknown): boolean {
  if (value === undefined || value === null) return true;
  if (typeof value === 'string' && value.trim() === '') return true;
  return false;
}

/**
 * Validate a required field and return a specific error message.
 */
export function validateRequired(value: unknown, fieldLabel: string): string | null {
  if (isEmpty(value)) {
    return `${fieldLabel} is required.`;
  }
  return null;
}

/**
 * Validate minimum length after trimming.
 */
export function validateMinLength(
  value: unknown,
  minLength: number,
  fieldLabel: string,
): string | null {
  if (typeof value !== 'string') return null;
  if (value.trim().length < minLength) {
    return `${fieldLabel} must be at least ${minLength} characters.`;
  }
  return null;
}

/**
 * Validate maximum length.
 */
export function validateMaxLength(
  value: unknown,
  maxLength: number,
  fieldLabel: string,
): string | null {
  if (typeof value !== 'string') return null;
  if (value.length > maxLength) {
    return `${fieldLabel} must not exceed ${maxLength} characters.`;
  }
  return null;
}
