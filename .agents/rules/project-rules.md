# CounselConnect - Mandatory Project Rules

These rules are automatically loaded by AI coding agents working in this repository.
All code changes must comply with these rules. The full rule documents are in `docs/rules/`.

## Critical Architecture Rules

**ONE CSR = ONE CONTINUOUS DIGITAL CASE LIFECYCLE.**

- The platform connects Police, Lawyer, and Court Authority.
- The client/party is NOT a separate user. They exist inside case records, represented through an authorized lawyer.
- Every entity (FIR, hearings, evidence, orders, judgment, audit history, etc.) stays connected to the same CSR.
- Changing lawyers must not create a new CSR.
- Rescheduling must not create a new CSR.
- Withdrawal/disposal must not delete historical records.

## AI Control Model

AI MAY: perform OCR, extract text/metadata, identify names/dates, organize/summarize documents, categorize cases, calculate priority, recommend scheduling, transcribe speech, identify conflicts, summarize absence/withdrawal documents, extract judgment metadata.

AI MUST NOT independently: determine guilt, convict, acquit, issue judgments/orders, approve/reject absences, assign lawyers, approve/reject lawyer retirement, select replacement lawyers, punish lawyers, approve/reject withdrawal, close cases, confirm hearing dates, override Court Authority decisions.

**Required flow: AI proposes -> Human reviews -> Authorized human confirms -> Database changes.**
Never allow AI-generated JSON alone to write consequential official state changes.

## UI Design

- Light theme, judicial/government interface, light sidebar, warm white backgrounds.
- Terracotta is an accent only, not the entire interface.
- Palette: Background `#F7F6F3`, Surface `#FFFFFF`, Sidebar `#FCFBF8`, Primary text `#1F2428`, Secondary text `#667085`, Border `#E4E1DC`, Terracotta `#B85C3A` / `#8E432B` / `#E8B49F` / `#F6E7E0`.
- Status: green (approved), amber (pending), red (rejected/error), blue/neutral (info). Do not misuse terracotta as error color.
- Border radius: 6px-10px. Rectangular buttons with modest rounding.
- One consistent icon library. No emoji icons.
- No: purple/neon/random gradients, glassmorphism, parallax, fake counters/metrics/testimonials, AI artwork, pill-shaped buttons, em dashes in copy.
- See `docs/rules/02-ui-design.md` for the full prohibition list.

## Functionality

- No button may exist unless it performs its stated operation.
- Unavailable features: hide or clearly mark as unavailable. No fake buttons, no silent success.
- Every important action needs: loading, success, error, and disabled states.
- See `docs/rules/03-functionality.md`.

## Form Validation

- Frontend AND backend validation required.
- Required fields: not undefined, not null, not whitespace-only, not empty, not bypassable.
- Trim before validate. Specific error messages (e.g., "FIR number is required."). No vague errors.
- Double-click protection / idempotency on submit buttons.
- See `docs/rules/04-form-validation.md`.

## Authentication

- Registration before first login. No silent account creation.
- Identity types: Police (Police Station Code), Lawyer (Bar Registration ID), Court Authority (JO Code).
- Registration and login are separate actions. No auto-login for unverified accounts.
- See `docs/rules/05-authentication.md`.

## Role Security

- Every protected endpoint must perform role authorization. Frontend menu hiding is NOT authorization.
- Police cannot access Court Authority APIs. Lawyer cannot modify court agenda or access unrelated cases.
- Verify: authenticated user, role, case authorization, action permission.
- 401 for unauthenticated. 403 for unauthorized.
- See `docs/rules/06-role-security.md`.

## Data Integrity

- Use database transactions for multi-step operations. Roll back on failure.
- Use foreign keys, unique constraints, indexes.
- No relational data in arbitrary JSON fields. No localStorage as authoritative database.
- See `docs/rules/07-data-integrity.md`.

## Audit

- Every consequential action creates an audit record with: audit ID, timestamp, actor user ID, actor role, CSR, entity type, entity ID, action, old state, new state, metadata.
- Append-oriented. Normal users cannot edit audit events.
- See `docs/rules/08-audit.md`.

## Security

- No plaintext passwords. Use Argon2id for password hashing.
- Never put passwords, tokens, credentials, or personal case info on NFC cards.
- File uploads: validate MIME type, extension, size; generate safe filenames; prevent path traversal.
- Brute-force protection, rate limiting, secure cookies, CSRF protection.
- Secrets in environment variables. Never commit secrets.
- See `docs/rules/09-security.md`.

## Accessibility

- Labels on every field. Keyboard navigation must work. Visible focus states. Dialog focus trapping.
- Important controls must not rely only on color. Tables need headings. Status indicators need text labels.
- Do not sacrifice accessibility for visual styling.
- See `docs/rules/10-accessibility.md`.

## Responsive Design

- Primary target: desktop/laptop. Also support tablets. Mobile for: login, NFC, case lookup, key lawyer ops, document capture.
- Do not compress complex interfaces into unusable mobile layouts.
- See `docs/rules/11-responsive-design.md`.

## Tech Stack Lock

- All technology choices are FINAL. See `docs/rules/12-tech-stack-lock.md`.
- Frontend: Next.js + TypeScript + Tailwind CSS + shadcn/ui + Lucide React.
- Backend: FastAPI + Pydantic + SQLAlchemy + Alembic.
- Database: PostgreSQL + pgvector. File Storage: MinIO. Cache/Broker: Redis.
- Background: Celery + Redis. OCR: OpenCV + PaddleOCR. LLM: Ollama + Qwen. STT: faster-whisper.
- Auth: Secure HttpOnly cookies + Argon2id + WebAuthn/Passkeys. Authorization: RBAC + case-level.
- Scheduling: Google OR-Tools. Priority: Deterministic Rule Engine. Deployment: Docker + Nginx.
- Do not substitute technologies without explicit approval.
