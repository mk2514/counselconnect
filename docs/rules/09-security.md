# Security Rules

These rules define password handling, NFC card security, file upload protection, authentication hardening, and secrets management for CounselConnect.

## Password Security

Passwords must **never** be stored as plaintext.

Use established password hashing algorithms (e.g., bcrypt, scrypt, Argon2). Store only the hashed value with a unique salt per password.

## NFC Card Security

Never place any of the following on an NFC card:

| Prohibited Data |
|-----------------|
| Password |
| Access token |
| Refresh token |
| Private credentials |
| Personal case information |

NFC cards may contain only non-sensitive identifiers or references that are validated server-side.

## File Upload Protection

All file upload functionality must enforce the following protections:

| Protection | Description |
|------------|-------------|
| **MIME type validation** | Validate the MIME type of uploaded files against an allowed list |
| **Extension validation** | Validate file extensions against an allowed list |
| **File size limits** | Enforce configurable file size limits |
| **Safe server filenames** | Generate safe, sanitized filenames on the server side |
| **Untrusted user filenames** | Do not trust user-provided filenames for storage or display |
| **Path traversal prevention** | Prevent directory traversal attacks (e.g., `../` in filenames) |

## Authentication Hardening

### Brute-Force Protection

Protect authentication endpoints against brute-force attacks. Implement account lockout, progressive delays, or similar mechanisms after repeated failed attempts.

### Rate Limiting

Apply rate limiting where appropriate, including but not limited to:

- Login endpoints
- Registration endpoints
- Password reset endpoints
- API endpoints with sensitive operations

## Session and Request Security

### Secure Cookies

Use secure cookies where session cookies are used:

- Set the `Secure` flag (HTTPS only)
- Set the `HttpOnly` flag (no JavaScript access)
- Set appropriate `SameSite` attribute

### CSRF Protection

Use CSRF protection where the architecture requires it. Any state-changing request that relies on cookie-based authentication must be protected against cross-site request forgery.

## Secrets Management

### Environment Variables

Use environment variables for secrets, including but not limited to:

- Database credentials
- API keys
- JWT signing keys
- Third-party service credentials
- Encryption keys

### No Committed Secrets

- Do not commit secrets to version control.
- Do not put production credentials in source code.
- Use `.env` files locally and ensure they are listed in `.gitignore`.
- Use secure secrets management in production environments.
