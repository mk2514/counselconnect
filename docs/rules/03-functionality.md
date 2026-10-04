# Functionality Rules

These rules govern button behavior, feature readiness, and frontend state management in CounselConnect.

## Buttons Must Perform Their Stated Operation

No button may exist unless it performs its stated operation.

### Examples

| Button Label | Required Behavior |
|---|---|
| "Create Case" | Must open a functioning case creation workflow |
| "Upload FIR" | Must upload a real file |
| "Approve" | Must call a protected backend endpoint and create an audit event |
| "View Case" | Must resolve the requested CSR from the backend |
| "Use NFC" | Must participate in the real NFC authentication workflow |
| "Logout" | Must invalidate the active session |

## Unavailable Features

If a feature is not ready, choose one of the following approaches:

1. **Hide the unavailable function** entirely from the interface.
2. **Clearly mark it as unavailable** in development (e.g., a visible "Coming Soon" or "In Development" label with the control disabled).

**Do not:**
- Display a fake working button
- Silently return success when no operation was performed

## Required Frontend States

Every important frontend action must implement the following states:

| State | Description |
|-------|-------------|
| **Loading** | Visual indicator that the operation is in progress |
| **Success** | Confirmation that the operation completed successfully |
| **Error** | Clear error message explaining what went wrong |
| **Disabled** | Visually distinct state when the action is not available (where appropriate) |

All four states must be implemented for any action that communicates with the backend or performs a consequential operation.
