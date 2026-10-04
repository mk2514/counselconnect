# Authentication Rules

These rules define registration, login, and identity verification requirements for CounselConnect.

## Registration Before First Login

An identity must be registered before it can authenticate.

### Unregistered Identifier Handling

If someone enters an identifier that is not registered:

- **Do not** silently create an account.
- **Do not** proceed with authentication.
- Return a clear message:

> "Account not registered. Complete registration before signing in."

## Required Identity Types

Each platform actor authenticates with a specific identity type:

| Role | Identity Field | Description |
|------|---------------|-------------|
| Police | Police Station Code | Or configured police identity |
| Lawyer | Bar Registration ID | Unique bar council registration |
| Court Authority | JO Code | Judicial Officer code |

## Registration vs. Login

Registration and login are distinct actions and must be treated as separate workflows.

| Action | Purpose |
|--------|---------|
| **Registration** | Creates and verifies an identity |
| **Login** | Authenticates an existing, verified identity |

### Rules

- Registration creates a new identity record and initiates verification.
- Login authenticates an identity that has already been registered and verified.
- **Do not automatically log in an unverified account.** Verification must complete before the account can be used to authenticate.
- Do not merge registration and login into a single flow that silently creates accounts.
