'use client';

import { useState, useCallback, useRef } from 'react';

/**
 * Form validation foundation.
 *
 * Per project rules (docs/rules/04-form-validation.md):
 * - Required fields cannot be undefined, null, whitespace-only, or empty strings
 * - Trim textual input before validating
 * - Each field must display a specific error message
 * - Submit buttons must not create duplicate records (double-click protection)
 */

export interface ValidationRule {
  /** Validation function. Return an error message string if invalid, or null if valid. */
  validate: (value: unknown) => string | null;
}

export interface FieldConfig {
  /** Human-readable field label for error messages */
  label: string;
  /** Whether the field is required */
  required?: boolean;
  /** Additional validation rules beyond the required check */
  rules?: ValidationRule[];
}

export interface UseFormValidationOptions<T extends Record<string, unknown>> {
  fields: Record<keyof T, FieldConfig>;
  onSubmit: (values: T) => Promise<void>;
}

export interface FormValidationResult<T extends Record<string, unknown>> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  isSubmitting: boolean;
  setValue: (field: keyof T, value: unknown) => void;
  setError: (field: keyof T, message: string) => void;
  clearError: (field: keyof T) => void;
  validateField: (field: keyof T) => boolean;
  validateAll: () => boolean;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
}

/**
 * Trim a string value. Returns the original value if not a string.
 */
function trimValue(value: unknown): unknown {
  return typeof value === 'string' ? value.trim() : value;
}

/**
 * Check if a value is empty per project rules:
 * undefined, null, empty string, or whitespace-only string.
 */
function isEmpty(value: unknown): boolean {
  if (value === undefined || value === null) return true;
  if (typeof value === 'string' && value.trim() === '') return true;
  return false;
}

export function useFormValidation<T extends Record<string, unknown>>(
  initialValues: T,
  options: UseFormValidationOptions<T>,
): FormValidationResult<T> {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const submitLockRef = useRef(false);

  const setValue = useCallback((field: keyof T, value: unknown) => {
    setValues((prev) => ({ ...prev, [field]: value }));
    // Clear error when user modifies the field
    setErrors((prev) => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }, []);

  const setError = useCallback((field: keyof T, message: string) => {
    setErrors((prev) => ({ ...prev, [field]: message }));
  }, []);

  const clearError = useCallback((field: keyof T) => {
    setErrors((prev) => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }, []);

  const validateField = useCallback(
    (field: keyof T): boolean => {
      const config = options.fields[field];
      if (!config) return true;

      const rawValue = values[field];
      const trimmed = trimValue(rawValue);

      // Required check
      if (config.required && isEmpty(trimmed)) {
        setErrors((prev) => ({
          ...prev,
          [field]: `${config.label} is required.`,
        }));
        return false;
      }

      // Additional rules
      if (config.rules) {
        for (const rule of config.rules) {
          const error = rule.validate(trimmed);
          if (error) {
            setErrors((prev) => ({ ...prev, [field]: error }));
            return false;
          }
        }
      }

      // Clear any existing error
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
      return true;
    },
    [values, options.fields],
  );

  const validateAll = useCallback((): boolean => {
    let valid = true;
    const newErrors: Partial<Record<keyof T, string>> = {};

    for (const field of Object.keys(options.fields) as Array<keyof T>) {
      const config = options.fields[field];
      const rawValue = values[field];
      const trimmed = trimValue(rawValue);

      if (config.required && isEmpty(trimmed)) {
        newErrors[field] = `${config.label} is required.`;
        valid = false;
        continue;
      }

      if (config.rules) {
        for (const rule of config.rules) {
          const error = rule.validate(trimmed);
          if (error) {
            newErrors[field] = error;
            valid = false;
            break;
          }
        }
      }
    }

    setErrors(newErrors);
    return valid;
  }, [values, options.fields]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      // Double-click protection
      if (submitLockRef.current || isSubmitting) return;

      if (!validateAll()) return;

      submitLockRef.current = true;
      setIsSubmitting(true);

      try {
        // Trim all string values before submission
        const trimmedValues = { ...values };
        for (const key of Object.keys(trimmedValues) as Array<keyof T>) {
          const val = trimmedValues[key];
          if (typeof val === 'string') {
            (trimmedValues as Record<keyof T, unknown>)[key] = val.trim();
          }
        }
        await options.onSubmit(trimmedValues);
      } finally {
        setIsSubmitting(false);
        submitLockRef.current = false;
      }
    },
    [values, isSubmitting, validateAll, options],
  );

  return {
    values,
    errors,
    isSubmitting,
    setValue,
    setError,
    clearError,
    validateField,
    validateAll,
    handleSubmit,
  };
}
