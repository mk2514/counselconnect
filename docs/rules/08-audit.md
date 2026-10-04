# Audit Rules

These rules define the audit logging requirements for all consequential actions in CounselConnect.

## Audit Requirement

Every consequential action must create an audit record.

A consequential action is any operation that changes official state, including but not limited to:

- Case creation, modification, or status changes
- FIR filing or updates
- Lawyer assignment or reassignment
- Hearing scheduling, rescheduling, or cancellation
- Absence request submission, approval, or rejection
- Evidence submission or modification
- Document uploads
- Court agenda changes
- Order issuance
- Judgment recording
- Withdrawal or disposal actions
- User registration or role changes
- Login and authentication events

## Audit Record Fields

Audit events should include the following fields, where applicable:

| Field | Description |
|-------|-------------|
| **Audit ID** | Unique identifier for the audit record |
| **Timestamp** | Date and time of the action (server-side, UTC or with timezone) |
| **Actor user ID** | The authenticated user who performed the action |
| **Actor role** | The role of the user (Police, Lawyer, Court Authority) |
| **CSR** | The Case Status Record associated with the action |
| **Entity type** | The type of entity affected (e.g., "hearing", "absence_request", "evidence") |
| **Entity ID** | The unique identifier of the affected entity |
| **Action** | The operation performed (e.g., "created", "approved", "rejected", "updated") |
| **Old state** | The state of the entity before the action (for updates) |
| **New state** | The state of the entity after the action |
| **Request/session/device metadata** | IP address, session ID, user agent, device info where appropriate |

## Audit Record Integrity

### Append-Oriented

Audit records must be append-oriented. New events are added; existing events are never modified in place.

### No User Editing

Normal application users must not be able to edit previous audit events.

Audit records are permanent, immutable references. The application must not expose any interface or API that allows standard users to modify, delete, or overwrite existing audit entries.
