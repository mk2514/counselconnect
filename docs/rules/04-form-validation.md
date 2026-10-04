# Form Validation Rules

These rules define validation requirements for all forms in CounselConnect, covering both frontend and backend validation, error messaging, and submission protection.

## Dual Validation Requirement

All important forms must have **frontend AND backend validation**.

A frontend validation rule alone is not sufficient. The backend must independently validate all submitted data regardless of what the frontend enforces.

## Required Field Rules

Required fields must enforce all of the following constraints:

| Constraint | Description |
|------------|-------------|
| Not undefined | Field must be present in the submission |
| Not null | Field must have a value |
| Not whitespace-only | Field cannot contain only spaces, tabs, or newlines |
| Not empty string | Field cannot be an empty string (`""`) |
| Not bypassable | Validation cannot be bypassed by modifying browser requests |

### Trimming

Trim textual input before validating where appropriate. Leading and trailing whitespace should not cause a field to pass validation when its trimmed value would fail.

## Error Messages

### Required Field Errors

Each required field must display a clear, specific message identifying the field.

**Correct examples:**
- "FIR number is required."
- "Bar Registration ID is required."
- "Hearing date is required."

**Do not use vague errors such as:**
- "Something went wrong."
- "An error occurred."
- "Invalid input."

### Error Message Content

Where possible, error messages must state:

| Component | Description |
|-----------|-------------|
| **What failed** | Identify the specific field or operation |
| **Why it failed** | Explain the validation rule that was violated |
| **What to correct** | Tell the user what action to take |

## Double-Click Protection

Submit buttons must not create duplicate records when double-clicked.

Implement one or more of the following protections:

- **Frontend:** Disable the submit button after the first click until the response is received.
- **Backend:** Use server-side idempotency keys or request-state protection to reject duplicate submissions.
- **Both:** Apply frontend and backend protection together for critical operations.
