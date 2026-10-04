# Role Security Rules

These rules define authorization enforcement for all protected endpoints in CounselConnect.

## Endpoint Authorization

Every protected backend endpoint must perform role authorization.

**Hiding a frontend menu is NOT authorization.** Authorization must be enforced at the backend API level regardless of what the frontend displays.

## Cross-Role Access Restrictions

| Restriction | Description |
|-------------|-------------|
| Police cannot access Court Authority administrative APIs | Police role is limited to investigation-related operations |
| Lawyer cannot modify the court agenda | Court agenda management is restricted to Court Authority |
| Lawyer cannot access unrelated cases | Lawyers may only access cases where they are an assigned representative |
| Court Authority scope | Court Authority does not automatically receive unrestricted system-administrator powers beyond the defined judicial workflow |

## Per-Request Verification

Every case request must verify:

| Check | Description |
|-------|-------------|
| **Authenticated user** | The request comes from a valid, authenticated session |
| **Role** | The user holds a role that is permitted to perform the action |
| **Case authorization** | The user is authorized to access the specific case/CSR |
| **Action permission** | The user is permitted to perform the specific requested action |

All four checks must pass before the request is processed.

## HTTP Status Codes

| Code | Condition |
|------|-----------|
| **401 Unauthorized** | The request is unauthenticated (no valid session, expired token, missing credentials) |
| **403 Forbidden** | The request is authenticated but the user is not authorized to perform the requested action |

Use the correct status code for each situation. Do not return 401 for authorization failures or 403 for authentication failures.
